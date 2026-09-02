---
name: desktop-commander-overview
description: Desktop Commander provides controlled access to local files, terminals, processes, structured documents, search, and SSH
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_2a39a607-a49b-4c5c-b320-6aa5ddedb9a9
---

Desktop Commander is a plugin that gives the AI controlled access to the user's computer. It supports file and folder operations, persistent terminal sessions, long-running process management, project-wide search, Excel/DOCX/PDF handling, data analysis, and SSH connections to remote machines. Access is limited by configured directories and potentially impactful operations such as deletion, restarts, deployment, or migrations should be confirmed.

**何时该用它（2026-08-23 与用户确认的选型结论，勿卸载）**：与内置 Bash/Read/Write/Edit 重叠度高，仅以下四类场景是内置工具替代不了的，遇到时应主动选它：
1. **大数据文件分析**——持久 Python REPL（`python3 -i`）把大 CSV/JSON 加载一次、多轮内存查询；内置 Bash 每次全新 shell 只能反复重载
2. **长跑进程盯日志**——dev server/训练/下载等任务的会话式输出跟踪与交互输入
3. **SSH 远程运维**——持久 SSH/数据库 shell（mysql/psql），免每条命令重连
4. **超大目录流式搜索**——分页可停，避免一次性撑爆上下文

另：`edit_block` 可对 docx/xlsx 做外科手术式小修改（与 document-skills 插件重叠）。一次性命令型工作（浏览器/配置/git 等）继续用内置工具即可，不必舍近求远。
