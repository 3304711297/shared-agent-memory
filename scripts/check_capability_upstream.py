#!/usr/bin/env python3
"""capability-upstream-watch 比对脚本。

读取仓库根的 capability-inventory.json，逐组件查询上游最新版本，
与已装版本比对，产出 capability-report.md（Issue 正文）并输出
GITHUB_OUTPUT：has_updates / update_count。纯标准库，可在本地直接运行。
"""
import base64
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV_PATH = os.path.join(REPO_ROOT, "capability-inventory.json")
REPORT_PATH = os.path.join(REPO_ROOT, "capability-report.md")
GH_TOKEN = os.environ.get("GH_TOKEN", "")
CLAUDE_MKT_REPO = "anthropics/claude-plugins-official"
ZCODE_MKT_URL = "https://raw.githubusercontent.com/zai-org/zcode-plugins/main/marketplace.json"
ZCODE_MKT_CDN = "https://cdn-zcode.z.ai/zcode/official-plugin/marketplace.json"

_cache = {}


def _open(req, timeout=30):
    last_err = None
    for attempt in range(2):  # 瞬时故障重试一次
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise last_err


def http_json(url, auth=False, accept="application/vnd.github+json"):
    if url in _cache:
        return _cache[url]
    req = urllib.request.Request(url, headers={
        "User-Agent": "capability-upstream-watch",
        "Accept": accept,
    })
    if auth and GH_TOKEN:
        req.add_header("Authorization", f"Bearer {GH_TOKEN}")
    with _open(req) as r:
        data = json.loads(r.read().decode("utf-8"))
    _cache[url] = data
    return data


def fetch_text(url, auth=False):
    if url in _cache:
        return _cache[url]
    req = urllib.request.Request(url, headers={"User-Agent": "capability-upstream-watch"})
    if auth and GH_TOKEN:
        req.add_header("Authorization", f"Bearer {GH_TOKEN}")
    with _open(req) as r:
        data = r.read().decode("utf-8")
    _cache[url] = data
    return data


def split_ver(v):
    v = v.lstrip("vV")
    parts = re.split(r"[.\-+_]", v)
    out = []
    for p in parts:
        if p.isdigit():
            out.append((0, int(p)))
        elif p:
            out.append((1, p))
    return out


def ver_cmp(a, b):
    """返回 -1/0/1；无法比较返回 None（如实标注，不猜）。"""
    ta, tb = split_ver(a), split_ver(b)
    if not ta or not tb:
        return None
    n = max(len(ta), len(tb))
    ta += [(0, 0)] * (n - len(ta))
    tb += [(0, 0)] * (n - len(tb))
    for x, y in zip(ta, tb):
        if x == y:
            continue
        if x[0] != y[0]:  # 数字段 vs 非数字段
            return None
        return -1 if x < y else 1
    return 0


def upstream_version(check):
    t = check["type"]
    if t == "npm":
        pkg = urllib.parse.quote(check["package"], safe="")
        return http_json(
            f"https://registry.npmjs.org/{pkg}/latest", accept="application/json"
        ).get("version")
    if t == "gh-release":
        tag = http_json(
            f"https://api.github.com/repos/{check['repo']}/releases/latest", auth=True
        ).get("tag_name")
        strip = check.get("tag_strip")
        if strip and tag:
            tag = re.sub(strip, "", tag)
        return tag
    if t == "zcode-marketplace":
        # 真源 = zai-org/zcode-plugins 仓库；CDN 为其镜像，仓库失败时回退
        try:
            mkt = http_json(ZCODE_MKT_URL, accept="application/json")
        except Exception:
            mkt = http_json(ZCODE_MKT_CDN, accept="application/json")
        for p in mkt.get("plugins", []):
            if p.get("name") == check["plugin"]:
                return p.get("version")
        return None
    if t == "hermes-skills-hub":
        data = http_json(check["url"], accept="application/json")
        return str(data.get("totalSkills", ""))
    raise ValueError(f"unknown check type: {t}")


