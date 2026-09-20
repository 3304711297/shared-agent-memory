# -*- coding: utf-8 -*-
"""DNS 槽位选型基准测试 —— 对比 Karing 内置 DNS 清单在各槽位的表现。

指标（按用户优先级：可用性 > 延迟 > 网速）：
  ① 解析成功率（可用性）
  ② 解析往返耗时（延迟）
  ③ 返回 IP 的实际 TCP 连接耗时（网速 —— 最有说服力，直接对应浏览体验）

用法：改 SLOT 变量。先确保客户端已连上（节点可用），否则槽②与槽④测不了。

【关键】本脚本含正确的 DNS 报文解析（CNAME + 名称压缩指针）。
  自己写 DNS 探测时最常见的两类误报：
   - 未处理压缩指针 \xc0\x0c ⇒ 遇 CNAME 先导的响应（阿里/Cloudflare）解析失败
   - DoT 裸 socket 未调 connect() 就握手 ⇒ 全部误报失败
  另：DoH 的 ?dns= 是 base64url 二进制（RFC 8484）；?name= 是 Google/CF 的 JSON 扩展，
  拿 ?name= 测阿里会得到 "no 'dns' query parameter found"——不是网络问题。
"""
import base64
import json
import os
import random
import re
import socket
import ssl
import statistics
import struct
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

SLOT = "direct"          # "direct" = 直连流量槽（解析国内域名）
                         # "outbound" = 代理服务器槽（解析节点域名）
                         # "throughput" = 网速实测（钉住各解析器给出的 IP 下载，含同IP对照组）
ROUNDS = 2               # 每个测点重复次数（取中位，A/B 交错）

# throughput 模式用：国内镜像站（大文件，同一路径便于公平比较）
THROUGHPUT_TARGETS = [
    ("mirrors.aliyun.com", "/ubuntu/ls-lR.gz"),
    ("mirrors.cloud.tencent.com", "/ubuntu/ls-lR.gz"),
    ("mirrors.huaweicloud.com", "/ubuntu/ls-lR.gz"),
    ("mirrors.163.com", "/ubuntu/ls-lR.gz"),
    ("mirror.nju.edu.cn", "/ubuntu/ls-lR.gz"),
    ("mirrors.bfsu.edu.cn", "/ubuntu/ls-lR.gz"),
    ("mirrors.zju.edu.cn", "/ubuntu/ls-lR.gz"),
    ("mirrors.pku.edu.cn", "/ubuntu/ls-lR.gz"),
]
MAX_BYTES = 20_000_000   # 单次下载上限（省流量）
MAX_TIME = 8             # 单次下载最长时间（秒）

ENV = {k: v for k, v in os.environ.items()
       if k.upper() not in ("ALL_PROXY", "HTTP_PROXY", "HTTPS_PROXY")}

# 槽③：国内域名（要连 443）
CN_DOMAINS = ["www.baidu.com", "www.taobao.com", "www.bilibili.com", "www.qq.com",
              "www.jd.com", "www.163.com", "www.zhihu.com", "www.ctrip.com",
              "www.meituan.com", "www.sina.com.cn"]


# ─────────── DNS 报文解析（含 CNAME + 压缩指针）───────────
def read_name(data, off):
    labels, jumped, orig = [], False, off
    while True:
        if off >= len(data):
            break
        ln = data[off]
        if ln & 0xC0 == 0xC0:
            ptr = struct.unpack(">H", data[off:off + 2])[0] & 0x3FFF
            if not jumped:
                orig, jumped = off + 2, True
            off = ptr
            continue
        if ln == 0:
            off += 1
            break
        off += 1
        labels.append(data[off:off + ln].decode("latin1"))
        off += ln
    return ".".join(labels), (orig if jumped else off)


def parse_dns(data):
    """遍历全部 answer 收集 A 记录（跳过 CNAME）"""
    if len(data) < 12:
        return []
    _, _, qd, an, _, _ = struct.unpack(">HHHHHH", data[:12])
    off = 12
    for _ in range(qd):
        _, off = read_name(data, off)
        off += 4
    ips = []
    for _ in range(an):
        _, off = read_name(data, off)
        if off + 10 > len(data):
            break
        rtype, _, ttl, rdlen = struct.unpack(">HHIH", data[off:off + 10])
        off += 10
        rd = data[off:off + rdlen]
        if rtype == 1 and rdlen == 4:
            ips.append(".".join(map(str, rd)))
        off += rdlen
    return ips


