---
name: hermes-shared-memory
description: hermes 通过 zcode-shared-memory skill 直接读写本记忆库；共享协议与边界
metadata:
  node_type: memory
  type: project
  originSessionId: sess_76a3a301-0dc5-444b-9b1a-8b0802281a9c
---

hermes-agent（[[hermes-agent-install]]）与 ZCode **共享本记忆库**（2026-09-02 设立，本目录即唯一真源）：

- hermes 侧入口：本地 skill `zcode-shared-memory`（`%LOCALAPPDATA%\hermes\skills\zcode-shared-memory\SKILL.md`）+ SOUL.md 常驻指针；协议见该 skill 文件（何时读写、frontmatter 格式、更新优先于新建）。
- **hermes 写入的文件不提交 git**（协议明确禁止）——发现未提交的记忆文件时由 ZCode 负责提交推送（符合既有自动备份铁律）。
- hermes 自己的会话记忆在其家目录 `%LOCALAPPDATA%\hermes\MEMORY.md` + `USER.md`，与会话状态相关，不必同步；跨 agent 持久事实才进本库。
- 如发现库中出现格式不符的条目，可按本库规范整理，视为 hermes 写入的待规范化内容。

**Why:** 两个 agent 各记一套会漂移；共享后用户在任一侧说过的持久事实另一侧都能回溯。
**How to apply:** 涉及 hermes 的持久事实可直接写本库（hermes 下次会话可读到）；看到库里有非 ZCode 风格的新文件时按上述边界处理，勿删除。
