---
name: hermes-config-baseline-and-sync-protocol
description: Hermes 完整配置基准快照、版本构建指纹与改动自识别同步记忆库铁律（双端协同规范）
metadata:
  type: reference
---

# Hermes 完整配置基准、版本指纹与自动同步规约 (2026-09-06 创建 · 2026-09-11 刷新)

## 一、 当前 Hermes 构建版本指纹 (Version Fingerprint)

为防止未来 Hermes 版本更新导致配置项语法（Schema）、默认行为或新特性（如 MoA 规范、Guardrails 策略等）发生差异，所有配置快照均严格绑定当前软件构建指纹：

| 组件 / 维度 | 当前版本与标识 | 来源 / 验证方式 |
| :--- | :--- | :--- |
| **Hermes Agent 版本** | `v0.21.1 (2026.9.7)` | `hermes --version` |
| **上游 Git Commit SHA** | `a3190625c0a2ed89ed33356ef8e3184e95dc08e5` (2026-09-11 07:14:55 -0500) | `git -C hermes-agent log -1` |
| **Desktop 桌面客户端** | `v0.17.2` | `apps/desktop/package.json` |
| **配置规范版本** | `_config_version: 42` | `config.yaml` 根字段 |
| **Python 运行时** | `Python 3.11.16` / 内置 3.14 测试解释器 | 内部运行时依赖 |
| **安装目录与方式** | `%LOCALAPPDATA%\hermes\hermes-agent` (Git source checkout) | 源码检出并可热更新 |

> **版本演进铁律**：后续 Hermes 升级（如执行 `hermes update` 或上游拉取新 commit）时，若检测到 `_config_version` 升级或新增/废弃了配置字段，同步记忆库时必须一并刷新上方表格中的版本号与 Git SHA，并简要记录该版本下的配置变迁（Changelog diff）。
>
> * **2026-09-08 更新**：Hermes 上游合入 commit `520e63661c`（fix: keep command-auth model discovery lazy across config and setup）；本地配置守卫自动化触发全绿通过，启用本地插件 `config-guard`，基线配置快照同步更新。
> * **2026-09-11 刷新**：`_config_version` 41 → **42**；上游推进至 `a3190625c0`；Desktop `v0.17.2`。配置结构发生**两处重大迁移**——① `custom_providers` 列表格式整体迁移为 `providers:` 键控结构（`radeon-cloud` / `cpa` / `workbuddy2api` 三段，详见第三节）；② 主力模型切换到 `workbuddy2api` 本地反代（`deepseek-v4.1-flash`）。新增 `security.protected_instruction_files: false`（详见第七节）。

---

## 二、 双 Agent 协同铁律：改动设置自识别与同步机制

1. **核心工作流触发**：
   - 当用户在日常对话中告知修改了 Hermes 的界面设置（或发截图、发通知）时，当前接待的 Agent（Hermes 或 ZCode）**严禁仅作口头附和**，必须**主动读取并自行识别最新配置**（源文件：`%LOCALAPPDATA%\hermes\config.yaml`）。
   - 提取最新变动要点与全量配置快照，更新本专题文档以及同目录下的独立配置文件 `hermes-config.yaml`，并同步提交推送到双端共享记忆库 GitHub `main` 分支（`https://github.com/3304711297/shared-agent-memory`）。
2. **脱敏保护铁律**：
   - 由于共享记忆库为公开仓库，写入与同步 YAML 快照时，必须严格将私有 API Key 或敏感 Token 过滤脱敏为 `<REDACTED_*>`，严禁明文凭据入库。

---

## 三、 当前核心模型与系统策略基准（2026-09-11 实机刷新）

1. **主力交互模型**：
   - `workbuddy2api` · `deepseek-v4.1-flash`（经本地 WorkBuddy2API 反代 `127.0.0.1:8787` 桥接腾讯 CodeBuddy/WorkBuddy 订阅，OpenAI + Anthropic 双协议）。
   - `model` 段：`default: deepseek-v4.1-flash` / `provider: workbuddy2api` / `base_url: http://127.0.0.1:8787/v1` / `key_env: HERMES_CUSTOM_WORKBUDDY2API_API_KEY`。
   - 历史：2026-09-10 前主力为 `cpa-gui · gemini-3.8-flash`（经 EasyCLIProxyAPI `127.0.0.1:18080` 桥接 Antigravity）；该通道现保留为 `cpa` provider（见下）。
