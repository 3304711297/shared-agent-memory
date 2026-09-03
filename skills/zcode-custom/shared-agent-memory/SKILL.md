---
name: shared-agent-memory
description: 读写双 Agent (Hermes & ZCode) 共享的跨端长期记忆库，变动自动提交推送至 GitHub
---

# 双 Agent 共享记忆库 (shared-agent-memory)

用户日常主力使用 Hermes Agent（ZCode 作为备用/不常用），长期记忆库是跨会话与跨 Agent 事实的**唯一真源**。

## 位置与结构

- **Hermes 主控记忆路径**：`C:\Users\VOS-User\AppData\Local\hermes\memories\`
  - 核心偏好与画像：`USER.md`
  - 系统与环境常驻：`MEMORY.md`
  - 专题与项目细分记忆：`topics/*.md`（索引包含在 `topics/MEMORY.md`）
- **远程仓库**：`https://github.com/3304711297/shared-agent-memory.git`（默认主分支为 `hermes`）
- **单条专题记忆**：一个 `.md` 文件，包含 YAML frontmatter + 正文。

## 何时读取

用户提到「之前 / 上次 / 记得吗 / 我们之前决定」等回溯性内容，或任务涉及用户环境、历史决策、进行中项目时：
1. 优先阅读常驻 `USER.md` 与 `MEMORY.md`；
2. 按需检索 `topics/` 下对应项目的详细文档。

## 何时写入与自动备份

用户说出值得跨会话保留的事实（偏好、纠正、环境约束、项目进展、拍板决定）且该库中尚无记录时：

1. 更新 `memories/USER.md` / `memories/MEMORY.md`，或在 `memories/topics/` 新建/更新专题记忆文件；
2. Frontmatter 格式：

```markdown
---
name: <短横线小写英文标识>
description: <一句话摘要>
metadata:
  type: user | feedback | project | reference
---

<事实正文；type 为 feedback 或 project 时，正文后跟 **Why:** 和 **How to apply:** 两行>
```

3. **【铁律】修改或新增记忆后自动推送 GitHub**：
   在当轮结束前自动执行静默提交并推送到 GitHub `hermes` 分支，无需等待用户提醒：
   ```bash
   git -C "C:/Users/VOS-User/AppData/Local/hermes" -c http.proxy=http://127.0.0.1:3067 add memories/ .gitignore skills/ && git -C "C:/Users/VOS-User/AppData/Local/hermes" commit -m "docs(memory): <简短说明>" && git -C "C:/Users/VOS-User/AppData/Local/hermes" -c http.proxy=http://127.0.0.1:3067 push origin hermes
   ```
