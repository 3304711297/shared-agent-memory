---
name: comfyui
description: "本地生图/跑工作流/教用户启动ComfyUI时必用。调度ComfyUI生成图像与视频。Generate images, video, and audio via diffusion workflows."
version: 5.2.0
author: [kshitijk4poor, alt-glitch, purzbeats]
license: MIT
platforms: [macos, linux, windows]
compatibility: "Requires ComfyUI (local, Comfy Desktop, or Comfy Cloud) and comfy-cli (auto-installed via pipx/uvx by the setup script)."
prerequisites:
  commands: ["python"]
setup:
  help: "Run scripts/hardware_check.py FIRST to decide local vs Comfy Cloud; then scripts/comfyui_setup.sh auto-installs locally (or use Cloud API key for platform.comfy.org)."
metadata:
  hermes:
    tags:
      - comfyui
      - image-generation
      - stable-diffusion
      - flux
      - sd3
      - wan-video
      - hunyuan-video
      - creative
      - generative-ai
      - video-generation
    related_skills: [stable-diffusion]
    category: creative
---

# ComfyUI

Generate images, video, audio, and 3D content through ComfyUI using the
official `comfy-cli` for setup/lifecycle and direct REST/WebSocket API
for workflow execution.

## What's in this skill

**Reference docs (`references/`):**

- `official-cli.md` — every `comfy ...` command, with flags
- `rest-api.md` — REST + WebSocket endpoints (local + cloud), payload schemas
- `workflow-format.md` — API-format JSON, common node types, param mapping
- `template-integrity.md` — converting `comfyui-workflow-templates` from
  editor format to API format: Reroute bypass, dotted dynamic-input keys
  (`values.a`, `resize_type.width`), Cloud quirks (302 redirect, 1 concurrent
  free-tier job, 1080p VRAM ceiling), Discord-compatible ffmpeg stitch.
  Authored by [@purzbeats](https://github.com/purzbeats). Load this whenever
  you're starting from an official template.

**Scripts (`scripts/`):**

| Script | Purpose |
|--------|---------|
| `_common.py` | Shared HTTP, cloud routing, node catalogs (don't run directly) |
| `hardware_check.py` | Probe GPU/VRAM/disk → recommend local vs Comfy Cloud |
| `comfyui_setup.sh` | Hardware check + comfy-cli + ComfyUI install + launch + verify |
| `extract_schema.py` | Read a workflow → list controllable params + model deps |
| `check_deps.py` | Check workflow against running server → list missing nodes/models |
| `merge_safetensors.py` | Merge HF sharded safetensors into one file ComfyUI can load (plan.json driven) |
| `localize_template.py` | Rewrite an official template to local filenames + fetch its example input images |
| `auto_fix_deps.py` | Run check_deps then `comfy node install` / `comfy model download` |
| `run_workflow.py` | Inject params, submit, monitor, download outputs (HTTP or WS) |
| `run_batch.py` | Submit a workflow N times with sweeps, parallel up to your tier |
| `ws_monitor.py` | Real-time WebSocket viewer for executing jobs (live progress) |
| `health_check.py` | Verification checklist runner — comfy-cli + server + models + smoke test |
| `fetch_logs.py` | Pull traceback / status messages for a given prompt_id |

**Example workflows (`workflows/`):** SD 1.5, SDXL, Flux Dev, SDXL img2img,
SDXL inpaint, ESRGAN upscale, AnimateDiff video, Wan T2V. See
`workflows/README.md`.

## When to Use

- User asks to generate images with Stable Diffusion, SDXL, Flux, SD3, etc.
- User wants to run a specific ComfyUI workflow file
- User wants to chain generative steps (txt2img → upscale → face restore)
- User needs ControlNet, inpainting, img2img, or other advanced pipelines
- User asks to manage ComfyUI queue, check models, or install custom nodes
- User wants video/audio/3D generation via AnimateDiff, Hunyuan, Wan, AudioCraft, etc.

## Architecture: Two Layers

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: comfy-cli (official lifecycle tool)        │
│   Setup, server lifecycle, custom nodes, models     │
│   → comfy install / launch / stop / node / model    │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│ Layer 2: REST/WebSocket API + skill scripts         │
│   Workflow execution, param injection, monitoring   │
│   POST /api/prompt, GET /api/view, WS /ws           │
│   → run_workflow.py, run_batch.py, ws_monitor.py    │
└─────────────────────────────────────────────────────┘
```

**Why two layers?** The official CLI is excellent for installation and server
management but has minimal workflow execution support. The REST/WS API fills
that gap — the scripts handle param injection, execution monitoring, and
output download that the CLI doesn't do.

## Quick Start

### Detect environment

```bash
# What's available?
command -v comfy >/dev/null 2>&1 && echo "comfy-cli: installed"
curl -s http://127.0.0.1:8188/system_stats 2>/dev/null && echo "server: running"

# Can this machine run ComfyUI locally? (GPU/VRAM/disk check)
python scripts/hardware_check.py
```

If nothing is installed, see **Setup & Onboarding** below — but always run the
hardware check first.

### One-line health check

```bash
python scripts/health_check.py
# → JSON: comfy_cli on PATH? server reachable? at least one checkpoint? smoke-test passes?
```

## Core Workflow

### Step 1: Get a workflow JSON in API format

Workflows must be in API format (each node has `class_type`). They come from:

- ComfyUI web UI → **Workflow → Export (API)** (newer UI) or
  the legacy "Save (API Format)" button (older UI)
- This skill's `workflows/` directory (ready-to-run examples)
- Community downloads (civitai, Reddit, Discord) — usually editor format,
  must be loaded into ComfyUI then re-exported

Editor format (top-level `nodes` and `links` arrays) is **not directly
executable**. The scripts detect this and tell you to re-export.

### Step 2: See what's controllable

```bash
python scripts/extract_schema.py workflow_api.json --summary-only
# → {"parameter_count": 12, "has_negative_prompt": true, "has_seed": true, ...}

python scripts/extract_schema.py workflow_api.json
# → full schema with parameters, model deps, embedding refs
```

### Step 3: Run with parameters

```bash
# Local (defaults to http://127.0.0.1:8188)
python scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "a beautiful sunset over mountains", "seed": -1, "steps": 30}' \
  --output-dir ./outputs

# Cloud (export API key once; uses correct /api routing automatically)
export COMFY_CLOUD_API_KEY="comfyui-..."
python scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "..."}' \
  --host https://cloud.comfy.org \
  --output-dir ./outputs

