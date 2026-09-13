---
name: skill-evaluation-and-admission
description: "评估新技能/值不值得装时必用。五步准入审计SOP。Use when evaluating new skills, tools, or repos; answers 「值得安装吗」."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, evaluation, admission, prompt-caching, trigger-design, watchdog]
    related_skills: [writing-skills, hermes-agent-skill-authoring]
---

# Skill Evaluation and Admission — Router

新技能/工具/仓库的五步准入审计 + 「Agent 无视技能」治理。**内容零改动，纯路由化。**

## Routing table

| Need | Read |
|---|---|
| 五步准入审计（Step 0 去重门 → Step 5 看门同步） | `references/five-step.md` |
| 安全红线清单（admission must-pass） | `references/security-checklist.md` |
| Skill-First 反射门禁 / 57字符规则 / 80/20 瘦身 | `references/invocation-discipline.md` |

## Always-on rules

1. 改技能 = 原子事务：文件改动 + `capability-inventory.json` + CI 全绿，同轮完成。
2. 本地中文 description 定制禁止被上游覆盖（drift 检查白名单语义）。
