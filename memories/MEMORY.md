Model: gemini-3.8-flash via EasyCLIProxyAPI (18080, provider=cpa-gui) -> Antigravity (2 accts, priority 10 round-robin + 1h sticky). auxiliary.* stays `auto` — never change.
§
Windows: Karing proxy 127.0.0.1:3067 (Karing itself 1666). 3067 listens only with an outbound node up; no listener = no route, check node first when push hangs. Bare push: `env -u ALL_PROXY -u HTTP_PROXY -u HTTPS_PROXY`. PyPI CDN = files.pythonhosted.org. gh acct 3304711297. Browser Edge Dev + chrome-devtools MCP. NO_PROXY list & Edge Dev CDP quirk -> OpenViking.
§
WorkBuddy = codebuddy2openai reverse proxy 127.0.0.1:8787/v1 (Tauri v2: multi-acct, credits, tray, Hermes write). Ops detail -> OpenViking.
§
Hardware: RTX 4070 Laptop 8GB + 24GB; models/runtime junctioned to D:. D:\HermesModels: bge-m3=OV embedding(18082), MiniCPM5-2B + Qwen3.5-9B chat. OpenViking venv on-demand, sleeps 2min idle. MCP: chrome-devtools (--autoConnect, connect-only) + deepwiki.
§
Memory: provider=openviking is ADDITIVE — built-in MEMORY.md/USER.md (3000/2000 chars) still inject in full every turn; low-freq -> viking_remember, built-in keeps high-frequency only. Near limit: SUBTRACT, never raise the cap. CJK costs 1.10x on Gemini's tokenizer vs 1.34x o200k (cap counts chars).
§
Tools: pure-read tools may batch concurrently; terminal/patch/write_file/memory/delegate_task are sequential barriers — never claim they ran in parallel. config.yaml needs no restart. PS5.1 .ps1/.cmd with CJK need BOM else mojibake; bash swallows $_/$var in inline powershell -Command, use .ps1. vision_analyze first call may fail, retry once.
§
Style: external-AI cross-review -> P0/P1/P2 spec; fixed scope, no opportunistic refactors. Local-First: full CI-equivalent + Release build locally, then push; never block the main session on CI. Config change: list candidates + defaults + cost, wait for the call. User keeps reasoning_effort=ultra (global default) — not a candidate for optimization.
§
serena removed; "(std v1beta 404s)" -> OpenViking.
§
Pitfalls: Desktop "session won't run" freeze = model switch injecting a user-role system msg + truncated retry rejected by gateway (upstream #94486); restart won't self-heal — SOP in shared lib topics/hermes-desktop-rewind-deadlock.md. Repo-local website/i18n/zh-Hans translations lag source (curator.md vs tools/skill_usage.py created_by=agent + adopt/ledger) — read source for behavior/defaults, never the translation.
§
ZCode decommissioned 09-09: client/config/sessions wiped; shared lib = D:/ai coding/GitRepos/shared-agent-memory; sessions in shared-agent-sessions zcode branch; only tie = promo tokens via zcode-api proxy.
§
OpenViking writes (viking_remember/add_resource/etc) -> SAME-TURN run D:\openviking-backup\sync.cmd (private repo 3304711297/openviking-backup), regardless of topic. Large-shrink guard aborts exit 2 leaving backup untouched; rerun with OV_BACKUP_FORCE=1 only if the shrink is intentional.