---
name: hermes-reasoning-display-internals
description: "Use when 推理过程块显示异常或 show_reasoning 开关不生效时。"
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [hermes, desktop, reasoning, display, troubleshooting]
---

# Hermes 推理显示机制与排查

源码考证基于 245e4800（2026-09-06）。升级后若行为变化，重新 grep 验证。

## 三个开关的真实作用域

| 开关 | 作用域 | 效果 |
|---|---|---|
| `display.show_reasoning`（桌面设置→对话→「推理过程块」） | **仅 CLI + 消息平台** | CLI: 推理是否流入推理框；消息平台: 是否把最后推理块拼进回复。**桌面端 write-only 摆设** |
| 外观→「默认折叠推理过程」（localStorage `hermes.desktop.reasoning.collapsedByDefault`） | 仅桌面 | 块始终渲染，控制实时预览展开 vs 默认折叠 |
| `agent.reasoning_effort`（/reasoning 运行时可切） | 全端 | 唯一真正省 token 的杠杆：档位 none→minimal→low→medium→high→xhigh→max→ultra |

## 桌面端数据流（为何 show_reasoning 无效）

tui_gateway/agent_callbacks.py:95 无条件 reasoning_callback→reasoning.delta 事件 → 桌面 use-message-stream/gateway-event/message-stream.ts:200 收到即 appendReasoningDelta → thread/message-parts.tsx 读 $reasoningCollapsedByDefault（仅折叠/展开）。无任何分支读 show_reasoning。

上游 bug 收录：NousResearch/hermes-agent#49664（P1，#93817 为 duplicate），修复 PR 簇 #49725/#101376/#103379。Hermes 已留言根因代码链（issuecomment-5557680014）。勿再提新 issue；跟进 #103379 合并状态即可。

## 排查清单

1. 桌面看不到思考块：检查「默认折叠推理过程」是否为开 + 模型是否思考型（reasoning.delta 是否有流量）
2. 桌面关不掉思考块：show_reasoning 无效是已知 bug（#49664），用折叠开关或降 effort
3. 思考吃光配额 content=null：思考型模型 max_tokens 给足（思考链先行），或降 effort
4. CLI 想看/藏推理框：/reasoning show|hide（写 display.show_reasoning，CLI 有效）

## 语义备忘

show_reasoning 纯显示开关：不影响思考生成、token 消耗、session 持久化（messages.reasoning 列）、provider 回传（多轮连续性+prompt cache）。reasoning token 计 output 口径。