def claude_marketplace_sha(plugin):
    repo = http_json(f"https://api.github.com/repos/{CLAUDE_MKT_REPO}", auth=True)
    branch = repo.get("default_branch", "main")
    raw = fetch_text(
        f"https://raw.githubusercontent.com/{CLAUDE_MKT_REPO}/{branch}/.claude-plugin/marketplace.json",
        auth=True,
    )
    mkt = json.loads(raw)
    for p in mkt.get("plugins", []):
        if p.get("name") == plugin:
            src = p.get("source") or {}
            return src.get("sha") if isinstance(src, dict) else None
    return None


def normalize_local_path(p: str) -> str:
    """展开环境变量（%VAR%、$VAR）、~ 用户目录并归一化为跨平台标准路径。"""
    if not p:
        return ""
    expanded = os.path.expandvars(p)
    if "%" in expanded:
        def _repl(m):
            var = m.group(1)
            return os.environ.get(var, m.group(0))
        expanded = re.sub(r"%([^%]+)%", _repl, expanded)
    return os.path.normpath(os.path.expanduser(expanded))


def local_merged_versions(path):
    """读取客户端本地合并市场清单（UI 真源），返回 {插件名: 版本}。"""
    with open(normalize_local_path(path), encoding="utf-8") as f:
        d = json.load(f)
    return {p.get("name"): p.get("version") for p in d.get("plugins", [])}


# ── 本地配置守卫（Hermes 更新后漂移检查）────────────────────────────────
# 纯标准库实现：不依赖 PyYAML。config.yaml 主体是简单嵌套映射，按缩进维护
# 路径栈即可取到叶子值；列表项（`- ` 开头）与注释行一律跳过，不干扰栈。

def _parse_scalar(raw):
    s = raw.strip()
    if s == "" or s.startswith("#"):
        return None
    low = s.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~"):
        return None
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s.strip("'\"")


def read_config_leaves(path):
    """把 config.yaml 解析成 {点分路径: 叶子值}。仅覆盖映射结构，列表分支跳过。"""
    leaves, stack = {}, []  # stack: [(indent, key)]
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            stripped = line.lstrip()
            if stripped.startswith("-") or stripped.startswith("|-") or stripped.startswith(">-"):
                continue  # 列表项 / 块标量：不参与路径栈
            indent = len(line) - len(line.lstrip())
            if ":" not in stripped:
                continue
            key, _, val = stripped.partition(":")
            key = key.strip()
            while stack and stack[-1][0] >= indent:
                stack.pop()
            stack.append((indent, key))
            parsed = _parse_scalar(val)
            if parsed is not None:
                leaves[".".join(k for _, k in stack)] = parsed
    return leaves


