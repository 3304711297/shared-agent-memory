Model routing: never hardcode a model name. Live model = session header (Model/Provider); persistent default = $HERMES_HOME/config.yaml 'model:' (default/provider/base_url). 'providers:' entries (cpa 127.0.0.1:18080, openrouter) are candidates only — verify the endpoint is listening before treating one as active. auxiliary.* stays 'auto' — never change.
§
gh account: 3304711297. Edge Dev + chrome-devtools MCP (connect-only) + deepwiki MCP.
§
WorkBuddy2API (repo/workspace at D:\ai coding\GitRepos\workbuddy2api): Local reverse proxy on 127.0.0.1:8787/v1 supporting OpenAI & Anthropic protocols. Tauri v2 shell + converter.py kernel; dynamic scheduler hot-reloads settings.json without restart.
§
Hardware: Mechrevo Aurora X (GM6AQ7C) i7-12800HX (8C8T) + 140W RTX 4070 Laptop 8GB VRAM + 24GB DDR5-6400 + 1TB NVMe. 8GB VRAM is scarce — keep background GPU consumers off. Models/runtime junctioned to D:. Local models at D:\HermesModels (MiniCPM5-2B, Qwen3.8-9B-Distill). Full ledger: topics/mechrevo-jiguangx-hardware-inventory.md; firmware: topics/mechrevo-jiguangx-bios-firmware-reference.md.
§
Memory single source of truth: Built-in MEMORY.md and USER.md inject in full each turn; Git shared lib 'shared-agent-memory' (memories/topics junction) holds long-form facts searched via search_files. No second memory store (OpenViking retired 2026-09-21). Keep entries compact: subtract rather than raise cap.
§
PowerShell convention: Use 'pwsh -NoProfile' (Store alias, version-independent) + '[Console]::OutputEncoding=[System.Text.Encoding]::UTF8' for CJK.
§
Style: External-AI cross-review -> P0/P1/P2 spec; fixed scope, zero opportunistic refactoring. Local-First: full CI-equivalent + Release build locally before push; never block main session on CI. Config changes: present candidates + defaults + cost, await user confirmation. Global default: reasoning_effort=ultra.
§
Pitfall: Desktop "session won't run" freeze = model switch injects a user-role system message (#94486); SOP in topics/hermes-desktop-rewind-deadlock.md.
§
Shared memory invariant: D:\ai coding\GitRepos\shared-agent-memory MUST stay on 'main'. Checking out 'hermes' unlinks projects/ and breaks the memories/topics junction silently while git status remains clean. Self-check: 'python scripts/check_memory_layout.py' (identical scripts in truth and home).
§
In-house projects: Workspaces located in 'D:\ai coding\GitRepos\<name>' (e.g. tweakbyjie, workbuddy2api) — inspect local workspace before touching GitHub. workbuddy2api changes require TDD + mutation testing. Tauri update builds: avoid rigid byte baselines (use loose floor + index-*.js hash check in exe); use ThinLTO + 16 codegen-units + input-aware frontend skip for fast rebuilds.
§
ComfyUI Portable at D:\ai coding\ComfyUI (run_nvidia_gpu.bat, 127.0.0.1:8188). Qwen-Image-2.1 = local bf16 singles, 2.8s/it on 8GB via offload; workflow in comfyui skill.
§
Hermes update: warm 20 critical files (cat-file --batch-check), bulk fetch if backlog >1500, then 'hermes update --yes --branch main' (no --keep-stash). If 'Desktop app build owed', run 'hermes desktop --build-only'. src deleted 2026-11-04, do not recreate.
§
Environment & Toolchain: Toolchain in D:\ai runtime (Node LTS, Py 3.14.8, PortableGit, uv, gh, pnpm via corepack). pnpm's bash shim needed a `pwd -W` patch (MSYS mangles /d mounts into D:\d\...); `corepack enable pnpm` overwrites that patch. %USERPROFILE%\.local is active (gateway-locks & python3.12 shim); never delete. ELECTRON_RUN_AS_NODE=1 leaks in WorkBuddy terminal (Electron apps exit rc=0 silently; unset first). PowerShell has no Recycle Bin (quarantine to D:\ai runtime\_quarantine\). Windows Update auto driver install disabled (SearchOrderConfig=0).
§
JDKs: Eclipse Temurin 8/16/17/21/25 at D:\JAVA\temurin-*, Azul Zulu deleted. PCL CE only accepts 4-segment java.exe FileVersion; 5-segment builds (Zulu/Corretto) get dropped and deadlock startup during Loading.
§
Pitfall: never kill the proxy client (Karing/FlClash) while Windows system proxy points at it (ProxyEnable=1 -> 127.0.0.1:3067) — that severs Hermes' own upstream and freezes the session. Run karing://disconnect or set ProxyEnable=0 first, then stop/swap the client.