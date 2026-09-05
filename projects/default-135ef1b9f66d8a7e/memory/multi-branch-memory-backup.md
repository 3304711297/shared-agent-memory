---
name: multi-branch-memory-backup
description: 共享记忆库三分支架构（2026-09-05 重构）：main=双端共享唯一真源，zcode/hermes=各自专属内容分支；谁改动谁当轮推送
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_888b469b-882a-4e84-aeed-8d68b401a67c
---

用户铁律要求（2026-09-05 定稿）：**记忆库采用「共享主分支 + Agent 专属分支」模型，有变动时自动静默提交并推送，严禁等用户提醒**。目的：切换 Agent 无需重新拉取文件——共有内容只有一份。

- 远程仓库：`https://github.com/3304711297/shared-agent-memory.git`（默认分支 `main`）
- **`main` 分支 = 双端共享记忆库唯一真源**：物理位于 `C:\Users\VOS-User\.zcode\cli\memories\`（本地检出分支），Hermes 经 NTFS 目录联接 `%LOCALAPPDATA%\hermes\memories\topics` 直读同一目录（见 [[hermes-shared-memory]]）。任何一方修改共享内容，当轮结束前执行：
  ```bash
  git -C "C:/Users/VOS-User/.zcode/cli/memories" add -A && git -C "C:/Users/VOS-User/.zcode/cli/memories" commit -m "memory: <简述>" && git -C "C:/Users/VOS-User/.zcode/cli/memories" push origin main
  ```
  （直连失败回退 `-c http.proxy=http://127.0.0.1:3067`；Hermes 与 ZCode 都可直接推 main，无需中转。）
- **`zcode` 分支 = ZCode 专属**（orphan 占位分支）：只放只能在 ZCode 端使用、不与 Hermes 共享的内容；`git checkout zcode` 提交后切回 main。
- **`hermes` 分支 = Hermes 专属**（本地目录 `%LOCALAPPDATA%\hermes\`）：SOUL.md、原生记忆 USER.md/MEMORY.md、技能与插件配置等 Hermes home 白名单内容；**已不再跟踪共享 topics 镜像**（.gitignore 排除 `memories/topics/`）。
- 安全铁律：hermes 分支 .gitignore 白名单严格过滤，严禁推送 `.env*`、`auth.json`、`*.db`、`*.log`、`sessions/` 等敏感与临时数据。

**Why:** 旧模型共享内容在 zcode/hermes 两分支各存一份镜像，频繁漂移，每次切 Agent 都要手工拉取合并；单一共享分支 + 物理单副本（junction）彻底消除双份维护。
**How to apply:** 判断内容归属：两端都该知道的 → main；仅 ZCode 用 → zcode；仅 Hermes 用 → hermes。相关：[[hermes-shared-memory]] [[auto-backup-memories-to-github]]
