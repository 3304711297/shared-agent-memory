---
name: receiving-code-review
description: "收到评审意见时必用。实证求真，禁止盲从迎合。Use when receiving code review feedback; verify before implementing."
---

# Code Review Reception — Router

收到评审意见：实证求真，禁止盲从迎合。先定回应模式，再按来源处理。

## Routing table

| Need | Read |
|---|---|
| 回应模式 + 禁止事项 + 模糊反馈处理 | `references/response-pattern.md` |
| 人类/外部评审来源处理 + YAGNI 检查 + 实现顺序 | `references/source-handling.md` |
| 外部 AI 评审实证复核（反向对拍/剥注释断言/锁死防退化） | `references/external-ai-review.md` |
| 何时 push back + 正确致谢/纠正 | `references/pushback-ack.md` |
| 真实例子 + GitHub thread 回复格式 | `references/examples-threads.md` |

## Always-on rules

1. 每条意见先复现/实证再改；「看着专业」的功能先过 YAGNI。
2. 修完加锁（测试/契约）防退化，不裸修。
