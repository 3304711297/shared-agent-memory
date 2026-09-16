---
name: tauri-desktop-development
description: "做Tauri应用时必用。开发构建调试。Use when developing, building, or debugging Tauri apps."
---

# Tauri Desktop Development

## Verification Before Push (Local-First)

Every CI step in this project's GitHub Actions has a local equivalent. Run them
locally BEFORE committing — waiting ~4.5 min for CI to catch what local would
have caught in seconds is the failure mode to avoid.

| CI step | Local equivalent |
|---|---|
| `npm ci` + `npm run build` | `npm run build` |
| `pytest -q` | `python -m pytest tests/` (venv: `C:\Users\<user>\.workbuddy\binaries\python\envs\default`) |
| `npm test` | `npm test` (node:test runner) |
| `cargo check --locked` | `cargo check --manifest-path src-tauri/Cargo.toml --locked` |
| `cargo test --locked` | `cargo test --manifest-path src-tauri/Cargo.toml --locked` |

Also run `npm run tauri build` when the desktop client artifact must be current
— CI never produces it, and a green CI does NOT mean the local exe/installer is
up to date. When the user asks "把本地构建到最新版了吗", answer directly with the
real artifact status: distinguish frontend `dist/` from full release installer/exe.
Before building, `taskkill /IM <app>.exe /F` (see Pitfall 3 on os error 32).

**Verifying a rebuilt exe actually embeds the new frontend** (post-build check):
grep the exe for the hashed asset filenames from `dist/assets/` (e.g.
`index-BiRZclqE.js`) — those hashes live in Tauri's generated asset manifest and
survive embedding, so a hit proves the build picked up the new `dist/`. Do NOT
grep the exe for frontend *string literals* (Chinese UI text etc.): Tauri embeds
assets **brotli-compressed** (the `brotli` crate appears in `Cargo.lock`), so raw
text never appears in the binary and a miss means nothing. Also expect window
capture to return a 16x16 blank frame when the app is hidden to tray — enumeration
showing `visible=False` on the main `Tauri Window` class is the explanation, not a
fault; verify via asset hashes instead of screenshots.

Only after local is green: commit → push → merge.
**Non-blocking CI Discipline**: Do NOT block the conversation synchronously
waiting for remote CI (`gh pr checks --watch` in foreground) when the local
equivalent suite has already verified 100% green — local and CI test pipelines
are identical. Remote CI is an asynchronous sanity check; run it in the
background via `terminal(command="gh pr checks <PR> --watch", background=true, notify=true)`
and proceed immediately with subsequent tasks instead of freezing the chat.

## Core Patterns & Pitfalls

### 1. WebView Link Opening (Shell Capabilities)
In Tauri v2, `window.open(url, '_blank')` is blocked or silently swallowed by WebView2 sandbox security policies.
- **Do NOT** rely on native HTML `target="_blank"` or `window.open()`.
- **Proper Approach**:
  1. Add `shell:allow-open` in `src-tauri/capabilities/default.json`:
     ```json
     {
       "permissions": ["core:default", "shell:allow-open"]
     }
     ```
  2. Call `window.__TAURI__.shell.open(url)` from JavaScript (or wrap with fallback):
     ```javascript
     async function openExternal(url) {
       if (window.__TAURI__?.shell?.open) {
         await window.__TAURI__.shell.open(url);
         return;
       }
       window.open(url, '_blank');
     }
     ```

### 2. Windows Path & Workspace Conventions
- **User Workspace Placement**: Unless explicitly instructed otherwise by the user (or for internal Hermes runtime plugins), application source code projects MUST be placed under the user's Desktop directory (`C:\Users\<user>\Desktop\<project>`), never under `%LOCALAPPDATA%\hermes\`.
- **Dynamic Executable Path Resolution**:
  When Tauri invokes helper scripts or sidecar binaries (e.g., Python scripts or CLI proxies), never hardcode relative offsets like `../../converter.py`. Resolve dynamically via:
  ```rust
  let exe_dir = std::env::current_exe().ok().and_then(|p| p.parent().map(|p| p.to_path_buf()));
  ```
  Check the executable directory first, then standard workspace fallback paths.

