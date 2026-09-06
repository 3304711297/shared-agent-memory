---
name: hermes-config-baseline-and-sync-protocol
description: Hermes 完整配置基准快照、版本构建指纹与改动自识别同步记忆库铁律（双端协同规范）
metadata:
  type: reference
---

# Hermes 完整配置基准、版本指纹与自动同步规约 (2026-09-06)

## 一、 当前 Hermes 构建版本指纹 (Version Fingerprint)

为防止未来 Hermes 版本更新导致配置项语法（Schema）、默认行为或新特性（如 MoA 规范、Guardrails 策略等）发生差异，所有配置快照均严格绑定当前软件构建指纹：

| 组件 / 维度 | 当前版本与标识 | 来源 / 验证方式 |
| :--- | :--- | :--- |
| **Hermes Agent 版本** | `v0.21.0 (2026.8.31)` | `hermes --version` |
| **上游 Git Commit SHA** | `00140a85574d4fc9e42f977a167aeda899b50ca9` (Sun Sep 6 20:50:02 2026) | `git -C hermes-agent log -1` |
| **Desktop 桌面客户端** | `v0.17.0` | `apps/desktop/package.json` |
| **配置规范版本** | `_config_version: 40` | `config.yaml` 根字段 |
| **Python 运行时** | `Python 3.11.16` / `OpenAI SDK 2.24.0` | 内部运行时依赖 |
| **安装目录与方式** | `C:\Users\VOS-User\AppData\Local\hermes\hermes-agent` (Git source checkout) | 源码检出并可热更新 |

> **版本演进铁律**：后续 Hermes 升级（如执行 `hermes update` 或上游拉取新 commit）时，若检测到 `_config_version` 升级或新增/废弃了配置字段，同步记忆库时必须一并刷新上方表格中的版本号与 Git SHA，并简要记录该版本下的配置变迁（Changelog diff）。

---

## 二、 双 Agent 协同铁律：改动设置自识别与同步机制

1. **核心工作流触发**：
   - 当用户在日常对话中告知修改了 Hermes 的界面设置（或发截图、发通知）时，当前接待的 Agent（Hermes 或 ZCode）**严禁仅作口头附和**，必须**主动读取并自行识别最新配置**（源文件：`C:\Users\VOS-User\AppData\Local\hermes\config.yaml`）。
   - 提取最新变动要点与全量配置快照，更新本专题文档以及同目录下的独立配置文件 `hermes-config.yaml`，并同步提交推送到双端共享记忆库 GitHub `main` 分支（`https://github.com/3304711297/shared-agent-memory`）。
2. **脱敏保护铁律**：
   - 由于共享记忆库为公开仓库，写入与同步 YAML 快照时，必须严格将私有 API Key 或敏感 Token 过滤脱敏为 `<REDACTED_*>`，严禁明文凭据入库。

---

## 三、 当前核心模型与系统策略基准（实测拍板）

1. **主力交互模型**：
   - `cpa-gui` · `gemini-3.8-flash`（经本地 EasyCLIProxyAPI `127.0.0.1:18080` 桥接 Antigravity / Google 个人 Pro 订阅）。
   - 原生支持 1M~2M 上下文、极速吞吐、免商业额外计费。
2. **上下文窗口 (Context Window)**：
   - 显式设为 `0`（自适应读取模型原生窗口）。配合内置 `compression.threshold: 0.5` 自动智能压缩，避免人工固定数值造成长文档意外截断。
3. **备用模型 (Fallback Models) 容灾梯队**：
   - **备用 1**：`custom:workbuddy-(127.0.0.1:8787)` · `glm-5.3-flash`
     - 本地实测 15 并发无 429、毫秒级响应、工具调用稳定，为抗 429 瞬间接管主力。
   - **备用 2**：`custom:workbuddy-(127.0.0.1:8787)` · `hy4-preview`
     - 二级综合推理容灾模型。
   - **严禁挂载项**：坚决剔除 `claude-opus-4-6-thinking` 等高延迟、高消耗的深度思考模型，防止自动静默降级导致 Agent 卡死或吃光贵重配额。
