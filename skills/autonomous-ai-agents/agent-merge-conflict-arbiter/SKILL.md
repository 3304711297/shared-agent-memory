---
name: agent-merge-conflict-arbiter
description: "两Agent合并冲突仲裁时必用。中性裁决双方分歧。Neutral arbiter for merge conflicts between two agents."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Multi-Agent, Git, Merge-Conflict, Kanban, Arbitration]
    related_skills: [hermes-agent]
---

# Agent Merge-Conflict Arbiter — Router

两 Agent 合并冲突的中性仲裁：收双方 → 逐 hunk 分类 → 按中立契约裁决 → 验证 → 交回。

## Routing table

| Need | Read |
|---|---|
| 五步仲裁 procedure | `references/procedure.md` |
| 坑 + 验证 | `references/pitfalls-verify.md` |

## Always-on rules

1. 中立性：不因「谁先写/谁写得多」偏袒，只按契约与测试裁决。
2. 每 hunk 必分类记录，裁决后跑相关测试再交回。