### 3. Tauri Build & Process Cleanups on Windows
- **Locked Target Binaries**: Before running `cargo tauri build`, terminate any running instances of the app (`taskkill /IM <app>.exe /F`) to avoid `os error 32 (The process cannot access the file because it is being used by another process)`.
- **BUILDING IS THE USER'S JOB on this machine — do not engineer around it.** The user builds WorkBuddy2API themselves with `npm run tauri build` (from the repo root, PowerShell). Do NOT invent isolated-target-dir builds, in-place-swap scripts, or any other scheme to build "without disturbing the session": the daemon is a child of the GUI, so any restart cuts the session — the user accepts that and owns the timing. **After changing code, just say so ("可以构建了") and stop.** Writing a build/swap helper for them is wasted work at best; at worst it produces an exe with no embedded frontend (see below) and wastes a rebuild cycle.
- **Why the shared target dir is the correct approach for the user's build:** `npm run tauri build` uses the normal `src-tauri/target`. An isolated `CARGO_TARGET_DIR` adds a 1.5 GB duplicate tree and, if you then run a plain `cargo build --release` in it, silently replaces the good artifact with a frontend-less one.
- **`cargo build --release` produces a SILENTLY BROKEN exe — always `cargo tauri build`.** `Cargo.toml` ships `[features] custom-protocol = ["tauri/custom-protocol"]`, which only the tauri CLI enables. A plain cargo release build links without it, so Tauri treats the app as *dev* mode: `frontendDist` is never embedded and the window loads `http://localhost:5173` instead (users see `ERR_CONNECTION_REFUSED` on a machine with no Vite server). It still prints `Built application at: ...` and exits 0. Tell them apart by size and embedded asset names:
  - correct tauri artifact ≈ **15,641,088 bytes** for this app; the broken plain-cargo one ≈ **15,572,992 bytes** (≈68 KB smaller).
  - decisive check (run from the repo root) — the hashed bundle filename is stored uncompressed in the asset manifest:
    ```powershell
    $js=(Get-ChildItem dist\assets -Filter 'index-*.js').Name
    $exe="src-tauri\target\release\workbuddy2api.exe"
    if([Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($exe)).Contains($js)){"OK: $js"}else{"FAIL: no frontend embedded"}
    ```
  - the frontend's own *string literals* are brotli-compressed and will NOT be found — asset filenames are the reliable marker, and `__BUILD_FINGERPRINT__` values like the git hash appear only in `dist/`, never in the exe.
- **A venv `python.exe` launcher + real interpreter is ONE logical process, not two.** On Windows, `<venv>\Scripts\python.exe` is a small (~240KB) forwarder that re-execs the base interpreter, so a spawned daemon legitimately shows up as a **parent/child pair with identical command lines** (the launcher has ~1 thread and a few MB RSS; the real one owns the listening socket). Do not diagnose it as a leftover/duplicate process and do not "clean it up" — distinguish them by thread count, working set, and which PID holds the port.
- **Target Folder Rebuilds**: If a project folder is moved, old build caches may retain absolute references to plugin metadata under the previous path. Run `cargo clean` prior to rebuilding.
- **GUI Launching in Terminal**: In Git Bash/terminal sessions on Windows, running `target/debug/<app>.exe` or `target/release/<app>.exe` directly in the foreground blocks CLI execution indefinitely. Furthermore, calling `start ""` inside Git Bash MSYS shells often fails to detach Windows GUI applications cleanly. Always use:
  ```powershell
  powershell -Command "Start-Process -FilePath '<absolute_path_to_exe>' -WorkingDirectory '<working_dir>'"
  ```
