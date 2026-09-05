---
name: auto-backup-memories-to-github
description: 记忆文件变动或新增后必须自动提交并推送到私有仓库 shared-agent-memory（无需询问用户，禁止漏推）
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_f34cdac1-9229-49df-a403-763533fbff52
---

用户铁律要求：**后续只要有任何 AI（ZCode 或 Hermes）生成或修改了本地记忆文件（`~/.zcode/cli/memories/`），必须自动将其提交并推送到 GitHub 私有备份仓库 `3304711297/shared-agent-memory`，严禁等待用户提醒，无需询问用户**。

**Why:** 用户希望在更换电脑或重装系统时防止记忆丢失，且记忆备份属于静默保障类操作，询问或漏推会打断会话。

**How to apply:** 只要在本会话中创建、编辑或更新了任何记忆文件（含 `MEMORY.md`），在 turn 结束前必须自动执行（共享内容推 `main` 分支，2026-09-05 三分支重构后）：
```bash
git -C "C:/Users/VOS-User/.zcode/cli/memories" add -A && git -C "C:/Users/VOS-User/.zcode/cli/memories" commit -m "memory: 自动备份最新共享记忆" && git -C "C:/Users/VOS-User/.zcode/cli/memories" push origin main
```
直连失败时回退 `-c http.proxy=http://127.0.0.1:3067`。若改动的是 ZCode 专属内容（zcode 分支），则 checkout zcode 提交推送后切回 main。分支归属详见 [[multi-branch-memory-backup]]。
