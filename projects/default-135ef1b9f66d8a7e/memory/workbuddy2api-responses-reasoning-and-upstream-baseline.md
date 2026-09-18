---
name: workbuddy2api-responses-reasoning-and-upstream-baseline
description: workbuddy2api 补齐 Responses 多轮 reasoning item 静默丢弃缺口（TDD+变异验证），并固化上游看门雷达的基线与自动收口口径
metadata:
  node_type: memory
  type: project
---

# workbuddy2api：Responses reasoning item 缺口与上游看门收口（2026-09-18）

## 一、真实缺口：Responses 多轮历史的 reasoning item 被静默丢弃

**现象**：采用 Responses wire format 的客户端（Codex CLI 等）会把上一轮的思维链以
`{"type":"reasoning", "id":"rs_...", "summary":[...]}` item 随多轮历史一并回传。
本仓 `responses_compat._convert_input_items` 原先**没有该类型分支**，而该 item 也**不带
`role`** —— 两个条件都不命中，落进末尾「其他类型保底」分支后因 `if role:` 为假被整个跳过：

> **无消息产出、无告警、无日志。** 表现为多轮对话后思维链凭空消失，客户端只见正文。

这是**静默数据丢失**，比"报错"难排查得多 —— 排查时不能只看日志，必须实跑转换函数比对输出。

**修复语义**（`responses_compat.py`）：
- 新增 `_extract_reasoning_text(item)`：规范位置 `summary`（部件数组 / 字符串），缺失时回退
  `content`（字符串 / 部件数组，兼容 `reasoning_text` / `text` / `output_text` / `summary_text`
  四种部件名 —— 上游日志显示各家实现在两处之间摇摆，漏一个就又是一次静默丢失）；
- 新增 `pending_reasoning` 暂存：reasoning 紧邻其所属 assistant 轮次**之前**（规范输出序），
  由 `_flush_assistant` 随该轮一并落地为 `reasoning_content`；
- 同轮多条 reasoning 按出现顺序 `\n` 拼接，**不覆盖**；
- **孤儿 reasoning 显式作废**：其后紧跟 user 消息、无归属轮次时在简单消息分支清空暂存。
  暂存语义下若不清理会漂到后面某个毫不相干的 assistant 上 —— **错误归因比缺失更难排查**；
- 空 reasoning 不注入空 `reasoning_content`，不制造伪字段。

## 二、与既有 `backfill_reasoning_content` 的关系（重要）

`deepseek_thinking.backfill_reasoning_content` 在「历史中已存在带 reasoning 的 assistant
消息」时才补齐同轮一致性，用于防上游 `11133 model_param_invalid`。

**它此前形同虚设**：reasoning 在**转换阶段就被丢掉**，回填根本无从触发。修复后两条链路
**互补而非重复** —— 转换阶段先保住数据，回填阶段再保一致性。判断某处"回填/兜底逻辑是否
真的在工作"时，必须先确认上游阶段没有把数据提前扔掉。

## 三、验证方法论（本项目的评审基线）

- **TDD**：先写 7 条测试并确认按预期失败（RED 证据：4 条 `KeyError: 'reasoning_content'`），
  再写实现。空 reasoning 那条修复前"碰巧"通过，修复后必须仍绿（防过拟合）。
- **变异验证（证明用例真能抓回归）**：① 删掉 reasoning 分支 → 5 条变红；② 多条改回
  "只取最后一条" → 拼接用例变红；还原 → 全绿。**只跑绿不算证据**。
- **CI 侧复核**：确认 CI 日志里出现新的用例总数（本例 431 passed），而非只看 job 结论 ——
  否则无法区分"新用例真跑了"与"CI 跑的是旧代码"。

## 四、上游看门雷达（借鉴雷达）的基线与自动收口口径

- `tools/upstream-sources.json` 的 `last_synced_commit` / `last_synced_sha` 是**收口凭据**：
  评估落地或判定无需采纳后推进基线并推 main，Upstream Watch CI 在
  `has_updates == false && has_query_failures == false` 时**自动关闭 Issue**（实测合并后
  约 20 秒内收口）。**不要手动关 Issue**，那是工作流的职责。
- **评估要看"最新"，不是"记得的那个"**：本次曾把某源判为"UI 调整、不吸收"，之后上游又推了
  一版把性质从 UI 变成了协议缺口。**每次收口前重新取 `commits/main` 的 HEAD**，不要复用
  上一轮的评估结论。
- **仓库更名要同步记录**：`ardeyouxipianyi/workbuddy2api-intl` → `-hub`，GitHub API 会重定向
  但基线里的 `repo` 字段应更新，`name` 一并注明更名，避免"名字写 intl、repo 却是 hub"的困惑。

## 五、把"跨 Agent 协作"当作常规工位（本项目实践）

除本地主控外，Arena 的 Agent Mode 承担云端副产线：在**非主分支**（本仓约定
`arena/<session-id>-workbuddy2api`）独立探路与打样，产出走 PR 交付，本地主控负责高精度
闭环（全量测试 + CI + Cherry-pick 择优）。本次该会话先提交 PR #15（SSRF 校验收敛、测试
配置隔离、上游基线推进），本地复核通过后合并。

## 相关

- 仓库：`3304711297/workbuddy2api`（本地工作区 `D:\ai coding\GitRepos\workbuddy2api`）
- 契约文件：`responses_compat.py` / `tests/test_responses_api.py` / `tools/upstream-sources.json`
- 相邻专题：[[Workbuddy2api Hot Reload and Rebrand Cleanup]]、[[Codebuddy2openai Upstream Benchmark]]