- **Desktop Shortcut Creation**: When delivering desktop applications to users, create a standard Windows `.lnk` shortcut on their Desktop pointing to `src-tauri/target/release/<app>.exe` via `WScript.Shell`:
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('C:\Users\<user>\Desktop\<AppName>.lnk'); $Shortcut.TargetPath = '<exe_path>'; $Shortcut.WorkingDirectory = '<dir>'; $Shortcut.Save()"
  ```
### 4. System Tray & Window Close Policies (Tauri v2)
Desktop proxy and utility apps frequently require running silently in the background rather than terminating when the main window is closed.
- **CloseRequested Interception**:
  In `on_window_event`, intercept `WindowEvent::CloseRequested`. To hide to tray instead of quitting, call `api.prevent_close()` and `window.hide()`.
  ```rust
  .on_window_event(|window, event| {
      if let WindowEvent::CloseRequested { api, .. } = event {
          match config.close_action {
              CloseAction::HideToTray => {
                  api.prevent_close();
                  let _ = window.hide();
              }
              CloseAction::Quit => {
                  // Stop child processes / daemons before exiting
                  if let Some(handle) = window.app_handle().try_state::<ProxyHandle>() {
                      let _ = commands::proxy_stop(handle);
                  }
              }
          }
      }
  })
  ```
- **Tray Left-Click & Menu Toggles**:
  Configure `TrayIconBuilder` with a menu (e.g., "打开主界面" / "退出程序"). For single left-clicks, toggle visibility via:
  ```rust
  .on_tray_icon_event(|tray, event| {
      if let TrayIconEvent::Click { button: MouseButton::Left, button_state: MouseButtonState::Up, .. } = event {
          if let Some(window) = tray.app_handle().get_webview_window("main") {
              if window.is_visible().unwrap_or(false) {
                  let _ = window.hide();
              } else {
                  let _ = window.show();
                  let _ = window.unminimize();
                  let _ = window.set_focus();
              }
          }
      }
  })
  ```
- **3-Tier Daemon / Core Lifecycle Tray Architecture (GUI.for.Cores Pattern)**:
  For local proxies, daemons, and bridge clients, users strongly prefer the 3-tier tray menu pattern with `PredefinedMenuItem::separator`:
  1. *View Tier*: `打开主界面`
  2. *Core Lifecycle Tier*:
     - Status Indicator (read-only / disabled): `内核状态：运行中` vs `内核状态：已停止`
     - Action Toggle: `停止内核` vs `启动内核` (dynamically switched based on process state)
     - Hot Restart: `重启内核` (cleanly kill child process, sleep 300ms, and respawn)
  3. *Exit Tier*: `退出` (kills child daemon before calling `app_handle.exit(0)`)
  - *Dynamic State Probing*: Check child process liveness (`child.try_wait().map(|s| s.is_none()).unwrap_or(false)`) inside `on_tray_icon_event` and `on_menu_event`, calling `status_item.set_text(...)` and `toggle_item.set_text(...)` so the menu labels are always accurate when opened.
  - *Bi-directional Tray-to-Webview Synchronization (Pitfall)*: When a user starts, stops, or restarts a daemon from the tray context menu, the main WebView window does NOT automatically detect the change if it only polls occasionally. Users switching back to the GUI will see stale indicators and complain that "tray operations have no effect".
    - **Backend Event Emission**: In the tray menu handler, broadcast an event using `tauri::Emitter`:
      ```rust
      use tauri::Emitter;
      let _ = app_handle.emit("proxy-status-changed", serde_json::json!({ "running": is_running }));
      ```
    - **Frontend Event Catching**: In frontend JS, immediately listen and re-check daemon health:
      ```javascript
      if (window.__TAURI__?.event?.listen) {
        window.__TAURI__.event.listen('proxy-status-changed', () => {
          setTimeout(checkHealth, 200);
          setTimeout(checkHealth, 800);
        });
      }
      ```
    - **Focus & Visibility Probes**: Add `window.addEventListener('focus', checkHealth)` and `document.addEventListener('visibilitychange', ...)` so restoring from tray instantly updates the UI, and keep background health polling responsive (~3s interval).
- **IPC Command Parameter Casing (Pitfall)**:
  Tauri v2 command macro `#[tauri::command]` enforces camelCase argument deserialization by default. If a Rust command is defined with `fn agent_configure(agent_type: String)`, invoking it from JS with `{ agent_type: "hermes" }` triggers runtime rejection: `invalid args agentType for command ...: command missing required key agentType`.
  - **Resolution**: Annotate the Rust command with `#[tauri::command(rename_all = "snake_case")]`, and pass dual keys in JS (`{ agent_type: val, agentType: val }`) for defensive forward/backward compatibility.
  - **Silent variant — `Option<T>` params fail with NO error at all (the dangerous one)**: when the Rust param is `Option<T>`, a wrong-case key is deserialized as `None` instead of rejecting the call. The frontend looks correct, testing passes, and the feature is simply dead. Real case: `usage_events(since_ms: Option<i64>, page_size: Option<usize>)` invoked as `{ since_ms, page_size }` → time-range filtering silently did nothing; `snapshot_replay(api_key: Option<String>)` invoked as `{ api_key }` → 401 whenever a client key was configured.
    - **Verify the contract, don't infer it from Rust signatures**: `tauri-macros`' `wrapper.rs` defaults to `ArgumentCase::Camel` and does `key = key.to_lower_camel_case()`. Fastest ground truth is grepping the built exe for the literal key names — the generated IPC key strings survive into the binary:
      ```bash
      # camelCase key present / snake_case absent ⇒ camelCase is the wire contract
      python -c "d=open('src-tauri/target/release/<app>.exe','rb').read(); print([(k, d.count(k)) for k in (b'sinceMs', b'since_ms', b'pageSize', b'page_size')])"
      ```
    - **Never write Rust parameter names into docs as if they were IPC keys.** A doc line `usage_events(model, status, since_ms, page, page_size)` gets copied verbatim into frontend `invoke` payloads and silently poisons every caller. Document the **camelCase wire key**, and note the Rust param separately.
    - **Static string assertions can lock a bug in**: a test asserting the source merely *contains* `since_ms` will stay green while the feature is broken. Assert the negative too (`!/since_ms|page_size/`), or better, derive the expected keys from the Rust signature / built binary.

