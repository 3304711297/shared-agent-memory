---
name: zcode-decommissioned
description: ZCode 客户端已于 2026-09-09 全量拆除；共享记忆库为 Hermes 单端所有；唯一遗留关联是未来活动赠额经反代进 Hermes
metadata:
  node_type: memory
  type: project
---

# ZCode 拆除终态（2026-09-09）

**Why:** 用户明确不再使用 ZCode 客户端（Hermes 为唯一主力 Agent），ZCode 客户端、全部配置、会话数据、注册表残留均已通过 HiBit Uninstaller 清除；所有有价值数据已先行抢救上云。唯一保留的关联：未来智谱在 ZCode 客户端发活动赠额时，经社区反代（TriDefender/zcode-api, start-plan 模式）转 OpenAI 兼容端点供 Hermes 消费（SOP 见 OpenViking zcode_api 卡）。

**How to apply:**
- 一切「双端 / Hermes×ZCode / 跨端」历史文档仍可读，但其中 ZCode 侧操作步骤已过时——执行前对照本卡判定；不确定时先查真源。
- 共享记忆库真源 = `D:/ai coding/GitRepos/shared-agent-memory`（git 仓库根），hermes `memories\topics` junction 指向 `projects\default-135ef1b9f66d8a7e\memory\`；`.zcode` 侧旧路径已不存在，严禁再引用。
- ZCode 会话转录归档于姊妹私有仓 `3304711297/shared-agent-sessions` 的 `zcode` orphan 分支（GUI db.sqlite.gz 75MB + 24 个 CLI 会话 agents/ + rollout/artifacts/exec）；Hermes 会话归档在同一仓库 `main` 分支。
- 历史归档类文档（hermes-to-zcode-capability-sync、cross-agent-handshake-mechanism、hermes-side-verification-handoff、hermes-zcode-token-gap-investigation、zcode-desktop-config-architecture 等）保留作知识沉淀，不删除、不再维护。
- watch_zcode.py 已随 ZCode 拆除失去目标（db.sqlite 不存在），脚本保留于 %LOCALAPPDATA%\hermes\scripts\ 但不可再调用；跨会话唤醒需求改由用户直接指令驱动。
