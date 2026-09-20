---
name: hermes-agent
description: "配置/扩展/编排Hermes时必用。Use, configure, theme, extend, and orchestrate Hermes Agent."
version: 3.2.0
author: Hermes Agent + Teknium
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, bots, bot-mode, features, themes, skins, desktop-plugins, tui-widgets, petdex, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, a native desktop app, messaging platforms, and IDEs. It's in the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, Google, DeepSeek, xAI, local models, and 20+ others) and runs on Linux, macOS, Windows, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills that load into future sessions.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, iMessage, Signal, Matrix, Teams, Email, and a dozen more platforms with full tool access, not just chat.
- **Many surfaces** — the same agent core drives the CLI, the Ink TUI, a native Electron desktop app, a web dashboard, and an ACP server for IDEs (VS Code / Zed / JetBrains).
- **Provider-agnostic** — swap models and providers mid-workflow; credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible & themeable** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, skins that theme every surface, desktop UI plugins, TUI widgets, and pet mascots.

**This skill is a hub.** The body covers identity, quick start, spawning/orchestration, and hard invariants. Everything else lives in reference files — **load the matching reference (below) before answering**; do not answer detail questions from the body alone.

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Scope & Verification

This skill is a concise operating guide, not the complete source of truth for every Hermes feature. If a Hermes feature, command, or setting is not mentioned here or in a reference, do not treat that absence as evidence that it does not exist. Check the live repository and official docs before giving a negative answer.

Good verification targets, cheapest first:

- **Every shipped feature, one line each: https://hermes-agent.nousresearch.com/docs/llms.txt.** Start here for any "can Hermes do X?" or "how do I do X?" — it indexes the entire documentation set with a link to the page that answers. It is generated from the docs tree on every build, so it is never behind the product. Fetch it with `web_extract`, or `curl -s https://hermes-agent.nousresearch.com/docs/llms.txt` when web tools are off. The whole documentation set in one file is at `/docs/llms-full.txt`.
- CLI commands: `hermes --help`, `hermes <command> --help`, and `hermes_cli/main.py`
- Source tree: https://github.com/NousResearch/hermes-agent

Never answer "Hermes can't do that" from memory. Hermes ships far more than this skill body describes, and the index exists so a negative answer is always checkable.

## Quick Start

```bash
# Install (shell installer — sets up uv, Python, the venv, and the launcher)
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Interactive chat (default surface; set display.interface: tui to launch the Ink TUI instead)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard  /  pick model+provider  /  health check
hermes setup
hermes model
hermes doctor

# Other surfaces
hermes desktop                 # launch the native desktop app (alias: hermes gui)
hermes dashboard               # web admin panel + embedded chat
hermes proxy                   # OpenAI-compatible local proxy backed by your OAuth provider
```

## Key Paths

