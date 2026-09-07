---
name: cross-agent-collaboration
description: Use when coordinating Hermes with ZCode or other agents.
---

# Cross-Agent Collaboration & Autonomous Handoff

Protocol for coordinating Hermes with ZCode or external coding agents running on the same host, observing task progress, and executing automated handoffs without user babysitting.

## 1. Observing External Agent Progress

When checking the live progress, active subagents, or tool traces of ZCode:
- Target database: `C:/Users/VOS-User/.zcode/cli/db/db.sqlite`
- **Lock-Free Read Protocol**: Always connect with SQLite URI read-only mode (`sqlite3.connect("file:C:/Users/VOS-User/.zcode/cli/db/db.sqlite?mode=ro", uri=True)`). Opening in standard read-write mode risks colliding with the external agent's active write transactions, causing `sqlite3.OperationalError: database is locked`.
- Hierarchy:
  - `session`: identify active task (`time_updated DESC`), parent-child delegation trees (`task_type='subagent_child'`, `parent_id`).
  - `message` & `part`: inspect `type='tool'` (tool status: running/completed/error) and `type='reasoning'` (Chain of Thought).

## 2. Autonomous Handoff & Session Watching

When instructed to "wait for the other agent to finish and then take over / review":

### Anti-Patterns (STRICTLY FORBIDDEN)
1. **The Verbal Idle Promise**: Saying "I am monitoring in the background" and then returning a final text turn. Hermes turns are turn-based; ending the turn puts the agent to sleep until the user speaks again.
2. **The Foreground Blocking Loop**: Writing `while not done: sleep(3)` inside a foreground `terminal` or `execute_code` call. This completely freezes the desktop chat UI, preventing user interaction, and risks exceeding tool execution timeouts (180s~300s).

### Canonical Non-Blocking Daemon Pattern
Launch a lightweight polling daemon in the background with process exit notification enabled:

```python
terminal(
    command="python C:/Users/VOS-User/AppData/Local/hermes/scripts/watch_zcode.py --session <SESSION_ID>",
    background=True,
    notify=True  # Critical: triggers autonomous turn wake-up when process exits
)
```

1. Background daemon polls `db.sqlite` periodically (every 3s) with read-only URI.
2. **Active Sliding Window Filter (CRITICAL)**: When checking child subagents under a parent session (`WHERE parent_id = ?`), always filter by a sliding activity window (`time_updated >= now - 15s`). Historical subagents from completed or cancelled earlier turns often leave their final event as `step-start` in SQLite; checking all historical children naively will mistake a stale subagent for active work, permanently deadlocking the watcher.
3. As soon as all actively updated subagents and the main task report no running/pending tools and settle (consecutive idle checks >= 2), the daemon exits with code 0.
4. The runtime notification (`[PROCESS EXITED]`) automatically re-enters the conversation and awakens Hermes.
5. **OS Notification Independence**: The `notify=True` parameter in Hermes relies strictly on the internal application event bus (Process Exit Event detected by the Hermes runtime gateway). It is 100% self-contained within Hermes and is completely independent of Windows 11 OS Toast Notifications (which can remain globally disabled in Windows Settings without affecting agent wake-up).

## 3. Takeover & Parallel Execution (Multi-Repo & Multi-Task Fan-out)

