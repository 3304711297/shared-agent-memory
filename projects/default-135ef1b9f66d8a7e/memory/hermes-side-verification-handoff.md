---
name: hermes-side-verification-handoff
description: 用户可指令 Hermes 旁路接手当前会话的全量构建/代码审查/验收——ZCode 此时只做底线检查、本地提交保护现场、冻结树待验收，验收后再推送
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_656a8367-2a67-4b01-be2c-f06bb80ecba5
---

2026-09-05 codebuddy2openai 批次4 拆分期间，用户通知「Hermes 已经在旁路监听当前会话与子代理」：ZCode 完成 4A（main.js）与 4B（commands.rs）拆分后**不必重复跑冗长全量验证**，汇报最终模块结果即可；Hermes 直接在本地接手跑全套构建、代码审查并给出验收反馈；中途卡死或编译死锁由 Hermes 直接介入修复。

**Why:** 双代理并跑时全量验证重复且耗时；Hermes 在同一台机器本地实时接手，用户以此分工省时。

**How to apply:** 遇到用户声明 Hermes 接手验收时——①只做秒级底线检查（如一次 cargo check）确认交接的不是坏树；②把工作落成**本地提交**保护现场（防误操作丢未跟踪文件），但**不推送**（推送触发 CI 与 Hermes 验收流程冲突）；③汇报模块清单与「审查重点」供其定向审查；④审查期间**冻结树**（不再叠加新改动，后续批次压后），验收反馈回来后再继续并推送。另注意：被取消的子代理可能已写完全部文件，接手前先 git status/diff 审计残骸。相关 [[codebuddy2openai-upstream-benchmark]] [[hermes-shared-memory]] [[user-global-preferences]]