```
~/.hermes/config.yaml       Main configuration (settings — never secrets)
~/.hermes/.env              API keys and secrets ONLY (under $HERMES_HOME if set)
$HERMES_HOME/skills/        Installed skills
~/.hermes/skins/            Custom themes (see references/themes.md)
~/.hermes/desktop-plugins/  Desktop app UI plugins (see references/desktop-plugins.md)
~/.hermes/tui-widgets/      TUI widget apps (see references/tui-widgets.md)
~/.hermes/pets/             Installed pet mascots (see references/petdex.md)
~/.hermes/state.db          Canonical session store (SQLite + FTS5)
~/.hermes/sessions/         Gateway routing index, request dumps, *.jsonl transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout. When a profile is active, resolve the real home from `$HERMES_HOME` — never hardcode `~/.hermes`.

## Routing Table — load the reference for the task

| User wants... | Load |
|---|---|
| **Anything not listed below — "can Hermes do X?", "how do I set up X?"** | **https://hermes-agent.nousresearch.com/docs/llms.txt** |
| Bots that chat, run routines, or message each other; the Bots tab | docs: `/user-guide/bot-mode` |
| CLI commands, subcommands, flags, "how do I run X" | `references/cli-reference.md` |
| In-session slash commands | `references/slash-commands.md` |
| Provider setup, API keys, OAuth | `references/providers-and-models.md` |
| config.yaml sections, toolsets, voice/STT/TTS | `references/configuration.md` |
| AGENTS.md / .hermes.md / CLAUDE.md project rules | `references/project-context-files.md` |
| Secret redaction, PII, approval modes, "reset permissions" | `references/security-privacy.md` |
| Delegation, cron, curator, kanban | `references/background-systems.md` |
| MCP servers (add, catalog, `hermes mcp`) | `references/native-mcp.md` |
| Webhook routes and event-driven runs | `references/webhooks.md` |
| A custom theme/skin ("synthwave theme", "change the gold ●") | `references/themes.md` + `templates/skin.yaml` |
| A desktop app UI element (pane, widget, ⌘K command, page) | `references/desktop-plugins.md` + `templates/plugin.js` |
| A live TUI panel or modal widget (ticker, clock, dashboard) | `references/tui-widgets.md` + `templates/clock.mjs` |
| Pet mascots — install, select, scale, diagnose | `references/petdex.md` |
| Windows-specific issues (keybinds, WinError 10106, BOM) | `references/windows-quirks.md` |
| Debugging: voice, tools missing, gateway, aux models | `references/troubleshooting.md` |
| Contributing code: adding tools, slash commands, tests | `references/contributor-guide.md` |
| delegate_task "capped at N" reports | `references/delegate-task-concurrency-diagnosis.md` |
| "Can app X use my Nous Portal subscription/OAuth?" | `references/portal-auth-for-third-party-apps.md` |
| Connecting a messaging platform (Telegram, Discord, Slack, WhatsApp, …) | docs: `/user-guide/messaging` |

The reference list above is not the feature list — it is the set of topics that
need more than their docs page. For everything else Hermes ships, fetch
`llms.txt` and it maps the question to the page that answers it.

Two theming rules that hold even without loading the reference: **you apply skins yourself** (`hermes config set display.skin <name>` — every surface repaints live within ~a second; don't tell the user to run `/skin`), and **to tweak one color, edit the ACTIVE skin** (`hermes skin set <key> <hex>`) — never fork `default`, which drops the palette and resets the background.

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry
- **"delegate_task is capped at N" reports** — see `references/delegate-task-concurrency-diagnosis.md`. Three real cap paths in Hermes; if none fired, the model is self-limiting and rationalising it as "the runtime caps."
- **"Can $external_app use my Nous Portal subscription / OAuth?"** — see `references/portal-auth-for-third-party-apps.md`. Walk the user through three layers (plugin-vs-app, what Portal actually exposes, local-broker-proxy option).

## Surfaces (quick orientation)

- **Desktop app** (`hermes desktop` / `hermes gui`) — native Electron app for macOS/Linux/Windows: streaming chat, session list, Cmd+K palette, drag-and-drop files, native notifications, per-profile remote-gateway login. Extend it with UI plugins — `references/desktop-plugins.md`.
- **Web dashboard** (`hermes dashboard`) — full admin panel: messaging channels, MCP catalog, webhooks, memory, profile builder, plus an embedded `hermes --tui` chat. Secured behind an OAuth/token gate.
- **Ink TUI** (`hermes --tui` or `display.interface: tui`) — terminal UI with docked widget apps — `references/tui-widgets.md`.
- **OpenAI-compatible proxy** (`hermes proxy`) — a local OpenAI API backed by whichever OAuth provider you're signed into. Point Codex CLI, Aider, Cline, or any script at it — no API key.

## Model-Picker「快速」(Fast) Toggle Semantics

Desktop model-menu「快速」= `/fast` = `agent.service_tier`, three mechanisms:
1. **param mode** — `service_tier:"priority"` (OpenAI Responses) / `speed:"fast"` (Anthropic Opus 4.8/5, Claude API only), gated by `_fast_mode_route_supported`: only sent to the FIRST-PARTY billing endpoints (`api.openai.com`, `chatgpt.com`, `api.anthropic.com`, `api.x.ai`) — `resolve_fast_mode_overrides()` returns None for any custom/proxy base_url, so the param never reaches a local reverse proxy.
2. **variant mode** — no param: fast = switching to the `…-fast` sibling model id (works through any proxy; a real different model).
3. **window modes** — `service_tier: auto|cold` (`/fast auto|cold`): bounded window (`fast_auto_seconds`, default 60s) where the fast override is layered per-request, so the prompt cache survives the boundary (`agent/fast_mode.py`).

Pitfall: the picker shows the 快速 toggle whenever `model_supports_fast_mode()` matches the id (gpt-*/o1/o3/o4 prefixes, opus-4.8/5, grok-4.6) WITHOUT the route check, so on custom providers it renders then fails at apply time with `fast mode is not available for this model` (desktop shows「快速模式更新失败」). When a user asks what it does on a proxy-routed model: explain mechanism 1 + the route gate, and check the provider's `models:` list for a `-fast` sibling (mechanism 2) as the only working alternative.

## Hard Invariants (never violate, regardless of what you loaded)

- **Never break prompt caching** — don't change past context, toolsets, or the system prompt mid-conversation. The only exception is context compression.
- **Message role alternation** — never two assistant or two user messages in a row; only `tool` results can repeat.
- **Secrets in `.env`, settings in `config.yaml`** — never tell a user to put a non-credential setting in `.env`.
- **Profile-safe paths** — `get_hermes_home()` in code, `$HERMES_HOME` when resolving paths in a session.
- **Never hand-edit or patch `config.yaml` directly** — Hermes file tools enforce a hard security guard (`Refusing to write to Hermes config file...`). Always use `hermes config set KEY VAL` or `hermes config unset KEY`; a stray indent can corrupt the file and break the live gateway.

## UI Disambiguation & Tool Concurrency Semantics

**Deferred `todo_list` schema:** Load `tool_describe` before invoking it. Write tasks as `{"todos":[{"id":"audit","content":"Review code","status":"in_progress"}]}`; valid statuses are `pending/in_progress/completed/cancelled`, and `merge:true` updates by id. Legacy-looking `action/items/title` arguments may silently return an empty unchanged board; `todos:null` fails validation. Read with `{}` and verify the returned revision and items before claiming initialization.

**`search_files` pattern vs glob distinction (`target='content'` vs `target='files'`):** In content mode, `pattern` is evaluated strictly as a ripgrep regular expression, NOT a shell glob. Passing glob wildcards like `*keyword*` triggers `rg: regex parse error: repetition operator missing expression` (`*` at the start has no operand). Use plain literal substrings (e.g. `keyword`) or valid regex (`.*keyword.*`). Reserve glob patterns like `*.py` exclusively for `target='files'` or the `file_glob` filter.

**HARD RULE — never claim terminal runs in parallel.** The kernel whitelist `_PARALLEL_SAFE_TOOLS` (`agent/tool_dispatch_helpers.py`) is read-only-only: read_file, search_files, web_search, web_extract, skill_view, skills_list, session_search, vision_analyze. `terminal`, `patch`, `write_file`, `memory`, `delegate_task` are **sequential barriers** — even when batched in one turn they execute strictly one-at-a-time. In thinking, reports, and summaries NEVER write「并行执行命令」/"executed in parallel" for terminal batches — the correct phrase is 「逐条串行」. A false parallelism claim is a fake-execution report and is treated as seriously as fabricating tool output. Terminal commands appearing one-by-one in the UI is intentional safety design (shared persistent shell session: cwd/env persist across calls), never a bug to debug.

**后台进程的 notify pattern 禁用泛词 —— `failed`/`error` 会命中良性告警行并误报（2026-09-19 实测）。** `terminal(background=true, notify=["failed"])` 是**子串**匹配任意输出行：llama-server 启动期的自述良性告警 `E llama_init_from_model: failed to initialize the context: dflash requires ctx_other to be set (this warning is normal during memory fitting)` 照样触发通知，而进程其实已正常加载并在服务（日志后续为 `model loaded` / `listening on http://...`）。处置顺序：先拉 `process_manage(action='log')` 看全量日志再下结论，别被通知措辞带走。写 pattern 前先裸跑一次、抄二进制**实际**打印的就绪行（llama-server 是 `listening on http://` 与 `model loaded`，不是臆想的 "server is listening"）；pattern 仅用于永不退出的常驻进程，有明确终点的任务一律 `notify=true`（退出即通知），避免 pattern 误报成为噪音。