Upon being awakened by a handoff signal, or when presented with multi-repository / multi-domain audit findings and fix items:
- **Fork-First 强约束门禁（Anti-Serialization Rule）**：只要用户输入包含 **2 个及以上独立诉求/目标**（如“一边修 A 一边查 B”、跨仓库、多文件批量检查、或修复+深度分析），**第一动作必须坚决直接调用 `delegate_task` 并行分派，严禁在主会话单线程串行起跑**；主会话仅做调度派发、最终结果聚合与用户决策，绝不允许中间繁杂数据与试探命令卡死主会话。
- **主聊天会话零阻塞铁律（Non-Blocking Main Turn）**：长跑命令（如 CI 轮询 `gh run watch`、大型打包构建、服务守护）永远严禁在主会话前台串行等待。必须显式放入后台 (`terminal(..., background=True, notify=True)`)，由进程退出信号或定时探针自动唤醒，保持主会话随时可与用户交互，杜绝任何形式的进度假死。
- **Strict Anti-Pattern — "Subsetting & Tentative Deferral"**: NEVER artificially pick 2~3 items to serialize in the foreground while kicking others into a backlog or asking "if you agree, I'll do X first". If tasks are independent, actionable, and verified, dispatch them in parallel in one turn without requiring the user to prompt "do it in parallel".
- **Zero-Prompting Fan-out Rule**: When presented with an audit list across multiple repositories or independent subsystems (e.g., bug fixes + workflow gates + security pins), do NOT pause to ask "which subset to fix first" or wait for the user to prompt "do it in parallel". Immediately partition all actionable items across 3~6 parallel subagents, execute concurrently, run localized test suites within each subagent, and push/verify CI in parallel. The user has zero tolerance for artificial serialization or passive waiting.
- **Single Source of Truth (SSOT) Pre-Transaction Hard Gate**: In multi-file persistence architectures with compatibility mirrors (e.g., `accounts.json` as SSOT, `.info` as legacy mirror), writing to the SSOT must be a hard pre-transaction gate. If SSOT write fails, the agent/service MUST immediately abort the entire commit with an explicit exception. Never catch and log the SSOT failure while proceeding to update the mirror or in-memory cache — doing so causes catastrophic state drift upon restart (especially during Token Rotation).
- **UID-Partitioned Runtime Caching**: In any local gateway or proxy supporting multi-account switching, all dynamic model catalogs, quotas, and capability caches MUST be keyed by `uid` (or tenant identifier). Global unkeyed singletons will leak preceding account permissions, beta models, or quota matrices across fast account switches.
- **Workflow Pre-Push Test Gate Invariant**: In all automated upstream-sync or maintenance workflows, always insert full test suite execution (`npm test` / `node --test ...`) immediately after build and syntax check, strictly BEFORE `git commit && git push`. Never allow untested builds to enter `main`.
- **Log Privacy Tri-tier Standard**: `info` MUST be strictly zero-prompt-leak (metadata only: model, stream, msg count, tool count, latency, status); truncated `last_user` or prompt snippet belongs strictly to `debug`; full request/response bodies belong to `trace`.
- Typical verification & multi-repo split:
  - Subagent 1: Frontend dependency closure & production build (`npm run build`).
  - Subagent 2: Backend compilation, type check, and unit tests (`cargo check --locked -D warnings`, `cargo test`).
  - Subagent 3: IPC command mapping / API bijection audit (`invoke` calls vs registered handlers) and Git tree sanity check.
- **Produce Structured Review Output**: Synthesize the subagents' findings into a concise, ready-to-forward review report for the user to pass back to the external agent.

## 4. Reverse Direction: ZCode Waiting for Hermes
ZCode has NO built-in process-exit wake mechanism (no `notify` hook; `zcode --help` confirms). The equivalent is a **turn-blocking handshake-file poll**: ZCode runs a foreground polling script inside its Bash tool that checks a Windows-native handshake file every second and continues autonomously once Hermes writes it.
- Handshake file path MUST be Windows-native (e.g. `%TEMP%\hermes_handshake.txt`) — git-bash `/tmp` and Python resolve to different directories on Windows; a bash-written `/tmp/file` is invisible to Python's `os.path.exists`.
- Hermes side: after finishing its work, write the handshake file (`open(path,'w').write(msg)`) as the last action; ZCode's poll picks it up on the next 1s tick.
- Caveat: ZCode's blocking poll keeps its session turn active (chat UI shows "working"), and long waits must be split into segments to respect Bash tool timeouts.

