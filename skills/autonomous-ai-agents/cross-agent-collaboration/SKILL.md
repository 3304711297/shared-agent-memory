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
| 浏览器 Arena AI (arena.ai) Agent 模式云端副产线 SOP（仅限 Agent Mode） | `references/arena-ai-browser-collaboration.md` |
| 浏览器 ChatGPT 对话接管与跨 Agent 交叉复核 SOP（备选） | `references/chatgpt-browser-collaboration.md` |
| 浏览器 Claude AI (claude.ai) 对话接管与架构复核/沙箱打样 SOP | `references/claude-browser-collaboration.md` |
| Windows MCP 进程树 / 孤儿进程清理 | `references/windows-process-invariants.md` |
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
7. **Arena Agent 异步接力铁律（2026-09-22 拍板）**：Arena Agent Mode 启动与沙箱推进较慢。向 Arena 发送提示词并确认进入运行态（in-flight）后，**主会话严禁原地干等**，必须立即在本地推进代码，并无缝切至 ChatGPT 或 Claude 接力对拍；
   - **选型路由**：用户当前指令中指定了哪个就用哪个（例如提到 ChatGPT 就用 ChatGPT，提到 Claude 就用 Claude）。
8. **跨平台免费额度耗尽熔断与即时切换铁律（2026-09-22 拍板）**：Arena、ChatGPT、Claude 均存在免费层额度/速率限制（触发 `You've reached your limit`、无法联网/分析文件、降级为弱模型或 429 报错）。一旦任一平台额度耗尽，**必须立即无缝切换到其他可用平台继续工作**，禁止停滞等待。
9. **CI 后台异步守护与主会话零阻塞铁律（2026-09-22 拍板）**：代码 push 后，盯 CI 任务必须置于后台（`terminal(background=True, notify=True)`），**严禁在主会话前台同步阻塞等待 CI 跑完**。在后台盯 CI 期间，主会话必须立即无缝切至与其他 AI（ChatGPT / Claude）沟通进展或提请交叉代码复核，最大化管线吞吐。
10. **多标签页独立常驻与单页覆写禁令（2026-09-22 拍板）**：各协同平台（ChatGPT、Claude、Arena、GitHub 等）在 Edge 浏览器中必须拥有**独立的标签页**（通过 `bsk tab create --url ...` 创建，`bsk tab select` 切换）；**严禁在同一个标签页内反复改写/跳转 URL 覆盖已有会话**。在单标签页内跨域反复跳转不仅丢失已有会话 DOM 与登录态，还会大概率触发 Cloudflare 人机风控。
11. **Cloudflare 真人验证拦截标准处置 SOP（2026-09-22 拍板）**：当遇到 Cloudflare Turnstile / 盾 / “请验证您是真人” 拦截时，**严禁盲目在 DOM / iframe 里摸索与反复试探**（自动化脚本无法伪造通过 Cloudflare 轨迹）。标准处置流程：① 检查是否可以通过 `bsk tab create` 新建独立标签页直连避开脏会话；② 若仍需人机点击，立即通过 `bsk request-help` 提示人工快速点过；③ 或立即执行多平台熔断，秒级切至 Claude AI 继续推进，杜绝原地卡死。
12. **代理切换/网络变动导致会话中断的刷新自愈铁律（2026-09-22 拍板）**：当用户切换代理节点、更换网络或发生网络抖动时，浏览器内的长连接（WebSocket / SSE 流）会被物理中断，表现为网页提示「连接已中断。正在等待完整回复」或生成流悬停卡死。此时**标准动作是直接刷新该标签页（`location.reload()` 或重新直达当前会话 URL）**。刷新后云端（ChatGPT/Claude 等）会从后台持久化数据库中自动回填已生成的完整答复，严禁误判为未完成或在断连态下原地无休止轮询。
13. **Arena Agent Mode 长程轮询节律铁律（单次 sleep 60s，2026-09-22 拍板）**：Arena Agent Mode 由于在云端真实沙箱中执行拉库、解析依赖、终端 Bash 编译、单测运行与深思熟虑，进展相对缓慢且耗时长。主会话在等待或轮询其运行状态时，**严禁使用 10s/15s/20s 频繁打断轮询**，**必须每次固定 sleep 一分钟（`sleep 60`）**。且必须始终在左侧历史会话列表中跟踪查看，绝不能在未读完回复或未等完进程前关闭标签页。

> ZCode client 已于 2026-09-09 退役，相关观察/握手协议已删除。
