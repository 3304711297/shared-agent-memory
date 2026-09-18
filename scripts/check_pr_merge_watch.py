#!/usr/bin/env python3
"""上游 PR 合并守望（issue 通知版，不依赖任何 LLM）。

只读 GitHub 公开仓库的 PR 状态，产出 issue 正文并输出 GITHUB_OUTPUT：
  has_update / pr_state / pr_merged
纯标准库，可本地直接运行。

设计要点（为什么不用 cron + agent）：
  cron 投递依赖模型路由（provider/base_url 快照），用户频繁切模型时会
  直接失败并静默 —— 通知必须与模型解耦。GitHub Actions 在云端跑，
  只依赖公开 API，通知走 GitHub 自身的 issue 通知链。
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

# ── 守望目标（新增 PR 只需往这里加一条）──────────────────────────────────
WATCHED = [
    {
        "repo": "NousResearch/hermes-agent",
        "number": 106399,
        "title": "per-tool spillover budgets（tool_output.tool_overrides）",
        "why": "让单个工具可配更低的 spillover 落盘阈值；本机 terminal 输出被 "
               "tool_output.max_bytes(50K) 截断、低于 spillover 阈值(100K)，"
               "故永不落盘。合并后可进一步细化 per-tool 阈值。",
    },
]

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_PATH = os.path.join(REPO_ROOT, "pr-watch-report.md")
GH_TOKEN = os.environ.get("GH_TOKEN", "")

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


def http_json(url):
    if url in _cache:
        return _cache[url]
    req = urllib.request.Request(url, headers={
        "User-Agent": "pr-merge-watch",
        "Accept": "application/vnd.github+json",
    })
    if GH_TOKEN:
        req.add_header("Authorization", f"Bearer {GH_TOKEN}")
    with _open(req) as r:
        data = json.loads(r.read().decode("utf-8"))
    _cache[url] = data
    return data


def fetch_pr(repo, number):
    """返回 {state, merged, merged_at, title, url, error}。"""
    url = f"https://api.github.com/repos/{repo}/pulls/{number}"
    try:
        d = http_json(url)
        return {
            "state": d.get("state"),
            "merged": bool(d.get("merged")),
            "merged_at": d.get("merged_at"),
            "closed_at": d.get("closed_at"),
            "title": d.get("title"),
            "url": d.get("html_url"),
            "error": None,
        }
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "url": f"https://github.com/{repo}/pull/{number}"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}", "url": f"https://github.com/{repo}/pull/{number}"}


def state_badge(info):
    if info.get("error"):
        return "⚠️ 查询失败"
    if info.get("merged"):
        return "🟢 已合并"
    if info.get("state") == "closed":
        return "⚪ 已关闭（未合并）"
    if info.get("state") == "open":
        return "🟡 等待合并"
    return "❓ 未知"


def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    results = []
    errors = 0

    for w in WATCHED:
        info = fetch_pr(w["repo"], w["number"])
        info.update(w)
        results.append(info)
        if info.get("error"):
            errors += 1

    # 分两个计数，别混用：
    #   waiting    = 还没合并（open）—— 用于正文说明
    #   actionable = 需要人跟进（已合并 / 已关闭）—— 用于标题与 has_update
    # 若把 waiting 当标题计数，「刚合并」时它会归零，标题就成了「0 项待跟进」，误导。
    waiting = sum(1 for r in results
                  if not r.get("error") and r.get("state") == "open" and not r.get("merged"))
    actionable = [r for r in results
                  if not r.get("error") and (r.get("merged") or r.get("state") == "closed")]
    has_update = bool(actionable)

    lines = [
        "# 🔀 上游 PR 合并守望",
        "",
        f"> 检查时间：{now.strftime('%Y-%m-%d %H:%M')}（北京时间）",
        "",
        "| PR | 状态 | 说明 |",
        "| --- | --- | --- |",
    ]
    for r in results:
        link = f"[{r['repo']}#{r['number']}]({r['url']})"
        lines.append(f"| {link} | {state_badge(r)} | {r.get('title') or r.get('error')} |")

    lines += ["", "## 明细", ""]
    for r in results:
        lines.append(f"### {r['repo']}#{r['number']} — {r.get('title') or '(查询失败)'}")
        lines.append("")
        if r.get("error"):
            lines.append(f"- ⚠️ 查询失败：`{r['error']}`")
        else:
            lines.append(f"- 状态：**{r.get('state')}**" + ("（已合并 ✅）" if r.get("merged") else ""))
            if r.get("merged_at"):
                lines.append(f"- 合并时间：{r['merged_at']}")
            if r.get("closed_at") and not r.get("merged"):
                lines.append(f"- 关闭时间：{r['closed_at']}")
        lines.append(f"- 关注理由：{r.get('why', '')}")
        if r.get("merged"):
            lines.append("")
            lines.append("**合并后待办**：")
            lines.append("- 确认本机 Hermes 是否已包含该功能（查 `tools/budget_config.py` 是否读取 `tool_output.tool_overrides`）")
            lines.append("- 若已包含，评估是否为本机工具配更低的 per-tool spillover 阈值")
        lines.append("")

    lines += [
        "---",
        "",
        f"**待合并：{waiting}** · **待跟进：{len(actionable)}** · **查询失败：{errors}** · "
        f"{'✅ 无需跟进时本 Issue 会自动关闭' if not has_update else '⬆️ 有可跟进项'}",
    ]

    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report + "\n")

    print(report)

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"has_update={'true' if has_update else 'false'}\n")
            f.write(f"waiting_count={waiting}\n")
            f.write(f"actionable_count={len(actionable)}\n")
            f.write(f"error_count={errors}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