**`read_file` dedup guard changes its RETURN SHAPE — never index `["content"]` blindly.** Repeat reads of the same path+region inside one conversation (or one `execute_code` kernel) trip a three-stage guard that protects against re-injecting the same bytes:

| Occurrence | Returned shape |
|---|---|
| 1st | `{content, total_lines, file_size, truncated, is_binary, is_image}` |
| 2nd (unchanged) | `{status:"unchanged", dedup:true, content_returned:false, message, path}` — **no `content` key** |
| 3rd+ | `{error:"BLOCKED: You have called read_file on this exact region 3 times…", already_read:3, path}` |

Writing `read_file(p)["content"]` and proceeding assumes stage 1. Stage 2 raises `KeyError: 'content'`; stage 3 silently yields no content. Both are the guard working correctly, not a tool failure. Rules: **(a)** treat the second read as authoritative "file unchanged — reuse the earlier result"; **(b)** before re-reading, gate on the shape (`if "content" in r`) or read the file with plain `open()` inside `execute_code` when you specifically need fresh bytes; **(c)** after 3 reads, the guard is telling you to stop — go back to the content already in context.

**插件改写工具参数：`{"action":"modify","args":{...}}` 与「原地改 args」都生效，但机理不同（2026-09-18 查源码实证）。**

