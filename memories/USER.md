Communicate in Chinese by default. Primary agent Hermes (ZCode backup). Shared lib shared-agent-memory (3304711297/shared-agent-memory): main = dual-end truth; sanitize before writing (no machine usernames or raw profile paths — use %USERPROFILE%/%LOCALAPPDATA%; redact credentials); push main that turn, Hermes-only -> `hermes` branch.
§
Skill-First gate: before any edit or command on feature work, bug fix, review, refactor, architecture or 3+ step task, check for a matching skill; if hit, skill_view and follow it exactly — never substitute model intuition (classic fail: hand-rolled sleep poll instead of `gh pr checks --watch`).
§
Cross-agent handoff: waiting on ZCode/external long runners requires backgrounding `watch_zcode.py(notify=True)` — no verbal promise then sleeping; wake on process exit.
§
Fork-First: several independent asks -> dispatch parallel subagents first (3-6/batch, max 10), never serially. Never edit user's workspace source while they build.
§
Scraping: 2 consecutive anti-bot hits -> stop and ask; never exhaust mirrors or launch a new browser. Login-gated content needs explicit consent.
§
Browser assets: compare extension count (Default\Extensions, baseline 10) before/after; close only via CloseMainWindow, never Stop-Process -Force.
§
Tool efficiency: read_file to read, patch for small edits (never full-file python rewrites), search_files to search or list dirs. Python only for logic-heavy batch work (process-tree audit, cross-store merge, signing, SQLite).
§
UI (09-08): micro-interaction, in-desktop embedding, dark geek-IDE aesthetic; 3+ step work -> native todo_list board, never a plain markdown list.
§
Skill-watchdog sync: any skill install/upgrade/prune/rejection syncs capability-inventory.json and pushes main for CI that turn. New-skill eval runs the 5-step SOP; pruned skills deleted. Find tools via Edge Dev 9k+ bookmarks.
§
CI & notifications: on all-green completion, DELETE /notifications/threads/{id} to mark related notifications Done.
