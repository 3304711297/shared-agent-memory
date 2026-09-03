---
name: shared-agent-memory
description: 读写双 Agent (Hermes & ZCode) 共享的跨端长期记忆库，变动自动提交推送至 GitHub
---

# 双 Agent 共享记忆库 (shared-agent-memory)

与 ZCode（用户的另一个 AI 编码助手）共用的长期记忆库，是跨 agent 事实的**唯一真源**。

## 位置

- 根目录：`C:\Users\VOS-User\.zcode\cli\memories\projects\default-135ef1b9f66d8a7e\memory\`
- 索引：`MEMORY.md`（每行一条 `- [标题](文件名.md) — 一句话钩子`）
- 远程仓库：`https://github.com/3304711297/shared-agent-memory.git`
- 单条记忆 = 一个 `.md` 文件，YAML frontmatter + 正文

## 何时读取

用户提到「之前 / 上次 / 记得吗 / 我们之前决定」等回溯性内容，或任务涉及用户环境、历史决策、进行中项目时：先读 `MEMORY.md` 索引，再按需读相关记忆文件。索引在上下文里就够回答时，不必展开全文。

## 何时写入与自动备份

用户说出值得跨会话保留的事实（偏好、纠正、环境约束、项目进展、拍板决定）且该库中尚无记录时：

1. 新建或更新记忆文件，frontmatter 格式：

```markdown
---
name: <短横线小写英文标识>
description: <一句话摘要>
metadata:
  type: user | feedback | project | reference
---

<事实正文；type 为 feedback 或 project 时，正文后跟 **Why:** 和 **How to apply:** 两行>
```

2. 若新建文件，在 `MEMORY.md` 追加对应索引行；更新优先于新建。
3. 相对日期改写为绝对日期；不写入密码、API key 等机密。
4. **【铁律】修改或新增记忆后自动推送 GitHub**：
   在当轮结束前自动执行静默提交并推送到 GitHub，无需等待用户提醒：
   ```bash
   git -C "C:/Users/VOS-User/.zcode/cli/memories" -c http.proxy=http://127.0.0.1:3067 add . && git -C "C:/Users/VOS-User/.zcode/cli/memories" commit -m "docs(memory): <简短说明>" && git -C "C:/Users/VOS-User/.zcode/cli/memories" -c http.proxy=http://127.0.0.1:3067 push origin zcode
   ```
