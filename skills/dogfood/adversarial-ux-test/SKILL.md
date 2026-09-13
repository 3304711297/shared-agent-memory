---
name: adversarial-ux-test
description: "挑刺UX/恶意用户测试时必用。扮演敌意用户找UX痛点。Roleplay a hostile user to find and triage UX pain points."
version: 1.1.0
author: Omni @ Comelse
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [qa, ux, testing, adversarial, dogfood, personas, user-testing]
    related_skills: [dogfood]
---

# Adversarial UX Test — Router

扮演恶意/刻薄用户找 UX 痛点：定 persona → 用 persona 浏览 → rant → 功利过滤 → 建 ticket → 报告。

## Routing table

| Need | Read |
|---|---|
| 完整六步法（含 persona 好坏例 + rant + 过滤器） | `references/method-steps.md` |
| 分行业 persona 库 + tips + 硬规则 | `references/personas-tips-rules.md` |

## Always-on rules

1. Step 4 功利过滤不许跳：rant 里只有可复现、可归因的才建 ticket。
2. 每个 ticket 带复现路径 + 截图/证据，不写感觉型反馈。
