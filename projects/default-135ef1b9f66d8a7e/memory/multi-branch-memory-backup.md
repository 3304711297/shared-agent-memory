---
name: multi-branch-memory-backup
description: 双 Agent 记忆多分支隔离备份规则：ZCode 推送 zcode 分支，Hermes 推送 hermes 分支
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_multi_branch_backup_20260903
---

用户铁律要求：**记忆库采用 GitHub 多分支隔离备份模式，有变动时自动静默提交并推送到对应分支**。

- 远程仓库：`https://github.com/3304711297/zcode-memories.git`
- **ZCode 专属分支**：`zcode`（本地目录 `C:\Users\VOS-User\.zcode\cli\memories\`）
  - 触发条件：修改或新增 `.zcode` 记忆文件后，执行 `cd "C:/Users/VOS-User/.zcode/cli/memories" && git add . && git commit -m "backup: 自动备份最新记忆" && git push`
- **Hermes 专属分支**：`hermes`（本地目录 `C:\Users\VOS-User\AppData\Local\hermes\`）
  - 触发条件：修改或新增 Hermes 记忆/技能后，执行 `cd "C:/Users/VOS-User/AppData/Local/hermes" && git add . && git commit -m "backup: 自动备份 hermes 记忆与配置" && git push`
  - 安全铁律：`.gitignore` 严格白名单过滤，严禁推送 `.env*`、`auth.json`、`*.db`、`*.log`、`sessions/` 等敏感与临时数据。

**Why:** 隔离两个 Agent 的记忆与配置演化，避免在同一个分支发生 Git 树合并冲突或互相覆盖。
