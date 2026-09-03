---
name: superpowers-usage
description: superpowers 插件是开发纪律套件（TDD/计划/调试方法论），用于编码项目而非运维型工作
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_7baee9ca-827c-4e0e-a934-428b42e9eb6a
---

superpowers 插件（brainstorming / writing-plans / test-driven-development / systematic-debugging / requesting-code-review / verification-before-completion 等）是**软件开发流程纪律**，不是工具箱。2026-08-23 与用户确认的选型结论（保留勿卸）：

- **对编码项目正好对口**：用户提「给 openrouter-chinese 加功能」「tweak 修 bug」这类需求时，应按其流程走：brainstorming 对齐需求 → writing-plans → TDD 实现 → 完工前 verification-before-completion（先跑验证再宣称完成）。用户 openrouter 项目「两轮工程复审 + 30 项单测」的质量标准与这套纪律同路。
- **对运维型工作（浏览器/配置/git/装软件）无触发场景**——2026-08-22~23 的 Edge 接管长会话中一次未用，属正常。
- 排障时若自然走了「假设→对照实验→逐个排除」的路径，即使没显式调用 systematic-debugging 技能也算符合其精神。
- 与 [[desktop-commander-overview]] 的分工：DC 管数据分析，superpowers 管开发纪律。
