# Local Custom Provider & Desktop GUI Registration

When exposing a local model proxy/bridge (e.g. `codebuddy2openai`, `antigravity`, `ollama`, or local adapters) to Hermes Desktop and CLI, follow these steps to ensure full visibility across the GUI dropdown and slash commands.

## 1. Local Adapter Execution
- Ensure the local proxy is listening on `127.0.0.1:<PORT>/v1` (e.g., `8787` for CodeBuddy/WorkBuddy, `18080` for Antigravity).
- Test endpoints with `curl http://127.0.0.1:<PORT>/health` and `curl http://127.0.0.1:<PORT>/v1/models`.

## 2. Register Credential in Hermes Auth
Use non-interactive `hermes auth add` with both `--api-key` and `--label` flags (omitting `--label` triggers interactive stdin prompt and raises `EOFError` in headless subshells):
```bash
hermes auth add "custom:<name>-(127.0.0.1:<PORT>)" --api-key "local" --label "<Label>"
```

## 3. Register in `custom_providers` (for Desktop GUI Picker)
Add to `~/.hermes/config.yaml` under `custom_providers`:
```yaml
custom_providers:
  - name: <Display Name> (127.0.0.1:<PORT>)
    base_url: http://127.0.0.1:<PORT>/v1
    api_key: local
    model: auto
    models:
      auto: {}
      glm-5.2: {}
      kimi-k2.7: {}
      deepseek-v4-pro: {}
    models_discovered: true
```

## 4. Update Model Picker Cache
Hermes Desktop GUI populates the dropdown from `~/.hermes/provider_models_cache.json`. Update or insert the cache entry:
```json
{
  "custom:http://127.0.0.1:<PORT>/v1": {
    "fp": "<cache_id>",
    "at": 1788431000.0,
    "models": ["auto", "glm-5.2", "kimi-k2.7", "deepseek-v4-pro"]
  }
}
```

