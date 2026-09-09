#!/usr/bin/env python3
"""技能级漂移检查（Skill Drift Check）

语义：只回答「我已装的技能，其上游同名技能是否变了，变了是否值得跟进」。
与「发现新技能」无关——新技能由 skill-plugin-resources.md 索引库按需检索。

三层判定：
  1. 内容哈希比对：本地 vs 上游同名 SKILL.md（行尾 CRLF/LF 归一后比较）
  2. 差异方向：本地多 = 本地增强（不动）；上游多/改写 = 需评估
  3. 噪声过滤：仅行尾差异视为一致，不报

输出：Markdown 报告，按「需人工评估 / 本地增强忽略 / 仅行尾差异」分类。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERMES_SKILLS = os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", "skills")

# 上游源定义：(source_key, repo, 技能根路径候选列表, 默认分支)
UPSTREAMS = [
    ("NousResearch/hermes-agent", "NousResearch/hermes-agent", ["skills", "optional-skills"], "main"),
    ("obra/superpowers", "obra/superpowers", ["skills"], None),
    ("DietrichGebert/ponytail", "DietrichGebert/ponytail", ["skills"], None),
    ("affaan-m/ECC", "affaan-m/ECC", [".agents/skills"], None),
    ("anthropics/skills", "anthropics/skills", ["skills"], None),
    ("google-gemini/gemini-skills", "google-gemini/gemini-skills", ["skills"], None),
    ("mattpocock/skills", "mattpocock/skills", ["skills"], None),
    ("BadTechBandit/skills", "BadTechBandit/skills", ["skills"], None),
]

# 本地技能到上游源键的映射（category -> source_key），无法按目录判定者走 provenance
CATEGORY_TO_SOURCE = {
    "superpowers": "obra/superpowers",
    "hermes": "NousResearch/hermes-agent",
    "hermes-auxiliary-models": "NousResearch/hermes-agent",
    "autonomous-ai-agents": "NousResearch/hermes-agent",
    "dogfood": "NousResearch/hermes-agent",
    "apple": "NousResearch/hermes-agent",
    "security": "NousResearch/hermes-agent",
}

# 明确自研/无上游的分类，直接跳过
SKIP_CATEGORIES = {"zcode-custom"}


def gh_token() -> str:
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok
    try:
        return subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=20
        ).stdout.strip()
    except Exception:
        return ""


TOKEN = gh_token()


def _get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "hermes-skill-drift", "Accept": "*/*"}
    )
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    return urllib.request.urlopen(req, timeout=timeout).read()


def api_json(url: str, timeout: int = 40):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "hermes-skill-drift",
            "Accept": "application/vnd.github+json",
        },
    )
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def normalize(text: str) -> str:
    """行尾归一 + 去 BOM + 去行尾空白，消除跨平台噪声。"""
    return "\n".join(
        line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff").splitlines()
    )


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def default_branch(repo: str, fallback: str | None) -> str:
    if fallback:
        return fallback
    try:
        return api_json(f"https://api.github.com/repos/{repo}").get("default_branch", "main")
    except Exception:
        return "main"


def build_upstream_index(repo: str, roots: list[str], branch: str) -> dict[str, str]:
    """返回 {skill_dir_name: raw_path}"""
    idx: dict[str, str] = {}
    try:
        tree = api_json(
            f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
        ).get("tree", [])
    except Exception as e:
        print(f"  ! {repo} 目录树获取失败: {type(e).__name__}: {e}", file=sys.stderr)
        return idx
    for item in tree:
        p = item.get("path", "")
        if not p.endswith("/SKILL.md"):
            continue
        parts = p.split("/")
        if len(parts) < 3:
            continue
        # 只接受位于指定根目录下的
        if parts[0] not in roots:
            continue
        name = parts[-2]
        # 优先较短路径（skills/ 优于 optional-skills/ 的重名）
        if name not in idx or len(p) < len(idx[name]):
            idx[name] = p
    return idx


def read_local_skill(cat: str, name: str) -> str | None:
    p = os.path.join(HERMES_SKILLS, cat, name, "SKILL.md")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def _body(text: str) -> str:
    """去掉 frontmatter，只留正文（用于判断是否为实质内容改动）。"""
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    return text[m.end():] if m else text


def _frontmatter_field(text: str, field: str) -> str | None:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    fm = m.group(1)
    mm = re.search(rf"^{field}:\s*(.+)$", fm, re.M)
    return mm.group(1).strip() if mm else None


def classify(local: str, remote: str) -> tuple[str, str]:
    """返回 (类别, 说明)"""
    ln, rn = normalize(local), normalize(remote)
    if ln == rn:
        return "same", ""
    if sha(ln) == sha(rn):
        return "same", ""

    # 特判：仅 frontmatter description 不同 = 本地强触发词定制（2026-09-07 截断优化），
    # 正文一致则视为本地增强，绝不可被上游英文原文覆盖。
    if _body(ln).strip() == _body(rn).strip():
        fd_l = _frontmatter_field(ln, "description")
        fd_r = _frontmatter_field(rn, "description")
        if fd_l != fd_r:
            return "local_extra", (
                "仅 description 不同（本地中文强触发词定制，正文一致，禁止被上游覆盖）"
            )

    ll, rl = ln.splitlines(), rn.splitlines()
    only_local = [x for x in ll if x not in set(rl)]
    only_remote = [x for x in rl if x not in set(ll)]

    if not only_remote and only_local:
        return "local_extra", f"本地多 {len(only_local)} 行（本地增强/定制，无需跟进）"
    if not only_local and only_remote:
        return "upstream_extra", f"上游新增 {len(only_remote)} 行（需评估是否跟进）"
    if len(only_remote) > len(only_local) * 2:
        return "upstream_rewrote", f"上游大幅改写（+{len(only_remote)}/-{len(only_local)} 行，需评估）"
    if len(only_local) > len(only_remote) * 2:
        return "local_rewrote", f"本地大幅改写（+{len(only_local)}/-{len(only_remote)} 行，本地增强）"
    return "both_changed", f"双向差异（本地+{len(only_local)}/上游+{len(only_remote)} 行，需人工判定）"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="输出 JSON 而非 Markdown")
    ap.add_argument("--repo", help="只检查指定上游（source key 子串匹配）")
    args = ap.parse_args()

    if not os.path.isdir(HERMES_SKILLS):
        print(f"找不到本地技能目录: {HERMES_SKILLS}", file=sys.stderr)
        return 2

    # 枚举本地技能
    local_skills = []
    for cat in sorted(os.listdir(HERMES_SKILLS)):
        d = os.path.join(HERMES_SKILLS, cat)
        if not os.path.isdir(d) or cat in SKIP_CATEGORIES:
            continue
        for name in sorted(os.listdir(d)):
            if os.path.exists(os.path.join(d, name, "SKILL.md")):
                local_skills.append((cat, name))

    # 按来源分组
    grouped: dict[str, list[tuple[str, str]]] = {}
    for cat, name in local_skills:
        src = CATEGORY_TO_SOURCE.get(cat)
        if not src:
            continue
        grouped.setdefault(src, []).append((cat, name))

    results = []
    stats = {"checked": 0, "unmapped": 0, "same": 0, "local_extra": 0,
             "upstream_extra": 0, "upstream_rewrote": 0, "local_rewrote": 0,
             "both_changed": 0, "error": 0}

    for src_key, repo, roots, fb in UPSTREAMS:
        if args.repo and args.repo not in src_key:
            continue
        targets = grouped.get(src_key)
        if not targets:
            continue
        print(f"[{src_key}] 本地归属 {len(targets)} 项，拉取上游索引…", file=sys.stderr)
        branch = default_branch(repo, fb)
        idx = build_upstream_index(repo, roots, branch)
        if not idx:
            print(f"  ! 上游索引为空，跳过", file=sys.stderr)
            for cat, name in targets:
                results.append({"skill": f"{cat}/{name}", "source": src_key,
                                "status": "error", "detail": "上游索引获取失败"})
                stats["error"] += 1
            continue

        for cat, name in targets:
            upath = idx.get(name)
            if not upath:
                results.append({"skill": f"{cat}/{name}", "source": src_key,
                                "status": "unmapped", "detail": "上游无同名技能"})
                stats["unmapped"] += 1
                continue
            local = read_local_skill(cat, name)
            if local is None:
                continue
            try:
                remote = _get(
                    f"https://raw.githubusercontent.com/{repo}/{branch}/{upath}"
                ).decode("utf-8", "replace")
            except Exception as e:
                results.append({"skill": f"{cat}/{name}", "source": src_key,
                                "status": "error", "detail": f"{type(e).__name__}: {e}"})
                stats["error"] += 1
                continue
            status, detail = classify(local, remote)
            stats["checked"] += 1
            stats[status] += 1
            results.append({
                "skill": f"{cat}/{name}", "source": src_key, "status": status,
                "detail": detail, "upstreamPath": upath,
                "localSha": sha(normalize(local)), "upstreamSha": sha(normalize(remote)),
            })
            time.sleep(0.15)

    if args.json:
        print(json.dumps({"stats": stats, "results": results}, ensure_ascii=False, indent=2))
        return 0

    # Markdown 报告
    lines = ["# 技能漂移检查报告", ""]
    lines.append(f"- 本地已检查：**{stats['checked']}** 项")
    lines.append(f"- 上游无同名（自研/已下架）：{stats['unmapped']} 项")
    lines.append(f"- 内容一致：{stats['same']} 项")
    needs = stats["upstream_extra"] + stats["upstream_rewrote"] + stats["both_changed"]
    lines.append(f"- **需人工评估：{needs} 项**")
    lines.append("")

    buckets = [
        ("需人工评估（上游有实质改动）", ["upstream_extra", "upstream_rewrote", "both_changed"]),
        ("本地增强（无需跟进）", ["local_extra", "local_rewrote"]),
        ("上游无同名", ["unmapped"]),
        ("错误", ["error"]),
    ]
    for title, keys in buckets:
        items = [r for r in results if r["status"] in keys]
        if not items:
            continue
        lines.append(f"## {title}（{len(items)}）")
        lines.append("")
        lines.append("| 技能 | 来源 | 说明 |")
        lines.append("|---|---|---|")
        for r in items:
            lines.append(f"| `{r['skill']}` | {r['source']} | {r.get('detail','')} |")
        lines.append("")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
