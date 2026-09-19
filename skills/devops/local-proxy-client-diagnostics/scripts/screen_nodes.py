# -*- coding: utf-8 -*-
"""节点可用性筛查（沙盒法）—— 判定哪些节点能调 Antigravity Gemini，零生成配额。

为什么用沙盒而不是直接切节点：
    Karing 的 clash API 不暴露节点切换（GLOBAL 是 Fallback 类型，/proxies/GLOBAL 返回 404，
    PUT 报 Must be a Selector），且本地所有端口（3065 强制直连 / 3066 强制代理 / 3067 规则）
    都走同一个当前选中节点。要批量测，只能自己起一个 sing-box 实例，每个节点一个本地端口。

三个必须知道的坑（均实测）：
    1. 机场用动态 DNS 轮换 IP —— 系统 DNS 常拿到过期 IP（实测系统 DNS 全部超时、
       DoH 拿到的新 IP 全部 80~124ms 可达）。必须经代理 DoH 解析，否则活节点全被判“不通”。
    2. countTokens / loadCodeAssist 对区域受限节点也返回 200，不能判别；
       参数校验失败也会先于区域检查。必须打生成端点 + “校验通过但不产出”的请求体，
       才能让请求走到区域检查那一层（否则只是连通测试，会严重高估可用节点数）。
    3. 单次/3 轮结果不可信 —— 同一节点可在 PASS/REGION 间大幅摆动
       （实测香港 1/10、台湾 4/10、日本-aw 10/10）。至少 10 轮统计通过率。

用法：
    python screen_nodes.py                        # 全部节点，每节点 10 轮
    python screen_nodes.py --rounds 5 --filter anytls
    python screen_nodes.py --model gemini-3.8-flash-high

依赖：curl、Karing 运行中（3067 可用）、CPA auth 目录下有 antigravity-*.json。
会自动下载并缓存 sing-box（版本对齐 Karing 内核）。不会修改任何 Karing 配置。
"""

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from collections import Counter

KARING_CTL = "http://127.0.0.1:3057"       # Karing clash 控制口
PROXY_PORT = 3067                          # Karing 规则端口（用于 DoH 解析与下载）
GEN_URL = "https://daily-cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse"
CACHE_DIR = pathlib.Path(os.environ.get("LOCALAPPDATA", ".")) / "hermes" / "cache" / "sing-box"


# ─────────────────────────── Karing ───────────────────────────

def karing_dir() -> pathlib.Path:
    p = pathlib.Path(os.environ.get("APPDATA", "")) / "karing" / "karing"
    if not p.is_dir():
        sys.exit(f"未找到 Karing 配置目录：{p}")
    return p


def karing_secret() -> str:
    return json.loads((karing_dir() / "service.json").read_text(encoding="utf-8"))["secret"]


def karing_version() -> str:
    req = urllib.request.Request(f"{KARING_CTL}/version",
                                 headers={"Authorization": f"Bearer {karing_secret()}"})
    with urllib.request.urlopen(req, timeout=8) as r:
        v = json.loads(r.read()).get("version", "")
    m = re.search(r"(\d+\.\d+\.\d+)", v)
    return m.group(1) if m else "1.13.19"


def load_nodes(flt: str = "") -> list[dict]:
    """从 service_core.json 取可作出口的节点（剔除 selector/urltest/direct/block）。"""
    core = json.loads((karing_dir() / "service_core.json").read_text(encoding="utf-8"))
    skip = {"selector", "urltest", "direct", "block"}
    out = []
    for o in core.get("outbounds", []):
        if o.get("type") in skip:
            continue
        n = json.loads(json.dumps(o))          # deep copy
        n.pop("domain_resolver", None)         # 引用的是 Karing 自己的 DNS tag
        out.append(n)
    if flt:
        out = [n for n in out if flt in (n.get("tag") or "")]
    return out


# ──────────────────── 新鲜 IP（经代理 DoH） ────────────────────

def resolve_fresh(hostname: str) -> list[str]:
    """经 Karing 代理查 DoH，拿当前生效的 IP。系统 DNS 可能是过期缓存。"""
    q = urllib.parse.urlencode({"name": hostname, "type": "A"})
    cmd = ["curl", "-s", "-m", "20", "-x", f"http://127.0.0.1:{PROXY_PORT}",
           f"https://dns.google/resolve?{q}"]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=26)
        d = json.loads(p.stdout.decode("utf-8", errors="replace"))
        ips = [a["data"] for a in d.get("Answer", []) if a.get("type") == 1]
        return ips
    except Exception:
        return []


