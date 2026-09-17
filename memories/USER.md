Hermes is the SOLE primary agent (ZCode decommissioned 09-09; promo-token reverse proxy only). Shared lib shared-agent-memory (3304711297/shared-agent-memory): main = truth; sanitize before writing (no machine usernames or raw profile paths — use %USERPROFILE%/%LOCALAPPDATA%; redact credentials); push main that turn, Hermes-only -> `hermes` branch.
§
never substitute model intuition.
§
— no verbal promise then sleeping; wake on process exit.
§
Fork-First: several independent asks -> dispatch parallel subagents first (3-6/batch, max 10), never serially. Never edit user's workspace source while they build.
§
Scraping: stop and ask at 2 anti-bot hits; never exhaust mirrors/new browser; login-gated needs consent.
§
Browser assets: compare extension count (Default\Extensions, baseline 10) before/after; close only via CloseMainWindow, never Stop-Process -Force.
§
Tool efficiency: read_file to read (offset/limit pages, next_offset past ~100K), patch for small edits (never full-file python rewrites), search_files to search or list dirs; terminal never cat/head/tail/grep/rg/find/ls; 3+ filtered calls collapse into one execute_code; CLI-only @file:L1-L2/@folder/@diff.
§
UI (09-08): micro-interaction, in-desktop embedding, dark geek-IDE aesthetic; 3+ step work -> native todo_list board, never a plain markdown list.
§
Skill-watchdog: skill install/upgrade/prune/rejection syncs capability-inventory.json + pushes main for CI that turn; new-skill eval runs 5-step SOP.
§
CI & notifications: on all-green completion, DELETE /notifications/threads/{id} to mark related notifications Done.
§
构建/部署 gui 应用（workbuddy2api 等 Tauri 桌面端）：**用户自己构建**，用 `npm run tauri build`（在仓库根的 PowerShell 里跑）。我不得自行琢磨"如何在不影响会话的情况下构建"，也不要搬文件到隔离目录或写替换脚本——会把会话链路搞断或产出空壳。**改完代码只需告知一声"可以构建了"，用户自己来。**
§
踩坑沉淀：遇到工具报错/平台拦截/参数暗坑，严禁以内存紧张为由推脱不记；区分全局记忆与技能，主动归位并 patch 沉淀到对应 skill（平台工具规则进 hermes-agent），禁等用户催促。