2. **上下文窗口 (Context Window)**：
   - 端点 live `/v1/models` 逐条下发顶层 `context_length`，Hermes 自适应读取；配合 `compression.threshold: 0.5` 自动智能压缩。
3. **provider 三段式结构（`providers:` 键控，2026-09-10 由 `custom_providers` 列表迁移）**：

   | provider key | 名称 | base_url | 模型数 | 定位 |
   | :--- | :--- | :--- | :--- | :--- |
   | `workbuddy2api` | workbuddy2api | `127.0.0.1:8787/v1` | 40 | **主力**（CodeBuddy/WorkBuddy 全量模型，含 `gpt-6-astra`） |
   | `cpa` | CPA | `127.0.0.1:18080/v1` | 11 | Antigravity/Gemini 通道（备用） |
   | `radeon-cloud` | AMD | `developer.amd.com.cn/radeon/api/v1` | 4 | AMD Radeon Cloud（Qwen/MiniCPM） |

   - 全部走 `key_env: HERMES_CUSTOM_<SLUG>_API_KEY` 引用形态（密钥在 `.env`，不入 config）。
   - `model_aliases` 7 条（`workbuddy` / `workbuddy-glm` / `workbuddy-glm53` / `workbuddy-kimi` / `workbuddy-kimi3` / `workbuddy-deepseek` / `workbuddy-hy4`）均指向 `custom` provider + `127.0.0.1:8787/v1`。
4. **备用模型容灾梯队**：
   - 备用 1：`glm-5.3-flash`（本地实测 15 并发无 429、毫秒级响应、工具调用稳定）。
   - 备用 2：`hy4-preview`（二级综合推理容灾）。
   - **严禁挂载项**：坚决剔除 `claude-opus-4-6-thinking` 等高延迟、高消耗的深度思考模型，防止自动静默降级导致 Agent 卡死或吃光贵重配额。
   - ⚠️ 当前 `fallback_providers: []` 为空（未配置自动容灾链），容灾靠人工切模型。
5. **Mixture of Agents (MoA)**：
   - 全局与预设 `enabled: false` 显式关闭。
   - 避免在 Agent 编程和工具调用（Tool Calling / Function Calling）场景下引入多模型扇出造成的格式破坏、多倍延迟和积分浪费；清理了原残留的 `OpenCode Free` 和 `OpenRouter` 无效通道。
   - ⚠️ 注：`moa` 段中残留 `provider: codebuddy` 引用（旧 provider 名，现已不存在于 `providers:` 表中），因 `enabled: false` 故无实际影响；若将来启用 MoA 需先修正为 `workbuddy2api`。

---

5. **后台技能维护器 (Curator)**：
   - 全局显式配置 `curator.enabled: false`（同时置为 paused）。
   - **核心考量**：Hermes 技能库实行 GitHub 单一真源（`shared-agent-memory`）、ZCode 双端对齐及 `capability-upstream-watch` 自动化看门狗机制；Curator 原生基于白名单的判定无法识别私有工作流与自研技能，默认会在 30~90 天闲置后擅自归档低频技能并破坏基线版本一致性，故彻底禁用由人工/CI 闭环接管。

---

6. **后台自我改进学习循环 (Background Review)**：
   - 三重禁用：`memory.nudge_interval: 0`、`skills.creation_nudge_interval: 0`、`auxiliary.background_review.enabled: false`（双保险防 fail-open 复活）。
   - **核心考量**：每 10 轮/15 次工具调用自动 fork 重放会话烧 ~30K token，且擅自写记忆/建技能，违反用户拍板制与看门同步铁律；禁用后 memory 工具、OpenViking、/refine 手动审查均不受影响。
   - serena 与 cliproxyapi 已于同日退出 capability-inventory.json 看门（插件已删/用户手动更新）。

