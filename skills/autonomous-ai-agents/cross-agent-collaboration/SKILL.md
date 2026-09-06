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
- **Mandatory Proactive Fan-out (Anti-Serialization Rule)**: The user strictly enforces parallel execution for all multi-step tasks, verifications, and multi-repo fixes. Immediately group independent tasks by domain/repository and dispatch parallel subagents via `delegate_task` (batch 3~6, up to 10 concurrent workers).
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
- **Skill Directory Physical Isolation & Unified Retirement Protocol**: Unlike shared memory (`memories/topics` which is a unified physical store via NTFS junction), the skill directories (`~/.zcode/skills` and `~/.hermes/skills`) are completely independent physical directories. Uninstalling or cleaning skills on one agent (e.g. `hermes skills uninstall`) does NOT propagate to the other. When deprecating or retiring a skill across agents, execute this mandatory 7-step closure:
  1. *Hermes Uninstall*: Run `hermes skills uninstall --yes <name>` to clean profile registration and lock files.
  2. *ZCode Cleanup*: Physically remove directory `rm -rf C:/Users/VOS-User/.zcode/skills/<name>`.
  3. *Sync Documentation*: Update `hermes-to-zcode-capability-sync.md` in shared memory with retirement rationale and updated count.
  4. *Watcher Inventory*: Update `capability-inventory.json` (decrement skill replica counts under `hermes-hub-skills`).
  5. *Local Smoke Test*: Run `python C:/Users/VOS-User/.zcode/cli/memories/scripts/check_capability_upstream.py` to ensure 0 outdated / 0 drift.
  6. *Dual-Branch Commit & Push*: Commit and push `main` on `~/.zcode/cli/memories` and `hermes` on `~/.hermes`.
  7. *CI & Memory Re-Index*: Watch GitHub Actions (`Capability Upstream Watch` / `Plugin Upstream Watcher`) until 100% green, then trigger `sync_shared_memory_openviking.py`.

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
   - `idle_timeout_seconds: 180` (or 300): If no tool calls occur for the duration, Hermes automatically triggers a clean `recycle`, terminating the stdio subprocess and freeing all memory/handles until the next call.
2. **Tier 2: System-Level Targeted Whitelist Reaper & Agent Guard (Exit Failsafe)**:
   When cleaning up or automating post-exit shutdown, never blindly `taskkill /IM node.exe` (which kills user web servers, Vite, Next.js). Target exclusively verified MCP signatures:
   - Node MCPs: `commandline` matching `chrome-devtools-mcp`, `desktop-commander`, `context7-mcp`.
   - Python MCPs: `serena.exe` and `cmdline` containing `serena`.
   - Implementation: canonical safe reaper at `C:/Users/VOS-User/AppData/Local/hermes/scripts/cleanup_agent_orphans.py`, orchestrated by background daemon `C:/Users/VOS-User/AppData/Local/hermes/scripts/agent_guard.py` (2.5s debounce after all Agent GUIs close).
- **OpenViking Service Decoupling**: OpenViking is the shared dual-agent memory service, decoupled from OS auto-start (per user preference: on-demand via `openviking_service.py` or Desktop shortcuts `启动 OpenViking.lnk` / `停止 OpenViking.lnk`). Never couple its lifecycle to a single agent's startup.