# Real-time progress via WebSocket (requires `pip install websocket-client`)
python scripts/run_workflow.py \
  --workflow flux_dev.json \
  --args '{"prompt": "..."}' \
  --ws

# img2img / inpaint: pass --input-image to upload + reference automatically
python scripts/run_workflow.py \
  --workflow sdxl_img2img.json \
  --input-image image=./photo.png \
  --args '{"prompt": "make it watercolor", "denoise": 0.6}'

# Batch / sweep: 8 random seeds, parallel up to cloud tier limit
python scripts/run_batch.py \
  --workflow sdxl.json \
  --args '{"prompt": "abstract"}' \
  --count 8 --randomize-seed --parallel 3 \
  --output-dir ./outputs/batch
```

`-1` for `seed` (or omitting it with `--randomize-seed`) generates a fresh
random seed per run.

### Step 4: Present results

The scripts emit JSON to stdout describing every output file:

```json
{
  "status": "success",
  "prompt_id": "abc-123",
  "outputs": [
    {"file": "./outputs/sdxl_00001_.png", "node_id": "9",
     "type": "image", "filename": "sdxl_00001_.png"}
  ]
}
```

## Decision Tree

| User says | Tool | Command |
|-----------|------|---------|
| **Lifecycle (use comfy-cli)** | | |
| "install ComfyUI" | comfy-cli | `bash scripts/comfyui_setup.sh` |
| "start ComfyUI" | comfy-cli | `comfy launch --background` |
| "stop ComfyUI" | comfy-cli | `comfy stop` |
| "install X node" | comfy-cli | `comfy node install <name>` |
| "download X model" | comfy-cli | `comfy model download --url <url> --relative-path models/checkpoints` |
| "list installed models" | comfy-cli | `comfy model list` |
| "list installed nodes" | comfy-cli | `comfy node show installed` |
| **Execution (use scripts)** | | |
| "is everything ready?" | script | `health_check.py` (optionally with `--workflow X --smoke-test`) |
| "what can I change in this workflow?" | script | `extract_schema.py W.json` |
| "check if W's deps are met" | script | `check_deps.py W.json` |
| "fix missing deps" | script | `auto_fix_deps.py W.json` |
| "generate an image" | script | `run_workflow.py --workflow W --args '{...}'` |
| "use this image" (img2img) | script | `run_workflow.py --input-image image=./x.png ...` |
| "8 variations with random seeds" | script | `run_batch.py --count 8 --randomize-seed ...` |
| "show me live progress" | script | `ws_monitor.py --prompt-id <id>` |
| "fetch the error from job X" | script | `fetch_logs.py <prompt_id>` |
| **Direct REST** | | |
| "what's in the queue?" | REST | `curl http://HOST:8188/queue` (local) or `--host https://cloud.comfy.org` |
| "cancel that" | REST | `curl -X POST http://HOST:8188/interrupt` |
| "free GPU memory" | REST | `curl -X POST http://HOST:8188/free` |

## Setup & Onboarding