## 5. Configure CLI Model Aliases (Optional)
In `~/.hermes/config.yaml`:
```yaml
model_aliases:
  <alias>:
    model: <model_name>
    provider: custom
    base_url: http://127.0.0.1:<PORT>/v1
```
## 6. WorkBuddy / CodeBuddy Specific Model Names & Upstream Mapping
When bridging Tencent CodeBuddy/WorkBuddy via `codebuddy2openai` (`8787`), the upstream backend (`copilot.tencent.com/v2/chat/completions`) recognizes specific model identifiers (extracted and verified from `product.json` & live tests):
- **Hunyuan**: `hy4-preview` (backend ID; map `hy4` -> `hy4-preview`), `hy3-preview-agent` (backend ID; map `hy3` / `hy3-preview` -> `hy3-preview-agent`).
- **GLM**: `glm-5.3`, `glm-5.3-flash`, `glm-5.2`, `glm-5.1`, `glm-5v-turbo` (`glm-5.0` is retired upstream).
- **Kimi**: `kimi-k3-1` (map `kimi-k3` -> `kimi-k3-1`), `kimi-k2.7`, `kimi-k2.6`, `kimi-k2.5`.
- **DeepSeek**: `deepseek-v4-pro`, `deepseek-v4-flash`.
- **MiniMax**: `minimax-m3-pay` (map `minimax-m3` -> `minimax-m3-pay`).
- **Routing/Defaults**: `auto`, `default``.

Always implement a `MODEL_MAP` in `converter.py` before forwarding the request body to upstream `copilot.tencent.com/v2/chat/completions` so shorthand model names (`hy4`, `hy3`, `kimi-k3`, `minimax-m3`) route seamlessly without 400 errors.

## 7. Migration Hygiene & Avoiding Duplicate Providers
When re-registering or migrating a local provider (e.g. migrating from a legacy `Local (127.0.0.1:18080)` entry to `cpa-gui` for EasyCLIProxyAPI):
- **Purge legacy duplicates**: Remove the obsolete entry from `custom_providers` in `config.yaml` AND remove the old entry from `auth.json` (`credential_pool`). Having two entries sharing the same `base_url` causes duplicate model entries in the desktop GUI model dropdown.
- **Discovery flag**: Ensure `models_discovered: true` is set on the active provider block to avoid redundant background model discovery probes.
- **EasyCLIProxyAPI (18080) Dual Protocol Support**: EasyCLIProxyAPI serves both `/v1/chat/completions` (OpenAI format, for Hermes) and `/v1/messages` (Anthropic format, for ZCode/Claude Code), providing Gemini 3.8/3.7/3.6/3.1 with thinking/reasoning.
- **Agent Path Detection on Windows**: EasyCLIProxyAPI hardcodes client discovery to `%LOCALAPPDATA%\Programs\<Agent>\<Agent>.exe` and `%ProgramFiles%\<Agent>\<Agent>.exe`. If an agent (e.g. ZCode) is installed on another drive (e.g. `D:\zcode\ZCode.exe`), create directory junctions (`mklink /J`) in standard locations so EasyCLIProxyAPI can detect the client and enable the launch button.

## 8. Embedded Desktop Quota Monitor Plugin Architecture (`token-stats`) & UI Design Rules
When running Hermes Desktop with the `token-stats` status-bar quota chip for Google / Antigravity:
- **Embedded Architecture Evolution (2026-09-04 / 2026-09-05)**:
  - The legacy standalone 18088 microservice and scheduled task `Hermes_Quota_Service` are retired. Quota is served by an embedded Hermes user plugin (`plugins/token-stats/dashboard/plugin_api.py`) mounted at `/api/plugins/token-stats/quota` on Hermes's own internal backend server.
  - Lifecycle follows the desktop app: app open → service up, app close → service down. Zero persistent background daemons or scheduled tasks.
  - The desktop UI (`desktop-plugins/token-stats/plugin.js`) communicates via `ctx.rest('/quota')`, requiring zero CORS configuration and no fixed port bindings.
  - Features full-surface integration: status-bar Chip (`statusBar.right`), Popover details, Sidebar nav entry (`SIDEBAR_NAV_AREA`, Pulse icon), dedicated full-page dashboard (`ROUTES_AREA: /quota`), Command Palette shortcut (`PALETTE_AREA`), and local preference persistence via `ctx.storage`.
  - Also integrates non-blocking local gateway probing for WorkBuddy (`127.0.0.1:8787/v1`) alongside Antigravity official credentials.
- **Direct Quota Architecture**:
  - Reads plaintext Google OAuth tokens from `D:\EasyCLIProxyAPI\auth\antigravity-*.json` (no DPAPI decryption needed).
  - Queries Google's official Antigravity Quota endpoint: `https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary` (via proxy `127.0.0.1:3067`). **Critical Distinction**: Google maintains two separate quota pools under the same OAuth token — `daily-cloudcode-pa` is the dedicated Antigravity quota bucket (used by Antigravity / EasyCLIProxyAPI GUI); querying generic `cloudcode-pa` reaches an unrelated CloudCode pool and returns completely mismatched quota fractions (e.g. 100%/43% vs. 74%/87%).
  - 30-second in-memory cache with fallback to disk cache `direct-quota.json`. Pass `?force=1` on explicit user click to bypass cache.
- **Desktop UI Design & Micro-Component Rules**:
  - **Popover vs. Tip Pitfall**: The Hermes native `<Tip>` component has `box-decoration-clone inline max-w-64` intended strictly for 1-line action hints. Using `<Tip>` for multi-line status dashboards produces ragged-right "torn tape" stepped backgrounds and splits Chinese words awkwardly across lines. Always use `Popover` (`PopoverContent` with `bg-elevated`, `backdrop-blur-xl`, rounded card, and visual progress bars) for multi-row overlays, keeping `<Tip>` only as a 1-line hover hint.
  - **Status Bar Key-Value Contrast**: In compact status chips (e.g. `5h:100%`), never paint label (`5h`), delimiter (`:`), and value (`100%`) in the same uniform color. Mute the label (`text-[10px] text-secondary`), de-emphasize punctuation (`text-quaternary font-mono`), and bold the numerical value in monospace (`font-mono font-bold text-emerald-400`) so users scan core metrics instantly without visual clutter.
  - **Tri-Feedback on Manual Actions (Refresh Button)**: If an interactive button triggers a data refresh and the cached data returns identical values, the lack of visible change makes users think the button is unresponsive. Always implement:
    1. **Cache-bypass parameter**: Pass `?force=1` on explicit user click to bypass in-memory caching and force an upstream network round-trip.
    2. **Active spinner state**: Switch to an SVG vector icon with `animate-spin` and `active:scale-90` while in flight, disabling the button to prevent duplicate clicks.
    3. **Tri-Feedback on completion**: (a) Morph button to a transient `✓ 已刷新` badge (reverts after 2-3s); (b) Send an explicit desktop notification toast via `host.notify`; (c) Display an exact timestamp in the UI (e.g. `(14:34:00)`) so the user has visual proof of a successful fresh sync.

## 9. Browser Automation & Extension Isolation Safeguard
When automating web tasks or taking snapshots in Hermes on Windows:
- **Extension Clear Pitfall**: Enabling `browser.use_real_profile: true` or launching `browser_exec` while the user's primary Edge Dev profile is closed can cause Chromium to snapshot the profile without extensions loaded. Upon process exit, Chromium writes its empty in-memory extension table back to disk, clearing `extensions.settings` in `Preferences` and making extensions (Tampermonkey, ScriptCat, KISS Translator, etc.) disappear from the browser UI (underlying data directories in `Local Extension Settings` remain intact).
- **Hardening Rules**:
  - Set `browser.use_real_profile: false` in `config.yaml` to guarantee automation runs in an isolated disposable sandbox.
  - Set `browser.allow_private_urls: true` when local Web development testing (`localhost`, `127.0.0.1`) is needed.
  - Avoid `browser_exec` launching new browser instances against user profiles; prioritize `smart-web-crawler` (static direct extraction) or attaching to an existing session via `chrome-devtools-mcp` with `--autoConnect`.

## 10. Verification Before Completion & Remote CI Gating
- **Remote CI Verification Iron Law**: When pushing commits or doc changes to any repository configured with GitHub Actions CI (e.g. `youshouldknow`, `tweakbyjie`, `make-bilibili-great-together`):
  - Local build passing or `git push` exiting with 0 is NOT sufficient evidence to claim completion.
  - The agent MUST actively poll or watch the remote CI pipeline (`gh run watch <run_id> --repo <repo>` or `gh run list --repo <repo>`).
  - Verify that the workflow status empirically reports `completed` and `success` (100% green).
  - Never end the turn, celebrate, or declare work complete until all remote CI workflows have verified successfully.

## 11. Upstream Watch & State-in-Issue Idempotency Pattern
When implementing or debugging automated upstream monitoring workflows (`upstream-watch.yml`) that track upstream commit SHAs via GitHub Issues (the state-in-issue pattern without external database):
- **The Closed-State Pitfall**: Querying only open issues (`state=open&per_page=1`) to discover the previously recorded SHA breaks idempotency. When an evaluation issue is reviewed and closed, `state=open` returns empty, causing `RECORDED` SHA to reset to empty. The workflow mistakenly concludes upstream advanced and re-opens duplicate issues on every schedule run (e.g. daily false-positive alarms for the exact same commit SHA).
- **The Robust Invariant**:
  - Always query `state=all&per_page=1` with the specific label filter (`labels=upstream-sync`) to retrieve the last recorded SHA from the most recent issue, regardless of whether it is currently open or closed.
  - Only when upstream HEAD SHA actually differs from `RECORDED` should the workflow advance: if an unclosed open issue exists (`state=open`), add a transitioning comment and close it, then open the new issue for the newly discovered commit range.

## 12. Windows Skill Platform & Environment Gating Diagnostics
When auditing or troubleshooting skills on Windows:
- **Platform Filtering Invariant**: Hermes Agent inspects each skill's `SKILL.md` frontmatter. If `platforms:` lists only `[linux, macos]` without `windows`, Hermes automatically and silently filters out the skill on Windows hosts. It remains physically on disk in `skills/` but will not appear in `hermes skills list` or `<available_skills>`.
- **Environment Scoping**: Skills declaring `environments: [kanban]` only activate inside Kanban dispatcher runs.
- **Auditing Discrepancies**: To diagnose why disk skill counts exceed CLI enabled counts, parse the YAML frontmatter of on-disk skills to distinguish true omissions from intended platform/environment filtering.

## 13. Userscript `@require` Remote Asset Failure & Manager Silent Crash Diagnostics
When diagnosing userscripts (ScriptCat, Tampermonkey) that appear enabled in the browser extension popup (`当前页运行脚本 1/1`) but have zero effect on the page:
- **The Silent `@require` Failure Trap**: Scripts relying on external `@require` assets (e.g. multi-megabyte dictionary files like `locals.js` hosted on `raw.githubusercontent.com`) often fail silently during installation or update in networks with DNS poisoning or CDN throttling. The script manager installs the script header successfully, but the external dependency payload is missing or empty.
- **Silent Exception Suppression**: At runtime, the script's entry guard (e.g. `if (typeof I18N === 'undefined') throw new Error(...)`) throws immediately on line 1 of initialization. Because Chromium extension content scripts execute in an isolated sandbox where `alert()` dialogs are suppressed without rendering to the user, the script crashes silently before injecting CSS, registering menu commands, or translating DOM nodes.
- **Empirical Diagnostic Path via CDP / DevTools**:
  1. Inspect `document.documentElement.lang` and check whether custom styles defined by the script are present in `document.querySelectorAll('style')`.
  2. Inspect the extension's LevelDB (`Local Extension Settings/<extension_id>`) for `compiled_resource` and cached `@require` payloads.
  3. Check console messages for competing scripts/extensions (e.g. simultaneous auto-translators like KISS-Translator or DOM-sanitizing ad-blockers) that mutate or capture target nodes before the userscript's MutationObserver settles.
- Resolution:
  - Prepend a reverse proxy / mirror accelerator (e.g. `https://ghproxy.net/` or fastly jsdelivr) to the `@require` URL in the script editor and force re-fetching external resources (`工具 -> 重新获取外部资源`).
  - Prefer using GreasyFork packaged releases where external dependencies are strictly mirrored or bundled inline.