`pre_tool_call` 的改写通道在 `hermes_cli/plugins.py::_get_pre_tool_call_directive_details`：逐回调取 `result.get("action")`，`action == "modify"` 时把 `result["args"]` 浅合并进 `modified_args`。调用方 `agent/tool_executor.py::_pre_tool_block` 收尾是 `ref.args if modified_args is None else modified_args`。于是两条路都能改：
- **(a) 返回值式（官方、推荐）**：`return {"action": "modify", "args": {"command": new}}`。显式、不依赖实现细节。
- **(b) 原地改（隐式生效）**：回调收到 `args` 后直接 `args["command"] = new` 并 `return None`。虽然 `plugins_dispatch.invoke_hook` 只收集非 None 结果（该结果被丢弃），但 `args` 从 `_get_pre_tool_call_directive_details` → `invoke_lifecycle_hook` → `plugins.invoke_hook` → `_invoke_hook_callback(cb, **payload)` 全程只经 `**kwargs` 解包、**不做拷贝**，`args` 始终是同一个 dict 对象，所以原地改会反映到调用方持有的 `ref.args` 上。rtk 的 Hermes 插件（`hooks/hermes/rtk-rewrite/__init__.py`）用的就是这条路。
- **验证纪律**：装任何第三方 `pre_tool_call` 改写插件后，必须**实测一条命令**确认真的被改写（看工具回显的命令变了没有）；"插件已加载"不等于生效。若日后 dispatch 链引入 `copy.deepcopy(args)`，通道 (b) 会静默失效——这也是为什么新写插件优先用 (a)。
- **安装路径坑**：Hermes 把插件目录固定解析为 `get_hermes_home()/plugins`（见 `plugins_cmd._plugins_dir`）。本机 `$HERMES_HOME=%LOCALAPPDATA%\hermes`，而 `~/.hermes` 只是迁移残留壳（其 config.yaml 仅一行 `mcp_servers: {}`）。第三方 installer 若在没设 `HERMES_HOME` 的 shell 里硬编码 `~/.hermes` 就会装进不被加载的目录（rtk 的 `HERMES_DIR` 常量即是此 fate，但它优先读 `$HERMES_HOME` 覆盖，所以带上环境变量跑才对）。

**⚠️ Hermes 没有任何钩子能改写【工具输出】——只能改写【命令】（2026-09-18 全链路查证）。这是所有"输出压缩器"类需求的前提。**

逐通道核实结果：

| 通道 | 能力 | 源码依据 |
|---|---|---|
| `pre_tool_call` | ✅ 能改**命令**参数 | `plugins.py::_get_pre_tool_call_directive_details` 的 `action=="modify"` |
| `post_tool_call` | ❌ 纯观察者，返回值被丢弃 | `model_tools.py::_emit_post_tool_call_hook` 调 `invoke_hook(...)` **不接收返回** |
| `hooks:` shell hooks | ❌ 只能 `{"context": ...}` 注入 | `shell_hooks.py:431` `_RESPONSE_PARSERS` 只有 `pre_tool_call`/`pre_verify` |
| middleware | ❌ 只有 `llm_request`/`tool_request` 两种 kind | 无结果改写 kind |

