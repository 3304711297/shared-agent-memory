---
name: hermes-shared-memory
description: hermes 通过 shared-agent-memory skill 直接读写本共享记忆库；共享协议与全自动同步边界
metadata:
  node_type: memory
  type: project
  originSessionId: sess_76a3a301-0dc5-444b-9b1a-8b0802281a9c
---

hermes-agent（[[hermes-agent-install]]）与 ZCode **共享本记忆库**（2026-09-02 设立，2026-09-03 重命名为 `shared-agent-memory`，本目录即唯一真源）：

- hermes 侧入口：本地 skill `shared-agent-memory`（`%LOCALAPPDATA%\hermes\skills\zcode-custom\shared-agent-memory\SKILL.md`）+ SOUL.md 常驻指针；协议见该 skill 文件（何时读写、frontmatter 格式、更新优先于新建）。
- **【铁律】记忆自动推送 GitHub**：任何 Agent（ZCode 或 Hermes）修改或新增共享记忆库文件后，在当前 turn 结束前必须自动提交并推送至 `3304711297/shared-agent-memory`（zcode 分支），严禁遗漏或等待用户提醒。
- hermes 专属的局部会话记忆在其家目录 `%LOCALAPPDATA%\hermes\memories\`，同样在有变动时自动推送到 `hermes` 分支隔离备份。
- 跨 agent 持久事实统一入本共享库。

**Why:** 两个 agent 共用一套记忆库消除漂移；自动备份至 GitHub 确保跨机与防丢失，零打扰用户。
**How to apply:** 涉及持久事实必须写入本库，并立即执行 git 自动提交推送。
