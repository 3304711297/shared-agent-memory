---
name: hermes-memory-tiering
description: "记忆库顶格/要分层时必用。内置记忆瘦身与分层。Use when built-in memory hits the cap."
---

# Hermes 记忆库管理（单真源：内置双库 + Git 共享库）

## 架构事实（动手前必知，防误诊）

- **只有两处持久记忆，无第三方 provider**（OpenViking 已于 2026-09-21 用户拍板物理卸载退役；退役理由：本地 Embedding 常驻占 6.57GB 显存，与 8GB 笔记本显卡上的 ComfyUI/本地模型严重冲突，且双记忆库维护成本过高）。
- 内置 `memories/MEMORY.md`（agent 笔记）与 `memories/USER.md`（用户画像）是**冻结快照，会话启动时全量注入系统提示词**。
- 内置限额在 config.yaml：`memory.memory_char_limit` / `memory.user_char_limit`（当前 4000/3000，以实机 config.yaml 为准）。系统提示里的「99% — x/y chars」就是这两库占用——「记忆库满」永远指内置库顶格。
- **长文真源是 Git 共享库 `shared-agent-memory`**（经 `memories/topics` junction 访问）：专题卡片存 `topics/*.md`，用 `search_files`（ripgrep）按关键字精确检索，零 GPU、零额外服务。工程排坑、组件演进史、事件收尾这类低频细节放这里，不放内置库。

## 语言成本（09-09 实测，动手前必读）

注入块的语言直接决定每轮开销：同义中文比英文贵约 **1.34x token**（o200k_base；同句 104 vs 80）。

**致命陷阱**：限额是 `memory_char_limit`（**字符**），成本是 token。同样 3000 字符，全中文 ≈2490 token，全英文 ≈615 token；但英文表达同样信息要多约 2.5x 字符——**直接翻译必然撑爆限额**。正确顺序：先做减法（低频条目移到共享库专题卡）压掉约 60%，再译英。改完必须实测字符数确认未超限。

**不要为了省几十 token 反复改 SOUL.md**：它位于 cache 前缀最头部，每次改动失效其后整段前缀一次。

## 分层铁律（用户拍板）

- 内置双库只留**高频必带**事实：身份、环境路径、安全铁律、活跃项目锚点、跨会话无条件触发的规则。
- 顶格时**做减法，不调限额**。调大限额 = 每个会话的系统提示词永久膨胀，禁走此路。
- 新增事实默认先进共享库专题卡；某事实开始几乎每个会话都要用时，才升入内置库。

## 瘦身 SOP（顶格时执行）

1. 通读两库，分类「高频必带」vs「低频可查」，列迁移清单交用户拍板（用户已拍板方案则直接执行）。
2. **先迁后删**：把低频条目写成 `topics/<topic>.md` 专题卡（YAML frontmatter + 正文），并同步登记 `topics/MEMORY.md` 索引。
3. 用 `memory` 工具的批量 `operations`（remove + replace 压缩）精简两库，同轮合并重复主题。
4. **检查 replace 的附带损伤**：replace 是整条替换——压缩某条时会连带丢掉该条里夹带的独立规则。替换后重读库全文，把误删的规则以独立条目补回。
5. 推 `hermes` 分支备份（命令见技能 shared-agent-memory）后核 CI。