⇒ 想减少超长工具输出，**只能在命令层让它少产出**，或在结果存储层配阈值（见下）。任何"事后过滤工具输出"的方案（rtk 那类）在 Hermes 里没有落点；rtk 之所以在别的 agent 能成立，正是因为它有 `pre_tool_call` 改命令这一条路。

**workbuddy2api 内核直接从检出目录加载 `converter.py`，改完只需重启内核、不必重建 exe（2026-09-20 实测）。**
运行中的内核命令行是 `...python.exe "D:\ai coding\GitRepos\workbuddy2api\converter.py" --port 8787 ...`
——脚本路径指向工作树而非打包资源。所以「改了内核代码要不要重新构建」的答案是：
**不需要 `npm run tauri build`，但需重启内核进程；而重启会切断本机 Hermes 对话链路，时机由用户决定**。
查当前内核实际加载的脚本路径（比猜快得多）：

```bash
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Select-Object ProcessId,CommandLine | Format-List"
```

**超大工具结果的两个现成旋钮：**
1. **spillover 阈值**（官方机制）：`tools/tool_result_storage.py` 把超过阈值的结果落盘到 `$HERMES_HOME/cache/spillover/{id}.txt`，上下文只留 1500 字符 preview + 路径。默认**单条 100K 字符**、单轮合计 200K（`tools/budget_config.py`）。
2. **按工具设更低阈值**：`tool_output.tool_overrides`（如 `web_search: 20000`）—— **截至 2026-09-18 尚未并入 main**，由 PR #106399 提供（维护者 salvage，#94679 的替代）。该字段（`BudgetConfig.tool_overrides`）本身已在 main 的代码里存在且优先级最高（`pinned → tool_overrides → mcp_前缀 → registry → default`），只是缺配置读取入口。**在 #106399 合并前，`tool_output.tool_overrides` 写进 config 不会生效**——不要以为配了就完事，必须实测。

**长输出命令的改写范式（零依赖、立刻可用）——以 CI 轮询为例：**

`gh run watch` 每 3-10 秒刷一屏全量状态，实测单条最大 33.5K 字符且**全部卡在 100K 线下、一个都没落盘**，是典型的"明知超长却拿不到 spillover 保护"的输出。改写为一次问询：

```bash
# 旧（持续刷屏，全量进上下文）
gh run watch <run-id> -R <owner/repo>

# 新（只出终态，几十字符）
gh run view <run-id> -R <owner/repo> --json status,conclusion,jobs \
  --jq '{status,conclusion,jobs:[.jobs[]|{name,conclusion}]}'
```

更根本的做法：CI 轮询不该占用 terminal —— 用 cronjob 定时跑 `gh run view --json` 并把结果写文件，上下文零占用。

可复用的 `pre_tool_call` 改写插件模板见 `templates/pre_tool_call_rewrite_plugin.py`（返回值式 `{"action":"modify","args":{...}}`，含 fail-open 与 CLI 不可用时静默放行）。

**cron 通知链依赖模型路由快照 —— 切模型就会静默失败（2026-09-18 实测）。**

job 创建时会把当时的 `provider`/`model` 写进 `jobs.json`（创建后显示为 `provider_snapshot`/`model_snapshot`）。用户后续切默认模型，**旧 job 仍走旧路由**。若那个端点已停（本机实测：`curl 127.0.0.1:18080/v1/models` → Connection refused），job 每次运行都以 `RuntimeError: Connection error.` 失败。

更隐蔽的第二层：**投递目标也可能无效**。工具创建的 job 抓不到 origin（`origin: null`），回退到 home channel —— 若本机唯一有 chat_id 的 platform 是 `enabled: false`（本机 qqbot 即如此），则 `delivery FAILED: platform 'qqbot' not configured/enabled`，**即使 agent 跑成功通知也送不到**。

