---
name: finishing-a-development-branch
description: "功能分支收尾/提PR时必用。合流清理与结论。Use when implementation is complete and ready to merge, PR, or conclude."
---

# Finishing a Development Branch — Router

分支收尾：验测试 → 判环境 → 定 base → 给选项 → 执行 → 清理工作区。

## Routing table

| Need | Read |
|---|---|
| Step 1-4 + 本地合并选项 | `references/steps-verify-merge.md` |
| PR/保持原样/丢弃 + 工作区清理 | `references/steps-pr-cleanup.md` |
| 常见 rationalization 对照 | `references/rationalizations.md` |

## Always-on rules

1. 合并先行、验证后删：merged 结果跑测试通过后才清理任何东西。
2. detached HEAD 推远端必须显式命名分支，不推匿名 HEAD。