When a user asks to set up ComfyUI, **the FIRST thing to do is ask whether
they want Comfy Cloud (hosted, zero install, API key) or Local (install
ComfyUI on their machine)**. Don't start running install commands or hardware
checks until they've answered.

**Official docs:** https://docs.comfy.org/installation
**CLI docs:** https://docs.comfy.org/comfy-cli/getting-started
**Cloud docs:** https://docs.comfy.org/get_started/cloud
**Cloud API:** https://docs.comfy.org/development/cloud/overview

### Step 0: Ask Local vs Cloud (ALWAYS FIRST)

Suggested script:

> "Do you want to run ComfyUI locally on your machine, or use Comfy Cloud?
>
> - **Comfy Cloud** — hosted on RTX 6000 Pro GPUs, all common models pre-installed,
>   zero setup. Requires an API key (paid subscription required to actually run
>   workflows; free tier is read-only). Best if you don't have a capable GPU.
> - **Local** — free, but your machine MUST meet the hardware requirements:
>   - NVIDIA GPU with **≥6 GB VRAM** (≥8 GB for SDXL, ≥12 GB for Flux/video), OR
>   - AMD GPU with ROCm support (Linux), OR
>   - Apple Silicon Mac (M1+) with **≥16 GB unified memory** (≥32 GB recommended).
>   - Intel Macs and machines with no GPU will NOT work — use Cloud instead.
>
> Which would you like?"

Routing:

- **Cloud** → skip to **Path A**.
- **Local** → run hardware check first, then pick a path from Paths B–E based on the verdict.
- **Unsure** → run the hardware check and let the verdict decide.

### Step 1: Verify Hardware (ONLY if user chose local)

```bash
python scripts/hardware_check.py --json
# Optional: also probe `torch` for actual CUDA/MPS:
python scripts/hardware_check.py --json --check-pytorch
```

| Verdict    | Meaning                                                       | Action |
|------------|---------------------------------------------------------------|--------|
| `ok`       | ≥8 GB VRAM (discrete) OR ≥32 GB unified (Apple Silicon)       | Local install — use `comfy_cli_flag` from report |
| `marginal` | SD1.5 works; SDXL tight; Flux/video unlikely                  | Local OK for light workflows, else **Path A (Cloud)** |
| `cloud`    | No usable GPU, <6 GB VRAM, <16 GB Apple unified, Intel Mac, Rosetta Python | **Switch to Cloud** unless user explicitly forces local |

The script also surfaces `wsl: true` (WSL2 with NVIDIA passthrough) and
`rosetta: true` (x86_64 Python on Apple Silicon — must reinstall as ARM64).

If verdict is `cloud` but the user wants local, do not proceed silently.
Show the `notes` array verbatim and ask whether they want to (a) switch to
Cloud or (b) force a local install (will OOM or be unusably slow on modern models).

### Choosing an Installation Path

Use the hardware check first. The table below is the fallback for when the
user has already told you their hardware:

| Situation | Recommended Path |
|-----------|------------------|
| `verdict: cloud` from hardware check | **Path A: Comfy Cloud** |
| No GPU / want to try without commitment | **Path A: Comfy Cloud** |
| Windows + NVIDIA + non-technical | **Path B: ComfyUI Desktop** |
| Windows + NVIDIA + technical | **Path C: Portable** or **Path D: comfy-cli** |
| Linux + any GPU | **Path D: comfy-cli** (easiest) |
| macOS + Apple Silicon | **Path B: Desktop** or **Path D: comfy-cli** |
| Headless / server / CI / agents | **Path D: comfy-cli** |

For the fully automated path (hardware check → install → launch → verify):

```bash
bash scripts/comfyui_setup.sh
# Or with overrides:
bash scripts/comfyui_setup.sh --m-series --port=8190 --workspace=/data/comfy
```

It runs `hardware_check.py` internally, refuses to install locally when the
verdict is `cloud` (unless `--force-cloud-override`), picks the right
`comfy-cli` flag, and prefers `pipx`/`uvx` over global `pip` to avoid polluting
system Python.

---

### Path A: Comfy Cloud (No Local Install)

For users without a capable GPU or who want zero setup. Hosted on RTX 6000 Pro.

**Docs:** https://docs.comfy.org/get_started/cloud

1. Sign up at https://comfy.org/cloud
2. Generate an API key at https://platform.comfy.org/login
3. Set the key:
   ```bash
   export COMFY_CLOUD_API_KEY="your-comfyui-key"
   ```
4. Run workflows:
   ```bash
   python scripts/run_workflow.py \
     --workflow workflows/flux_dev_txt2img.json \
     --args '{"prompt": "..."}' \
     --host https://cloud.comfy.org \
     --output-dir ./outputs
   ```

