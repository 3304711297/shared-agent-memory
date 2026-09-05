---
name: hermes-shared-memory
description: 共享记忆库单一真源架构：物理位于 ZCode 记忆目录（main 分支），hermes 经 NTFS junction 直读，双方各自当轮推送
metadata:
  node_type: memory
  type: project
  originSessionId: sess_888b469b-882a-4e84-aeed-8d68b401a67c
---

hermes-agent（[[hermes-agent-install]]）与 ZCode **共享同一份记忆库**（2026-09-02 设立，2026-09-05 重构为单一物理真源 + 三分支云备份，见 [[multi-branch-memory-backup]]）：

- **唯一物理真源**：`C:\Users\VOS-User\.zcode\cli\memories\projects\default-135ef1b9f66d8a7e\memory\`（git `main` 分支检出）。
- **Hermes 接入方式**：原生记忆系统的 `memories\topics` 已是 NTFS 目录联接（junction）指向上述真源目录——hermes 读写 topics/*.md 即读写共享库，零拷贝零拉取；`topics\MEMORY.md` 即共享库索引。hermes 侧入口协议在其本地 skill `shared-agent-memory` + SOUL.md 常驻指针。
- **【铁律】自动推送**：任何 Agent（ZCode 或 Hermes）修改共享库后，当轮结束前必须在 `C:/Users/VOS-User/.zcode/cli/memories` 仓库提交并推送 `main` 分支（旧规则「hermes 只写不推、由 ZCode 代推」已作废——hermes 现在直接自行推 main）。
- **归属划分**：跨 agent 持久事实 → 共享库（main）；hermes 专属会话记忆（`memories/USER.md`、根 `MEMORY.md` 等）→ 留在 hermes home，由 hermes 分支备份；ZCode 专属 → zcode 分支。
- 单条记忆格式：`.md` 文件 + YAML frontmatter（name/description/metadata.type: user|feedback|project|reference），更新优先于新建。

**Why:** 单一物理副本 + 单一共享分支彻底消除双端镜像漂移，切换 Agent 零同步成本。
**How to apply:** 涉及持久事实写入本库并立即 git 推 main；勿再往 hermes home 的 topics 里复制共享内容（那已是 junction）。
