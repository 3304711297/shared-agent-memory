---
name: using-git-worktrees
description: "多分支并行开发时必用。Git工作区隔离免冲突。Use when starting feature work needing isolated worktrees."
---

# Using Git Worktrees — Router

多分支并行开发隔离：检存量隔离 → 建 worktree → 项目 setup → 验干净基线。

## Routing table

| Need | Read |
|---|---|
| 建隔离区 + 各语言 setup + 基线验证 | `references/setup-verify.md` |
| 速查 + 常见 rationalization | `references/rationalizations.md` |

## Always-on rules

1. 优先原生 worktree 工具，fallback 才用 `git worktree` 手工。
2. 开工前验干净基线（对应语言的 build/test 最小集），脏基线先记后修。