**Pricing:** https://www.comfy.org/cloud/pricing
**Concurrent jobs:** Free/Standard 1, Creator 3, Pro 5. Free tier
**cannot run workflows via API** — only browse models. Paid subscription
required for `/api/prompt`, `/api/upload/*`, `/api/view`, etc.

---

### Path B: ComfyUI Desktop (Windows / macOS)

One-click installer for non-technical users. Currently Beta.

**Docs:** https://docs.comfy.org/installation/desktop
- **Windows (NVIDIA):** https://download.comfy.org/windows/nsis/x64
- **macOS (Apple Silicon):** https://comfy.org

Linux is **not supported** for Desktop — use Path D.

---

### Path C: ComfyUI Portable (Windows Only)

**Docs:** https://docs.comfy.org/installation/comfyui_portable_windows

Download from https://github.com/comfyanonymous/ComfyUI/releases, extract,
run `run_nvidia_gpu.bat`. Update via `update/update_comfyui_stable.bat`.

---

### Path D: comfy-cli (All Platforms — Recommended for Agents)

The official CLI is the best path for headless/automated setups.

**Docs:** https://docs.comfy.org/comfy-cli/getting-started

#### Install comfy-cli

```bash
# Recommended:
pipx install comfy-cli
# Or use uvx without installing:
uvx --from comfy-cli comfy --help
# Or (if pipx/uvx unavailable):
pip install --user comfy-cli
```

Disable analytics non-interactively:
```bash
comfy --skip-prompt tracking disable
```

#### Install ComfyUI

```bash
comfy --skip-prompt install --nvidia              # NVIDIA (CUDA)
comfy --skip-prompt install --amd                 # AMD (ROCm, Linux)
comfy --skip-prompt install --m-series            # Apple Silicon (MPS)
comfy --skip-prompt install --cpu                 # CPU only (slow)
comfy --skip-prompt install --nvidia --fast-deps  # uv-based dep resolution
```

Default location: `~/comfy/ComfyUI` (Linux), `~/Documents/comfy/ComfyUI`
(macOS/Win). Override with `comfy --workspace /custom/path install`.

#### Launch / verify

```bash
comfy launch --background                       # background daemon on :8188
comfy launch -- --listen 0.0.0.0 --port 8190    # LAN-accessible custom port
curl -s http://127.0.0.1:8188/system_stats      # health check
```

---

### Path E: Manual Install (Advanced / Unsupported Hardware)

For Ascend NPU, Cambricon MLU, Intel Arc, or other unsupported hardware.

**Docs:** https://docs.comfy.org/installation/manual_install

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu130
pip install -r requirements.txt
python main.py
```

---

### Post-Install: Download Models

```bash
# SDXL (general purpose, ~6.5 GB)
comfy model download \
  --url "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
  --relative-path models/checkpoints

# SD 1.5 (lighter, ~4 GB, good for 6 GB cards)
comfy model download \
  --url "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" \
  --relative-path models/checkpoints

# Flux Dev fp8 (smaller variant, ~12 GB)
comfy model download \
  --url "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors" \
  --relative-path models/checkpoints

# CivitAI (set token first):
comfy model download \
  --url "https://civitai.com/api/download/models/128713" \
  --relative-path models/checkpoints \
  --set-civitai-api-token "YOUR_TOKEN"
```

List installed: `comfy model list`.

### Post-Install: Install Custom Nodes

```bash
comfy node install comfyui-impact-pack             # popular utility pack
comfy node install comfyui-animatediff-evolved     # video generation
comfy node install comfyui-controlnet-aux          # ControlNet preprocessors
comfy node install comfyui-essentials              # common helpers
comfy node update all
comfy node install-deps --workflow=workflow.json   # install everything a workflow needs
```

### Post-Install: Verify

```bash
python scripts/health_check.py
# → comfy_cli on PATH? server reachable? checkpoints? smoke test?

python scripts/check_deps.py my_workflow.json
# → are this workflow's nodes/models/embeddings installed?

python scripts/run_workflow.py \
  --workflow workflows/sd15_txt2img.json \
  --args '{"prompt": "test", "steps": 4}' \
  --output-dir ./test-outputs
```

## Portable Windows: Everyday Use for a Non-CLI User

The portable package needs no CLI at all. Teach the user this and stop there —
do not reach for `comfy-cli`, the REST API, or a python script.

1. Open the folder (here `D:\ai coding\ComfyUI`).
2. Double-click **`run_nvidia_gpu.bat`**. A black console window opens — the
   window *is* the server. It must stay open. Wait for
   `[INFO] To see the GUI go to: http://127.0.0.1:8188`.
3. Browse to `http://127.0.0.1:8188`.

Verify from the outside with `curl -s http://127.0.0.1:8188/system_stats`.
**Stopping** = close the console window or `Ctrl+C` in it; closing the browser
tab does NOT stop the server (it keeps the VRAM). Do not tell a user to
"restart ComfyUI" by killing a python PID — they should use the window.