### 5. Windows Subprocess Window Suppression (`CREATE_NO_WINDOW`) & Embedded Live Logging
When a desktop GUI application launches backend CLI tools, Python runtimes, or proxies, Windows defaults to creating a visible black console (CMD) window for child processes unless explicitly suppressed. Users generally dislike intrusive black CMD popups and expect all runtime/debug logs to be accessible directly inside the GUI console itself.
- **Silent Background Launch**:
  Import `std::os::windows::process::CommandExt` and apply `CREATE_NO_WINDOW (0x08000000)`:
  ```rust
  #[cfg(target_os = "windows")]
  {
      use std::os::windows::process::CommandExt;
      const CREATE_NO_WINDOW: u32 = 0x08000000;
      if !show_debug_console {
          cmd.creation_flags(CREATE_NO_WINDOW);
      }
  }
  ```
- **Embedded Live Console vs External CMD**:
  Instead of forcing users to look at an external console window or popups:
  1. Redirect child process `stdout` and `stderr` to a dedicated application log file (e.g., `%LOCALAPPDATA%/<app>/proxy_stdout.log`):
     ```rust
     let log_file = std::fs::OpenOptions::new().create(true).write(true).append(true).open(&log_path)?;\n     let log_err = log_file.try_clone()?;\n     cmd.stdout(Stdio::from(log_file)).stderr(Stdio::from(log_err));
     ```
  2. **UTF-8 Encoding & Lossy Decoding Safeguard (Pitfall)**:
     On Windows, child runtimes (especially Python) frequently default to system code page (e.g. GBK/CP936) output, causing `std::fs::read_to_string` in Rust to crash with: `stream did not contain valid UTF-8`.
     - **Force UTF-8 Environment**: In Rust, inject UTF-8 environment variables before spawning:
       ```rust
       cmd.env("PYTHONIOENCODING", "utf-8");
       cmd.env("PYTHONUTF8", "1");
       ```
     - **Lossy Fallback in File Reading**: Never call `read_to_string`. Read raw bytes and decode using `String::from_utf8_lossy(&bytes)`:
       ```rust
       let bytes = std::fs::read(&log_path).map_err(|e| e.to_string())?;
       let text = String::from_utf8_lossy(&bytes);
       ```
  3. Provide an in-app **"实时日志" (Live Logs)** navigation page or tab with auto-polling (e.g., every 2s via `proxy_get_logs`), tailing the last ~80KB of logs, autoscrolling, and "刷新 / 清空" controls.
  4. Keep the external CMD popup option as a secondary toggle in settings, defaulted to OFF.

