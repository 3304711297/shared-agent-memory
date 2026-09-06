---
name: hermes-auxiliary-models
description: "Use when Hermes auxiliary models fail while chat works."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# Hermes Auxiliary Models

Hermes runs background tasks (image parsing, context compression,
session search) on **auxiliary models** configured independently from
the chat model (`auxiliary.vision.*`, `auxiliary.compression.*`, …).
Chat working while an auxiliary call fails is a routing/config problem,
not a model-capability problem. This skill covers the diagnosis path.

## The core invariant

Auxiliary calls do NOT inherit the chat session's provider or
credentials. Each auxiliary task resolves its own `provider` + `model`:

- `provider: auto` only finds **key-backed** providers (e.g.
  `OPENROUTER_API_KEY`, `GOOGLE_API_KEY`, or a `custom:` provider with
  an `api_key` in config). It cannot see OAuth or desktop-session-scoped
  credentials.
- The `model` id must exist on the backing provider. A local
  OpenAI-compatible proxy only serves the ids in its `models:` list;
  anything else fails with `400 unknown provider for model … /
  model_not_found`.
- Pointing an auxiliary task at an OAuth/session provider (e.g.
  `opencode-free`) fails with `401 Invalid API key` because the
  auxiliary path does not carry that credential (`auth.json`
  `credential_pool` will show no entry for it).

## Procedure

1. Inspect: `hermes config get auxiliary.<task>` (shows provider,
   model, base_url). Check `hermes auth list` for which providers
   actually hold credentials.
2. Point the task at a credential-bearing provider (never hand-edit
   `config.yaml` — always `hermes config set`):
   ```bash
   hermes config set auxiliary.vision.provider '<provider-id>'
   hermes config set auxiliary.vision.model '<model-on-that-provider>'
   ```
   Pick the model from the provider's served list (`custom_providers:`
   → `models:` in config, or the provider's model catalog).
3. Verify with a REAL call (e.g. `vision_analyze` on a real image),
   not by re-reading config. Config reads confirm intent; only a live
   call confirms the route works.
4. If the needed provider has no stored credential:
   `hermes auth add <provider>` — note key-type providers prompt
   `Paste your API key:` with no browser-OAuth path, so the user must
   supply a key. Run it in a PTY (`pty=true`) or it will hang silently
   waiting on stdin in background.
5. On failure, revert to the last working provider/model and say so
   plainly — do not leave the user on a broken route.

## Pitfalls

- Do not assume the chat model can serve auxiliary duty. A chat model
  working says nothing about auxiliary routing.
- KEYLESS providers (e.g. `opencode-free`, which pins an empty
  `Authorization` header) must stay credential-free: adding an api-key
  credential makes the relay 401 on every call, because it rejects ANY
  bearer it doesn't recognize. If you added one while debugging,
  `hermes auth remove <provider> 1` to restore the keyless path.
  A 401 that persists across ALL models on such a provider is
  auth-level — changing model ids will not fix it.
- To prove WHICH model value is actually on the wire, use a
  negative-control probe: set the task model to a bogus id
  (`probe-xyz-123`) and re-run. If the error echoes that id
  (`unknown provider for model probe-xyz-123`), routing follows the
  config value verbatim and the problem is the value, not the
  plumbing. Restore the working model immediately after.
- `hermes auth add` reads from the TTY when flags are omitted. For non-interactive adds,
  ALWAYS provide both `--label` and `--api-key` (omitting `--label` triggers an interactive prompt and causes `EOFError` in headless subshells):
  `hermes auth add <provider> --label "<LABEL>" --api-key "<KEY>"`
  When running interactive OAuth/prompts, use `pty=true` + poll.
- Never print or re-echo secrets seen in config (`api_key` values).
  Redact key/token/secret fields when inspecting `auth.json`.
- See `references/vision-401-case.md` for a full worked example of 401 keyless recovery.
- See `references/provider-quirks-gemini-and-opencode-free.md` for Google AI Studio location restrictions, Antigravity OAuth bridge, and OpenCode Free relay 429 patterns.
- See `references/custom-local-provider-gui-registration.md` for registering local custom providers/proxies (WorkBuddy `8787`, EasyCLIProxyAPI `18080`), avoiding GUI duplicate model entries, multi-agent path discovery on Windows, desktop quota plugin (`token-stats`) microservice architecture & Popover/Tip UI design rules, browser automation profile protection, upstream watch state-in-issue idempotency invariants, Windows skill platform/environment gating diagnostics, userscript @require silent crash debugging, modern Chromium MV3 userscript manager global failure diagnostics, the local gateway `gemini-web-search` alias fallacy vs. Hermes search engine keyless routing, Exa key configuration & backend locking, skill provenance diagnostics & single-name non-interactive uninstallation invariants, the overseas search provider card-wall trap vs. zero-card local fallback hierarchy, cross-agent dual-library cleanup parity (Hermes vs. ZCode), Hermes Desktop managed local models & `llama.cpp` runtime storage relocation on Windows (C: drive space protection via NTFS junctions), and OpenViking context database dual-drive memory architecture with local GPU RAG pipelines, serverless socket-activation on-demand auto-wake, 2-minute idle auto-sleep VRAM reclamation, and Hermes Desktop supervised local runtime (local_runtime) RAM termination decoupling.
- When committing code or docs to repositories with GitHub Actions CI, ALWAYS watch/poll the remote workflow (`gh run watch` or `gh run list`) and verify CI turns 100% green before ending the conversation.