4. **Mixture of Agents (MoA)**：
   - 全局与预设 `enabled: false` 显式关闭。
   - 避免在 Agent 编程和工具调用（Tool Calling / Function Calling）场景下引入多模型扇出造成的格式破坏、多倍延迟和积分浪费；清理了原残留的 `OpenCode Free` 和 `OpenRouter` 无效通道。

---

## 四、 独立配置文件与全量配置快照

* **同目录下独立配置文件**：[`hermes-config.yaml`](./hermes-config.yaml)（可直接供脚本解析或一键恢复）
* **本地源文件路径**：`C:\Users\VOS-User\AppData\Local\hermes\config.yaml` (450行全量)

```yaml
model:
  default: gemini-3.8-flash
  provider: cpa-gui
  base_url: http://127.0.0.1:18080/v1
fallback_providers: []
database:
  journal_mode: wal
runtime:
  nofile_soft_limit: 4096
agent:
  max_turns: 500
  service_tier: ''
  fast_auto_seconds: 60
  verbose: false
  reasoning_effort: ultra
  personalities: {}
terminal:
  backend: local
  cwd: .
  timeout: 180
  home_mode: auto
  container_cpu: 1
  container_memory: 5120
  container_disk: 51200
  container_persistent: true
  docker_mount_cwd_to_workspace: false
  lifetime_seconds: 300
web:
  backend: exa
  search_backend: exa
  extract_backend: exa
browser:
  inactivity_timeout: 120
  allow_private_urls: true
  use_real_profile: false
  extension_control:
    enabled: false
tool_loop_guardrails:
  warnings_enabled: true
  hard_stop_enabled: false
  non_interactive_hard_stop_enabled: true
  warn_after:
    exact_failure: 2
    same_tool_failure: 3
    idempotent_no_progress: 2
  hard_stop_after:
    exact_failure: 5
    same_tool_failure: 8
    idempotent_no_progress: 5
compression:
  enabled: true
  checkpoint_required: false
  progress_notices: false
  threshold: 0.5
  target_ratio: 0.2
  protect_last_n: 20
  min_tail_user_messages: 1
  max_attempts: 3
  proactive_prune_tokens: 0
  proactive_prune_min_result_chars: 8000
  proactive_prune_min_reclaim_tokens: 4096
  hygiene_max_turn_hold_seconds: 10
  protect_first_n: 3
  codex_gpt55_autoraise: true
  codex_app_server_auto: native
  codex_responses_native: false
  idle_compact_after_seconds: 0
prompt_caching:
  cache_ttl: 5m
auxiliary:
  vision:
    provider: auto
    model: ''
display:
  compact: false
  busy_input_mode: interrupt
  bell_on_complete: true
  bell_on_prompt: false
  show_reasoning: true
  background_process_notifications: concise
  streaming: true
  skin: default
  language: zh
  interim_assistant_messages: true
  tool_progress: all
  cleanup_progress: false
  long_running_notifications: true
  busy_ack_detail: true
  message_reactions: false
stt:
  enabled: false
  language: en
  local:
    model: base
  openai:
    model: whisper-1
    language: ''
voice:
  auto_tts: false
  beep_volume: 1
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 3000
  user_char_limit: 2000
  nudge_interval: 10
  provider: openviking
  openviking:
    endpoint: http://127.0.0.1:1933
    account: default
    user: default
    agent: hermes
    recall_limit: 3
    recall_score_threshold: 0.35
    recall_prefer_abstract: true
    recall_resources: true
    recall_timeout_seconds: 15.0
delegation:
  max_iterations: 250
moa:
  presets:
    default:
      reference_models:
      - provider: custom:workbuddy-(127.0.0.1:8787)
        model: glm-5.3-flash
        enabled: false
      aggregator:
        provider: custom:workbuddy-(127.0.0.1:8787)
        model: glm-5.3-flash
      enabled: false
      degraded_reference_policy: loud
      fanout: user_turn
  reference_models:
  - provider: custom:workbuddy-(127.0.0.1:8787)
    model: glm-5.3-flash
    enabled: false
  aggregator:
    provider: custom:workbuddy-(127.0.0.1:8787)
    model: glm-5.3-flash
  degraded_reference_policy: loud
  max_tokens: 4096
  fanout: user_turn
  enabled: false
skills:
  creation_nudge_interval: 15
  disabled: []
approvals:
  mode: 'off'
plugins:
  enabled:
  - superpowers
  - token-stats
  disabled: []
  entries:
    superpowers:
      allow_tool_override: false
security:
  allow_private_urls: true
  allow_data_training_tiers_noninteractive: true
kanban:
  review_dispatch: true
code_execution:
  timeout: 300
  max_tool_calls: 50
streaming:
  enabled: true
onboarding:
  seen:
    busy_input_prompt: true
telemetry:
  shared_metrics:
    enabled: false
    send: false
updates:
  pre_update_backup: false
  backup_keep: 5
  non_interactive_local_changes: stash
computer_use:
  backend: cua
local_runtime:
  enabled: false
_config_version: 40
mcp_servers:
  chrome-devtools:
    command: cmd
    args:
    - /c
    - npx
    - -y
    - chrome-devtools-mcp@1.8.0
    - --autoConnect
    - --ignore-default-chrome-arg=--disable-extensions
    timeout: 300
    enabled: true
    lazy: true
    idle_timeout_seconds: 60
  deepwiki:
    url: https://mcp.deepwiki.com/mcp
    enabled: true
session_reset:
  mode: none
  idle_minutes: 1440
  at_hour: 4
group_sessions_per_user: true
platform_toolsets:
  cli:
  - clarify
  - code_execution
  - computer_use
  - cronjob
  - delegation
  - file
  - image_gen
  - kanban
  - memory
  - session_search
  - skills
  - terminal
  - todo
  - video
  - vision
  - web
  telegram:
  - hermes-telegram
  discord:
  - hermes-discord
  whatsapp:
  - hermes-whatsapp
  slack:
  - hermes-slack
  signal:
  - hermes-signal
  homeassistant:
  - hermes-homeassistant
  qqbot:
  - hermes-qqbot
  yuanbao:
  - hermes-yuanbao
  teams:
  - hermes-teams
  google_chat:
  - hermes-google_chat
custom_providers:
- api_key: <REDACTED_LOCAL_KEY>
  api_mode: chat_completions
  base_url: http://127.0.0.1:18080/v1
  model: gemini-3.8-flash
  models:
    gemini-3.1-flash-image: {}
    gemini-pro-agent: {}
    gpt-oss-120b-medium: {}
    gemini-web-search: {}
    claude-opus-4-6-thinking: {}
    claude-sonnet-4-6: {}
    gemini-3-flash: {}
    gemini-3.1-pro-low: {}
    gemini-3.6-flash: {}
    gemini-3.7-flash: {}
    gemini-3.8-flash: {}
  models_discovered: true
  name: cpa-gui
- name: WorkBuddy (127.0.0.1:8787)
  base_url: http://127.0.0.1:8787/v1
  api_key: local
  model: auto
  models:
    auto: {}
    hy4-preview: {}
    hy4-preview-x: {}
    hy3: {}
    hy3-x: {}
    glm-5.3: {}
    glm-5.3-flash: {}
    glm-5.2: {}
    glm-5.1: {}
    glm-5.0: {}
    glm-5v-turbo: {}
    glm-4.7: {}
    glm-4.6: {}
    glm-4.6v: {}
    minimax-m3: {}
    minimax-m2.5: {}
    kimi-k3-1: {}
    kimi-k3: {}
    kimi-k2.7: {}
    kimi-k2.6: {}
    kimi-k2.5: {}
    kimi-k2-thinking: {}
    deepseek-v4-pro: {}
    deepseek-v4-flash: {}
    deepseek-v3-2-volc: {}
    hunyuan-2.0-thinking: {}
    hunyuan-chat: {}
    default: {}
  models_discovered: true
platforms:
  webhook:
    enabled: true
  qqbot:
    enabled: false
    home_channel:
      platform: qqbot
      chat_id: 078DEECF2FF6867028A5CADEDC823720
      name: 078DEECF2FF6867028A5CADEDC823720
      user_id: 078DEECF2FF6867028A5CADEDC823720
known_plugin_toolsets:
  cli:
  - a2a
  - spotify
known_builtin_toolsets:
  cli:
  - browser
  - clarify
  - code_execution
  - computer_use
  - context_engine
  - cronjob
  - delegation
  - discord
  - discord_admin
  - file
  - homeassistant
  - image_gen
  - memory
  - session_search
  - skills
  - spotify
  - stt
  - terminal
  - todo
  - tts
  - video
  - video_gen
  - vision
  - web
  - x_search
  - yuanbao
model_aliases:
  workbuddy:
    model: auto
    provider: custom
    base_url: http://127.0.0.1:8787/v1
  workbuddy-glm:
    model: glm-5.2
    provider: custom
    base_url: http://127.0.0.1:8787/v1
  workbuddy-glm53:
    model: glm-5.3-flash
    provider: custom
    base_url: http://127.0.0.1:8787/v1
  workbuddy-kimi:
    model: kimi-k2.7
    provider: custom
    base_url: http://127.0.0.1:8787/v1
  workbuddy-kimi3:
    model: kimi-k3
    provider: custom
    base_url: http://127.0.0.1:8787/v1
  workbuddy-deepseek:
    model: deepseek-v4-pro
    provider: custom
    base_url: http://127.0.0.1:8787/v1
  workbuddy-hy4:
    model: hy4-preview
    provider: custom
    base_url: http://127.0.0.1:8787/v1

# ── Security ──────────────────────────────────────────────────────────
# Secret redaction is ON by default — strings that look like API keys,
# tokens, and passwords are masked in tool output, logs, and chat
# responses before the model or user ever sees them. Set redact_secrets
# to false to disable (e.g. when developing the redactor itself).
# tirith pre-exec scanning is enabled by default when the tirith binary
# is available. Configure via security.tirith_* keys or env vars
# (TIRITH_ENABLED, TIRITH_BIN, TIRITH_TIMEOUT, TIRITH_FAIL_OPEN).
#
# security:
#   redact_secrets: true
#   tirith_enabled: true
#   tirith_path: "tirith"
#   tirith_timeout: 5
#   tirith_fail_open: true

# ── Fallback Model ────────────────────────────────────────────────────
# Automatic provider failover when primary is unavailable.
# Uncomment and configure to enable. Triggers on rate limits (429),
# overload (529), service errors (503), or connection failures.
#
# Supported providers:
#   openrouter   (OPENROUTER_API_KEY)  — routes to any model
#   openai-codex (OAuth — hermes auth) — OpenAI Codex
#   nous         (OAuth — hermes auth) — Nous Portal
#   zai          (ZAI_API_KEY)         — Z.AI / GLM
#   kimi-coding  (KIMI_API_KEY)        — Kimi / Moonshot
#   kimi-coding-cn (KIMI_CN_API_KEY)   — Kimi / Moonshot (China)
#   minimax      (MINIMAX_API_KEY)     — MiniMax
#   minimax-cn   (MINIMAX_CN_API_KEY)  — MiniMax (China)
#   bedrock      (AWS IAM / boto3)     — AWS Bedrock (Converse API)
#
# For custom OpenAI-compatible endpoints, add base_url and key_env.
#
# fallback_model:
#   provider: openrouter
#   model: anthropic/claude-sonnet-4
```

---

## 五、 关键实施与检索指南

- **Why**: Hermes 拥有复杂的桌面与多模型配置，且随版本持续迭代。将软件构建指纹与全量配置快照绑定，不仅杜绝跨端协作时的信息差，还能在未来版本升级出现配置兼容性问题时秒级追溯回滚。
- **How to apply**: 当用户提及「我改了设置 / 看一下我改的 / 同步一下设置」时，立即执行 `read_file(C:/Users/VOS-User/AppData/Local/hermes/config.yaml)`，同步核对 `hermes --version`，对比变动点后覆写更新本文件与 `hermes-config.yaml` 并提交推送 `main`。
