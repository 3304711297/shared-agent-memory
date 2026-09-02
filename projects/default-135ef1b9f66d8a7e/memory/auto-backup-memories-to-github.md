---
name: auto-backup-memories-to-github
description: 记忆文件变动或新增后必须自动提交并推送到私有仓库 zcode-memories（无需询问用户）
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_f34cdac1-9229-49df-a403-763533fbff52
---

用户铁律要求：**后续只要有任何 AI 生成或修改了本地记忆文件（`~/.zcode/cli/memories/`），必须自动将其提交并推送到 GitHub 私有备份仓库 `3304711297/zcode-memories`，无需询问用户**。

**Why:** 用户希望在更换电脑或重装系统时防止记忆丢失，且记忆备份属于静默保障类操作，询问会打断会话。

**How to apply:** 只要在本会话中创建、编辑或更新了任何记忆文件（含 `MEMORY.md`），在 turn 结束前必须自动执行：
```bash
cd "C:/Users/VOS-User/.zcode/cli/memories" && git add . && git commit -m "backup: 自动备份最新记忆" && git push
```