def pin_fresh_ips(nodes: list[dict]) -> None:
    """就地把节点的 server 换成经 DoH 解析、**且已验证 TCP 可达**的新鲜 IP。

    机场的 IP 轮换很快（实测：上一次抓到的 IP 几分钟后就全超时），所以只解析不够，
    必须逐个试连；全部不可达时保留域名交给沙盒自己的解析器，并在沙盒起后用连通性预检报道。
    """
    import socket

    def tcp_ok(ip: str, port: int, t: float = 4.0) -> bool:
        s = socket.socket(); s.settimeout(t)
        try:
            s.connect((ip, port)); return True
        except Exception:
            return False
        finally:
            s.close()

    cache: dict[str, list[str]] = {}
    for n in nodes:
        host = n.get("server", "")
        if not host or re.match(r"^[\d.]+$", host) or ":" in host:
            continue                                  # 已是字面 IP
        port = int(n.get("server_port") or 443)
        if host not in cache:
            sys_ips: list[str] = []
            try:
                sys_ips = sorted({ai[4][0] for ai in socket.getaddrinfo(host, None, socket.AF_INET)})
            except Exception:
                pass
            doh_ips = resolve_fresh(host)
            # 去重排序：DoH 在前（更新鲜），系统解析兜底
            cands = list(dict.fromkeys([*doh_ips, *sys_ips]))
            reachable = [ip for ip in cands if tcp_ok(ip, port)]
            cache[host] = reachable
            print(f"  {host}: 系统={sys_ips or '无'} DoH={doh_ips or '无'} → 可达={reachable or '无'}")
        if cache[host]:
            n["_orig_server"] = host
            n["server"] = cache[host][0]
        # 无可达 IP 时保留域名：沙盒自己的解析器可能比这里宽容


# ────────────────────── sing-box 沙盒 ──────────────────────

def ensure_singbox() -> pathlib.Path:
    """找/下载 sing-box 可执行文件（版本对齐 Karing 内核）。"""
    ver = karing_version()
    exe_name = "sing-box.exe" if os.name == "nt" else "sing-box"
    target = CACHE_DIR / f"v{ver}" / exe_name
    if target.is_file():
        return target

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    asset = {"nt": "windows-amd64", "posix": "linux-amd64"}.get(os.name, "linux-amd64")
    zip_name = f"sing-box-{ver}-{asset}.zip"
    url = f"https://github.com/SagerNet/sing-box/releases/download/v{ver}/{zip_name}"
    zp = CACHE_DIR / zip_name
    if not zp.is_file():
        print(f"  下载 sing-box {ver} …")
        cmd = ["curl", "-sL", "-m", "180", "-x", f"http://127.0.0.1:{PROXY_PORT}",
               "-o", str(zp), "-w", "%{http_code}", url]
        p = subprocess.run(cmd, capture_output=True, timeout=200)
        if p.stdout.decode().strip() != "200" or not zp.is_file():
            sys.exit(f"sing-box 下载失败（{p.stdout.decode().strip()}）。可从 {url} 手动下载到 {CACHE_DIR}")
    dest = CACHE_DIR / f"v{ver}"
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zp) as z:
        for m in z.namelist():
            if m.endswith(exe_name):
                with z.open(m) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                break
    if os.name != "nt":
        target.chmod(0o755)
    if not target.is_file():
        sys.exit(f"解压后未找到 {exe_name}（压缩包结构可能变了）")
    return target


