---
name: hermes-dual-memory-architecture
description: Hermes 双记忆库并行架构定案：provider=openviking 是叠加层而非替换；内置库限额顶格时做减法迁移 OpenViking，不调限额
metadata:
  node_type: memory
  type: project
---

**Hermes 双记忆库并行架构**（2026-09-07 源码考证 + 用户拍板方案 B）：

- **根因考证**（hermes-agent 源码 `agent/agent_init.py` + `tools/memory_tool.py`）：`memory.provider: openviking` 只是**叠加**外部 provider（源码注释原话 "one at a time, **alongside built-in**"），内置 MEMORY.md/USER.md 始终并行存在且作为**每会话冻结快照全量注入系统提示词**。所以「记忆库满」永远指内置库，与 OpenViking 无关。
- **限额**：`memory.memory_char_limit: 3000` / `user_char_limit: 2000`（官方默认 2200/1375，~800 tokens @ 2.75 chars/token）。顶格表现：系统提示标注 99%。
- **用户拍板（方案 B，2026-09-07）**：**维持限额，低频内容迁 OpenViking**，不调大限额（调大=每会话系统提示词固定膨胀，全部上下文买单）。
- **分层准则**：
  - **内置库（高频必带）**：身份、环境拓扑、铁律、工作偏好等每会话都该直接可见的事实；
  - **OpenViking（低频可检索）**：运维细节、项目进展、排障记录、变更历史——用 `viking_remember` 提交（异步 session 抽取，可能被合并/跳过），需要时 `viking_search` 召回。
- **迁移操作规范**：先 `viking_remember` 全部 accepted → **抽验 `viking_search` 召回命中后再删内置条目**（防抽取失败丢数据）；删后用一次 `memory` batch op 收尾。
- **首轮迁移实绩（09-07）**：7 条低频事实迁 OpenViking（WorkBuddy 细节/浏览器治理/token-stats/TG 频道/ZCode 跨端规范/token 双口径/架构杂项），抽验 4 条全部高分召回（TG 0.747、浏览器治理 0.74）；内置库 MEMORY.md 99%→49%、USER.md 99%→77%；hermes 分支备份 commit `27dffeb`。
- **防复发**：内置库已写入「记忆架构」条目——低频细节默认走 viking_remember，双库顶格时优先做减法，不调限额。

**Why:** 内置库内容每轮随系统提示词发送，盲目扩容等于为冷门事实支付全量 token 成本；OpenViking 检索层无此限额且专为召回设计，分层才是正确形态。
**How to apply:** 日常新增事实默认先进 OpenViking；只有「每个会话开头就该知道」的才进内置库；顶格时按本准则迁移而非申请扩容。相关：[[hermes-shared-memory]] [[capability-upstream-watch]]
