---
name: auto-backup-memories-to-github
description: 记忆文件变动后必须自动提交推送到 shared-agent-memory（无需询问用户，禁止漏推）
metadata:
  node_type: memory
  type: feedback
---

用户铁律要求：**只要有任何 AI 生成或修改了本地记忆文件，必须自动将其提交并推送到 GitHub 仓库 `3304711297/shared-agent-memory`，严禁等待用户提醒，无需询问用户**。

**Why:** 用户希望在更换电脑或重装系统时防止记忆丢失，且记忆备份属于静默保障类操作，询问或漏推会打断会话。

**How to apply:** 只要在本会话中创建、编辑或更新了任何记忆文件，在 turn 结束前必须自动执行（共享内容推 `main`，Hermes 专属内容推 `hermes` 分支）：

```bash
git -C "D:/ai coding/GitRepos/shared-agent-memory" add -A && git -C "D:/ai coding/GitRepos/shared-agent-memory" commit -m "memory: 自动备份最新共享记忆" && git -C "D:/ai coding/GitRepos/shared-agent-memory" push origin main
```

直连失败时回退 `-c http.proxy=http://127.0.0.1:3067`。分支归属与脱敏要求详见 [[multi-branch-memory-backup]]。

## ⛔ 已撤销：OpenViking 写后即时灾备（原 2026-09-09 增补）

原规则要求「凡本轮写入过 OpenViking 就在 turn 结束前跑 `D:\openviking-backup\sync.cmd`」。**该服务与备份仓已于 2026-09-21 物理卸载**（见 [OpenViking Retired](openviking-retired.md)）：`~/.openviking`、`D:\openviking-backup`、私有仓 `3304711297/openviking-backup`、Windows 计划任务 `OpenVikingDailyBackup` 均已删除，`sync.cmd` 不存在了 —— **不要再尝试执行它**。

## 规则放置原则（2026-09-11 教训，仍然适用）

**跨会话必须自动执行的约束，不能只存放在检索层**（共享库文档）——它们仅在当前话题语义命中时才进入上下文。凡属「无条件触发」类规则（如写后同步），必须**同时**写入：

1. 内置 `MEMORY.md`（每轮无条件注入，永远可见）；
2. 对应技能正文（任务命中时加载，提供执行细节）。

**事故记录**：2026-09-11 修 Hermes 插件 bug 时执行了记忆写入，但同步规则当时只存在于本文件与检索层中，话题不相关故未被召回；当轮已加载的 `shared-agent-memory` 技能正文也只含 git 推送规则。结果整轮无人提醒同步，直到用户手动贴出仓库 URL 才补跑（补跑时已积压 82 个文件变更）。修复：三处补齐。
