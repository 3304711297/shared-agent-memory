Model: gemini-3.8-flash via EasyCLIProxyAPI (18080, provider=cpa-gui) -> Antigravity (2 accts, priority 10 round-robin + 1h sticky). auxiliary.* stays `auto` — never change.
§
Windows: Karing proxy 127.0.0.1:3067 (Karing itself 1666). 3067 listens only with an outbound node up; no listener = no route, check node first when push hangs. Bare push: `env -u ALL_PROXY -u HTTP_PROXY -u HTTPS_PROXY`. PyPI CDN = files.pythonhosted.org. gh acct 3304711297. Browser Edge Dev + chrome-devtools MCP. NO_PROXY list & Edge Dev CDP quirk -> OpenViking.
§
WorkBuddy = codebuddy2openai reverse proxy 127.0.0.1:8787/v1 (Tauri v2: multi-acct, credits, tray, Hermes write). Ops detail -> OpenViking.
§
Hardware: RTX 4070 Laptop 8GB + 24GB; models/runtime junctioned to D:. OpenViking venv on-demand, sleeps 2min idle. MCP: chrome-devtools (--autoConnect, connect-only) + deepwiki.
§
Retrieval = Exa only (EXA_API_KEY in .env). EasyCLIProxyAPI `gemini-web-search` is an alias with no live search — unusable.
§
Memory (09-07): provider=openviking is ADDITIVE, not a replacement — built-in MEMORY.md/USER.md (3000/2000 CHARS) still inject in full every turn. Low-frequency facts -> viking_remember; built-in keeps high-frequency only. Near limit: SUBTRACT, never raise the cap. 09-09: rewritten to English (1525->~820 tok) since CJK costs ~1.34x tokens per meaning while the cap counts chars.
§
Tools: only pure-read tools (read_file/search_files/web_search/web_extract/skill_view/skills_list/session_search/vision_analyze) may go concurrently; terminal/patch/write_file/memory/delegate_task are sequential barriers, one at a time (shared persistent shell by design). Never call batched terminal calls "parallel" in thinking/reports/summaries — false claim, as serious as fake execution. config.yaml needs no restart (re-read at spawn).
§
Style: external-AI cross-review -> P0/P1/P2 spec; fixed scope, no opportunistic refactors. Local-First: full CI-equivalent + Release build locally, then push; never block the main session on CI. Config change: list candidates + defaults + cost, wait for the call.
§
Background loops off (09-07): nudge_interval=0 + creation_nudge_interval=0 + background_review.enabled=false (triple, anti-fail-open). Foreground memory/OpenViking//refine unaffected. serena & cliproxyapi off the capability-inventory watchlist; serena purged.
§
Pitfalls: Desktop "session won't run" freeze = model switch injecting a user-role system msg + truncated retry rejected by gateway (upstream #94486); restart won't self-heal — SOP in shared lib topics/hermes-desktop-rewind-deadlock.md. Repo-local website/i18n/zh-Hans translations lag source (curator.md vs tools/skill_usage.py created_by=agent + adopt/ledger) — read source for behavior/defaults, never the translation.
