---
name: github
description: "操作GitHub时必用。PR/Issue/评审/仓库/认证。GitHub via gh CLI: PRs, issues, reviews, repos, auth."
version: 2.0.0
author: Ben Barclay (benbarclay), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, gh, git, pull-requests, issues, code-review, repos, auth, ci]
    category: software-development
    related_skills: [codebase-inspection, requesting-code-review]
---

# GitHub

Work GitHub end to end with the `gh` CLI (REST fallback where noted): auth,
issues, the PR lifecycle, issue-to-PR delivery, code review, and repo
management. This skill consolidates six former skills; each workflow lives
complete in its reference file — ALWAYS read the matching reference before
starting that workflow, the body below only routes.

## Routing

| Task | Read first |
|---|---|
| Auth broken / new machine / token or SSH setup / gh login | `references/auth.md` |
| Create, triage, label, assign, close issues | `references/issues.md` |
| Branch, commit, open PR, watch CI, merge | `references/pr-workflow.md` |
| Carry an ISSUE to a verified PR (full delivery loop) | `references/issue-to-pr.md` |
| Review someone's PR: diffs, inline comments, verdict | `references/code-review.md` |
| Clone/create/fork repos, remotes, releases | `references/repo-management.md` |

Supporting assets: `scripts/gh-env.sh` + `scripts/git-credential-token.py`
(auth helpers), `templates/` (PR bodies, bug report, feature request),
`references/ci-troubleshooting.md`, `references/conventional-commits.md`,
`references/github-api-cheatsheet.md`, `references/review-output-template.md`.

## 本机代理前提（Windows，必读）

本机 git 走本地代理 `127.0.0.1:3067`，已固化为**全局 URL-scoped 配置**（任何 `git init` 的新仓库自动继承，不需逐仓加）：

```bash
git config --global 'http.https://github.com.proxy'  http://127.0.0.1:3067
git config --global 'https.https://github.com.proxy' http://127.0.0.1:3067
```

**三个实测踩过的坑：**

1. **Hermes 的 `terminal` 会剥掉 `ALL_PROXY`/`HTTP(S)_PROXY`** —— 环境变量里有代理不代表 git 能用它。只靠环境变量时直连 `ls-remote` 实测 45s 超时。所以必须写进 `git config`，而不是依赖 shell 环境。
2. **URL-scoped 键会在 `url.insteadOf` 注入凭据后仍然匹配** —— 本机全局有 `url.https://<token>@github.com/.insteadof https://github.com/`，一度担心 URL 变成带 userinfo 后 scope 失配；实测 `--get-urlmatch` 对 `https://user:TOKEN@github.com/...` 仍返回代理值。因而不必改用通用 `http.proxy`。
3. **URL-scoped 优先于仓库本地通用键** —— 同时存在时 URL-scoped 胜出（实测）。二者兼有是双保险，不冲突。

**排障纪律**：复现网络问题必须在干净环境跑（`env -u ALL_PROXY -u HTTP_PROXY -u HTTPS_PROXY ...`），否则会在“看起来能用”的环境里得出错误结论。反之，**验证修复也要先确认问题真实存在**（先直连测出超时，再加代理测通）。

排查单仓为何推不动时，先比对：`git -C <repo> config --local --get http.proxy`。

## Core discipline (applies to every workflow)

- Load THIS skill before any push/PR/CI work — do not hand-roll `gh` loops from
  memory. Monitoring CI with a bash `for` + `sleep` poll is the classic mistake:
  it either blocks the main session or gets backgrounded and floods the chat.
  Use `gh pr checks <n> --watch --interval 15` (or `--fail-fast`) instead; it
  blocks once and prints the final state. Only fall back to polling when
  `--watch` is unavailable.
- Preflight once per session: `gh auth status` — if it fails, go to
  `references/auth.md` before anything else.
- Prefer `gh` over raw REST; drop to `gh api` only for endpoints the
  porcelain lacks (the cheatsheet lists them).
- Never report CI green without checking `gh pr checks` yourself; never
  claim merged without verifying `state,mergedAt`.
- Read full context before writing: `gh issue view --comments` /
  `gh pr view --comments` — decisions live in threads, not titles.
- Sweep for duplicates before creating anything:
  `gh pr list --search` / `gh issue list --search`.

## Verification

- The workflow's own reference file defines done for that task.
- Cross-cutting: every claim about remote state (CI, merge, release,
  issue state) is backed by a fresh `gh` read, never memory.