## 5. Headless Cross-Agent Probes (`zcode.cjs -p`)
ZCode's runtime lives at `D:/zcode/resources/glm/zcode.cjs`; `node zcode.cjs -p "<prompt>" --cwd <dir>` runs a one-shot headless agent session — use it to have ZCode independently execute probes (curl endpoints, compute checks) for cross-verification.
- **Gateway dependency**: ZCode's main model routes via `cpa-gui` (EasyCLIProxyAPI, port 18080). If that gateway is down, headless runs fail instantly with `ECONNREFUSED 127.0.0.1:18080` — restart EasyCLIProxyAPI.exe first.
- **Quota exhaustion surfaces as APICallError**: Gemini 429s read "All credentials ... are cooling down ... Resets in Xm". When this fires, no ZCode headless work is possible until reset or the user switches ZCode's provider in its Desktop UI (never edit ZCode's `config.json` programmatically).

## 6. Delegation Model Routing & Dynamic Chat Models (User Rule)
`delegate_task` subagents inherit the parent chat model by default. The user deliberately keeps `delegation.provider`/`delegation.model` EMPTY in config.yaml: the user frequently and dynamically switches chat models across local gateways (EasyCLIProxyAPI at 18080, WorkBuddy at 8787) based on current task requirements. Never assume or hardcode a single fixed "primary model". The user will explicitly state when subagents should use a different model. NEVER pin delegation to a fixed model — if the user did not name a model for subagents, subagents run on the current chat model. (For quality-sensitive single tasks, Hermes' kanban per-task model override exists, but respect the user's stated model choice first.)

## 7. Operational Boundaries & Conflict Prevention
- **Producer-Reviewer Separation**: When one agent is editing a codebase, the other agent acts exclusively as reviewer, tester, or CI monitor. Never edit working tree files simultaneously to prevent file lock collisions.
- **Parallel memory-file edits**: both agents may append to the same `shared-agent-memory` files in the same session; git merges handle it, but expect a possible fast-forward push and never force-push.
- **Shared Memory Invariant**: Ground truth facts, architectural decisions, and handoff contracts must be committed to the shared repository (`shared-agent-memory` `main` branch).
- **Skill Directory Physical Isolation, Slimming & Physical Teardown Protocol**: Unlike shared memory (`memories/topics` which is a unified physical store via NTFS junction), the skill directories (`~/.zcode/skills` and `~/.hermes/skills`) are completely independent physical directories. Modifying skills on one agent does NOT propagate to the other.
  - **Two-Stage Slimming & Physical Deletion (User Rule)**:
    1. *Stage 1 (Staged Isolation)*: When pruning candidate skills, temporarily move them out of active `skills/` into staging (`skills-archived/`) to immediately reduce prompt token overhead and verify zero functional regressions.
    2. *Stage 2 (Physical Deletion on User Confirmation)*: Upon user confirmation, **physically delete (`rm -rf`) the archived skill directories** from disk. Never let offline archive directories hoard redundant files locally; open-source and upstream skills can be cleanly re-installed on demand.
    3. *Memory-as-Traceability Invariant*: Record the slimming rationale, pruned category mapping, and superior replacement tools directly in `shared-agent-memory` (`topics/<name>.md` and `topics/MEMORY.md`). The shared memory is the durable audit trail, not obsolete file trees.
  - **Four High-Noise / Inefficient Skill Categories to Prune**:
    1. *Local Crawlers*: Custom scraper scripts (`smart-web-crawler`, `scrapling`) that get blocked by Cloudflare/WAF/proxy TLS timeouts; replace with high-throughput cloud-cleaned `web_search`/`web_extract` (Exa backend).
    2. *Heavy / Unsupported Local MLOps*: Local LLM fine-tuning/inference (`llama-cpp`, `comfyui`, `dspy`, `huggingface-*`, `qdrant`) when local runtimes are disabled or hardware VRAM is constrained (e.g. 8GB laptop); vector retrieval is handled on-demand by OpenViking.
    3. *Uncredentialed SaaS Integrations*: Cloud SaaS suites (`airtable`, `box`, `notion`, `google-workspace`, `teams-meeting-pipeline`, `himalaya`, `1password`) where local API keys/OAuth do not exist, preventing hallucinated tool probes.
    4. *Redundant External Agent Wrappers*: Standalone CLI delegators (`claude-code`, `codex`, `opencode`) when native `delegate_task` parallel subagents or cross-agent watch patterns are the standard.
  - **Unified Dual-Agent Retirement & Cleanup Closure**:
    1. *Dual-End Pruning*: Remove target directories on both Hermes and ZCode, followed by physical cleanup of `skills-archived/`.
    2. *Shared Memory & Index*: Record the slimming/retirement rationale in `topics/<name>.md` and update `topics/MEMORY.md`.
    3. *Dual Commit & Push*: Commit and push `main` on `~/.zcode/cli/memories` (and `hermes` on `~/.hermes` if Hermes profile state changed).
    4. *CI & OpenViking Re-Index*: Confirm GitHub Actions CI passes green, and ensure `sync_shared_memory_openviking.py` synchronizes the new commit.