排查与修复：
```bash
hermes cron list                          # 看 last_status / last_error / last_delivery_error
hermes cron runs <job_id>                  # 看历史
hermes cron runs <job_id> --help           # 查看单次输出
hermes cron edit <job_id> --model M --provider P   # 改模型路由（注意：工具 schema 无此参数，必须走 CLI）
hermes cron edit <job_id> --deliver local  # 或换成真实可投递的目标
```
**关键取舍**：当通知的可靠性重要时，**不要用 cron + agent**，改用 GitHub Actions 工作流发 issue（见 `github` skill）—— CI 在云端跑，只依赖公开 API，与模型路由完全解耦。

另一个坑：`cron status` 报「Gateway is not running」但**心跳仍在推进**时，那些错的是独立 gateway 服务；**桌面内调度器可独立存活**（实测 `.tick.lock` 每分钟更新）。但**定时触发确实依赖 gateway**（实测手建的一次性 job 未按时触发）；手工 `cron run` 则立刻执行。先看 `cron/jobs.json` 的 `last_run_at` 与 `cron/output/<job_id>/` 实际产物再下结论。

**Monitor 模式会让 agent 完全不跑 —— 不要用它验证 LLM 链路。** `monitor` 脚本输出未变时整个 run 被抑制，状态记 `no_change (agent run suppressed)`，**模型连接问题根本不会暴露**。验证 LLM 层必须用不带 monitor 的临时 job。

- The orange「已保存到记忆 N entries」badge is the **foreground `memory` tool call's title template** (desktop i18n `zh.ts` → `toolTitles.memory.done`), NOT a background review fork write. Background-fork writes surface via `display.memory_notifications` (`💾 Memory updated` system line) — a different UI element.
- `config.yaml` changes need **no restart**: `background_review.enabled` is re-read at every spawn (file mtime+size signature cache invalidates on edit); nudge intervals are read when each message constructs its agent.
- **Desktop Composer 焦点劫持与 Popover 自动关闭排查（2026-09-17）**：上游 `floating-target.ts` 监听全局 `pointermove` 跟踪跨分屏浮动输入框，但因缺少覆盖层保护和未判定 composer 宿主，导致只要光标在聊天区滑动就会强行执行 `editor.focus()` 抢焦点，使状态栏 Popover（如 token-stats）遭遇失焦并自动关闭。排查时需确保：① `BLOCKING_OVERLAY_SELECTOR`（包含 `[data-radix-popper-content-wrapper]` 等）检测到活动浮层时直接放弃焦点抢占；② `pointermove` 仅在光标直指 composer 宿主或浮动输入框跨分屏输入时才聚焦，绝不在光标滑过聊天内容或状态栏时窃取焦点。

**删除目录报 `Device or resource busy` / `WinError 32` —— 先查自己的 persistent shell 与 execute_code 内核（2026-09-18 实测）。**

`terminal` 是**持久会话**，`cd` 进去过的目录会一直作为该 shell 进程的 CWD；`execute_code` 的 kernel 同理。Windows 不允许删除任何进程将其作为 CWD 的目录 ⇒ `rm -rf` / `Remove-Item` / `rd /s /q` 全部报「另一个程序正在使用此文件」。

- **定位**：先 `cd` 到中性目录（如 `C:/`）再删，不要从目标目录内发起。仍失败则枚举各进程 CWD（读 PEB → `ProcessParameters.CurrentDirectory.DosPath`）找出持有者 —— 大概率就是自己的 shell/kernel 进程。
- **ctypes 陷阱（本次连错两轮的真因）**：`OpenProcess` 必须 `PROCESS_QUERY_INFORMATION | PROCESS_VM_READ`（0x0400|0x0010）才能 `ReadProcessMemory`；只给 `PROCESS_QUERY_LIMITED_INFORMATION`(0x1000) 会**全部读取失败**，探针返回「无持有者」的**假阴性**。另：不声明 `restype` 时 ctypes 默认 32 位 int，**会截断 64 位 HANDLE**。用 `--selftest`（起一个已知 CWD 的子进程验证探针能认出）证伪，否则会在坏工具上反复得到错误结论。
- **`EnumProcesses` 在 `psapi.dll`**，不在 kernel32。
- **处置**：`execute_code(reset=True)` 换新内核可释放旧内核的 CWD；若旧内核进程仍持有，确认它已废弃后结束该 PID 再删。