## 14. Modern Chromium MV3 UserScript Manager Global Failure & Handshake Diagnostics
When a user reports that **all userscripts** across all websites fail to take effect despite being enabled in a Manifest V3 userscript manager (e.g. ScriptCat 1.4+, Tampermonkey 5+):
- **Popup (N/N) Fallacy**: The popup displaying `当前页运行脚本 (1/1)` or active script chips is purely a client-side static URL regex check against `@match` patterns. It is NOT proof that the script or manager runtime was injected into the DOM.
- **Handshake Verification**: ScriptCat injects `scriptcat-inject.js` into the MAIN world and expects a CustomEvent handshake (`requestEventFlag` -> `broadcastEventFlag` over a channel like `0be4e6a5-a95a-4982-ae64-eaed28361dfc`) with `scripting.js` in the USER_SCRIPT world before running user scripts. If dispatching `{action: "requestEventFlag"}` on that channel yields zero response, the extension's scripting runtime failed to inject.
- **Chromium 138+ / Edge 144+ "Allow User Scripts" Switch**:
  - In modern Chromium (e.g. Edge Dev 154), the global "Developer Mode" toggle alone is no longer sufficient.
  - Chromium introduced a per-extension switch **"Allow user scripts" (允许用户脚本)** on the extension's Details page (`edge://extensions/?id=<extension_id>`). If disabled or uninitialized after a browser update, Chromium silently blocks `chrome.userScripts` execution without page-level warnings.