## 8. Hermes Native Bot Mode & Multi-Profile Orchestration
When orchestrating internal specialized bots (profiles under `~/.hermes/profiles/<name>/`) alongside the default agent:
- **CLI Creation Pattern**: Always use `hermes profile create --clone-from default <name> --description "<role description>"` to inherit current gateway endpoints, `.env` API keys, and essential baseline configurations.
- **Shared Memory Junction (CRITICAL)**: Newly created profiles instantiate an isolated `memories/` directory. To prevent memory fragmentation and state divergence, immediately establish an NTFS Directory Junction pointing `memories/topics` directly to the shared memory single physical source of truth:
  ```cmd
  cmd.exe /c "mklink /J C:\Users\VOS-User\AppData\Local\hermes\profiles\<name>\memories\topics C:\Users\VOS-User\.zcode\cli\memories\projects\default-135ef1b9f66d8a7e\memory"
  ```
- **Specialized SOUL.md Contracts**: Replace the default prompt in `profiles/<name>/SOUL.md` with explicit role boundaries: Identity, Mandates & Rules, Cross-Bot Handoffs (@mentions / Agent Inbox protocols), and Shared Memory Protocols.
- **In-Session Handoffs**: Use `@<bot-name>` in conversation turns for synchronous task handoffs, or rely on Agent Inbox for asynchronous batch deliveries.

## 9. Windows MCP Process Tree, Lazy Startup & Orphan Teardown Invariant
In Windows, Agent GUIs (Hermes Desktop / ZCode) spawn stdio MCP servers through deep process trees:
`Agent GUI -> cmd.exe -> npx/uvx -> node.exe / serena.exe`.
Because Windows does not cascade process termination to grandchildren upon GUI window close without an explicit Windows Job Object, grandchildren become orphaned background zombies (CPU 0%, but holding 300MB~500MB RAM across multiple restarts).

### Dual-Tier Defense Architecture
1. **Tier 1: Hermes Native On-Demand Lazy Connect & Idle Recycle (In-App Hygiene)**:
   Never run heavy stdio MCP servers in persistent eager mode. In Hermes `config.yaml` (`mcp_servers.<name>`), configure:
   - `lazy: true`: Enables cold-on-demand start. Hermes registers tools at startup from its local schema cache (`cache/mcp_schema_cache.json`) with **zero subprocesses spawned** (0 Node, 0 Serena, 0 Python), achieving instant boot and zero idle RAM. The process is spawned only on the first actual tool call.
   - `idle_timeout_seconds: 60`: If no tool calls occur for 60 seconds, Hermes automatically triggers a clean `recycle`, terminating the stdio subprocess and freeing all memory/handles until the next call.
2. **Tier 2: System-Level Targeted Whitelist Reaper & Agent Guard (Exit Failsafe)**:
   When cleaning up or automating post-exit shutdown, never blindly `taskkill /IM node.exe` (which kills user web servers, Vite, Next.js). Target exclusively verified MCP signatures:
   - Node MCPs: `commandline` matching `chrome-devtools-mcp`, `desktop-commander`, `context7-mcp`.
   - Python MCPs: `serena.exe` and `cmdline` containing `serena`.
   - Implementation: canonical safe reaper at `C:/Users/VOS-User/AppData/Local/hermes/scripts/cleanup_agent_orphans.py`, orchestrated by background daemon `C:/Users/VOS-User/AppData/Local/hermes/scripts/agent_guard.py` (2.5s debounce after all Agent GUIs close).
