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

INV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "capability-inventory.json")
REPORT_PATH = "capability-report.md"
GH_TOKEN = os.environ.get("GH_TOKEN", "")
CLAUDE_MKT_REPO = "anthropics/claude-plugins-official"
ZCODE_MKT_URL = "https://cdn-zcode.z.ai/zcode/official-plugin/marketplace.json"

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
        return http_json(
            f"https://api.github.com/repos/{check['repo']}/releases/latest", auth=True
        ).get("tag_name")
    if t == "zcode-marketplace":
        mkt = http_json(ZCODE_MKT_URL)
        for p in mkt.get("plugins", []):
            if p.get("name") == check["plugin"]:
                return p.get("version")
        return None
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


def local_merged_versions(path):
    """读取客户端本地合并市场清单（UI 真源），返回 {插件名: 版本}。"""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return {p.get("name"): p.get("version") for p in d.get("plugins", [])}


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
    rows = []
    details = []
    on_actions = os.environ.get("GITHUB_ACTIONS") == "true"

    for comp in inv["components"]:
        cid = comp["id"]
        check = comp["checks"][0]

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

        # 技能库路径提交检查：对比基线 sha，报告新增提交数
        if check["type"] == "github-commits-path":
            try:
                commits = github_commits_for_path(check["repo"], check["path"])
            except Exception as e:
                rows.append(f"| {comp['display']} | `{cid}` | N/A | ⚠️ 查询失败 |")
                details.append("\n".join([
                    f"### {comp['display']}（{cid}）", "",
                    f"- ⚠️ 上游查询失败：{type(e).__name__}: {e}",
                ]))
                continue
            head = commits[0]["sha"] if commits else None
            rec = next((loc.get("sha") for loc in comp.get("installed", []) if loc.get("sha")), None)
            behind = bool(head and rec and head != rec)
            count = None
            if behind and commits:
                for i, c in enumerate(commits):
                    if c["sha"] == rec:
                        count = i
                        break
                if count is None:
                    count = f"{len(commits)}+"
            head_msg = (commits[0]["commit"]["message"].split("\n")[0][:60]) if commits else ""
            head_date = commits[0]["commit"]["committer"]["date"][:10] if commits else ""
            state = "🔴 有更新" if behind else ("✅ 最新" if head else "⚠️ 查询失败")
            rows.append(f"| {comp['display']} | `{cid}` | {head[:8] if head else 'N/A'} | {state} |")
            if behind:
                outdated += 1
            detail = [f"### {comp['display']}（{cid}）", ""]
            if head:
                detail.append(f"- 上游最新：**{head[:8]}**（{head_date}）{head_msg}")
            detail.append(f"- 基线：`{(rec or '未记录')[:8]}` → " + (f"**{count} 笔新提交涉及技能库**" if behind else "✅ 一致"))
            if behind:
                detail.append("- 跟进：Hermes GUI 技能页更新/重跑迁移同步到 ZCode 后，把清单 `installed.sha` 回写为最新 HEAD 并推 main。")
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
