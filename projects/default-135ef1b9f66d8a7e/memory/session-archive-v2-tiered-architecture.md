# 会话归档系统升级至 v2.0 (L0/L1/L2 结构化真源 + SPA 查看器)

> 状态：生效中 (2026-09-23 用户拍板并完成闭环落地)  
> 归档私有仓：`3304711297/shared-agent-sessions`

---

## 一、 升级背景与 ChatGPT 对拍裁决

原有备份流程存在三大痛点：
1. **解析严重失真**：SQLite 中 `messages.tool_calls` 为 TEXT JSON 字符串，旧导出脚本误将其当做列表遍历，导致生产 Markdown 出现大量无意义的 `- 🔨 调用 tool` 刷屏，工具名与参数全部丢失；
2. **缺乏层次（信息过载）**：单会话导出动辄 3~5 万行纯流水账，打开卡死，无法一眼看清意图和决策；
3. **流程老套繁琐**：每次收尾都要求人工反查 session_id 并显式传参敲长命令。

对标 OpenViking Web Studio 与分层上下文规范，经与 ChatGPT 深度对拍审查（确立 12 条落地契约），完成系统性重构。

---

## 二、 核心架构规范 (v2.0)

1. **唯一历史真源**：
   - `messages.jsonl` (L2) 为**唯一历史真源**。
   - 所有 L0（`.abstract.md`）、L1（`.overview.md`）、`meta.json`、`catalog/index.json`、README 与 Markdown 均为**无状态可重建派生物**。删除任何派生文件，随时可通过 `python tools/rebuild_catalog.py` 100% 幂等无损全量重建。
2. **OpenViking 风格分层投影**：
   - **L0 (`.abstract.md`)**：一句话意图、产出与状态规范 `[Intent] | [Result] | [Status]`，供秒级扫读；
   - **L1 (`.overview.md`)**：提炼任务核心意图、改动文件清单、关键单测/验证命令与执行状态；
   - **`meta.json`**：严格固化 schema_version 2、session_id、主力模型与摘要。
3. **Session Studio 现代化静态查看器 (`viewer/index.html`)**：
   - 零后端依赖的纯前端现代 SPA，对标 OpenViking Web Studio 审美与布局；
   - 左侧：跨会话实时模糊搜索（标题/意图/产出/模型）、时间线折叠树、会话卡片；
   - 右侧：顶部 L0/L1 概览卡片、对话气泡、深度推理思考过程（Thinking）折叠块、工具调用胶囊（参数格式化、超长输出折叠与一键复制）；
   - 启动命令：`python tools/view_sessions.py`（秒级拉起本地 HTTP 并自动弹窗打开）。
4. **零负担一键式备份命令**：
   - 终端直接运行：
     ```bash
     python tools/upload_session.py
     # 或 tools/archive.cmd
     ```
     无需任何参数，自动精准定位当前最新活跃会话，一键完成 L0/L1 提炼、L2 归档、catalog 更新与 path-scoped 安全推送！
5. **健壮性安全加固**：
   - 彻底废除 `wal_checkpoint(TRUNCATE)`，避免争抢生产写锁；
   - 快照采用临时文件校验后原子替换（`os.replace`），杜绝快照失败导致旧库丢失；
   - 废除 `git add -A`，全面推行 path-scoped 精确 staging。
