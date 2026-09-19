---
name: cross-agent-collaboration
description: "跨Agent协作/多仓并行时必用。协调外部Agent与工具链。Use when coordinating Hermes with external agents or multi-repo fan-out."
version: 2.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, fan-out, delegation, cross-repo, handoff]
    category: autonomous-ai-agents
    related_skills: [hermes-agent, computer-use]
---

# Cross-Agent Collaboration — Router

Multi-agent / multi-repo coordination on one host. **This file is a router only.**
Read a reference *only* when the task actually needs it.

## Routing table

| Need | Read |
|---|---|
| 2+ 独立任务 / 多仓 fan-out / delegate_task 分派 | `references/parallel-execution.md` |
| 外部长跑进程等待（后台 + notify 唤醒） | `references/parallel-execution.md` §Anti-Patterns |
| 浏览器 Arena AI (arena.ai) 对话接管与跨 Agent 协作 SOP（首选） | `references/arena-ai-browser-collaboration.md` |
| 浏览器 ChatGPT 对话接管与跨 Agent 交叉复核 SOP（备选） | `references/chatgpt-browser-collaboration.md` |
| 浏览器 Claude AI (claude.ai) 对话接管与架构复核/沙箱打样 SOP | `references/claude-browser-collaboration.md` |
| Windows MCP 进程树 / 孤儿进程清理 / OpenViking 懒启动 | `references/windows-process-invariants.md` |
| chrome-devtools MCP / Edge 配置保护 | `references/browser-boundary.md` |
| 多 profile / bot 编排 | `references/profile-orchestration.md` |
| 工具调用效率（read_file / patch / search_files 优先） | `references/native-tool-prioritization.md` |
| 会话归档 / teardown | `references/session-teardown.md` |
| 跨仓 knowledge lock SHA 同步 | `references/cross-repo-lock.md` |
| 技能裁剪与退役闭环 | `references/skill-pruning.md` |

## Always-on invariants (不需要读文件，直接适用)

0. **新仓库 git 代理自动继承（2026-09-18 拍板）**：本机不靠逐仓配置，也不必我手动加 —— git 全局已设 URL-scoped 代理键，任何 `git init` 的新仓库/新项目自动继承：
   ```bash
   git config --global 'http.https://github.com.proxy'  http://127.0.0.1:3067
   git config --global 'https.https://github.com.proxy' http://127.0.0.1:3067
   ```
   为什么必须是 `git config` 而非环境变量：**Hermes 的 `terminal` 会剥掉 `ALL_PROXY`/`HTTP(S)_PROXY`**，只靠环境变量的 git 在会话里必然被墙（实测直连 `ls-remote` 45s 超时）。URL-scoped 键同时满足两点：① `git init` 即继承；② 只作用于 github.com，其余主机（gitlab 等）不被误代理（已实测）。
   排障时也要带上 `env -u ALL_PROXY ...`，否则会在干净环境里重现不出问题。防漂移由 `shared-agent-memory` 的 config-guard ④ 段每日核对（改坏会报红，已做变异测试验证）。
1. **Fork-First 立体并发**：用户输入含 2 个及以上独立诉求时，第一动作必须 `delegate_task` 并行分派，且可将独立探路或代码审查并行分派至 Arena AI 协同推进，禁止主会话串行。
2. **主会话零阻塞**：长跑命令一律 `terminal(background=True, notify=True)`，禁止前台 sleep 轮询。
3. **Producer-Reviewer Separation**：一个 Agent 编辑时，另一个只做 review/test/CI 监控，禁止同时写同一工作树。
4. **浏览器会话与标签页常驻复用**：任务执行周期内严禁频繁关闭/释放 `bsk` session 与标签页，全程维持热连接、会话上下文与 DOM 状态，仅在最终全局交付确认收口时统一释放。
5. **Delegation 模型**：`delegation.provider`/`model` 保持为空，子代理继承当前聊天模型，除非用户显式指定。
6. **Shared Memory SSOT**：跨 Agent 事实与交接契约必须落 `shared-agent-memory` `main` 分支。

> ZCode client 已于 2026-09-09 退役，相关观察/握手协议已删除。