### Ship UI-format workflows, NOT API format

This is the single most common way a hand-off goes wrong. Both formats load in
the frontend, but **API format carries no layout data**, so every node
overlaps at the origin and the user sees an unusable pile. The official docs
state it plainly: API format "can be loaded in UI — yes, but without layout."

| | Save format | API format |
|---|---|---|
| Detect | top-level `nodes` + `links` + `version` | numeric keys, each with `class_type` |
| Use for | handing a workflow to a human in the UI | `POST /prompt` |

So: for a human, start from the official template (already save format) and
rewrite only the widget values. For a script, use API format. Exporting a
save-format workflow as API is `File → Export Workflow (API)` in the frontend.

### Rewriting a template to local filenames

Official templates reference the *repackaged* checkpoint name, which is often
not what is on disk (e.g. the Qwen-Image-2.1 templates ship pointing at
`..._int8_convrot.safetensors` while the user has the bf16 merge).
`scripts/localize_template.py` does this end to end — read it before doing it by
hand. The rule that matters:

Do a plain **string replace over the raw JSON text**, not a walk of `widgets_values`:
the filename also appears inside `properties.models[].url`, `widgets_values_named`,
and the MarkdownNote documentation, and leaving those stale makes the workflow
inconsistent (the note tells the user to download a file the graph no longer uses).

```python
raw = z.read(member).decode("utf-8")
for old, new in RENAME:
    raw = raw.replace(old, new)
wf = json.loads(raw)  # must still parse
```

Then assert: no old name survives, the new names are present, and
`nodes`/`links`/`version` all exist. **Also assert each OLD name actually
matched** — a rename that hits nothing (typo, or the template never referenced
it) means the workflow still points at a missing file, and reporting success
there silently hands over a broken graph.

### Templates reference example input images that are NOT bundled

A template with a `LoadImage` node ships the *filename* but not the file. The
UI then shows an error badge on that node. The images live in the
`Comfy-Org/workflow_templates` repo under `input/`, and the URLs are embedded
in the template's MarkdownNote — grep them out rather than guessing:

```python
re.findall(r'https://raw\.githubusercontent\.com/[^"\')\s]+\.(?:png|jpg|jpeg|webp)', raw)
```

Download into `<portable>\ComfyUI\input\` and check the PNG magic
(`\x89PNG\r\n\x1a\n`) — a failed fetch otherwise leaves an HTML error page
that still "exists" and still errors in the UI. See the pitfall about jsdelivr
below: raw.githubusercontent.com is frequently unreachable.

### Confirming a workflow works before handing it over

Loading without errors is not proof. Run it in the real UI at least once:

- The desktop preview pane can drive the live frontend: open
  `http://127.0.0.1:8188`, then `drive_preview` → `elements` to inventory the
  page, `click` a workflow in the sidebar, and `click` the run button
  (`[data-testid="queue-button"]`). The run button belongs to whatever is on the
  canvas — **check the page title / `elements` first**: ComfyUI opens a default
  workflow on load, so clicking run blindly executes *that*, not yours.
- Then verify from the server, not the UI:
  `GET /history?max_items=2` → `status.status_str == "success"` and
  `completed == true`, and `GET /api/userdata?dir=workflows&recurse=true&split=false`
  to prove the file is visible to the frontend.
- For RGBA output assert on the pixels, not the appearance: an alpha histogram
  (`getchannel("A").histogram()` — a real cutout has a large `hist[0]` bucket)
  plus corner-pixel alpha. Pasting the image on a checkerboard and viewing it
  only shows that alpha *exists*; it cannot prove the background is what got
  cut, so pair it with a before/after pixel sample at known coordinates.

**8 GB VRAM reality check (measured, RTX 4070 Laptop, bf16 Qwen-Image-2.1):**
~32 GB of weights via dynamic offload still runs — 1024x1024 at 25 steps landed
at 2.76 s/it, ~73 s, plus ~8 s one-time model staging on the first run of a
workflow. Do not tell the user it "won't fit" and do not promise a fast run;
give the measured number instead. Re-runs on the same workflow skip the
staging cost.

## Image Upload (img2img / Inpainting)

The simplest way is to use `--input-image` with `run_workflow.py`:

```bash
python scripts/run_workflow.py \
  --workflow workflows/sdxl_img2img.json \
  --input-image image=./photo.png \
  --args '{"prompt": "make it cyberpunk", "denoise": 0.6}'
```

The flag uploads `photo.png`, then injects its server-side filename into
whatever schema parameter is named `image`. For inpainting, pass both:

```bash
python scripts/run_workflow.py \
  --workflow workflows/sdxl_inpaint.json \
  --input-image image=./photo.png \
  --input-image mask_image=./mask.png \
  --args '{"prompt": "fill with flowers"}'
```

