Hermes is the SOLE primary agent (ZCode decommissioned 09-09; promo-token reverse proxy only). Shared lib shared-agent-memory (3304711297/shared-agent-memory): main = truth; sanitize before writing (no machine usernames or raw profile paths — use %USERPROFILE%/%LOCALAPPDATA%; redact credentials); push main that turn, Hermes-only -> `hermes` branch.
§
Scraping safety: Stop and ask after 2 consecutive anti-bot hits; never exhaust mirrors or launch new browsers without consent; login-gated targets require explicit approval.
§
Browser asset protection: Compare extension count (Default\Extensions, baseline 10) before and after Edge/Chrome automation; close only via CloseMainWindow graceful exit, never Stop-Process -Force.
§
UI preference: Micro-interactions, desktop-embedded widgets, dark geek-IDE aesthetic.
§
GUI build workflow: User builds GUI/Tauri apps (e.g. workbuddy2api) manually via 'npm run tauri build' (PowerShell at repo root). Agent must NEVER attempt builds, isolate directories, or script workarounds that break sessions or output empty shells. When code changes are done, simply notify 'Ready to build' and let the user execute.
§
Workspace integrity: Never edit user workspace source files while the user is actively building.
§
tweakbyjie upstream sync: Any tuning item benchmarked or adopted from a new open-source project MUST be automatically recorded into tools/upstream-sources.json and README.md upstream adoption table during the same turn, with no user reminder needed.
§
Local image generation (Qwen-Image-2.1): Quality strictly over speed; fixed to full-precision bf16 trio (lossless ceiling, matching official template). Never propose GGUF or int8_convrot quantizations for speed.
§
Session closeout dual push (v2.0): When user asks to end/delete session or all tasks complete green, MUST first run one-click archive in shared-agent-sessions ('python tools/upload_session.py' or 'tools/archive.cmd' to auto-locate session, generate L0/L1/L2 summaries and catalog, and push), THEN push shared-agent-memory (main). User manually deletes local session in desktop app; never push memory without archiving session.
§
CI notifications: On all-green task completion, call GitHub API (DELETE /notifications/threads/{id}) to mark related notification threads as Done.