---

## 四、 独立配置文件与全量配置快照

* **完整脱敏快照**：[`hermes-config.yaml`](./hermes-config.yaml) —— **461 行全量**，可直接供脚本解析或一键恢复。
  * ⚠️ 2026-09-11 起本节**不再内嵌全文**：此前内嵌副本与独立文件双份维护，两处曾同时过期（内嵌停留在 `cpa-gui` 时代）。现改为单一真源，避免漂移。
* **本地源文件路径**：`%LOCALAPPDATA%\hermes\config.yaml`（461 行，`_config_version: 42`）
* **快照再生成流程**：本地 `config.yaml` → 脱敏（`%USERPROFILE%` 路径泛化、第三方应用目录泛化 `<EKKO_STUDIO_HOME>`、QQ chat_id 类账户标识替换 `<REDACTED_*>`；密钥本就全部为 `key_env` 引用形态，无明文） → 覆写本目录 `hermes-config.yaml` → 同步更新本文指纹表与变动表 → 提交推送 `main`。

### 关键段速查（快速比对漂移用）

```yaml
model:
  default: deepseek-v4.1-flash          # 主力：本地 workbuddy2api 反代
  provider: workbuddy2api
  base_url: http://127.0.0.1:8787/v1
  key_env: HERMES_CUSTOM_WORKBUDDY2API_API_KEY

providers:                              # 键控结构（2026-09-10 由 custom_providers 列表迁移）
  workbuddy2api:                        # 127.0.0.1:8787/v1 · 40 模型 · 主力（含 gpt-6-astra）
  cpa:                                  # 127.0.0.1:18080/v1 · 11 模型 · Antigravity 通道
  radeon-cloud:                         # developer.amd.com.cn · 4 模型 · AMD Radeon Cloud
  # 全部 key_env 引用，无明文密钥

fallback_providers: []                  # 空 —— 无自动容灾链，容灾靠人工切模型

agent:
  reasoning_effort: ultra               # 用户硬约束，严禁改动

approvals:
  mode: 'off'                           # 危险 shell 命令审批已关闭

security:
  protected_instruction_files: false    # 指令文件写入门禁已关闭（2026-09-11 拍板，详见独立记忆卡 hermes-approval-two-tier-gates）

memory:
  provider: openviking                  # 内置字符限额 3000/2000 + OpenViking 召回

plugins:
  enabled: [superpowers, token-stats, config-guard]

display:
  language: zh
  show_reasoning: true

mcp_servers:
  # 6 个：chrome-devtools（connect-only）、deepwiki、ekko-studio ×4（路径已泛化）
```

### 2026-09-11 相比上版快照的结构性变动

| 维度 | 旧值 | 新值 |
| :--- | :--- | :--- |
| `_config_version` | 41 | **42** |
| 主力模型 | `cpa-gui · gemini-3.8-flash`（18080） | **`workbuddy2api · deepseek-v4.1-flash`（8787）** |
| provider 组织 | `custom_providers` 列表（含 `api_key: <REDACTED_LOCAL_KEY>` 明文形态） | **`providers:` 键控三段**（全部 `key_env` 引用，无明文） |
| 指令文件门禁 | （默认开启） | `security.protected_instruction_files: false` |
| `mcp_servers` | 2 个（chrome-devtools 1.8.0 / deepwiki） | **6 个**（chrome-devtools 1.9.0 / deepwiki / ekko-studio ×4） |
| `model_aliases` | 7 条（`provider: custom`） | 7 条（不变，仍指向 `custom` + 8787） |
| `moa` 段 | — | ⚠️ 残留 `provider: codebuddy` 旧名引用（`enabled: false` 无实际影响；将来启用前需修正为 `workbuddy2api`） |
| 行数 | 409 | 461 |

---

## 五、 工具集 (Toolsets) 与能力体系启用基准矩阵 (2026-09-11 刷新)

