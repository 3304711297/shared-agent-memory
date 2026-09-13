---
name: node-inspect-debugger
description: "调Node.js时必用。--inspect加DevTools协议断点。Debug Node.js via --inspect + Chrome DevTools Protocol CLI."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, nodejs, node-inspect, cdp, breakpoints, ui-tui]
    related_skills: [systematic-debugging, python-debugpy]
---

# Node.js Inspect Debugger — Router

`node inspect` REPL + SIGUSR1 attach + 程序化 CDP + Hermes TUI/Worker 调试。

## Routing table

| Need | Read |
|---|---|
| REPL 速查 + attach 已运行进程 | `references/repl-attach.md` |
| 程序化 CDP 脚本（terminal 内驱动） | `references/cdp-scripts.md` |
| Hermes ui-tui / Ink 组件 / _SlashWorker·PTY / Vitest | `references/hermes-tui-vitest.md` |
| Heap/CPU 非交互采集 + 坑 + 验证 + one-shot | `references/heap-pitfalls-recipes.md` |

## Always-on rules

1. 已运行进程用 SIGUSR1 开 inspector，拿 WS URL 再 attach。
2. hang/泄漏类先非交互采集（heap snapshot / cpu profile），再交互式定帧。
