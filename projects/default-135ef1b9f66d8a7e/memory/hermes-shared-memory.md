---
name: hermes-shared-memory
description: 共享记忆库单一真源架构：物理位于 ZCode 记忆目录（main 分支），hermes 经 NTFS junction 直读，双方各自当轮推送
metadata:
  node_type: memory
  type: project
  originSessionId: sess_888b469b-882a-4e84-aeed-8d68b401a67c
---

hermes-agent（[[hermes-agent-install]]）与 ZCode **共享同一份记忆库**（2026-09-02 设立，2026-09-05 重构为单一物理真源 + 三分支云备份，见 [[multi-branch-memory-backup]]）：

- **唯一物理真源**：`%USERPROFILE%\.zcode\cli\memories\projects\default-135ef1b9f66d8a7e\memory\`（git `main` 分支检出）。
- **Hermes 接入方式**：原生记忆系统的 `memories\topics` 已是 NTFS 目录联接（junction）指向上述真源目录——hermes 读写 topics/*.md 即读写共享库，零拷贝零拉取；`topics\MEMORY.md` 即共享库索引。hermes 侧入口协议在其本地 skill `shared-agent-memory` + SOUL.md 常驻指针。
- **【铁律】自动推送**：任何 Agent（ZCode 或 Hermes）修改共享库后，当轮结束前必须在 `%USERPROFILE%/.zcode/cli/memories` 仓库提交并推送 `main` 分支（旧规则「hermes 只写不推、由 ZCode 代推」已作废——hermes 现在直接自行推 main）。
- **归属划分**：跨 agent 持久事实 → 共享库（main）；hermes 专属会话记忆（`memories/USER.md`、根 `MEMORY.md` 等）→ 留在 hermes home，由 hermes 分支备份；ZCode 专属 → zcode 分支。
- 单条记忆格式：`.md` 文件 + YAML frontmatter（name/description/metadata.type: user|feedback|project|reference），更新优先于新建。
- **【公开脱敏铁律】**：共享记忆库为公开仓库，写入与更新时**必须执行前置脱敏**——严禁硬编码开发机用户名（必须用标准环境变量 `%USERPROFILE%`、`%LOCALAPPDATA%` 或 `$HOME`），严禁真实密钥凭据入库（一律转为 `<REDACTED_*>` 或占位符），CI 配有自动化卫生扫描门禁。

**Why:** 单一物理副本 + 单一共享分支彻底消除双端镜像漂移，切换 Agent 零同步成本。
**How to apply:** 涉及持久事实写入本库时严格执行前置脱敏，写入后立即 git 推 main 闭环；勿再往 hermes home 的 topics 里复制共享内容（那已是 junction）。

## 【09-09 实证】第二克隆漂移事故与处置
- 发现 `D:\ai coding\GitRepos\shared-agent-memory` **第二克隆**（TUI 会话 20260909_115310_a7e8a4 经它提交推送 94991c1/76856db，导致真源端 push 被拒 non-fast-forward；会话经网关 tui_gateway 接入、state.db 无档案，仅 request_dump 可取证）。日常一律用 `%USERPROFILE%/.zcode/cli/memories` 真源，**严禁再用 GitRepos 副本提交**。
- **recover SOP**：push 被拒时先 `git pull --rebase origin main` 再推（复现于 09-09，成功 e153b6b）；跨端取证顺序：GitHub events（推送账号）→ 提交是否签名（unsigned=git 客户端，web-flow=网页）→ 网关 request_dump 的 messages 反查命令路径 → reflog 判定本地从未有该提交。
- 收口动作（09-09）：GitRepos 副本 fetch 后已与远端对齐，仅作快照不作为写入端；后续若再发现 GitRepos 副本产生新提交，按 recover SOP 回收并对齐真源。