根据 `platform_toolsets.cli` 与 `known_builtin_toolsets.cli` 严格对齐：

### 1. 活跃启用工具集（`platform_toolsets.cli` 16 项）

terminal, file, web, skills, vision, session_search, delegation, memory, clarify, code_execution, computer_use, cronjob, image_gen, todo, video, kanban。

（`known_builtin_toolsets.cli` 另含 browser / stt / tts / video_gen / x_search / spotify / discord / homeassistant / yuanbao 等，均为已登记但未在 `platform_toolsets.cli` 启用的能力。）

### 2. 关键停用项与安全决议

| 工具集 | 状态 | 原因 |
| :--- | :--- | :--- |
| **Browser Automation** | 显式关闭 | 曾因无头启动踩踏真实 Edge Dev Profile 导致扩展被删；网页抓取已由 Exa 后端覆盖。浏览器交互改走 `chrome-devtools` MCP（connect-only） |
| **A2A (Agent-to-Agent)** | 关闭 | 当前场景无需跨智能体局域网 A2A 协议 |
| **Home Assistant / Spotify / STT** | 关闭 | 无对应需求；STT 停用避免麦克风占用 |
| **Computer Use** | 开启（备用） | `computer_use.backend: cua`，桌面 GUI 控制备选通道 |

### 3. Edge 浏览器接管彻底加固铁律
- **MCP 纯连接模式**：`chrome-devtools` 严格剔除 `--user-data-dir` 参数，仅保留 `--autoConnect`（当前版本 `chrome-devtools-mcp@1.9.0`）。若用户未启动 Edge Dev，MCP 立即抛出连接等待异常，严禁擅自在后台拉起带自动化参数的无头实例破坏用户 Profile。
- **数据解耦与秒级复活**：扩展安装包与用户数据解耦（脚本及配置保存在 `Local Extension Settings` 中不受影响）。若发生异常，重新在 Edge 商店点击获取对应扩展，因全球唯一 Extension ID 恒定，所有脚本与设置将瞬间自动重新挂载，100% 原地满血复活。
- **MCP 服务器清单（6 个）**：`chrome-devtools`（lazy, idle 60s）、`deepwiki`（远程 URL）、`ekko-studio-{api,browser,devices,use}`（本地 Electron MCP，`HERMES_WEB_UI_URL: http://127.0.0.1:8748`）。

### 4. 审批与安全门禁现状（2026-09-11）

| 配置项 | 值 | 说明 |
| :--- | :--- | :--- |
| `approvals.mode` | `off` | 危险 shell 命令审批关闭 |
| `security.protected_instruction_files` | `false` | 指令文件（AGENTS.md 等）写入门禁关闭 —— 用户拍板，详见独立记忆卡 `hermes-approval-two-tier-gates.md` |
| `security.redact_secrets` | 默认（开） | 工具输出密钥脱敏，保持开启 |
| `security.allow_private_urls` | `true` | 允许访问内网回环地址（本地反代需要） |

---

## 六、 关键实施与检索指南

- **Why**: Hermes 拥有复杂的桌面与多模型配置，且随版本持续迭代。将软件构建指纹与全量配置快照绑定，不仅杜绝跨端协作时的信息差，还能在未来版本升级出现配置兼容性问题时秒级追溯回滚。
- **How to apply**: 当用户提及「我改了设置 / 看一下我改的 / 同步一下设置」时，立即执行 `read_file(%LOCALAPPDATA%/hermes/config.yaml)`，同步核对 `hermes --version` 与 `_config_version`，对比变动点后按第四节「快照再生成流程」覆写 `hermes-config.yaml`、更新本文指纹表与变动表，并提交推送 `main`。
- **脱敏铁律（公开仓）**：任何写入快照的路径必须泛化为 `%USERPROFILE%` / `%LOCALAPPDATA%` / `<EKKO_STUDIO_HOME>` 等占位；账户标识（QQ chat_id 等）替换为 `<REDACTED_*>`。本仓为 **public**，推导式脱敏永远优先于「看着不像敏感」的主观判断。