- **OpenViking Automated Demand-Wake & Zero-Focus-Steal Invariant**:
  - OpenViking is the shared dual-agent memory service, completely decoupled from OS auto-start (`Startup/OpenVikingGateway.vbs` removed) and free of desktop shortcut clutter.
  - **Native GUI PATH Shim**: Hermes' OpenViking plugin runs `shutil.which("openviking-server")` on 1933 connection drops. A compiled Go binary with `-H=windowsgui` PE subsystem header at `C:/Users/VOS-User/.openviking/shim-bin/openviking-server.exe` (placed first on User PATH) intercepts the call and transparently boots the full lazy-gateway stack without spawning `cmd.exe` or flashing console windows.
  - **Zero Console-Allocation / Zero Focus-Steal (CRITICAL)**: In background supervisor or auto-sleep routines running under `pythonw.exe` (such as `openviking_lazy_gateway.py` or `agent_guard.py`), NEVER invoke console executables (`netstat.exe`, `taskkill.exe`) without `CREATE_NO_WINDOW = 0x08000000`. On Windows, running console apps from a windowless process forces the OS to allocate a transient `conhost.exe` host window; even a 10ms transient console creation steals foreground input focus, disrupting active typing and destroying uncommitted IME candidate buffers. Always terminate processes via native `psutil` (`proc.kill()` / Win32 `TerminateProcess`) and query ports via `psutil.net_connections()`.
  - **Tri-phase Lifecycle**: Demand-wake on first memory access -> 2-minute idle auto-sleep (100% VRAM release) -> automatic termination upon Agent GUI close via `agent_guard`.

## 10. Native Tool Prioritization & Tool Call Efficiency (User Rule)
The user strictly enforces tool execution efficiency and minimal round-trip overhead:
- **Direct Native Tools First**: Always use specialized Hermes native tools directly:
  - File reading: `read_file` (built-in line numbers & pagination; never `python open().read()`).
  - Targeted edits: `patch` (fuzzy matching, AST validation, unified diffs; never full-file python rewrites that destroy indentation/formatting).
  - Search & inspection: `search_files` (ripgrep-backed content/filename search; never custom `python os.walk`).
- **Python Invocation Boundary**: Reserve `python -c` or execution scripts strictly for complex multi-step batch logic that genuinely requires code execution (e.g. process tree auditing, cryptographic/Wbi signing algorithms, SQLite database analysis, cross-store reconciliation).
- **config.yaml Security Exception**: Hermes core prevents `patch`/`write_file` edits on its own `config.yaml` as a security-sensitive guard. For this file specifically, use `python` with `ruamel.yaml` (`preserve_quotes=True`) to maintain structural fidelity without clobbering formatting.
- **ZCode config.json Schema Guard**: Whenever editing ZCode's `config.json` (such as modifying `plugins.enabledPlugins`), ALWAYS run `node "D:/zcode/resources/glm/zcode.cjs" plugins list --json` immediately afterwards to verify schema compliance and prevent silent configuration drop.

## 11. Real-Browser Automation Boundary & Edge Profile Protection Invariant
- **Strictly Omit `--user-data-dir` (The Cold-Launch Trap)**: Previously, `--user-data-dir` was mistakenly supplied to `chrome-devtools-mcp` under the assumption of seamless extension profile reuse. In reality, triggering the MCP while Edge Dev is closed forces Chromium to cold-launch in headless/automation mode without loading regular extensions; exiting writes an empty registry back to `Secure Preferences`, causing Chromium's internal `ExtensionGarbageCollector` on subsequent starts to classify installed extension folders as orphans and **physically delete extension binaries from disk**. In `config.yaml`, **strictly omit `--user-data-dir`** and pass only `--autoConnect` (plus `--ignore-default-chrome-arg=--disable-extensions`).
- **Prune Built-in Browser Automation**: Native Hermes `browser` toolset (`browser_*`) cannot drive user profile extensions. Explicitly disable the \"Browser Automation\" toolset in the Hermes Desktop settings (`platform_toolsets.cli` removes `browser`) whenever dedicated search backends (e.g. Exa) are active to eliminate accidental profile stamping by background agents.
- **autoConnect Prerequisite**: The `--autoConnect` flag attaches to an **already-running** Edge Dev browser (version 144+) with remote debugging enabled (`edge://inspect/#remote-debugging`). If Edge is closed, the MCP must fail fast and wait for the user to launch it, never autonomously spinning up headless background instances.
- **Instant Decoupled Extension Recovery**: Extension code and data are decoupled. User scripts and configurations reside safely in `Default/Local Extension Settings/<id>` (unaffected by garbage collection). Re-installing the extension from Microsoft Edge Add-ons (or loading unpacked extensions with pinned `key` attributes) instantly rebinds the existing local database, achieving 100% in-place recovery without re-importing scripts.