Manual upload via REST:
```bash
curl -X POST "http://127.0.0.1:8188/upload/image" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
# Returns: {"name": "photo.png", "subfolder": "", "type": "input"}

# Cloud equivalent:
curl -X POST "https://cloud.comfy.org/api/upload/image" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
```

## Cloud Specifics

- **Base URL:** `https://cloud.comfy.org`
- **Auth:** `X-API-Key` header (or `?token=KEY` for WebSocket)
- **API key:** set `$COMFY_CLOUD_API_KEY` once and the scripts pick it up automatically
- **Output download:** `/api/view` returns a 302 to a signed URL; the scripts
  follow it and strip `X-API-Key` before fetching from the storage backend
  (don't leak the API key to S3/CloudFront).
- **Endpoint differences from local ComfyUI:**
  - `/api/object_info`, `/api/queue`, `/api/userdata` — **403 on free tier**;
    paid only.
  - `/history` is renamed to `/history_v2` on cloud (the scripts route
    automatically).
  - `/models/<folder>` is renamed to `/experiment/models/<folder>` on cloud
    (the scripts route automatically).
  - `clientId` in WebSocket is currently ignored — all connections for a
    user receive the same broadcast. Filter by `prompt_id` client-side.
  - `subfolder` is accepted on uploads but ignored — cloud has a flat namespace.
- **Concurrent jobs:** Free/Standard: 1, Creator: 3, Pro: 5. Extras queue
  automatically. Use `run_batch.py --parallel N` to saturate your tier.

## Queue & System Management

```bash
# Local
curl -s http://127.0.0.1:8188/queue | python -m json.tool
curl -X POST http://127.0.0.1:8188/queue -d '{"clear": true}'    # cancel pending
curl -X POST http://127.0.0.1:8188/interrupt                      # cancel running
curl -X POST http://127.0.0.1:8188/free \
  -H "Content-Type: application/json" \
  -d '{"unload_models": true, "free_memory": true}'

# Cloud — same paths under /api/, plus:
python scripts/fetch_logs.py --tail-queue --host https://cloud.comfy.org
```

## Pitfalls

1. **API format is required for the scripts and `/prompt` — NOT for handing a
   workflow to a human.** These are two different consumers, and conflating them
   is a common mistake:

   | Consumer | Format | Why |
   |---|---|---|
   | `run_workflow.py`, `POST /prompt`, `check_deps.py` | **API format** (numeric keys + `class_type`) | that is what the executor consumes |
   | a person opening it in the Web UI | **Save/UI format** (top-level `nodes`+`links`+`version`) | API format loads but has **no layout**, so every node piles up at the origin |

   See *Portable Windows → Ship UI-format workflows, NOT API format* for the
   hand-off procedure. The scripts detect editor format and tell you to re-export
   via "Workflow → Export (API)" (newer UI) or "Save (API Format)" (older UI).

2. **Server must be running** — all execution requires a live server.
   `comfy launch --background` starts one. Verify with
   `curl http://127.0.0.1:8188/system_stats`.

3. **Model names are exact** — case-sensitive, includes file extension.
   `check_deps.py` does fuzzy matching (with/without extension and folder
   prefix), but the workflow itself must use the canonical name. Use
   `comfy model list` to discover what's installed.

4. **Missing custom nodes** — "class_type not found" means a required node
   isn't installed. `check_deps.py` reports which package to install;
   `auto_fix_deps.py` runs the install for you.

5. **Working directory** — `comfy-cli` auto-detects the ComfyUI workspace.
   If commands fail with "no workspace found", use
   `comfy --workspace /path/to/ComfyUI <command>` or
   `comfy set-default /path/to/ComfyUI`.

6. **Cloud free-tier API limits** — `/api/prompt`, `/api/view`, `/api/upload/*`,
   `/api/object_info` all return 403 on free accounts. `health_check.py` and
   `check_deps.py` handle this gracefully and surface a clear message.

7. **Timeout for video/audio workflows** — auto-detected when an output node
   is `VHS_VideoCombine`, `SaveVideo`, etc.; the default jumps from 300 s to
   900 s. Override explicitly with `--timeout 1800`.

8. **Path traversal in output filenames** — server-supplied filenames are
   passed through `safe_path_join` to refuse anything escaping `--output-dir`.
   Keep this protection on — workflows with custom save nodes can produce
   arbitrary paths.

9. **Workflow JSON is arbitrary code** — custom nodes run Python, so
   submitting an unknown workflow has the same trust profile as `eval`.
   Inspect workflows from untrusted sources before running.

10. **Auto-randomized seed** — pass `seed: -1` in `--args` (or use
    `--randomize-seed` and omit the seed) to get a fresh seed per run.
    The actual seed is logged to stderr.

11. **`tracking` prompt** — first run of `comfy` may prompt for analytics.
    Use `comfy --skip-prompt tracking disable` to skip non-interactively.
    `comfyui_setup.sh` does this for you.

12. **Portable package updates: the 4 pinned packages are the whole story.**
    The startup WARNING block (`comfyui-frontend-package` /
    `comfyui-workflow-templates` / `comfyui-embedded-docs` / `comfy-kitchen`
    "lower than recommended") is fixed by exactly the command it prints:
    `<portable>/python_embeded/python.exe -s -m pip install -r <portable>/ComfyUI/requirements.txt`.
    That installs ~180 MB across 11 packages (the templates meta-package pulls
    `-core`, `-json`, and several `media-*` bundles of 90-100 MB each), so on a
    throttled link expect 15-30 min — it is not hung. Run it in the background
    and verify afterwards with `/system_stats`, whose
    `installed_templates_version` must equal `required_templates_version`.
    A new model's templates appear only after this; e.g. Qwen-Image-2.1's three
    templates live in `comfyui-workflow-templates-json` and were absent below it.

13. **A missing model template is a templates-package version gap, not a
    frontend/cache problem.** Probe it without the GUI: after updating, list
    `iter_templates()` from `comfyui_workflow_templates` for the expected
    template_id, and confirm `FrontendManager.template_asset_map()` resolves its
    assets. Both are importable from the portable python.

14. **Diffusers-layout model folders are NOT directly loadable, and
    `DiffusersLoader` will not save you.** `comfy/diffusers_load.py` only looks
    for `unet/` + `text_encoder/model.safetensors` (its `first_file` list omits
    the HF sharded names), and ComfyUI has no `*.safetensors.index.json` /
    `weight_map` handling anywhere in the codebase. A HF repo laid out as
    `transformer/diffusion_pytorch_model-0000N-of-0000M.safetensors` +
    `text_encoder/model-0000N-of-0000M.safetensors` therefore fails both the
    single-file loaders and `DiffusersLoader`. Merging the shards yourself is
    cheap and avoids re-downloading tens of GB — see `scripts/merge_safetensors.py`.

15. **Check whether the weights actually need redownloading before downloading.**
    ComfyUI's detectors accept more layouts than the shipped checkpoint uses:
    `model_detection.py` sets `fused_mlp = gate_up is not None` so both the fused
    (`img_mlp.gate_up`) and unfused (`img_mlp.gate_layer` + `.proj`) mlp layouts
    load, and `comfy/sd.py` prefix-replaces `model.language_model.` -> `model.`
    for the Qwen3-VL text encoder itself. Compare the local tensor header
    against the official single-file header (keys + dtypes) before concluding
    you must re-download; only a genuine architecture/naming mismatch justifies it.
    The VAE is the usual exception: the diffusers naming
    (`decoder.conv_in` / `mid_block.attentions`) can be misdetected as a
    HunyuanVideo VAE by the generic `decoder.conv_in.weight` branch, while the
    official repack uses the Wan-2.2 layout
    (`decoder.middle.0.residual.0.gamma`, 5D `decoder.head.2.weight` with
    `shape[2] == 1`) — that one genuinely must come from the official repack.

16. **When HF downloads keep dying with SSL errors, load the `hf-model-download` skill FIRST.**
    Do not hand-roll a downloader: that skill already ships
    `scripts/resilient_hf_download.py` (native HTTP `Range` -> `.part`, so a drop
    resumes instead of restarting) plus the four settings that actually matter —
    `HF_ENDPOINT=https://hf-mirror.com` with proxies cleared (an overseas node
    gets 308-redirected back to huggingface.co), `HF_HUB_DISABLE_XET=1` (domestic
    mirrors do not proxy the CAS endpoint and return 401),
    `HF_HUB_DOWNLOAD_TIMEOUT=60` (the 10 s default dies on flaky Wi-Fi), and
    `*.lock` cleanup. Reach for ModelScope only if that still fails.

    Diagnosis, if you are already stuck: `URLError: [SSL:
    UNEXPECTED_EOF_WHILE_READING]` and `Cannot send a request, as the client has
    been closed` from both `urlopen` and `hf download` on a large HF blob are
    link-level, not credential-level; `curl` against the same URL failing with
    `schannel: failed to receive handshake` confirms it. A working PyPI channel
    does NOT imply HF works — different CDNs (observed: pip steady at 150-400 KB/s
    while HF and hf-mirror both died at the TLS handshake).

    If HF *and* hf-mirror are both down, the same script has a ModelScope source:
    `--provider modelscope --repo <org>/<name>`. Verified behaviour there, so you
    do not have to re-derive it: LFS weight files (all the big ones) 302 to
    `cdn-lfs-cn-1.modelscope.cn` and return a real `206 Partial Content`, so
    resume works; plain small files (README/config) are served by the gateway as
    `200` with an inconsistent `Content-Length` on open-ended `bytes=N-`, so they
    cannot be resumed. A request for a filename that does not exist returns
    `200` plus a JSON error body rather than 404 — check the `repo/files` listing
    before downloading, or you will save a 145-byte error blob as a model file.

17. **A 16 GB-plus model can still run on an 8 GB card via offload — measure, don't assume.**
    bf16 Qwen-Image-2.1 totals ~32 GB of weights (14.2 GB transformer +
    17.5 GB text encoder + 0.7 GB VAE) against 8 GB VRAM and 25 GB RAM, yet it
    runs: 1024x1024 at 25 steps landed at ~2.8 s/it (~73 s per image). Set
    expectations from a real timed run rather than a VRAM rule of thumb.

18. **`raw.githubusercontent.com` is often unreachable from CN links — use jsdelivr.**
    Fetching a template's example input image from
    `raw.githubusercontent.com/Comfy-Org/...` failed with
    `schannel: failed to receive handshake` both directly and through the local
    proxy (same link-level TLS failure as the HF case in #16; a different CDN).
    The jsdelivr mirror worked immediately and serves identical bytes:
    `https://cdn.jsdelivr.net/gh/<org>/<repo>@<branch>/<path>`
    (e.g. `.../gh/Comfy-Org/workflow_templates@main/input/angry_broccoli.png`).
    Always confirm the downloaded file's magic bytes — a blocked fetch can leave
    a 0-byte or HTML file that still "exists" and still breaks the UI node.

19. **Loading a workflow without errors is not evidence it runs.**
    A template can render perfectly and still fail on execution because a
    referenced input image or model filename is absent. Before telling a user a
    workflow is ready, execute it once and read `status.status_str` /
    `completed` from `GET /history`. Two failure modes this catches that the UI
    will not warn you about: (a) `LoadImage` nodes pointing at example images
    that ship with the template's docs but not on disk, (b) widget values naming
    the repackaged checkpoint while only the merged bf16 file exists.

20. **"Uncensored" GGUF repos of a base model are the base model — verify, don't assume a finetune.**
    `abenzerps/Qwen-Image-2.1-Uncensored-GGUF` is a pure quantization of `Qwen/Qwen-Image-2.1`
    at the same revision; its tensor names/shapes match the upstream merge exactly and its VAE
    is byte-identical (sha256) to Comfy-Org's. "Uncensored" there only means "no safety checker",
    which is already true of any local ComfyUI pipeline. Before treating a community repo as a
    different model, compare tensor headers (names + dtypes + shapes) and file hashes instead of
    trusting the card: fetch the remote header with an HTTP `Range` request for
    `bytes=0-(7+header_len)` (the first 8 bytes little-endian give the header length) — a handful
    of KB answers the whole question without downloading tens of GB.

21. **K-quant GGUF keeps 1D tensors in BF16; the legacy plain quants do not — that is the real
    breakage.** In `qwen-image-2.1-Q4_K_M/Q5_K_M/Q6_K.gguf` all 65 1D tensors (RMSNorm scales) are
    BF16, while `Q8_0` and `Q4_0` quantize their 64 1D tensors too, which is exactly why Q8_0 fails
    at sampling with a `[136] vs [128]` shape mismatch (documented in that repo's README). Check
    per-tensor GGML types from the header before blaming the loader.

22. **GGUF needs a custom node that is NOT part of core ComfyUI.** A fresh portable install has
    nothing under `custom_nodes/` (only the two official example files), so a GGUF workflow fails
    until `git clone https://github.com/leejet/ComfyUI-GGUF`; the older `city96` fork raises
    `Unknown model architecture!` for Qwen-Image 2.1. GGUF models go in
    `models/diffusion_models/` and the loader node is `Unet Loader (GGUF)` in place of `UNETLoader`.
    These community GGUFs may also carry zero KV metadata (`nkv=0`), so the loader resolves the
    architecture purely from tensor naming.

## Verification Checklist

Use `python scripts/health_check.py` to run the whole list at once. Manual:

- [ ] `hardware_check.py` verdict is `ok` OR the user explicitly chose Comfy Cloud
- [ ] `comfy --version` works (or `uvx --from comfy-cli comfy --help`)
- [ ] `curl http://HOST:PORT/system_stats` returns JSON
- [ ] `comfy model list` shows at least one checkpoint (local) OR
      `/api/experiment/models/checkpoints` returns models (cloud)
- [ ] Workflow JSON is in API format
- [ ] `check_deps.py` reports `is_ready: true` (or only `node_check_skipped`
      on cloud free tier)
- [ ] Test run with a small workflow completes; outputs land in `--output-dir`
