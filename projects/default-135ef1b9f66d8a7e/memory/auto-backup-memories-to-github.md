---
name: auto-backup-memories-to-github
description: 记忆文件或 OpenViking 数据变动后必须自动提交推送（shared-agent-memory 主库 + openviking-backup 私有仓，无需询问用户，禁止漏推）
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_f34cdac1-9229-49df-a403-763533fbff52
---

用户铁律要求：**后续只要有任何 AI（ZCode 或 Hermes）生成或修改了本地记忆文件（`~/.zcode/cli/memories/`），必须自动将其提交并推送到 GitHub 公开备份仓库 `3304711297/shared-agent-memory`，严禁等待用户提醒，无需询问用户**。

**Why:** 用户希望在更换电脑或重装系统时防止记忆丢失，且记忆备份属于静默保障类操作，询问或漏推会打断会话。

**How to apply:** 只要在本会话中创建、编辑或更新了任何记忆文件（含 `MEMORY.md`），在 turn 结束前必须自动执行（共享内容推 `main` 分支，2026-09-05 三分支重构后）：
```bash
git -C "%USERPROFILE%/.zcode/cli/memories" add -A && git -C "%USERPROFILE%/.zcode/cli/memories" commit -m "memory: 自动备份最新共享记忆" && git -C "%USERPROFILE%/.zcode/cli/memories" push origin main
```
直连失败时回退 `-c http.proxy=http://127.0.0.1:3067`。若改动的是 ZCode 专属内容（zcode 分支），则 checkout zcode 提交推送后切回 main。分支归属详见 [[multi-branch-memory-backup]]。

## OpenViking 写后即时灾备（2026-09-09 增补）

用户拍板：**凡本轮 AI 写入过 OpenViking**（viking_remember、add_resource、记忆/资源/技能挂载、任何 data/ 目录写入），**turn 结束前必须额外静默执行一次 OpenViking 灾备脚本**（幂等，无变更秒退）：

```bash
cmd /c "D:\\openviking-backup\\sync.cmd"
```

- 脚本行为：robocopy 镜像 `~/.openviking/data/viking/default/` 的 user+resources → `D:\openviking-backup\repo` → 有差异才 commit+push 私有仓 `3304711297/openviking-backup` main
- 与每日计划任务 `OpenVikingDailyBackup`（09:30）**互补共存**：即时触发压缩暴露窗口，计划任务兜底会话后台异步提炼等 AI 无感知的写入，两者都不可省
- 失败不重试不阻塞（本地 commit 保留，下轮或计划任务补推）；恢复 SOP 见 OpenViking entities/软件工具/openviking.md