## 12. Session Archive & Teardown Protocol (User Rule)
When the user issues a directive to delete or archive the active session, or when session consumption approaches the reset threshold (≥1M tokens):
1. **Curate High-Value Knowledge & Dual-Store Sync**:
   - Extract all critical technical decisions, verified failure root causes, configuration baseline changes, and debugging invariants discovered during the turn.
   - Commit operational facts and cross-agent invariants to the shared repository (`shared-agent-memory`, `main` branch).
   - Author or update applicable domain articles, system guides, or hardware knowledge in the `youshouldknow` (YSK) documentation repository.
2. **Physical Teardown of Ephemeral Session Artifacts**:
   - Perform an exhaustive scan of the workspace, temporary directories (`%LOCALAPPDATA%\\Temp`), and repository trees.
   - Physically delete all ephemeral test scripts (e.g. temporary `.py`, `.cjs`, `.sh` probes), scratch output logs, and transient scraper outputs generated during the conversation. Zero untracked diagnostic clutter must remain on disk.
3. **Automated Remote Push & Continuous CI Confirmation**:
   - Stage and commit all persistent knowledge updates, pushing to their authoritative remote branches (`main` for shared repositories, `hermes` for profile-local state).
   - Actively monitor and poll remote GitHub Actions workflows (`gh run watch` / `gh run list`) until 100% green (Success ✓) before completing the turn. Never conclude an archive request without remote CI verification.

## 13. Dual-Agent Workspace Alignment & Cross-Repo Lock Invariants

### Desktop Workspace Alignment (`D:\ai coding`)
When aligning workspace boundaries between Hermes Desktop and ZCode:
- **Root Anchor**: ZCode's default workspace directory is anchored to `D:\ai coding` (with `dataBaseDir` and internal spaces residing within).
- **Hermes Desktop Project Tool**: Anchor the active Hermes session to the same root via `desktop_project(action='create', name='ai coding', path='D:/ai coding')` (or `switch`). This aligns the desktop sidebar file-tree without manual path hopping.
- **Persistent Shortcut WorkingDir**: On Windows, update the desktop shortcut `C:\Users\VOS-User\Desktop\Hermes Agent.lnk` with `WorkingDirectory = 'D:\ai coding'` via `WScript.Shell`. This ensures fresh GUI launches default directly to the shared coding root.

### Cross-Repo Knowledge Lock Invariant (`tweakbyjie` <-> `youshouldknow`)
When maintaining interdependent repositories where one locks the documentation commit of the other (e.g. `tweakbyjie/tools/knowledge.lock.json` tracking `youshouldknow`):
- **Exact 40-Hex Commit SHA**: Always retrieve the commit SHA programmatically using `git -C <path> rev-parse HEAD` or `gh api repos/<owner>/<repo>/commits/main --jq .sha`.
- **Zero-Splicing / Zero-Truncation**: Never hand-type or splice truncated SHAs into lock files. Audit scripts (e.g. `Test-CrossRepoCoverage.ps1`) construct direct Raw GitHub URLs (`raw.githubusercontent.com/.../<ref>/...`); a malformed or non-existent commit SHA immediately fails with HTTP 404, blocking Coverage and CI pipelines.
- **Push Order Constraint**: Always commit and push the knowledge documentation repository first, verify the commit exists on remote `main`, update the downstream lock file, run local cross-repo coverage and test suites (`Invoke-Pester`), and only then push the downstream repository.

