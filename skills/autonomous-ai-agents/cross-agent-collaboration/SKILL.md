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

## 3. Takeover & Parallel Execution

Upon being awakened by the handoff signal:
- **Mandatory Proactive Fan-out**: The user strictly enforces parallel execution for all multi-step verifications and audits. Immediately dispatch parallel subagents via `delegate_task` (batch 3~6, up to 10 concurrent workers) rather than executing sequentially. Never execute verification steps one-by-one in the foreground. Typical verification split:
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

## 6. Delegation Model Routing (User Rule)
`delegate_task` subagents inherit the parent chat model by default. The user deliberately keeps `delegation.provider`/`delegation.model` EMPTY in config.yaml: they may switch the chat model at any time and will explicitly state when subagents should use a different model. NEVER pin delegation to a fixed model — if the user did not name a model for subagents, subagents run on the current chat model. (For quality-sensitive single tasks, Hermes' kanban per-task model override exists, but respect the user's stated model choice first.)

## 7. Operational Boundaries & Conflict Prevention
- **Producer-Reviewer Separation**: When one agent is editing a codebase, the other agent acts exclusively as reviewer, tester, or CI monitor. Never edit working tree files simultaneously to prevent file lock collisions.
- **Parallel memory-file edits**: both agents may append to the same `shared-agent-memory` files in the same session; git merges handle it, but expect a possible fast-forward push and never force-push.
- **Shared Memory Invariant**: Ground truth facts, architectural decisions, and handoff contracts must be committed to the shared repository (`shared-agent-memory` `main` branch).