def check_config_guard(check):
    """返回 (problems, detail_lines)。problems 非空即视为待跟进。"""
    problems, detail = [], []
    raw_cfg_path = check["file"]
    cfg_path = normalize_local_path(raw_cfg_path)

    try:
        leaves = read_config_leaves(cfg_path)
    except Exception as e:
        return [f"配置读取失败：{type(e).__name__}: {e}"], [
            f"- ⚠️ 无法读取 `{raw_cfg_path}`：{type(e).__name__}: {e}"
        ]

    detail.append(f"- 配置文件：`{raw_cfg_path}`")
    detail.append("")
    detail.append("**① 拍板配置键（上游深合并新增默认值不会冲掉叶子，但需确认仍在）**")
    detail.append("")
    for item in check.get("expect", []):
        path, want = item["path"], item["value"]
        got = leaves.get(path, "<缺失>")
        ok = (got == want)
        icon = "✅" if ok else "🔴"
        detail.append(f"- {icon} `{path}` = `{got}`（拍板值 `{want}`）" + ("" if ok else " — **已漂移/缺失**"))
        if not ok:
            problems.append(f"{path} 期望 {want!r}，实际 {got!r}")

    # ② 本地源码 stash 残留（桌面端更新会 stash 且不自动 pop）
    detail.append("")
    detail.append("**② 本地源码 stash 残留（桌面端更新不自动还原）**")
    detail.append("")
    for repo in check.get("stashRepos", []):
        norm_repo = normalize_local_path(repo)
        try:
            import subprocess
            out = subprocess.run(
                ["git", "-C", norm_repo, "stash", "list", "--format=%gd|%s"],
                capture_output=True, text=True, timeout=20,
            )
            stashes = [l for l in (out.stdout or "").splitlines() if l.strip()]
            if stashes:
                detail.append(f"- 🔴 `{repo}` 有 {len(stashes)} 条未还原 stash：")
                for s in stashes[:5]:
                    ref, _, subject = s.partition("|")
                    kind = "（hermes 更新自动暂存）" if "hermes-update-autostash" in subject else "（手动暂存 ⚠️ 可能含本地定制）"
                    detail.append(f"  - `{ref}` {subject}{kind}")
                auto_n = sum(1 for s in stashes if "hermes-update-autostash" in s)
                manual_n = len(stashes) - auto_n
                msg = f"{repo} 存在 {len(stashes)} 条未还原 stash"
                if manual_n:
                    msg += f"（其中 {manual_n} 条为手动暂存，务必确认）"
                msg += "；确认无本地定制后可用 `git stash drop` 清理"
                problems.append(msg)
            else:
                detail.append(f"- ✅ `{repo}` 无 stash 残留")
        except Exception as e:
            detail.append(f"- ⚠️ `{repo}` stash 检查失败：{type(e).__name__}: {e}")

    # ③ 核心自研技能是否被误打 created_by: agent（新版 curator 管辖标记）
    detail.append("")
    detail.append("**③ 核心自研技能 `created_by` 标记巡查**")
    detail.append("")
    raw_usage_path = check.get("usageFile")
    usage_path = normalize_local_path(raw_usage_path) if raw_usage_path else None
    protected = check.get("protectedSkills", [])
    if usage_path and protected:
        try:
            with open(usage_path, encoding="utf-8") as f:
                usage = json.load(f)
            flagged = []
            for name in protected:
                rec = usage.get(name)
                if isinstance(rec, dict) and (
                    rec.get("created_by") == "agent" or rec.get("agent_created") is True
                ):
                    flagged.append(name)
            if flagged:
                detail.append(f"- 🔴 以下核心技能已被标记为 `created_by: agent`，会进入 curator 归档倒计时：{', '.join(flagged)}")
                detail.append("- 处理：`hermes curator unpin` 无效，需人工编辑 `.usage.json` 改回或确认是否接受归档。")
                problems.append(f"核心技能被标为 agent-created：{', '.join(flagged)}")
            else:
                detail.append(f"- ✅ {len(protected)} 项核心自研技能均为非 agent 标记，curator 不会触碰")
        except Exception as e:
            detail.append(f"- ⚠️ `.usage.json` 读取失败：{type(e).__name__}: {e}")
    else:
        detail.append("- ⏭️ 未配置 usageFile / protectedSkills，跳过")

    return problems, detail


def github_commits_for_path(repo, path):
    """取仓库某路径最近 100 笔提交（新→旧）。"""
    q = urllib.parse.quote(path, safe="/")
    return http_json(
        f"https://api.github.com/repos/{repo}/commits?path={q}&per_page=100", auth=True
    )