### 6. Dynamic Model Matrices & Reasoning Parameter Overrides
When bridging upstream AI platforms (e.g. WorkBuddy, Copilot, or multi-model proxies) to OpenAI endpoints in a desktop GUI:
- **Never Hardcode Static Model Lists**: Static lists quickly become outdated. Expose an IPC command (`models_fetch_all`) that queries the upstream provider's model directory endpoint (e.g., `/v2/enterprises/personal/models`) using current credentials, extracting official credit multipliers (`credits`), maximum input/output token limits, and supported reasoning parameters.
- **Support In-App Parameter Tuning**:
  1. **Credit Multipliers Formatting**: Do NOT display redundant units like `credits` or inconsistent prefix formatting (e.g. `x0.51 credits` vs `x0.06`). Reverse engineering confirms official client code extracts the numeric value via regex `/(\d+(?:\.\d+)?)/` and standardizes it with a clean `x` suffix (`0.06x`, `0.51x`, `1.62x`, or green `免费 (0.00x)` badge) for concise, uniform typography.
  2. **Context Window Sliders/Inputs**: Allow users to set per-model context token limits (e.g., 1024 to hardware max) saved in a local config (`model_settings.json`), auto-enforcing `max_tokens` clipping during proxy forwarding.
  3. **Thinking/Reasoning Mode Control**: For reasoning-capable models, dynamically populate reasoning effort options (`low`, `high`, `xhigh`, `max`) from metadata, and provide a `🚫 关闭思考` option that injects `chat_template_kwargs: {"enable_thinking": false}` into upstream requests.

### 7. Local Daemon & Microservice Resilience
When desktop plugins or panels depend on a background microservice running on a local loopback port (e.g. `fetch_quota.py --serve` on `127.0.0.1:18088`):
- **Ghost Socket Hangs**: If a background process is terminated improperly during update cycles or file-lock clearance, Windows may leave the socket unresponsive or hung in `TIME_WAIT`/deadlock, surfacing UI alerts like `刷新配额失败：本地微服务未响应`.
- **Clean Recovery Workflow**: Query the port owner (`netstat -ano | grep <port>`), kill lingering PIDs (`Stop-Process -Force`), relaunch via detached silent `pythonw.exe <script> --serve`, and immediately probe `/quota?force=1` for an HTTP 200 payload.

### 8. Network Exposure Security Boundaries & Authentication Enforcing
When a local desktop proxy/daemon exposes an HTTP API (e.g. converting upstream services to an OpenAI-compatible API):
- **Host Header Defense-in-Depth vs Access Control**: `Host` header inspection (like rejecting non-loopback Host values) defends solely against web browser DNS rebinding attacks. It does NOT provide network access control, as any remote attacker in the local network can spoof `Host: 127.0.0.1`.
- **Enforce Mandatory Authentication on Non-Loopback Binding**: When the server binds to `0.0.0.0` or a public/LAN interface, refuse to start without an API key unless an explicit flag like `--unsafe-expose` is provided.
- **Unified Credential Source of Truth**: When both a desktop UI multi-account store (`accounts.json`) and an auth file (`.info`) exist, prioritize the active account in the UI store to prevent credential drift between chat forwarding and billing/quota summary endpoints.
- **Log Sanitation & Log Levels**: Avoid dumping raw prompt/completion payloads by default. Use a 3-tier log level (`info` for latency/summary, `debug` for error bodies, `trace` for raw streams) and apply regex masks on tokens, authorization headers, and cookies to prevent credential leakage to disk.

### 9. Environment Proxy Bypass for Loopback & Direct Upstreams (`no_proxy`)
`reqwest` / HTTP clients automatically inherit system/environment proxies (`ALL_PROXY`, `HTTP_PROXY`). If a local proxy client (e.g. Karing on `127.0.0.1:3067`) is listening but disconnected from an outbound node, requests to `127.0.0.1` health endpoints or domestic direct upstreams hang or timeout, causing false-positive "proxy kernel failed to start".
- **Rule**: Build loopback and direct-connect HTTP clients with `.no_proxy()` explicitly:
  ```rust
  reqwest::Client::builder().no_proxy().timeout(Duration::from_secs(10)).build()
  ```