- **MV3 Service Worker Desynchronization & Zombie State**:
  - In MV3, background workers terminate after 30 seconds of inactivity. During browser updates, sudden restarts, or external debugging attachments (CDP), the Service Worker may fail to bind to the browser's `Extension Scripts` LevelDB upon wake-up, leaving dynamic scripts unregistered.
- **Standard Recovery Sequence**:
  1. Go to `edge://extensions` (or `chrome://extensions`).
  2. Toggle the userscript manager (ScriptCat) **OFF then ON** (or click the reload icon 🔄). This kills the zombie Service Worker and forces clean re-registration of dynamic scripts via `chrome.userScripts.register()` and `chrome.scripting.registerContentScripts()`.
  3. Open the extension's **Details** page and verify both **"Allow user scripts"** (if present) and **"Site access: On all sites"** are enabled.
  4. Fully restart the browser process if Chromium's internal `Extension Scripts` LevelDB locks persist.

## 15. Local Gateway `gemini-web-search` Fallacy vs. Hermes Search Engine Routing
When diagnosing search capabilities or encountering `gemini-web-search` in EasyCLIProxyAPI (`18080`):
- **The Alias Fallacy**: In EasyCLIProxyAPI (`cpa-core/config.yaml`), `gemini-web-search` is merely an alias to `gemini-3.1-flash-lite`. In standard OpenAI `/v1/chat/completions` calls, Antigravity/Gemini does NOT trigger Google Search Grounding unless `tools: [{'google_search': {}}]` is explicitly injected in the payload. Unaugmented calls return static cutoff training data.
- **LLM Grounding vs. Agent Tool Invariant**: Even if a chat model has web grounding, it generates conversational prose with inline citations. An Agent's `web_search` tool contract requires structured JSON metadata (`[{'title', 'url', 'description'}]`). Never substitute a grounded LLM for an Agent's search provider.
- **Hermes Built-in Search Hierarchy & Keyless Ring**:
  - Hermes checks `web.search_backend` > explicit credentials (`BRAVE_SEARCH_API_KEY`, `TAVILY_API_KEY`, `EXA_API_KEY`, `SEARXNG_URL`, `ddgs` package).
  - When zero search keys are configured, Hermes automatically routes through its public **Keyless Ring** (`plugins/web/keyless_mcp.py`: Exa -> Parallel -> Firecrawl -> Keenable), defaulting to `exa` via its public MCP endpoint (`https://mcp.exa.ai/mcp`).
  - **Zero-Key Local Fallback**: Installing `ddgs` into Hermes's venv (`pip install ddgs`) enables pure local, credential-free DuckDuckGo search without public MCP rate limits.
  - **Exa Key Activation & Backend Locking**: To graduate from public keyless MCP to dedicated Exa service:
    1. Pre-validate key via `POST https://api.exa.ai/search` with header `x-api-key: <KEY>`.
    2. Persist credential into `~/.hermes/.env` via `save_env_value('EXA_API_KEY', '<KEY>')`.
    3. Lock engine via `hermes config set web.backend exa`, `hermes config set web.search_backend exa`, and `hermes config set web.extract_backend exa`.
  - **Key-Backed Recommendations**: For reliable technical research without public rate limits, configure `brave-free` (2,000 free req/mo via `BRAVE_SEARCH_API_KEY`), `exa` (via `EXA_API_KEY`), or `tavily` (1,000 free req/mo via `TAVILY_API_KEY`).

