---
name: inspecting-hermes-desktop-dom
description: "读桌面端DOM时必用。CDP看实时DOM/CSS。Read the live Hermes desktop DOM/CSS over CDP."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [desktop, electron, cdp, dom, ui-verification, self-inspection]
    related_skills: [node-inspect-debugger, systematic-debugging, dogfood]
---

# Inspecting Hermes Desktop DOM — Router

读桌面端实时 DOM（CDP）：定端口 → 读 DOM → 判定「哪条规则赢了」。

## Routing table

| Need | Read |
|---|---|
| 端口 + DOM 读取方法 | `references/port-dom.md` |
| which-rule-won 判定 + 独立实例 | `references/rule-won-instance.md` |
| 坑 | `references/pitfalls.md` |

## Always-on rules

1. 只读不写线上 DOM；改样式走主题 skill，不直接改 live DOM。
2. 端口占用先确认实例归属，不杀错进程。
