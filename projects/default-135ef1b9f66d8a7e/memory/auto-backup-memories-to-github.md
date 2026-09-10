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
git -C "D:/ai coding/GitRepos/shared-agent-memory" add -A && git -C "D:/ai coding/GitRepos/shared-agent-memory" commit -m "memory: 自动备份最新共享记忆" && git -C "D:/ai coding/GitRepos/shared-agent-memory" push origin main
```
直连失败时回退 `-c http.proxy=http://127.0.0.1:3067`。若改动的是 ZCode 专属内容（zcode 分支），则 checkout zcode 提交推送后切回 main。分支归属详见 [[multi-branch-memory-backup]]。

## OpenViking 写后即时灾备（2026-09-09 增补）

用户拍板：**凡本轮 AI 写入过 OpenViking**（viking_remember、add_resource、记忆/资源/技能挂载、任何 data/ 目录写入），**turn 结束前必须额外静默执行一次 OpenViking 灾备脚本**（幂等，无变更秒退）：

```bash
cd "D:/openviking-backup" && MSYS_NO_PATHCONV=1 cmd /c "sync.cmd"
```

- 脚本行为：robocopy 镜像 `~/.openviking/data/viking/default/` 的 user+resources → `D:\openviking-backup\repo` → 有差异才 commit+push 私有仓 `3304711297/openviking-backup` main
- 与每日计划任务 `OpenVikingDailyBackup`（09:30）**互补共存**：即时触发压缩暴露窗口，计划任务兜底会话后台异步提炼等 AI 无感知的写入，两者都不可省
- 失败不重试不阻塞（本地 commit 保留，下轮或计划任务补推）；恢复 SOP 见 OpenViking entities/软件工具/openviking.md
- **大删守卫（2026-09-11 加固）**：/MIR 镜像会同步删除备份中源已不存在的文件，若源被误删则备份会被一起清空。现脚本在镜像前比对文件数——源 < 备份的 70%（且备份 ≥100 文件）即中止并返回 **exit 2**，备份保持不动，中止记录写 `D:\openviking-backup\abort.log`。确认是真实删减后，用 `OV_BACKUP_FORCE=1` 覆盖重跑。守卫阈值可用 `OV_SRC`/`OV_DST`/`OV_LOG` 环境变量做沙箱测试。
- 调用方式注意：git-bash 下直接 `cmd //c` 会落进交互式提示符不执行；必须 `MSYS_NO_PATHCONV=1 cmd /c "sync.cmd"`。
- 计数实现注意：守卫内部用 PowerShell 统计文件数而非 `dir | find /c`——后者在 git-bash 环境下 `find` 会解析到 MSYS 版本导致全盘扫描挂死。

## 规则放置原则（2026-09-11 教训）

**跨会话必须自动执行的约束，不能只存放在语义召回层**（OpenViking 资源 / 本共享库文档）——它们仅在当前话题语义命中时才进入上下文。凡属「无条件触发」类规则（如 viking 写后同步），必须**同时**写入：

1. 内置 `MEMORY.md`（每轮无条件注入，永远可见）；
2. 对应技能正文（任务命中时加载，提供执行细节）。

**事故记录**：2026-09-11 修 Hermes 插件 bug 时执行了 `viking_remember`，但灾备规则当时只存在于本文件与 OpenViking 资源中，话题不相关故未被召回；当轮已加载的 `shared-agent-memory` 技能正文也只含 git 推送规则。结果整轮无人提醒同步，直到用户手动贴出仓库 URL 才补跑（补跑时已积压 82 个文件变更）。修复：三处补齐——内置 MEMORY 新增约束条目、技能正文新增第 5 条铁律、本文档补充本节。