def build(d, qtype=1):
    tid = random.randint(0, 0xFFFF)
    hdr = struct.pack(">HHHHHH", tid, 0x0100, 1, 0, 0, 0)
    q = b"".join(bytes([len(p)]) + p.encode() for p in d.split(".")) + b"\x00"
    return hdr + q + struct.pack(">HH", qtype, 1)


# ─────────── 各协议查询 ───────────
def q_udp(host, d, timeout=4.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(build(d), (host, 53))
        data, _ = s.recvfrom(4096)
        return parse_dns(data)
    except Exception:
        return []
    finally:
        s.close()


def q_dot(host, d, force_ip=None, timeout=6.0):
    """DoT：注意必须 connect() 后再 wrap_socket（漏掉是常见误报源）"""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    raw = socket.socket()
    raw.settimeout(timeout)
    try:
        raw.connect((force_ip or host, 853))
        ss = ctx.wrap_socket(raw, server_hostname=host)
        pkt = build(d)
        ss.sendall(struct.pack(">H", len(pkt)) + pkt)
        ln = struct.unpack(">H", ss.recv(2))[0]
        buf = b""
        while len(buf) < ln:
            c = ss.recv(ln - len(buf))
            if not c:
                break
            buf += c
        return parse_dns(buf)
    except Exception:
        return []
    finally:
        raw.close()


def q_doh(url, d, proxy=None, timeout=7):
    if not url.startswith("http"):
        url = f"https://{url}"
    b64 = base64.urlsafe_b64encode(build(d)).decode().rstrip("=")
    cmd = ["curl", "-sS", "--max-time", str(timeout), "-k",
           "-H", "content-type: application/dns-message"]
    if proxy:
        cmd += ["--proxy", proxy]
    cmd.append(f"{url}?dns={b64}")
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout + 3, env=ENV)
        return parse_dns(r.stdout)
    except Exception:
        return []


def q_local(d):
    try:
        return sorted({i[4][0] for i in getattr(socket, "getaddrinfo")(d, 443, socket.AF_INET)})
    except Exception:
        return []


def tcp_best(ip, port=443, tries=2, timeout=3.0):
    best = None
    for _ in range(tries):
        t0 = time.perf_counter()
        s = socket.socket()
        s.settimeout(timeout)
        try:
            s.connect((ip, port))
            v = (time.perf_counter() - t0) * 1000
            best = v if best is None else min(best, v)
        except Exception:
            pass
        finally:
            s.close()
    return best


# ─────────── 内置清单（source: setting_manager.dart SettingConfigItemDNS）───────────
CATALOG = [
    ("Local(系统/路由器)", lambda d: q_local(d)),
    ("AliDNS udp 223.5.5.5", lambda d: q_udp("223.5.5.5", d)),
    ("AliDNS udp 223.6.6.6", lambda d: q_udp("223.6.6.6", d)),
    ("AliDNS dot 223.5.5.5", lambda d: q_dot("223.5.5.5", d)),
    ("AliDNS dot 域名", lambda d: q_dot("dns.alidns.com", d, "223.5.5.5")),
    ("AliDNS doh 223.5.5.5", lambda d: q_doh("https://223.5.5.5/dns-query", d)),
    ("AliDNS doh 域名", lambda d: q_doh("https://dns.alidns.com/dns-query", d)),
    ("DNSPod dot.pub", lambda d: q_dot("dot.pub", d, "1.12.12.12")),
    ("DNSPod doh 1.12.12.12", lambda d: q_doh("https://1.12.12.12/dns-query", d)),
    ("DNSPod doh 域名", lambda d: q_doh("https://doh.pub/dns-query", d)),
    ("TrafficRoute 180.184.1.1", lambda d: q_udp("180.184.1.1", d)),
    ("TrafficRoute 180.184.2.2", lambda d: q_udp("180.184.2.2", d)),
    ("Google udp 8.8.8.8", lambda d: q_udp("8.8.8.8", d)),
    ("Google udp 8.8.4.4", lambda d: q_udp("8.8.4.4", d)),
    ("CF udp 1.1.1.1", lambda d: q_udp("1.1.1.1", d)),
    ("CF dot 1.1.1.1", lambda d: q_dot("1.1.1.1", d)),
    ("CF doh 域名", lambda d: q_doh("https://cloudflare-dns.com/dns-query", d)),
    ("Google doh 域名", lambda d: q_doh("https://dns.google/dns-query", d)),
    ("AdGuard udp 94.140.14.14", lambda d: q_udp("94.140.14.14", d)),
    ("OpenDNS 208.67.222.222", lambda d: q_udp("208.67.222.222", d)),
    ("Comodo 8.26.56.26", lambda d: q_udp("8.26.56.26", d)),
    ("Yandex 77.88.8.8", lambda d: q_udp("77.88.8.8", d)),
]


