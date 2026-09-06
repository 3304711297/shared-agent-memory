---
name: hermes-bots-mode-team-practice
description: Hermes Desktop Bot Mode 核心机制拆解、实践验证、出处归档与用户偏好（仅用普通会话模式）沉淀
metadata:
  type: project
---

# Hermes Desktop Bot Mode 深度解析、实践归档与出处（2026-09-06）

## 一、 来源与权威出处
- **原作者与推文**：YanXbt (`@IBuzovskyi`) 在 X 发布的深度专栏《HERMES AGENT BOT MODE: Full Guide to Building Your AI Team》
- **推文链接**：`https://x.com/IBuzovskyi/status/2089701386887868653`
- **X Article ID**：`2089647871666671616`
- **官方源码与文档位置**：
  - Hermes 桌面文档：`https://hermes-agent.nousresearch.com/docs/desktop`
  - 内置插件源码路径：`NousResearch/hermes-agent` 仓库中的 `apps/desktop/src/plugins/hermes-bots/`
  - 底层 CLI 命令集：`hermes profile [list|create|delete|describe]`

## 二、 Bot Mode 核心机制与三大协作链路
1. **本质即 Profile**：
   - 每个 Bot 本质对应宿主环境中的独立 Profile（位于 `~/.hermes/profiles/[name]/`）；
   - 具备完全隔离的 `config.yaml`、`.env`、`SOUL.md`、`skills`、`memories` 与会话历史。
   - Desktop 端通过内置插件将其渲染为左侧团队花名册（Roster），免除命令行切换摩擦。
2. **多智能体协作机制**：
   - **`@Mentions`（同窗口实时交接）**：在与 Bot A 的对话中直接 `@bot_b 做某事`，Bot A 自动派发子任务并在返回后向用户汇报；
   - **`Agent Inbox`（异步收发信箱）**：每个 Bot 具备独立的入站邮箱，以 `[Message from agent 'xxx']` 格式投递，目标 Bot 在下一次任务开始时统一批处理；
   - **`Group Chat`（团队群聊）**：创建 Team 房间，支持 `@botname` 单独触发，或输入 `everyone` 广播给团队内所有 Agent。
3. **高阶设计模式**：
   - **Bot HR 模式**：设置专职 HR Bot，由它分析项目需求 Spec，自动配置合适模型并编写队员的 `SOUL.md`；
   - **Interpreter 模式**：封装 SSH/远程 VPS 的代理 Bot；
   - **独立 Cronjobs 流**：各 Bot 绑定专属定时流水线。

## 三、 本地实践验证与安全回滚（2026-09-06 验收）
1. **实践验证**：
   - 创建了 3 个对应核心场景的专职 Bot（`channel-ops`、`devops`、`researcher`）；
   - 各自注入针对性的 `SOUL.md`（明确排版美学、CI 全绿铁律、事实核查要求与协作契约）；
   - 解决多 Profile 记忆割裂问题：通过在各 Profile 的 `memories/topics` 建立 NTFS Junction，无缝打通全局唯一真源 `shared-agent-memory`。
2. **清理与回滚**：
   - 验证流程完全跑通后，安全解除 Junction 并通过 `hermes profile delete -y` 彻底清理上述 3 个 Profile；
   - 本地 Profile 列表已恢复为纯净的单一 `◆default`。

## 四、 用户习惯与偏好确立（铁律）
- **仅使用普通会话模式**：用户在日常使用中**明确偏好单一普通会话模式（default profile 一体化流转）**，无需在本地常驻维护多 Profile / 多 Bot；
- 避免多 Profile 带来的环境分散、配置漂移与维护负担；
- 本文档作为技术储备留档，后续如需临时创建专用多智能体团队或研究相关协作协议时，按本文档规范操作即可。

**Why:** 用户验证了 Bot Mode 的功能可行性与记忆打通路径，但确认自身更偏好集中一体化的单一会话，需将要点、出处与偏好统一入库归档。
**How to apply:** 保持默认普通会话模式运作，不主动创建分散的 profiles；后续若有大型复杂团队协作需求，查阅本文档的机制设计。
