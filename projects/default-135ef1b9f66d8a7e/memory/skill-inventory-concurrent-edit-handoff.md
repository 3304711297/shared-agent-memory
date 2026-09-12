---
title: 技能清单并发编辑交接（2026-09-12 双会话）
tags: [skills, provenance, 并发, 交接]
updated: 2026-09-12
---

# 技能清单并发编辑交接

两个 Hermes 会话同晚都在改技能，且都会写 `skills-provenance.json`。
**本文是交接便签，避免后推的一方覆盖先推一方的记录。**

## 冲突背景

| 会话 | 时间 | 动作 |
|---|---|---|
| A（本会话，workbuddy2api 修复线） | ~23:4x | 新建 `software-development/diagnosing-probe-false-failures`，把清单 93→94 并推送 `36fa760` |
| B（`@session:default/20260912_234048_1b2985`，Astra 瘦身线） | ~23:50 起 | 执行 OpenAI 官方 6 条瘦身标准：删 5 个 Ekko 生图/视频技能、拆分巨型 skill 为 router+references |

**冲突点**：B 删技能后磁盘从 94 → 89，而 A 的 `36fa760` 把清单锁在 94。
B 推送时会重算清单，届时 A 的记录会被覆盖——这是**预期且正确的**（以磁盘真源为准）。

## B 会话收尾时必须保留的 A 侧记录

重算清单时，以下条目必须仍在（它们是磁盘上真实存在的新增/修改）：

1. **`software-development/diagnosing-probe-false-failures`**（新增，归入「自研(无 author)」组）
   - 内容：探针/健康检查/连通性测试失败的分层诊断法
     （区分「路由错误 404+近零延迟」与「预算饿死正文 HTTP 200 空结果」）
2. **`superpowers/receiving-code-review`**（既有技能，A 做了**本地增强**）
   - 新增章节「外部 AI 评审（ChatGPT / Claude / 其它模型）的实证复核」
   - ⚠️ **这是本地增强，不得被上游同名文件同步覆盖**（三仓库维护规则）

## 被 B 删除、清单中须同步移除的 5 条

`apikey-image-gen`、`grok-image-to-video`、`hyperframes`、`minimax-image-to-video`、`remotion`
（均为 Ekko 生图/生视频类，B 已确认删除，保留 `g​emini-image-gen` 为生图主入口）

## 并发协作规则（本次确立，后续同场景复用）

1. **后推者重算，先推者让路**：清单以「磁盘 `skills/` 目录」为唯一真源，
   谁最后推谁负责按当时磁盘状态重算，不要求先推者回补。
2. **先推者留交接便签**：发现并发编辑时，先推方把「自己新增/修改的条目」
   写进 `topics/` 便签（就是本文），后推方重算时照单保留。
   不要抢写清单文件本身——两个会话同时写 JSON 必然互相覆盖。
3. **本地增强必须标注**：任何对上游同名技能的本地修改都要在便签里点名，
   否则后推方按上游同步时会静默冲掉（本次 `receiving-code-review` 即此例）。
