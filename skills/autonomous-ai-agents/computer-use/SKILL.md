---
name: computer-use
description: "操作桌面/GUI时必用。后台优先驱动桌面，遇信号升级。Drive the desktop background-first; escalate on signal."
version: 2.1.0
author: Francesco Bonacci (f-trycua), Hermes Agent
license: MIT
platforms: [macos, windows, linux]
metadata:
  hermes:
    tags: [computer-use, desktop, automation, gui, cross-platform]
    category: desktop
    related_skills: []
---

# Computer Use — Router

Drive the desktop in the **background** via `computer_use` (cua-driver under the hood).
Actions do NOT move the user's cursor or steal focus. Any tool-capable model works.

## Routing table

| Need | Read |
|---|---|
| 标准流程（canonical workflow） | `references/workflow.md` |
| 截图模式 + 动作词汇表 | `references/actions-capture.md` |
| 验证→升级阶梯（background-first） | `references/verify-escalate.md` |
| 平台按键/拖拽/滚动/焦点管理 | `references/platform-input.md` |
| 截图交付/安全硬规则/故障模式/何时不用 | `references/safety-failures.md` |
| 驱动 internals | cua-driver skill pack (`~/.cua-driver/skills/cua-driver`) |

## Always-on rules

1. **Background-first**：默认后台操作，用户可继续打字；需前台确认时才升级。
2. 调用本 skill 记录的 action 词汇，不直接调 raw cua-driver MCP。
3. 每次动作后截图验证效果，suspected_noop / unverifiable 则按阶梯升级后重抓确认。
4. 安全硬规则见 refs——不可逆/敏感操作先停手确认。
