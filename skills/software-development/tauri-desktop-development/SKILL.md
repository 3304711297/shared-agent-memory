---
name: tauri-desktop-development
description: Use when developing, building, or debugging Tauri apps.
---

# Tauri Desktop Development

## Overview
Guidelines and best practices for developing, debugging, and migrating Tauri v2 desktop applications on Windows, covering WebView sandboxing, native OS process launching, build artifact paths, and desktop workspace layout.

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

## References & Deep-Dives
- `references/proxy-console-architecture-and-pitfalls.md` — Detailed recipes and code patterns for subprocess window suppression (`CREATE_NO_WINDOW`), full-stack UTF-8 stream decoding, 3-tier daemon tray management with bi-directional event broadcast, Tauri v2 snake_case IPC deserialization, and upstream model matrix reverse-engineering.