### 10. Atomic Multi-Process State Persistence (`.tmp` + sync_all + Rename)
Direct file overwriting via `std::fs::write(&path, ...)` or Python `open(path, 'w')` risks file truncation and JSON parse corruption if the app crashes, reboots, or is read concurrently by backend daemons.
- **Rule**: Write to a `.tmp` file in the same directory, flush to disk media via `file.sync_all()`, close the file handle (releasing Windows locks), then execute an atomic rename (`std::fs::rename` in Rust / `os.replace` in Python). On error, remove the `.tmp` file to leave no residue and preserve the original intact.

### 11. Subprocess Termination: Direct PID Tree Kill & Bounded Wait
Never use `powershell Get-CimInstance Win32_Process ... Where-Object CommandLine -like '*name*'` to kill background daemons on Windows. WMI scanning takes 1-2s and risks killing other projects running same-named scripts.
- **Rule**: Track the child PID from `child.id()` and terminate the exact process tree via native `taskkill /F /T /PID <pid>`. Check exit status (non-zero is Err). Never call indefinite `child.wait()` on an alive process; use a bounded polling loop (`try_wait()` with timeout ~600ms), fallback to `child.kill()` if needed, and retain the Child in state if termination fails so the process remains tracked.

### 12. Dual-Channel SSE Streaming: Reasoning, Content & Tool Calls Coexistence
In streaming / SSE adapters, never use exclusive branching like `if tool_calls: ... elif content:`.
- **Rule**: When models generate text content, reasoning tokens (`reasoning_content`), and tool calls in the same turn, stream `reasoning_content` and `content` chunks before or alongside `tool_calls` chunks; otherwise agent explanations are silently swallowed.

### 13. DOM ID Scoping Across Static & Dynamic Tabs
In vanilla JS desktop webviews, giving the same `id` (e.g. `btn-refresh-usage`) to both a static tab button and a dynamically rendered card element in another tab causes `document.getElementById` to target the first element in DOM, attaching duplicate or conflicting listeners.
- **Rule**: Scope element IDs per domain (`btn-refresh-account-quota` vs `btn-refresh-usage`) or use `data-action` with container-level event delegation.

### 14. Window Resize Debouncing: Single-Worker with `latest` Mutex Source of Truth
Spawning a new thread on every `WindowEvent::Resized` causes severe thread storming during rapid drag operations on Windows.
- **Rule**: Use a persistent background Worker thread coupled with a notification Channel (`SyncSender<()>`). The latest dimensions are stored in an `Arc<Mutex<(f64, f64)>>`. The channel carries only lightweight signals (`()`) to reset the ~500ms debounce timer. Even if rapid resize events overflow the channel and drop notifications, the worker strictly reads from the `latest` Mutex upon debounce timeout, guaranteeing 100% final state consistency with zero thread churn.

### 15. CSP `script-src 'self'` Kills Inline Event Handlers — Externalize ALL of Them
Tauri's `app.security.csp` commonly sets `script-src 'self'` (no `'unsafe-inline'`, and no nonce unless the HTML literally contains the `__TAURI_SCRIPT_NONCE__` token for Tauri to replace — check with a plain grep/count, an absent token means zero exemption).
- **Consequence**: any `onclick="..."` in a template string or in `index.html` is blocked at runtime, producing **no error the user can see** — the control is simply dead. It works in a plain browser / `vite dev`, so it passes every manual check and every static source assertion.
- **Real case**: a first-run empty-state CTA rendered via `innerHTML` with `onclick="document.querySelector('.nav-item[data-tab=...]').click()"` — the only inline handler in the whole app, left behind when the app had already externalized its inline theme script for exactly this reason.
- **Rules**:
  1. Never emit `on*=` attributes from JS templates. Use `id` + `addEventListener`, or container-level event delegation (`data-act` + `closest('[data-act]')`) — the delegation pattern also survives `innerHTML` rebuilds without leaking listeners.
  2. Add a regression assertion so it cannot come back: scan the sources for `/\son(?:click|change|input|submit)\s*=/` and fail if found (with a guard asserting the CSP really lacks `'unsafe-inline'`, so the test self-invalidates if the CSP is ever relaxed).
  3. When auditing for this class, grep the **built bundle** too, not just the source — it confirms the handler actually shipped.

