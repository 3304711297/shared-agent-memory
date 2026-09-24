Model routing: gemini-3.8-flash via EasyCLIProxyAPI (127.0.0.1:18080, provider=cpa) -> Antigravity (2 accounts, priority 10 round-robin + 1h sticky). auxiliary.* stays 'auto' — never change. Mid-session switch possible (workbuddy2api 8787); read runtime metadata, never assume.
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
Pitfall: Desktop "session won't run" freeze = model switch injecting a user-role system message + truncated retry rejected by gateway (#94486); restart won't fix — recovery SOP in topics/hermes-desktop-rewind-deadlock.md.
§
ZCode decommissioned 09-09; promo-token proxy relation only.
§
Shared memory invariant: D:\ai coding\GitRepos\shared-agent-memory MUST stay on 'main'. Checking out 'hermes' unlinks projects/ and breaks the memories/topics junction silently while git status remains clean. Self-check: 'python scripts/check_memory_layout.py' (identical scripts in truth and home).
§
In-house projects: Workspaces located in 'D:\ai coding\GitRepos\<name>' (e.g. tweakbyjie, workbuddy2api) — inspect local workspace before touching GitHub. workbuddy2api changes require TDD + mutation testing (N touchpoints = N explicit contract assertions).
§
ComfyUI Portable: Located at D:\ai coding\ComfyUI (start via run_nvidia_gpu.bat, http://127.0.0.1:8188). Qwen-Image-2.1 uses locally merged bf16 single files (14.2G transformer + 17.5G text encoder + official repack VAE); 8GB VRAM runs at 2.8s/it via offload. Workflow in comfyui v5.2 skill.