def node_domains():
    """从运行态配置取节点域名 + 端口（供槽②）"""
    import re
    kr = os.path.join(os.environ["APPDATA"], "karing", "karing", "service_core.json")
    try:
        core = json.load(open(kr, encoding="utf-8"))
    except Exception:
        return []
    pat = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9.\-]*\.[a-zA-Z]{2,}$")
    seen = {}
    for o in core.get("outbounds", []):
        sv = o.get("server")
        if isinstance(sv, str) and pat.match(sv):
            seen.setdefault(sv, o.get("server_port", 443))
    return list(seen.items())[:8]


def download_speed(host, path, ip, tmpfile, max_time=MAX_TIME, max_bytes=MAX_BYTES):
    """钉住 IP 实测下载。返回 (MB/s, 连接ms, 字节, http码)

    注意：Windows/git-bash 下 `curl -o /dev/null` 会报 `(23) write error`，
    必须写真实临时文件（本坑导致首版测速全部 0 MB/s）。
    """
    cmd = ["curl", "-sS", "-o", tmpfile, "--max-time", str(max_time),
           "--range", f"0-{max_bytes}", "--resolve", f"{host}:443:{ip}",
           "-w", "%{speed_download}|%{time_connect}|%{size_download}|%{http_code}",
           f"https://{host}{path}"]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=max_time + 8, env=ENV)
        spd, tc, size, code = r.stdout.decode("utf-8", "replace").strip().split("|")
        return float(spd) / 1_000_000, float(tc) * 1000, int(float(size)), code
    except Exception as e:
        return None, None, 0, f"ERR:{type(e).__name__}"


def detect_local_dns():
    """自动探测本机系统 DNS（= 'local' 解析器实际使用的地址），避免把内网 IP 写进仓库。

    Windows: 解析 `ipconfig /all` 的 DNS Servers 段；失败则回退到网关。
    """
    try:
        r = subprocess.run(["ipconfig", "/all"], capture_output=True, timeout=20)
        text = r.stdout.decode("gbk", "replace")
        m = re.search(r"(?:DNS Servers|DNS 服务器)[^\d]*?:\s*([\d.]+)", text)
        if m and m.group(1):
            return m.group(1)
    except Exception:
        pass
    try:
        r = subprocess.run(["ipconfig"], capture_output=True, timeout=20)
        text = r.stdout.decode("gbk", "replace")
        m = re.search(r"(?:Default Gateway|默认网关)[^\d]*?:\s*([\d.]+)", text)
        if m:
            return m.group(1)
    except Exception:
        pass
    return "223.5.5.5"          # 兜底：直接对比两个公共 DNS