## 16. Skill Provenance Diagnostics: Bundled vs. Installed vs. Platform Gating
When determining whether a skill on disk was shipped with Hermes or installed later by the user:
- **Official Bundled Manifest**: Check `skills/.bundled_manifest`. It contains the complete, authoritative list of out-of-the-box skills (e.g. `arxiv`, `github`, `hermes-agent`). If a skill is absent, it was not bundled.
- **Lifecycle Metadata (`.usage.json`)**: Check the skill's entry in `skills/.usage.json`:
  - `"created_by": "bundled"` = bundled default.
  - `"created_by": "installed"` = installed via `hermes skills install` or marketplace.
  - Inspect `"created_at"` and `"author"` in frontmatter (e.g. community authors like `gamedevCloudy`) to confirm install history.
- **Windows Platform Gating**: If a skill exists in `skills/` on disk but is absent from `hermes skills list` or `<available_skills>`, check its `SKILL.md` frontmatter `platforms:`. If it specifies only `[linux, macos]` without `windows`, Hermes automatically and silently excludes it on Windows hosts without raising errors.
- **Skill Uninstallation & Cleanup Invariants**:
  - `hermes skills uninstall` accepts only **one** positional argument `name`. Passing multiple names raises `unrecognized arguments`. To remove multiple skills, chain commands: `hermes skills uninstall -y <name1> && hermes skills uninstall -y <name2>`.
  - Always pass `-y` (or `--yes`) in non-interactive/scripted contexts; omitting it triggers an interactive `[y/N]` confirmation that auto-cancels on EOF/closed stdin.

