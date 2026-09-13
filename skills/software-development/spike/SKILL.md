---
name: spike
description: "验证想法/试水时必用。一次性实验再决定是否开工。Throwaway experiments to validate an idea before build."
version: 1.1.0
author: Hermes Agent (adapted from gsd-build/get-shit-done)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [spike, prototype, experiment, feasibility, throwaway, exploration, research, planning, mvp, proof-of-concept]
    related_skills: [sketch, subagent-driven-development]
---

# Spike — Router

一次性实验验证想法，再决定是否开工。Decompose → Align → Research → Build → Verdict。

## Routing table

| Need | Read |
|---|---|
| 核心五步法 + verdict 模板 | `references/core-method.md` |
| 对比型 spike + frontier 选题 + 输出格式 | `references/comparison-frontier-output.md` |

## Always-on rules

1. 先查「何时不用」：用户已有完整 GSD 系统时走 GSD，不另起 spike。
2. 每个 spike 以 Verdict（VALIDATED/PARTIAL/INVALIDATED）+ 真实构建建议收尾，不留开放式探索。
