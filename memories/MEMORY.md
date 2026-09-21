Model: gemini-3.8-flash via EasyCLIProxyAPI (18080, provider=cpa) -> Antigravity (2 accts, priority 10 round-robin + 1h sticky). auxiliary.* stays `auto` — never change. Current chat may be switched mid-session (workbuddy2api 8787); read runtime metadata, never assume.
§
gh acct 3304711297. Edge Dev + chrome-devtools MCP (connect-only) + deepwiki MCP.
§
WorkBuddy2API (原 codebuddy2openai；仓库+工作区已改名) = 本地反代 127.0.0.1:8787/v1，OpenAI+Anthropic 双协议；Tauri v2 控制台（多账号/调度策略/积分），调度策略热读 settings.json 免重启。
§
Hardware: RTX 4070 Laptop 8GB + 24GB; models/runtime junctioned to D:. D:\HermesModels: MiniCPM5-2B (fast) + Qwen3.8-9B-Distill (quality) chat. Desktop-managed runtime: models auto-discovered by dir scan; spec-decode drafts/mmproj must live in models\assets\ and be prefixed `dspark-`/`mmproj`; presets.ini is auto-generated (never hand-edit); context window floor is 64K and overrides only grow. 8GB VRAM is the scarce resource — keep background GPU consumers off (OpenViking retired 09-21 for this reason).
§
Memory (single source of truth): built-in MEMORY.md/USER.md inject in full every turn; the Git shared lib `shared-agent-memory` (memories/topics junction) holds long-form facts and gets grepped via search_files. NO second memory store — OpenViking retired 2026-09-21 (VRAM cost + dual-store overhead). Near the char cap: SUBTRACT, never raise the cap. CJK costs 1.10x on Gemini's tokenizer vs 1.34x o200k (cap counts chars).
§
PS scenarios -> pwsh -NoProfile (Store alias, version-independent) + [Console]::OutputEncoding=UTF8 for CJK;
§
Style: ext-AI cross-review -> P0/P1/P2 spec; fixed scope, no opportunistic refactors. Local-First: full CI-equivalent + Release build locally, then push; never block main session on CI. Config change: list candidates + defaults + cost, wait for the call. reasoning_effort=ultra stays (global default).
§
Pitfalls: Desktop "session won't run" freeze = model switch injecting a user-role system msg + truncated retry rejected by gateway (upstream #94486); restart won't self-heal — SOP in shared lib topics/hermes-desktop-rewind-deadlock.md.
§
ZCode 退役 09-09；仅存 zcode-api proxy 促销 token 关系。
§
Hermes 工具三坑（本机复现）: ① search_files pattern 反斜杠被转成 /（\( → /( 、\d → /d）→静默 0 命中，改用字符类 [(] / [0-9]；上游已报 #92260，修复 PR #92267（唯一能打在 main 上的）；② read_file 重复读同一文件返回 {status:unchanged}/{error,already_read} 无 content 键，循环取值必须 .get('content')；③ execute_code 的 Python 是原生 Windows，subprocess 调 grep/rg 必 FileNotFoundError，用 terminal 工具或纯 pathlib。
§
workbuddy2api 构建由用户自己跑 `npm run tauri build`（PowerShell @ 仓库根）；我只说「可以构建了」，不自行琢磨隔离目录/替换脚本等绕行方案。
§
Hermes 工具输出预算（源码级 09-19 实证）：层1 `tool_output.max_bytes`（默认50000/本机8000）只管 terminal，溢出 tee 到 `cache/terminal-output/`（153文件，完整可读）；层2 落盘 `cache/spillover/`（0文件，从未触发）。`read_file` 被 PINNED 为 inf（budget_config.py:9-10，防 persist→read→persist 死循环），单次注入~100K字符，两预算均够不着——**设计非bug**，修复须按路径豁免而非降阈值。#106399 tool_overrides 仍 OPEN 未入 main，写配置不生效须实测；#86401 已发实证评论（其 terminal 部分已过时）。
§
共享记忆真源（GitRepos/shared-agent-memory）必须常驻 main：checkout hermes 会让 projects/ 消失、memories/topics junction 断链，而 git status 仍干净（静默故障）。自检 `python scripts/check_memory_layout.py`（真源/home 各一份，须同源）。
§
自研项目本地工作区在 D:\ai coding\GitRepos\<name>（如 tweakbyjie），分析/改码前先查本地工作区，勿直接克隆 GitHub。
§
ComfyUI portable 在 D:\ai coding\ComfyUI（双击 run_nvidia_gpu.bat，服务 127.0.0.1:8188）。Qwen-Image-2.1 用本地合并的 bf16 单文件（transformer 14.2G + TE 17.5G 由 HF 分片字节级合并，VAE 走官方 repack），8GB 显存靠 offload 跑 2.8s/it。启动/模板本地化/示例图补齐流程见 comfyui v5.2 技能。