def main_throughput():
    """网速对比：钉住各解析器给出的 IP 实际下载。

    含**同 IP 对照组**（两解析器返回同一 IP 的目标）——用它量出噪声底线，
    再判断“不同 IP”的差异是否可信。没有对照组就会把噪声当收益。
    """
    import tempfile
    tmpfile = os.path.join(tempfile.gettempdir(), "hermes_slot_bench.bin")
    local_dns = detect_local_dns()
    rnames = [("local(系统DNS)", local_dns), ("AliDNS", "223.5.5.5")]
    print(f"本机系统 DNS = {local_dns}\n")

    print("网速实测（钉住 IP 下载同一文件；A/B 交错重复）\n")
    same_group, diff_group = [], []

    for host, path in THROUGHPUT_TARGETS:
        ipmap = {}
        for rname, rip in rnames:
            ips = q_udp(rip, host)
            ipmap[rname] = ips[0] if ips else None
        avail = {k: v for k, v in ipmap.items() if v}
        if len(avail) < 2:
            continue

        results = {r: [] for r, _ in rnames}
        for _ in range(ROUNDS):
            for rname, _ in rnames:
                ip = ipmap.get(rname)
                if not ip:
                    continue
                spd, tc, size, code = download_speed(host, path, ip, tmpfile)
                if spd is not None and size > 100_000:
                    results[rname].append(spd)

        med = {r: (statistics.median(v) if v else None) for r, v in results.items()}
        if len(set(avail.values())) == 1:
            same_group.append((host, med))
            print(f"  [同IP] {host:<32} "
                  + "  ".join(f"{r}={med[r]:.2f}" if med[r] else f"{r}=X" for r, _ in rnames))
        else:
            diff_group.append((host, med))
            print(f"  [异IP] {host:<32} "
                  + "  ".join(f"{r}={med[r]:.2f}" if med[r] else f"{r}=X" for r, _ in rnames)
                  + f"   ({ipmap[rnames[0][0]]} vs {ipmap['AliDNS']})")

    print("\n  ── 噪声基线（同 IP 组：理论上应无差异，差异即噪声）──")
    for host, med in same_group:
        vals = [v for v in med.values() if v]
        if len(vals) == 2:
            d = abs(vals[0] - vals[1]) / max(vals) * 100
            print(f"    {host:<32} 差异 {d:5.1f}%")

    print("\n  ── 待验证（异 IP 组：只有超出上面的噪声才算真实收益）──")
    for host, med in diff_group:
        vals = [v for v in med.values() if v]
        if len(vals) == 2:
            d = abs(vals[0] - vals[1]) / max(vals) * 100
            winner = "local" if vals[0] > vals[1] else "AliDNS"
            print(f"    {host:<32} 差异 {d:5.1f}%  胜者 {winner}")

    try:
        os.remove(tmpfile)
    except Exception:
        pass


def main():
    if SLOT == "throughput":
        main_throughput()
        return

    if SLOT == "direct":
        items, label = CN_DOMAINS, "槽③『直连流量』：国内域名（TCP 连 443）"
        port_of = lambda d: 443  # noqa: E731
    else:
        nodes = node_domains()
        if not nodes:
            print("取不到节点域名；确认客户端已连接且 service_core.json 可读")
            return
        items = [d for d, _ in nodes]
        pmap = dict(nodes)
        label = f"槽②『代理服务器』：节点域名（TCP 连节点端口）— {len(items)} 个样本"
        port_of = lambda d: pmap.get(d, 443)  # noqa: E731

    print(f"{label}\n")

    def job(entry):
        name, fn = entry
        res, tcp = [], []
        for d in items:
            t0 = time.perf_counter()
            ips = fn(d)
            ms = (time.perf_counter() - t0) * 1000
            if not ips:
                continue
            res.append(ms)
            t = tcp_best(ips[0], port_of(d))
            if t:
                tcp.append(t)
        return name, res, tcp

    with ThreadPoolExecutor(max_workers=6) as ex:
        rows = list(ex.map(job, CATALOG))

    rows.sort(key=lambda r: (statistics.median(r[2]) if r[2] else 9999, -len(r[1])))
    print(f"  {'服务器':<26} {'成功':>7} {'解析中位':>9} {'TCP中位':>8}")
    print("  " + "-" * 56)
    for name, res, tcp in rows:
        if not tcp:
            print(f"  {name:<26} {len(res):>3}/{len(items):<4} {'失败':>18}")
        else:
            print(f"  {name:<26} {len(res):>3}/{len(items):<4} "
                  f"{statistics.median(res):>8.0f}ms {statistics.median(tcp):>7.0f}ms")


if __name__ == "__main__":
    main()
