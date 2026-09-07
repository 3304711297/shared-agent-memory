---
name: hermes-memory-tiering
description: "Use when 内置记忆库顶格告警或需分层整理。低频迁 OpenViking，内置只留高频。"
---

# Hermes 内置记忆库分层管理（内置双库 + OpenViking）

## 架构事实（动手前必知，防误诊）

- `memory.provider: openviking` 是**叠加**而非替换（agent_init.py 原注释：external provider runs "alongside built-in"）。内置 `memories/MEMORY.md`（agent 笔记）与 `memories/USER.md`（用户画像）始终存在，作为**冻结快照在会话启动时全量注入系统提示词**。
- 内置限额在 config.yaml：`memory.memory_char_limit` / `memory.user_char_limit`（当前 3000/2000，以实机 config.yaml 为准）。系统提示里「99% — x/y chars」就是这两库的占用，**与 OpenViking 无关**——「记忆库满」永远是内置库顶格，不要往 provider 方向排查。
- OpenViking（viking_remember / viking_search）无字符限额，按语义检索召回，是低频事实的正确去处。

## 分层铁律（用户拍板）

- 内置双库只留**高频必带**事实：身份、环境路径、安全铁律、活跃项目锚点。低频细节（单次排障记录、组件演进史、事件收尾）用 `viking_remember` 入 OpenViking。
- 顶格时**做减法，不调限额**。调大限额 = 每个会话的系统提示词永久膨胀，禁走此路。
- 新增事实默认先进 OpenViking；某事实开始几乎每个会话都被检索到时，才升入内置库。

## 迁移 SOP（顶格时执行）

1. 通读两库，分类「高频必带」vs「低频可检索」，列迁移清单交用户拍板（用户已拍板方案则直接执行）。
2. **先迁后删**：逐条 `viking_remember`（content 开头加【主题标签】便于日后检索），确认全部 accepted。
3. **验证召回再删**：`viking_remember` 是异步抽取，OpenViking 可能合并或跳过条目——删内置前必须 `viking_search` 抽验 2~3 条关键迁移项，命中高分（≥0.5）才算落库；未命中的先重试提交，严禁凭 accepted 状态直接删源。
4. 用 `memory` 工具的批量 `operations`（remove + replace 压缩）精简两库，同轮合并重复主题。
5. **检查 replace 的附带损伤**：replace 是整条替换——压缩某条时会连带丢掉该条里夹带的独立规则。替换后重读库全文，把误删的规则以独立条目补回。
6. 补一条「记忆架构」自描述条目进内置库（分层策略 + 顶格做减法不做加法），防止未来会话重踩「provider=openviking 为什么还满」。
7. 推 `hermes` 分支备份（命令见技能 shared-agent-memory）后核 CI：该 home 仓库的工作流若仅 schedule/workflow_dispatch 触发，push 后无新 run 属预期——先查 `.github/workflows/` 的 `on:` 触发器再下结论，不算跳过 CI 铁律；有 push 触发器则照常盯绿。
