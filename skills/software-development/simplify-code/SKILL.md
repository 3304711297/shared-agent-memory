---
name: simplify-code
description: "简化代码/重构收尾时必用。四代理并行审查去冗余。Use when asked to simplify, clean up, or refactor recent code changes."
version: 1.2.0
author: Hermes Agent (inspired by Claude Code /simplify)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, cleanup, refactor, delegation, subagent, parallel, simplify]
    related_skills: [requesting-code-review, test-driven-development]
---

# Simplify Code — Router

Four narrow parallel reviewers (reuse/quality/efficiency/altitude) over recent changes.
**Cleanup pass, not a bug hunt** — 正确性 bug 走 `requesting-code-review`。

## Routing table

| Need | Read |
|---|---|
| 变更范围界定（worktree/staged/scoped） | `references/workflow.md` |
| 四 reviewer 并行提示词 | `references/reviewers.md` |
| 聚合裁决 + 应用修复 | `references/aggregate-apply.md` |
| 常见坑 | `references/pitfalls.md` |

## Always-on rules

1. 四 reviewer 并发跑，只付一份 latency。
2. 只改值得改的：去重/降复杂/删浪费/加深 band-aid；不顺手重构无关代码。
3. 应用前聚合去重，冲突项由主会话裁决。
