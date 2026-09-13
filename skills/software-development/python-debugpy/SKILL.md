---
name: python-debugpy
description: "调Python时必用。pdb与debugpy远程调试。Debug Python: pdb REPL + debugpy remote (DAP)."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, python, pdb, debugpy, breakpoints, dap, post-mortem]
    related_skills: [systematic-debugging, node-inspect-debugger]
---

# Python Debugger — Router

pdb 本地断点 + debugpy 远程 attach。先选场景，再读对应 ref。

## Routing table

| Need | Read |
|---|---|
| pdb 速查 + 本地/pytest/post-mortem 配方 | `references/pdb-recipes.md` |
| debugpy 远程（wait-for-client / -m launch / attach 已运行进程 + DAP 客户端） | `references/remote-debugpy.md` |
| Hermes 进程（tests / run_agent.py / tui_gateway / _SlashWorker / gateway） | `references/hermes-processes.md` |
| 常见坑 + 验证清单 + one-shot 配方 | `references/pitfalls-recipes.md` |

## Always-on rules

1. 能本地复现就不上远程；远程优先 `-m debugpy` 免改源码。
2. attach 已运行进程前确认端口与权限，事后清理调试钩子。