## 17. Hermes Desktop Managed Local Models & Runtime Storage Relocation on Windows (C Drive Space Protection)
When using Hermes Desktop's integrated **Local Models** (`本地模型`) feature (powered by managed `llama.cpp` runtime):
- **Hardcoded Path Invariant**: In `hermes_cli/local_runtime/bootstrap.py`, models are staged at `bootstrap.models_dir()` (`%LOCALAPPDATA%\hermes\models`), and engine binaries land at `runtimes_root()` (`%LOCALAPPDATA%\hermes\runtimes\llamacpp`). The download manager streams `.gguf` and `.part` files directly into `models_dir()` without utilizing Hugging Face Hub cache.
- **The C: Drive Exhaustion Pitfall**: Local GGUF models range from 16 GB (Qwen 27B) to 150+ GB (DeepSeek V4). On Windows systems where the C: drive partition is limited (e.g. ~150 GB total, 40-50 GB free), downloading even a single medium agent model can immediately exhaust system disk space, triggering OS instability or failed downloads.
- **The Non-Invasive NTFS Junction Solution**:
  Because `models_dir()` lacks a config-level override knob, redirect the directories to a secondary drive (e.g. `D:\`) using standard NTFS Directory Junctions (`mklink /J`, which requires **no** administrator privileges):
  ```cmd
  cmd.exe /c "if not exist D:\HermesModels mkdir D:\HermesModels && mklink /J %LOCALAPPDATA%\hermes\models D:\HermesModels"
  cmd.exe /c "if not exist D:\HermesRuntimes mkdir D:\HermesRuntimes && mklink /J %LOCALAPPDATA%\hermes\runtimes D:\HermesRuntimes"
  ```
  - Windows handles transparent kernel-level I/O redirection: all `.part` downloads, completed `.gguf` weights, companion `assets/` (e.g. `mmproj` vision projectors), and `llama-server` engine binaries physically reside on `D:\`, consuming **0 bytes** on C:.
  - Fully transparent to the Hermes Desktop GUI, progress bars, and supervised `llama-server` process; survives Hermes application updates and profile resets.

## 18. OpenViking Context Database & Local Model Dual-Drive Memory Architecture
When integrating OpenViking (`volcengine/OpenViking`) as an external memory provider for Hermes Agent (`hermes memory setup openviking`):
- **Dual-Drive Synchronization Invariant (Git SSOT)**: Git `main` is the Single Source of Truth (SSOT); OpenViking's vector index and L0/L1 summaries are strictly rebuildable derived caches. To prevent index drift across clones, rebases, or direct file edits, employ dual-drive synchronization:
  1. **Instant Trigger**: `.git/hooks/post-commit` and `post-merge` trigger incremental `ov add-resource` or reindex calls.
  2. **Reconciliation Fallback**: Hermes startup and turn probes compare the local/remote HEAD commit SHA against the last indexed SHA and reindex upon drift.
  3. **Strict One-Way Flow**: Content flows exclusively `Markdown/Git -> OpenViking`. OpenViking data must NEVER write back directly to shared Markdown without explicit human/agent review.
- **Namespace Isolation**: Map shared repository knowledge exclusively to `viking://resources/shared-memory`. Keep user-private profile facts, preferences, and agent states strictly isolated within `viking://user/...` namespaces.
- **Zero-Cost Fully Local RAG Pipeline**:
  - **Embedding**: Use Hermes Desktop's managed `llama.cpp` runtime with GPU CUDA acceleration (e.g. RTX 4070 Laptop) to serve lightweight GGUF embeddings (e.g. `bge-small-zh` or `bge-m3`) via `/v1/embeddings`, eliminating cloud API dependency and preventing privacy leaks.
  - **L0/L1 Extraction**: Route OpenViking's VLM/LLM configuration to existing local OpenAI gateways (e.g. WorkBuddy `127.0.0.1:8787/v1` with `glm-5.3-flash`), achieving 100% free local execution.
- **Prompt Contamination Defense**: Hermes prefetch automatically injects recalled context into upcoming user turns. To prevent answer drift in reasoning models (Gemini 3.8 Flash), enforce conservative settings:
  ```env
  OPENVIKING_RECALL_LIMIT=3
  OPENVIKING_RECALL_SCORE_THRESHOLD=0.35
  OPENVIKING_RECALL_PREFER_ABSTRACT=true
  ```



