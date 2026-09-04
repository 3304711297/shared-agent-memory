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

## 8. Desktop Quota Monitor Plugin Architecture (`token-stats`) & UI Design Rules
When running Hermes Desktop with the `token-stats` status-bar quota chip for Google / Antigravity:
- **Legacy Trap**: Earlier iterations depended on ZCode-Antigravity's private `/v0/management/api-call` hook and `%LOCALAPPDATA%\ZCodeAntigravity\auth`. Upstream official CLIProxyAPI (7.2.149 in EasyCLIProxyAPI) does not ship that custom endpoint, and polling `/v0/management/` using API keys triggers a 30-minute anti-bruteforce IP ban on `127.0.0.1`.
- **Direct Quota Architecture**:
  - `fetch_quota.py` directly reads plaintext Google OAuth tokens from `D:\EasyCLIProxyAPI\auth\antigravity-*.json` (no DPAPI decryption needed).
  - Queries Google's official Antigravity Quota endpoint: `https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary` (via proxy `127.0.0.1:3067`). **Critical Distinction**: Google maintains two separate quota pools under the same OAuth token — `daily-cloudcode-pa` is the dedicated Antigravity quota bucket (used by Antigravity / EasyCLIProxyAPI GUI); querying generic `cloudcode-pa` reaches an unrelated CloudCode pool and returns completely mismatched quota fractions (e.g. 100%/43% vs. 74%/87%).
  - Runs a local lightweight microservice on `127.0.0.1:18088/quota` (with CORS and 30s cache) registered as Windows Scheduled Task `Hermes_Quota_Service` (`pythonw.exe`).
  - `desktop-plugins/token-stats/plugin.js` queries `http://127.0.0.1:18088/quota` cleanly, displaying 5h limit %, weekly limit %, and reset countdowns without touching the proxy's management port.
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
- **Remote CI Verification Iron Law**: When pushing commits or doc changes to any repository configured with GitHub Actions CI (e.g. `youshouldknow`, `tweakbyjie`):
  - Local build passing or `git push` exiting with 0 is NOT sufficient evidence to claim completion.
  - The agent MUST actively poll or watch the remote CI pipeline (`gh run watch <run_id> --repo <repo>` or `gh run list --repo <repo>`).
  - Verify that the workflow status empirically reports `completed` and `success` (100% green).
  - Never end the turn, celebrate, or declare work complete until all remote CI workflows have verified successfully.