def main():
    with open(INV_PATH, encoding="utf-8") as f:
        inv = json.load(f)

    now = datetime.now(timezone(timedelta(hours=8)))
    lines = [
        "# 🔔 本地能力组件上游更新报告",
        "",
        f"> 生成时间：{now.strftime('%Y-%m-%d %H:%M')}（北京时间） · 清单：`capability-inventory.json`",
        ">",
        "> **跟进方式**：升级对应组件后，把清单里的 `installed.version` 更新为新版本并随共享库推 `main`，本看门会在下次运行时自动收口本 Issue。",
        "",
    ]
    outdated = 0
    skipped = 0
    failed_queries = 0
    rows = []
    details = []
    on_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    local_only = "--local-only" in sys.argv

    for comp in inv["components"]:
        cid = comp["id"]
        check = comp["checks"][0]

        # 本地模式跳过远程检查：CI 负责 18 项外部上游，本地只跑本地专属 2 项，杜绝重复查询与配额耗尽
        if local_only and check["type"] not in ("local-merged-marketplace", "local-config-guard"):
            skipped += 1
            rows.append(f"| {comp['display']} | `{cid}` | 云端托管 | ⏭️ 本地模式跳过 |")
            details.append("\n".join([
                f"### {comp['display']}（{cid}）", "",
                "- ⏭️ 本组件由 GitHub Actions CI 每日定时比对托管，本地 `--local-only` 模式已跳过网络查询。",
            ]))
            continue

        # 本地源组件：读客户端本地合并清单，仅在本地运行时可比对
        if check["type"] == "local-merged-marketplace":
            if on_actions:
                skipped += 1
                rows.append(f"| {comp['display']} | `{cid}` | 本地源 | ⏭️ Actions 跳过 |")
                details.append("\n".join([
                    f"### {comp['display']}（{cid}）", "",
                    "- ⏭️ 本地源检查在 Actions 上跳过。客户端更新种子后请在本地运行 `watch-capability.cmd` 比对并回写清单。",
                ]))
                continue
            try:
                merged = local_merged_versions(check["file"])
            except Exception as e:
                rows.append(f"| {comp['display']} | `{cid}` | 本地源 | ⚠️ 读取失败 |")
                details.append("\n".join([
                    f"### {comp['display']}（{cid}）", "",
                    f"- ⚠️ 本地清单读取失败：{type(e).__name__}: {e}",
                ]))
                continue
            behind = False
            detail = [f"### {comp['display']}（{cid}）", "", f"- 本地清单：`{check['file']}`"]
            for loc in comp.get("installed", []):
                name = loc.get("name", "")
                installed = loc.get("version", "")
                upv = merged.get(name)
                if upv is None:
                    st = "🟡 本地清单无此项"
                else:
                    c = ver_cmp(installed, upv)
                    if c is None:
                        st = "❓ 无法自动比对"
                    elif c < 0:
                        st = "🔴 落后"
                        behind = True
                    else:
                        st = "✅ 一致"
                detail.append(f"- `{loc.get('where','')}`：已装 **{installed}** / 本地清单 **{upv or '缺失'}** → {st}")
            state = "🔴 有更新" if behind else "✅ 最新"
            rows.append(f"| {comp['display']} | `{cid}` | 本地源 | {state} |")
            if behind:
                outdated += 1
            details.append("\n".join(detail))
            continue

        # 本地配置守卫：Hermes 更新后检查拍板配置漂移 / stash 残留 / 核心技能标记
        if check["type"] == "local-config-guard":
            if on_actions:
                skipped += 1
                rows.append(f"| {comp['display']} | `{cid}` | 本地源 | ⏭️ Actions 跳过 |")
                details.append("\n".join([
                    f"### {comp['display']}（{cid}）", "",
                    "- ⏭️ 本地配置检查在 Actions 上跳过（runner 无本地环境）。Hermes 更新后请在本地运行 `watch-capability.cmd`。",
                ]))
                continue
            problems, detail = check_config_guard(check)
            state = "🔴 有更新" if problems else "✅ 最新"
            rows.append(f"| {comp['display']} | `{cid}` | 本地源 | {state} |")
            if problems:
                outdated += 1
            head = [f"### {comp['display']}（{cid}）", ""]
            if problems:
                head.append(f"- 🔴 发现 **{len(problems)}** 项需人工确认：")
                for p in problems:
                    head.append(f"  - {p}")
                head.append("")
                head.append("- 跟进：处理完毕后（恢复配置 / `git stash apply` 或丢弃 / 修正 `.usage.json`），"
                            "本项会在下次运行时自动恢复 ✅。")
                head.append("")
            else:
                head.append("- ✅ 拍板配置齐全、无 stash 残留、核心技能未被 curator 标记。")
                head.append("")
            details.append("\n".join(head + detail))
            continue

        # 技能库路径提交检查：【语义变更 2026-09-09 用户拍板】
        # 旧语义：仓库有新提交即报「有更新」→ 会误导用户去同步（实为误导性噪音）。
        # 新语义：新增技能由 skill-plugin-resources.md 索引库按需检索，本看门不负责「发现新技能」；
        #        此处仅保留基线 sha 作为信息展示，且**永不计入 outdated**，
        #        真正的「已装技能是否落后」由 scripts/check_skill_drift.py 做技能级内容比对。
        if check["type"] == "github-commits-path":
            try:
                commits = github_commits_for_path(check["repo"], check["path"])
            except Exception as e:
                failed_queries += 1
                rows.append(f"| {comp['display']} | `{cid}` | N/A | ⚠️ 查询失败 |")
                details.append("\n".join([
                    f"### {comp['display']}（{cid}）", "",
                    f"- ⚠️ 上游查询失败：{type(e).__name__}: {e}",
                ]))
                continue
            head = commits[0]["sha"] if commits else None
            rec = next((loc.get("sha") for loc in comp.get("installed", []) if loc.get("sha")), None)
            # 不再判定 behind / 不再计入 outdated
            head_msg = (commits[0]["commit"]["message"].split("\n")[0][:60]) if commits else ""
            head_date = commits[0]["commit"]["committer"]["date"][:10] if commits else ""
            rows.append(f"| {comp['display']} | `{cid}` | {head[:8] if head else 'N/A'} | ℹ️ 漂移检查 |")
            detail = [f"### {comp['display']}（{cid}）", ""]
            if head:
                detail.append(f"- 上游最新 HEAD：**{head[:8]}**（{head_date}）{head_msg}")
            detail.append(f"- 基线：`{(rec or '未记录')[:8]}`")
            detail.append("- ℹ️ **本项不再由提交数判定更新**（2026-09-09 语义变更）：新技能发现走 "
                          "`skill-plugin-resources.md` 索引库按需检索；已装技能是否落后由 "
                          "`scripts/check_skill_drift.py` 做技能级内容比对。")
            details.append("\n".join(detail))
            continue

        # Hermes 官网 Skills Hub 聚合全网技能库检查（9万+ 索引）
        if check["type"] == "hermes-skills-hub":
            try:
                data = http_json(check["url"], accept="application/json")
            except Exception as e:
                failed_queries += 1
                rows.append(f"| {comp['display']} | `{cid}` | N/A | ⚠️ 查询失败 |")
                details.append("\n".join([
                    f"### {comp['display']}（{cid}）", "",
                    f"- ⚠️ 上游查询失败：{type(e).__name__}: {e}",
                ]))
                continue
            total = data.get("totalSkills", 0)
            extracted_at = data.get("extractedAt", "")[:10]
            rec_loc = comp.get("installed", [{}])[0]
            rec_total = rec_loc.get("totalSkills", 0)
            rec_date = rec_loc.get("extractedAt", "")
            # 误报治理（09-07）：上游索引每日重跑，extractedAt 必然刷新，而本工作流无
            # contents:write 无法回写清单日期，日期差不可作为更新信号；仅技能总数增长
            # （有新技能上架）才计为待跟进，总数缩量属上游数据波动，无需本地动作。
            behind = total > rec_total
            diff_str = f"+{total - rec_total}" if total > rec_total else (f"{total - rec_total}" if total < rec_total else "0")
            state = "🔴 有更新" if behind else "✅ 最新"
            rows.append(f"| {comp['display']} | `{cid}` | {total:,} ({extracted_at}) | {state} |")
            if behind:
                outdated += 1
            detail = [f"### {comp['display']}（{cid}）", ""]
            detail.append(f"- 上游最新：**{total:,}** 技能（索引时间：`{extracted_at}`，自营: {data.get('localSkills', 0)}, 外部: {data.get('externalSkills', 0)}）")
            detail.append(f"- 基线记录：**{rec_total:,}** 技能（记录时间：`{rec_date}`）→ " + (f"**全网索引有变动（{diff_str} 技能）**" if behind else "✅ 一致"))
            top_sources = sorted(data.get("bySource", {}).items(), key=lambda x: x[1], reverse=True)[:5]
            src_summary = ", ".join(f"{k}: {v:,}" for k, v in top_sources)
            detail.append(f"- 主要源分布：{src_summary} 等")
            if behind:
                detail.append("- 跟进：访问 https://hermes-agent.nousresearch.com/docs/skills/ 浏览新技能；评估后更新 `capability-inventory.json` 中 `totalSkills` 与 `extractedAt` 并推 main。")
            details.append("\n".join(detail))
            continue

        # SkillHub 腾讯云社区技能库检查（防爬虫失效 & 优雅降级）
        if check["type"] == "skillhub-market":
            total = None
            err_msg = None
            try:
                req = urllib.request.Request(
                    check["url"],
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept": "application/json",
                    },
                )
                with _open(req, timeout=15) as r:
                    res = json.loads(r.read().decode("utf-8"))
                    if isinstance(res, dict) and res.get("code") == 0 and isinstance(res.get("data"), dict):
                        raw_total = res["data"].get("total")
                        if isinstance(raw_total, int) and raw_total > 0:
                            total = raw_total
                    if total is None:
                        err_msg = "响应结构未包含有效 data.total"
            except Exception as e:
                err_msg = f"{type(e).__name__}: {e}"

            rec_loc = comp.get("installed", [{}])[0]
            rec_total = rec_loc.get("totalSkills", 0)

            # 铁律：非 GitHub 站点抓取异常时 behind 严格为 False，绝不误计入 outdated，绝不误开 Issue
            if total is None:
                rows.append(f"| {comp['display']} | `{cid}` | N/A | ⚠️ 抓取暂不可达 |")
                details.append("\n".join([
                    f"### {comp['display']}（{cid}）", "",
                    f"- ⚠️ 上游查询异常（已自动跳过，不阻塞其他检查）：{err_msg}",
                    f"- 基线记录：**{rec_total:,}** 技能",
                    "- 说明：非 GitHub 外部站点受网络波动或反爬策略影响可能临时不可达，保持当前基线，不触发误报。",
                ]))
                continue

            behind = bool(total != rec_total)
            diff_str = f"+{total - rec_total}" if total > rec_total else (f"{total - rec_total}" if total < rec_total else "0")
            state = "🔴 有更新" if behind else "✅ 最新"
            rows.append(f"| {comp['display']} | `{cid}` | {total:,} | {state} |")
            if behind:
                outdated += 1
            detail = [f"### {comp['display']}（{cid}）", ""]
            detail.append(f"- 上游最新：**{total:,}** 社区技能")
            detail.append(f"- 基线记录：**{rec_total:,}** 技能 → " + (f"**社区有新技能上架（{diff_str} 项）**" if behind else "✅ 一致"))
            if behind:
                detail.append("- 跟进：访问 https://www.skillhub.cn/ 浏览新技能；评估后更新 `capability-inventory.json` 中 `totalSkills` 并推 main。")
            details.append("\n".join(detail))
            continue

        # Cola Skill 优质技能策展市场检查（防爬虫失效 & 优雅降级）
        if check["type"] == "colaskill-market":
            total = None
            sample_skills = []
            err_msg = None
            try:
                req = urllib.request.Request(
                    check["url"],
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                )
                with _open(req, timeout=15) as r:
                    html = r.read().decode("utf-8", errors="ignore")
                    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
                    if m:
                        ld_data = json.loads(m.group(1))
                        items = ld_data.get("mainEntity", {}).get("itemListElement", [])
                        total = ld_data.get("mainEntity", {}).get("numberOfItems") or len(items)
                        sample_skills = [it.get("name") for it in items if it.get("name")][:3]
                    else:
                        err_msg = "页面未提取到 application/ld+json 结构化数据"
            except Exception as e:
                err_msg = f"{type(e).__name__}: {e}"

            rec_loc = comp.get("installed", [{}])[0]
            rec_total = rec_loc.get("totalSkills", 0)

            # 铁律：非 GitHub 站点抓取异常时 behind 严格为 False，绝不误计入 outdated，绝不误开 Issue
            if total is None:
                rows.append(f"| {comp['display']} | `{cid}` | N/A | ⚠️ 抓取暂不可达 |")
                details.append("\n".join([
                    f"### {comp['display']}（{cid}）", "",
                    f"- ⚠️ 上游查询异常（已自动跳过，不阻塞其他检查）：{err_msg}",
                    f"- 基线记录：**{rec_total}** 精品技能",
                    "- 说明：非 GitHub 外部站点受网络波动或模板变动影响可能临时不可达，保持当前基线，不触发误报。",
                ]))
                continue

            behind = bool(total != rec_total)
            diff_str = f"+{total - rec_total}" if total > rec_total else (f"{total - rec_total}" if total < rec_total else "0")
            state = "🔴 有更新" if behind else "✅ 最新"
            rows.append(f"| {comp['display']} | `{cid}` | {total} | {state} |")
            if behind:
                outdated += 1
            detail = [f"### {comp['display']}（{cid}）", ""]
            detail.append(f"- 上游最新：**{total}** 个精选技能（包含：{', '.join(sample_skills)} 等）")
            detail.append(f"- 基线记录：**{rec_total}** 个技能 → " + (f"**发现新增策展技能（{diff_str} 项）**" if behind else "✅ 一致"))
            if behind:
                detail.append("- 跟进：访问 https://colaskill.com/zh/ 挑选优质新技能；评估后更新 `capability-inventory.json` 中 `totalSkills` 并推 main。")
            details.append("\n".join(detail))
            continue

        upstream = None
        src_err = None
        try:
            upstream = upstream_version(check)
        except Exception as e:  # 单源失败不拖垮整体
            src_err = f"{type(e).__name__}: {e}"

        loc_status = []
        behind = False
        for loc in comp.get("installed", []):
            installed = loc.get("version", "")
            if upstream is None:
                st = "⚠️ 上游查询失败"
            else:
                c = ver_cmp(installed, upstream)
                if c is None:
                    st = "❓ 无法自动比对"
                elif c < 0:
                    st = "🔴 落后"
                    behind = True
                else:
                    st = "✅ 一致"
            loc_status.append(f"- `{loc.get('where','')}`：已装 **{installed}** → {st}")

        mkt_note = ""
        mkt = comp.get("claudeMarketplaceSha")
        if mkt:
            try:
                cur_sha = claude_marketplace_sha(mkt["plugin"])
                if cur_sha and cur_sha != mkt["installedSha"]:
                    behind = True
                    mkt_note = (
                        f"- 📦 claude-plugins-official 市场已推进到新版本（pin `{cur_sha[:12]}` ≠ 本地 `{mkt['installedSha'][:12]}`），"
                        "可在 ZCode 插件管理里更新该插件。"
                    )
            except Exception as e:
                mkt_note = f"- ⚠️ claude 市场查询失败：{type(e).__name__}: {e}"

        if behind:
            state = "🔴 有更新"
        elif src_err:
            state = "⚠️ 查询失败"
            failed_queries += 1
        elif upstream is None:
            state = "🟡 上游清单中无此组件"
        else:
            state = "✅ 最新"
        rows.append(f"| {comp['display']} | `{cid}` | {upstream or 'N/A'} | {state} |")
        if behind:
            outdated += 1
        detail = [f"### {comp['display']}（{cid}）", ""]
        if src_err:
            detail.append(f"- ⚠️ 上游查询失败：{src_err}")
        elif upstream is None:
            detail.append("- 🟡 上游清单中不存在该组件（可能已下架或改名）；请人工确认后从清单移除或调整检查源。")
        else:
            detail.append(f"- 上游最新：**{upstream}**")
        detail.extend(loc_status)
        if mkt_note:
            detail.append(mkt_note)
        details.append("\n".join(detail))

    lines.append("## 概览")
    lines.append("")
    lines.append("| 组件 | ID | 上游最新 | 状态 |")
    lines.append("|------|----|----------|------|")
    lines.extend(rows)
    lines.append("")
    lines.append("## 明细")
    lines.append("")
    lines.append("\n\n".join(details))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"**待跟进组件数：{outdated}** · 未纳入看门的组件见清单 `notWatched` 字段。")

    report = "\n".join(lines)

    # 本地非 local-only 模式且遭遇大面积失败（API 限额或网络中断）时，拒绝写盘覆盖已有报告
    if not on_actions and not local_only and failed_queries >= 3:
        sys.stderr.write(
            f"\n[WARN] 本地检测到 {failed_queries} 项上游查询失败（如未带 GH_TOKEN 触发 GitHub API 403 限额或网络波动）。\n"
            f"为防止以残缺数据覆盖云端 Issue/报告，已中止写入 {REPORT_PATH}。\n"
            f"💡 本地若仅需检查客户端内置插件与配置守卫，请使用: python scripts/check_capability_upstream.py --local-only\n"
        )
        if not gh_out:
            print(report)
        return 1

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    has_updates = "true" if outdated > 0 else "false"
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"has_updates={has_updates}\nupdate_count={outdated}\nskipped_count={skipped}\n")

    print(f"components={len(inv['components'])} outdated={outdated} skipped={skipped} has_updates={has_updates}")
    # 本地运行时直接展示概览
    if not gh_out:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