def build_sandbox(nodes: list[dict], base_port: int, cfg: pathlib.Path, portmap: pathlib.Path):
    """每节点一个本地 mixed 入站；端口即节点。每个节点分配不同的可达 IP（多 IP 时可均衡）。"""
    inbounds, rules, pm = [], [], {}
    for i, n in enumerate(nodes):
        port = base_port + i
        inbounds.append({"type": "mixed", "tag": f"in_{i}",
                         "listen": "127.0.0.1", "listen_port": port})
        rules.append({"inbound": [f"in_{i}"], "outbound": n["tag"]})
        pm[str(port)] = n["tag"]
        n.pop("_orig_server", None)
    conf = {
        "log": {"level": "error", "output": "sb.log", "timestamp": True},
        "dns": {"servers": [{"tag": "dns_local", "type": "local"}],
                "final": "dns_local", "strategy": "ipv4_only"},
        "inbounds": inbounds,
        "outbounds": nodes + [{"type": "direct", "tag": "direct_out"},
                              {"type": "block", "tag": "block_out"}],
        "route": {"rules": rules, "final": "direct_out"},
    }
    cfg.write_text(json.dumps(conf, ensure_ascii=False, indent=1), encoding="utf-8")
    portmap.write_text(json.dumps(pm, ensure_ascii=False, indent=1), encoding="utf-8")
    return pm


# ───────────────── 零消耗判别器 ─────────────────

def load_credentials() -> tuple[str, str]:
    """从 CPA auth 目录读 antigravity 凭据。token 不打印、不落盘。

    查找顺序：环境变量 CPA_AUTH_DIR > 常见默认位置 > 自动扫盘（常见盘符的
    一级目录下叫 *CLIProxyAPI* 的文件夹）。自动扫盘是为了让本机开箱即用，
    同时不把具体盘符/用户名写死在技能文件里。
    """
    cands: list[pathlib.Path] = []
    for env in ("CPA_AUTH_DIR", "CLI_PROXY_API_AUTH_DIR"):
        v = os.environ.get(env)
        if v:
            cands.append(pathlib.Path(v))
    cands += [pathlib.Path.home() / ".cli-proxy-api" / "auth",
              pathlib.Path(os.environ.get("LOCALAPPDATA", "")) / "cli-proxy-api"]

    # 自动扫盘（仅在前面都没命中时）
    for drive in ("C:", "D:", "E:"):
        try:
            for d in pathlib.Path(drive + "\\").iterdir():
                if d.is_dir() and "cliproxyapi" in d.name.lower():
                    cands.append(d / "auth")
                    cands.append(d / "cpa-core" / "auth")
        except Exception:
            continue

    for base in cands:
        if not base.is_dir():
            continue
        for f in sorted(base.glob("antigravity-*.json")):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if d.get("access_token"):
                return d["access_token"], d.get("project_id") or "aicode-consumers"
    sys.exit("未找到 antigravity 凭据。请设置 CPA_AUTH_DIR 环境变量指向含 antigravity-*.json 的目录。")


def probe(port: int, token: str, project: str, model: str, timeout: int = 20) -> str:
    """零消耗判别：校验通过（能触达区域检查）但不产生输出 token。
    返回 PASS / REGION / TIMEOUT / ERR<code>。"""
    body = {"model": model, "project": project,
            "request": {"contents": [{"role": "user", "parts": [{"text": ""}]}],
                        "generationConfig": {"maxOutputTokens": 1}}}
    cmd = ["curl", "-s", "-m", str(timeout),
           "-x", f"http://127.0.0.1:{port}", "-X", "POST",
           "-H", f"Authorization: Bearer {token}",
           "-H", "Content-Type: application/json",
           "-H", "User-Agent: antigravity/2.15.0 (windows/amd64)",
           "-d", json.dumps(body),
           "-o", "-", "-w", "\n#CODE#%{http_code}", GEN_URL]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout + 8)
        out = p.stdout.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERR({type(e).__name__})"
    if "User location" in out:
        return "REGION"
    if '"response"' in out:
        return "PASS"
    code = out.rsplit("#CODE#", 1)[-1].strip() if "#CODE#" in out else "000"
    return f"ERR{code}"