### 16. Cross-Layer Field Contracts: Assert Producer Fields, Not Just Consumer Code
A frontend consumer reading `h.ok` / `h.input_tokens` while the Rust producer's hourly bucket only emitted `ts/requests/output_tokens` yields silent zeros — a statistics card that permanently reads “成功 0 · 失败 0” with no error anywhere.
- **Rule**: for every aggregated payload, keep one test that extracts the fields the JS actually accumulates (`matchAll(/h\.([a-z_]+)/g)`) and asserts each appears in the producer's JSON construction. This catches drift in **both** directions (renamed producer field, or new consumer field) and is mutation-testable: delete the producer field, the test must go red.
- Prefer extending the producer over degrading the consumer when the consumer's semantics are the product intent (e.g. “stats card follows the selected range”), then lock the new field with a producer-side assertion.

### 17. Vanilla-JS Frontend: Test the MECHANISM, Not the Identifier
In a plain-JS Tauri frontend there is no component framework to hitch tests on, and the
tempting test form — `assert.ok(src.includes('pollInFlight'))` — is nearly worthless:
renaming the guard to `pollInFlightXX` still passes it, so it only catches whole-block
deletion and silently green-lights real regressions. Measured on a real audit: of 17
mutations to newly added guards, that style caught **6**. The same 104 include-style
assertions had previously passed a dead CSP-blocked button and a dead refresh button.

**Three test tiers, in order of value:**

1. **Behavioral (best).** Real modules with stubbed globals. It works: modules only touch
   `document`/`window` inside functions, so installing stubs before calling them is enough.
   - Keep one stub helper (`tests/helpers/dom-stub.mjs`) that **caches elements by id** —
     a fresh object per `getElementById` call splits "register listener" from "fire
     listener" and the test silently no-ops.
   - Expose a `dispatch(event)` on stub elements so tests drive real handlers.
   - Node ≥20 makes `navigator`/`crypto` **getter-only globals**: override with
     `Object.defineProperty(globalThis, name, {value, writable: true, configurable: true})`.
   - Wait for conditions (`waitFor(() => calls.length >= 1)`), never fixed `sleep(300)` —
     timer-driven code needs wall-clock guarantees you can't guess.
   - **Never append a cache-busting query to a module that SHARES module-level state.**
     `import('./utils.js?t=1')` from the test while the code under test does
     `import('./utils.js')` yields two instances; a `showConfirm` promise then never
     settles and the suite hangs until timeout. Same-path import = same instance.
   - Any module that starts an interval needs an exported `stopX()` for test teardown,
     or `node --test` never exits (symptom: tests all pass, process hangs).
2. **Structural (cheap breadth).** Assert *relationships*, not names: a bump **and** a
   comparison for sequence guards (`/\+\+_seq/` **and** `/[!=]==_seq/`), a `= true` **and**
   a `= false` for in-flight flags, ordering (clear-before-branch), and negative forms
   (`!/navigator\.clipboard\.writeText/`).
3. **Include-only (avoid).** Only acceptable for literal user-facing copy that must ship.

**Always strip comments before structural assertions.** Fix-explaining comments quote the
rejected pattern verbatim (`// 不再用 display: none`, `// 清空提到「暂无数据」之前`), so
naive greps match the *comment* and both false-fail and mask the real site. Also scope
`indexOf` to the right function — `indexOf('function renderUsage')` matches
`renderUsageEvents` first because it appears earlier in the file; use `search(/...\(/)`.

**Mutation-verify every assertion** (revert the source to the defect shape; the test must
fail). An assertion you never watched fail is not evidence. Accept that this is
iterative: expect your first cut to catch ~1/3 of mutations and refine from there.

**Behavioral tests earn their keep by finding real bugs the static passes missed** — e.g.
a `let x = null` interval handle that was declared but never assigned, so the timer could
never be cleared (only surfaced because the test process refused to exit).

