Model: gemini-3.8-flash via EasyCLIProxyAPI (18080, provider=cpa-gui) -> Antigravity (2 accts, priority 10 round-robin + 1h sticky). auxiliary.* stays `auto` — never change.
§
Windows: Karing proxy 127.0.0.1:3067 (UI 1666). 3067 listens only with an outbound node up — no listener = no route; check node first when push hangs. Bare push: `env -u ALL_PROXY -u HTTP_PROXY -u HTTPS_PROXY`. gh acct 3304711297. Edge Dev + chrome-devtools MCP; NO_PROXY/CDP quirks -> OpenViking.
§
WorkBuddy2API (原 codebuddy2openai；仓库+工作区已改名) = 本地反代 127.0.0.1:8787/v1，OpenAI+Anthropic 双协议；Tauri v2 控制台（多账号/调度策略/积分），调度策略热读 settings.json 免重启。Ops -> OpenViking。
§
Hardware: RTX 4070 Laptop 8GB + 24GB; models/runtime junctioned to D:. D:\HermesModels: bge-m3=OV embedding(18082), MiniCPM5-2B + Qwen3.5-9B chat. OpenViking venv on-demand, sleeps 2min idle. MCP: chrome-devtools (--autoConnect, connect-only) + deepwiki.
§
Memory: provider=openviking is ADDITIVE — built-in MEMORY.md/USER.md (3000/2000 chars) still inject in full every turn; low-freq -> viking_remember, built-in keeps high-frequency only. Near limit: SUBTRACT, never raise the cap. CJK costs 1.10x on Gemini's tokenizer vs 1.34x o200k (cap counts chars).
§
PS scenarios -> pwsh -NoProfile (Store alias, version-independent) + [Console]::OutputEncoding=UTF8 for CJK;
§
Style: ext-AI cross-review -> P0/P1/P2 spec; fixed scope, no opportunistic refactors. Local-First: full CI-equivalent + Release build locally, then push; never block main session on CI. Config change: list candidates + defaults + cost, wait for the call. reasoning_effort=ultra stays (global default).
§
Lookup-Before-Build (先检索再造轮子, 09-13 拍板): before hand-rolling ANY parser/signature/scraper/protocol adapter/boilerplate, search first — skills pool -> official docs -> mature OSS source. Stop-and-search: 3 param combos already failed, tuning from hearsay not docs, >50 lines of glue, or can't state the official semantics of the error code you're fighting. Hand-rolling's real cost is direction cost; say "searched X/Y/Z, none exists" before writing your own. Case: bilibili -352 risk control unsolvable by param tuning — one search gave "change egress IP or endpoint".
§
Pitfalls: Desktop "session won't run" freeze = model switch injecting a user-role system msg + truncated retry rejected by gateway (upstream #94486); restart won't self-heal — SOP in shared lib topics/hermes-desktop-rewind-deadlock.md.
§
ZCode decommissioned 09-09: sessions in shared-agent-sessions zcode branch; only tie = promo tokens via zcode-api proxy.
§
OpenViking writes (viking_remember/add_resource/etc) -> SAME-TURN run D:\openviking-backup\sync.cmd (private repo 3304711297/openviking-backup), regardless of topic. Large-shrink guard aborts exit 2 leaving backup untouched; rerun with OV_BACKUP_FORCE=1 only if the shrink is intentional.