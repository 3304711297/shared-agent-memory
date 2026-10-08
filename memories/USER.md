Hermes is the SOLE primary agent (ZCode decommissioned 09-09; promo-token reverse proxy only). Shared lib shared-agent-memory (3304711297/shared-agent-memory): main = truth; sanitize before writing (no machine usernames or raw profile paths — use %USERPROFILE%/%LOCALAPPDATA%; redact credentials); push main that turn, Hermes-only -> `hermes` branch.
§
Scraping safety: Stop and ask after 2 consecutive anti-bot hits; never exhaust mirrors or launch new browsers without consent; login-gated targets require explicit approval.
§
Browser asset protection: Compare extension count (Default\Extensions, baseline 10) before and after Edge/Chrome automation; close only via CloseMainWindow graceful exit, never Stop-Process -Force.
§
UI preference: Micro-interactions, dark geek-IDE aesthetic. Always render interactive components, widgets, and frontend artifacts directly embedded into the chat session via '::preview{file=...}'.
§
GUI build workflow: User builds GUI/Tauri apps (workbuddy2api) manually via 'npm run tauri build' (repo root). Agent must NEVER attempt builds, isolate dirs, or script workarounds; notify 'Ready to build' when code changes are done.
§
Workspace integrity: Never edit user workspace source files while the user is actively building.
§
tweakbyjie upstream sync: Any tuning item benchmarked or adopted from a new open-source project MUST be automatically recorded into tools/upstream-sources.json and README.md upstream adoption table during the same turn, with no user reminder needed.
§
Local image generation (Qwen-Image-2.1): Quality strictly over speed; fixed to full-precision bf16 trio (lossless ceiling, matching official template). Never propose GGUF or int8_convrot quantizations for speed.
§
Session closeout SOP (4-step sequence): When user says "delete/end session" or tasks complete green: 1. Audit learnings (topics/ or skills); 2. Clean residuals (temp probes/logs); 3. Archive session ('python tools/upload_session.py' in shared-agent-sessions); 4. Push memory: Commit & push shared-agent-memory (main/hermes) with green CI. Only then confirm deletion.
§
CI notifications: On all-green task completion, call GitHub API (DELETE /notifications/threads/{id}) to mark related notification threads as Done.
§
Core instruction and memory language invariant: 'SOUL.md', 'USER.md', and 'MEMORY.md' MUST be authored and updated STRICTLY in English. Agents must NEVER introduce Chinese or mixed languages into these core instruction and memory files.
§
Knowledge base and issue workflow: NEVER write directly to youshouldknow knowledge bases without explicit user selection/confirmation. Upstream-watch and evaluation-only GitHub Issues with no needed code changes must be summarized and closed automatically without asking.
§
Hermes updates: Prefer CLI 'hermes update --yes --branch main --keep-stash' over desktop GUI click.