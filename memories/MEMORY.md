Model: gemini-3.8-flash via EasyCLIProxyAPI (18080, provider=cpa-gui) -> Antigravity (2 accts, priority 10 round-robin + 1h sticky). auxiliary.* stays `auto` — never change.
§
Windows: Karing proxy 127.0.0.1:3067 (UI 1666). 3067 listens only with an outbound node up — no listener = no route; check node first when push hangs. Bare push: `env -u ALL_PROXY -u HTTP_PROXY -u HTTPS_PROXY`. gh acct 3304711297. Edge Dev + chrome-devtools MCP; NO_PROXY/CDP quirks -> OpenViking.
§
WorkBuddy2API (原 codebuddy2openai；仓库+工作区已改名) = 本地反代 127.0.0.1:8787/v1，OpenAI+Anthropic 双协议；Tauri v2 控制台（多账号/调度策略/积分），调度策略热读 settings.json 免重启。Ops -> OpenViking。
§
Hardware: RTX 4070 Laptop 8GB + 24GB; models/runtime junctioned to D:. D:\HermesModels: bge-m3=OV embedding(18082), MiniCPM5-2B + Qwen3.5-9B chat. OpenViking venv on-demand, sleeps 2min idle. MCP: chrome-devtools (--autoConnect, connect-only) + deepwiki.
§
Memory: provider=openviking is ADDITIVE — built-in MEMORY.md/USER.md (4000/3000 chars) still inject in full every turn; low-freq -> viking_remember, built-in keeps high-frequency only. Near limit: SUBTRACT, never raise the cap. CJK costs 1.10x on Gemini's tokenizer vs 1.34x o200k (cap counts chars).
§
PS scenarios -> pwsh -NoProfile (Store alias, version-independent) + [Console]::OutputEncoding=UTF8 for CJK;
§
Style: ext-AI cross-review -> P0/P1/P2 spec; fixed scope, no opportunistic refactors. Local-First: full CI-equivalent + Release build locally, then push; never block main session on CI. Config change: list candidates + defaults + cost, wait for the call. reasoning_effort=ultra stays (global default).
§
Pitfalls: Desktop "session won't run" freeze = model switch injecting a user-role system msg + truncated retry rejected by gateway (upstream #94486); restart won't self-heal — SOP in shared lib topics/hermes-desktop-rewind-deadlock.md.
§
ZCode 退役 09-09；仅存 zcode-api proxy 促销 token 关系。
§
OpenViking writes (viking_remember/add_resource/etc) -> SAME-TURN run D:\openviking-backup\sync.cmd (private repo 3304711297/openviking-backup), regardless of topic. Large-shrink guard aborts exit 2 leaving backup untouched; rerun with OV_BACKUP_FORCE=1 only if the shrink is intentional.
§
Hermes 工具三坑（本机复现）: ① search_files pattern 反斜杠被转成 /（\( → /( 、\d → /d）→静默 0 命中，改用字符类 [(] / [0-9]；上游已报 #92260，修复 PR #92267（唯一能打在 main 上的）；② read_file 重复读同一文件返回 {status:unchanged}/{error,already_read} 无 content 键，循环取值必须 .get('content')；③ execute_code 的 Python 是原生 Windows，subprocess 调 grep/rg 必 FileNotFoundError，用 terminal 工具或纯 pathlib。
§
workbuddy2api 构建由用户自己跑 `npm run tauri build`（PowerShell @ 仓库根）；我只说「可以构建了」，不自行琢磨隔离目录/替换脚本等绕行方案。
§
Hermes 工具输出预算（源码级 09-19 实证）：层1 `tool_output.max_bytes`（默认50000/本机8000）只管 terminal，溢出 tee 到 `cache/terminal-output/`（153文件，完整可读）；层2 落盘 `cache/spillover/`（0文件，从未触发）。`read_file` 被 PINNED 为 inf（budget_config.py:9-10，防 persist→read→persist 死循环），单次注入~100K字符，两预算均够不着——**设计非bug**，修复须按路径豁免而非降阈值。#106399 tool_overrides 仍 OPEN 未入 main，写配置不生效须实测；#86401 已发实证评论（其 terminal 部分已过时）。