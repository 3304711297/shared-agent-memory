---
name: dispatching-parallel-agents
description: "有2个以上独立任务时必用。Fork-First并行调度子代理。Use when facing 2+ independent tasks; dispatch parallel subagents."
---

# Dispatching Parallel Agents — Router

2+ 独立任务 Fork-First：定独立域 → 写聚焦任务 → 并行分派 → 评审集成。

## Routing table

| Need | Read |
|---|---|
| 四步模式 + Agent 提示词结构 | `references/pattern-prompts.md` |
| 常见错 + 何时不用 + 真实例子 + 验证 | `references/mistakes-example-verify.md` |

## Always-on rules

1. 同文件只许一个 writer；主会话做调度聚合，不串行代跑。
2. 非独立/需顺序的任务不用 fan-out，别为并行而并行。
