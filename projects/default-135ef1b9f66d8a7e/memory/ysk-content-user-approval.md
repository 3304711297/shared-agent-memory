---
name: ysk-content-user-approval
description: 往 youshouldknow 塞内容前必须先给可选项让用户拍板，禁止自行决定写什么
metadata:
  type: feedback
---

用户明确要求（2026-09-05）：没有具体说明把什么内容放进 ysk（youshouldknow）时，**不要自行决定写哪些内容**，必须先给出建议清单（可选项 + 一句话理由），由用户选择后再动手。

**Why:** ysk 是用户的知识库，收录什么体现用户的意图与定位；自行判断"有用"直接写入是越权行为。本轮《本地回环服务的暴露面与防护》即属自行决定写入，被此规则纠正。

**How to apply:** 凡涉及 ysk 内容摄入（新文章、现有页扩充、结构调整），先列候选方案让用户勾选；用户明确点名的内容（如"把 X 写进 ysk"）才可直接执行。执行仍须遵守 ysk 文档规范（front matter 三必填、nav+分类索引同步、gen-matrix 重跑，见 [[youshouldknow-doc-details]]）。