**A leaking timer is an environment bug, not just a test bug.** The same defect shape
(a handle declared but never assigned, or never cleared on the error path) leaves an
interval running after its owner is gone. Detect it structurally: every
`setInterval`/`setTimeout` needs a matching `clearInterval`/`clearTimeout` on **all**
paths including early returns, and the module needs an exported `stopX()` so tests can
tear down. The tell in tests is a suite that reports every test passing yet **never
exits** — treat "tests pass but the process hangs" as a real finding, not harness noise.

### 18. Instrumented Console Commands: Audit Authorization Per Call Site
When a desktop console proxies to its own local daemon over HTTP, every forwarding command
must carry the configured credential — and this is exactly the kind of thing that regresses
silently, because it **only breaks once the user enables the security feature**. With a key
configured (or LAN exposure on, which usually *requires* a key), the unauth'd commands 401
and the UI either shows a raw error or, worse, degrades to an empty state that looks like
"no data".
- **Rule:** enumerate every `local_client(...).get/post(...)` call site and assert each either
  attaches `Authorization` or has a documented reason not to.
- **Corollary:** do not collapse `401` into the same branch as `404`/connection-refused. The
  first means "fix the key" (user action required); the others mean "old daemon / not running"
  (degrade quietly). Merging them makes the failure unactionable. Model them as separate
  variants of a `ForwardFailure`-style enum and only degrade on the latter set.
- **Verify end-to-end with a throwaway daemon:** start the backend on a *different* port with
  a key set, then curl each endpoint with and without the header (expect 401 → 200). This
  proves the fix direction without touching the user's running instance.

**Corollary — the failure classifier must exclude success itself.** When you introduce a
helper like `classify_status(code) -> ForwardFailure` to split 401 from 404, do NOT map
*every* code into that failure enum. Callers naturally write
`if let Some(msg) = forward_failure_message(status) { return Err(msg) }`, so a 200 that lands
in the enum turns a success into an error. Real case: the check-in button showed
`签到请求失败: 内核返回 HTTP 200` and was fully dead, while every unit test stayed green
because they only asserted the 401/404 branches.
- Make the classifier return `Option<Failure>`, with `None` for **all** 2xx (`!(200..300).contains(&code)`),
  and have the message helper short-circuit through it (`classify_status(code)?`).
- Test success explicitly, not just failure: assert `classify_status(200) == None` and that
  200/201/202/204/299 produce **no** failure message. Mutation-check it by forcing the
  predicate to `true` — the success tests must go red.
- When fixing a classifier, grep every call site for the *old* value shape. Changing a
  return type from `T` to `Option<T>` silently breaks `matches!(x, Variant)` guards into
  always-false and `match x { Variant => ... }` into a non-exhaustive compile error.

**Client-side key resolution must mirror the daemon's own precedence chain.** When the daemon
accepts a key from several sources (GUI config, env var, legacy env name), a forwarding client
that reads only the GUI config will 401 the moment the daemon is started with a key supplied
any other way — even though the two are "the same" feature. Enumerate the daemon's sources in
order (here: `GUI 配置 > 继承环境变量 > 无鉴权`, legacy name `CODEBUDDY2OPENAI_KEY`) and assert
each tier with a unit test, including the operator precedence (`resolve_api_key("", Some(env))`
→ `env`). Note the trapless inverse too: a GUI left *empty* deliberately does not clear the
parent process's env var, so "GUI shows no key" ≠ "no auth".

### 19. Tauri ACL: A Command Existing in the Catalog Is Not Permission
`core:window:allow-set-background-color` (and similar) are real permissions but are **not**
all in `core:window.default_permission`. Calling such an API from JS rejects at runtime, and
because these calls are decorative they're typically wrapped in `.catch(() => {})` — so the
feature silently never works (e.g. native window background never follows the theme).
Check `src-tauri/gen/schemas/acl-manifests.json` for the permission identifier, then confirm
it is actually listed under the plugin's `default_permission.permissions`; if not, add it
explicitly to `src-tauri/capabilities/default.json`.

## References & Deep-Dives
- `references/proxy-console-architecture-and-pitfalls.md` — Detailed recipes and code patterns for subprocess window suppression (`CREATE_NO_WINDOW`), full-stack UTF-8 stream decoding, 3-tier daemon tray management with bi-directional event broadcast, Tauri v2 snake_case IPC deserialization, upstream model matrix reverse-engineering, and local network security boundary enforcement.