# ─────────────────────────── 主流程 ───────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=10,
                    help="每节点采样轮数（默认 10；低于 10 结论不可信）")
    ap.add_argument("--filter", default="", help="只测 tag 含此子串的节点")
    ap.add_argument("--model", default="gemini-3.8-flash-high")
    ap.add_argument("--base-port", type=int, default=30200)
    ap.add_argument("--keep", action="store_true", help="保留沙盒（调试用）")
    args = ap.parse_args()

    work = pathlib.Path(os.environ.get("LOCALAPPDATA", ".")) / "Temp" / "node-screen"
    work.mkdir(parents=True, exist_ok=True)
    cfg, portmap = work / "cfg.json", work / "portmap.json"

    print("[1/5] 读取节点…")
    nodes = load_nodes(args.filter)
    if not nodes:
        sys.exit("没有匹配的节点")
    print(f"      {len(nodes)} 个出口节点")

    print("[2/5] 经代理 DoH 解析新鲜 IP（系统 DNS 可能是过期缓存）…")
    pin_fresh_ips(nodes)

    print("[3/5] 准备沙盒…")
    sb = ensure_singbox()
    pm = build_sandbox(nodes, args.base_port, cfg, portmap)
    chk = subprocess.run([str(sb), "check", "-c", str(cfg)], capture_output=True, timeout=30)
    if chk.returncode != 0:
        sys.exit(f"配置校验失败：{chk.stderr.decode('utf-8','replace')[:400]}")
    proc = subprocess.Popen([str(sb), "run", "-c", str(cfg)], cwd=str(work),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4)

    # 连通性预检：先确认沙盒真的能出网。否则后面每一轮 20s 超时会白烧几分钟，
    # 而且会把“IP 轮换失效”误报成“该节点被区域拒绝”（两者必须区分）。
    print("      连通性预检…")
    offline = []
    for port_s, tag in pm.items():
        try:
            r = subprocess.run(["curl", "-s", "-m", "10",
                                "-x", f"http://127.0.0.1:{port_s}", "-o", "/dev/null",
                                "-w", "%{http_code}", "https://www.gstatic.com/generate_204"],
                               capture_output=True, timeout=16)
            if r.stdout.decode().strip() not in ("204", "200"):
                offline.append(tag)
        except Exception:
            offline.append(tag)
    if len(offline) == len(pm):
        print("\n❌ 所有节点都连不上（沙盒无法出网）。最可能原因：")
        print("   机场 IP 再次轮换，上面解析到的 IP 已失效。请稍后重跑，或检查 Karing 是否在线。")
        print("   ——这种情况下测出的“区域拒绝”是假的，不要采信。\n")
    elif offline:
        print(f"      {len(offline)}/{len(pm)} 个节点预检不通（其结果将标为 ⚪ 网络不可达）：")
        for t in offline:
            print(f"        - {t}")

    try:
        print("[4/5] 零消耗探针…")
        token, project = load_credentials()
        print(f"{'节点':<34} {'通过率':<8} 明细")
        print("-" * 78)
        results = {}
        for port_s, tag in sorted(pm.items(), key=lambda x: int(x[0])):
            seq = [probe(int(port_s), token, project, args.model) for _ in range(args.rounds)]
            c = Counter(seq)
            pass_rate = c["PASS"] / args.rounds
            # 区分三种失败：区域拒绝 / 网络不可达 / 其他错误。
            # 网络不可达与区域判定无关，不能计入“不可用”。
            net_fail = sum(v for k, v in c.items() if k in ("TIMEOUT",) or k.startswith("ERR0"))
            results[tag] = {"pass_rate": pass_rate, "counts": dict(c), "port": int(port_s),
                            "net_fail": net_fail}
            bar = "█" * c["PASS"] + "░" * (args.rounds - c["PASS"])
            note = "  ⚠网络不可达" if net_fail > args.rounds / 2 else ""
            print(f"  {tag:<32} {c['PASS']:>2}/{args.rounds}  {bar}  {dict(c)}{note}")

        print("\n" + "=" * 78)
        print("排序结论（阈值：≥90% 稳定 / 50~90% 高抖动 / <50% 基本不可用）")
        print("=" * 78)
        for tag, r in sorted(results.items(), key=lambda x: -x[1]["pass_rate"]):
            rate = r["pass_rate"]
            if r.get("net_fail", 0) > args.rounds / 2:
                verdict = "⚪ 网络不可达"
            else:
                verdict = "🟢 稳定可用" if rate >= 0.9 else ("🟡 高抖动" if rate >= 0.5 else "🔴 基本不可用")
            print(f"  {verdict:<12} {tag:<34} {rate*100:>5.0f}%")

        out = work / "result.json"
        out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n结果：{out}")
    finally:
        print("[5/5] 清理沙盒…")
        if not args.keep:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except Exception:
                proc.kill()


if __name__ == "__main__":
    main()
