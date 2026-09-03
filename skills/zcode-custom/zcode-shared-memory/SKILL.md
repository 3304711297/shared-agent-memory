---
name: zcode-shared-memory
description: 读写与 ZCode 共享的跨 agent 长期记忆库（读取回溯、写入持久事实）
---

# ZCode 共享记忆库

与 ZCode（用户的另一个 AI 编码助手）共用的长期记忆库，是跨 agent 事实的**唯一真源**。

## 位置

- 根目录：`C:\Users\VOS-User\.zcode\cli\memories\projects\default-135ef1b9f66d8a7e\memory\`
- 索引：`MEMORY.md`（每行一条 `- [标题](文件名.md) — 一句话钩子`）
- 单条记忆 = 一个 `.md` 文件，YAML frontmatter + 正文

## 何时读取

用户提到「之前 / 上次 / 记得吗 / 我们之前决定」等回溯性内容，或任务涉及用户环境、历史决策、进行中项目时：先读 `MEMORY.md` 索引，再按需读相关记忆文件。索引在上下文里就够回答时，不必展开全文。

## 何时写入

用户说出值得跨会话保留的事实（偏好、纠正、环境约束、项目进展、拍板决定）且该库中尚无记录时：

1. 新建记忆文件，frontmatter 格式：

```markdown
---
name: <短横线小写英文标识>
description: <一句话摘要>
metadata:
  type: user | feedback | project | reference
---

<事实正文；type 为 feedback 或 project 时，正文后跟 **Why:** 和 **How to apply:** 两行>
```

2. 在 `MEMORY.md` 末尾追加对应索引行
3. **更新优先于新建**：先查索引确认没有已覆盖该事实的文件，有就更新原文件
4. 相对日期改写为绝对日期；不写入密码、API key 等机密

## 禁止事项

- 不要在该目录执行任何 git 命令（提交推送由 ZCode 的自动备份机制负责）
- 不要改动已有记忆文件里与本任务无关的内容
- 会话内的临时信息、一次性任务细节不入库
