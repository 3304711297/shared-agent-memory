# Proxy Console Architecture & Tauri v2 Pitfalls

## 1. Windows Subprocess Suppression & Live Log Streaming

### CREATE_NO_WINDOW
On Windows, child processes (especially Python, Node, or CLI executables) spawn an external black terminal console window unless explicitly suppressed. Always apply `CREATE_NO_WINDOW` via `std::os::windows::process::CommandExt`:

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

### Full-Stack UTF-8 Encoding & Lossy Stream Decoding
Windows console runtimes frequently default to the active OEM code page (GBK/CP936 in Chinese locales). Writing stdout to file and reading it in Rust via `std::fs::read_to_string` causes crashes:
`stream did not contain valid UTF-8`

**Rule 1: Force UTF-8 in Child Process Environment**
```rust
cmd.env("PYTHONIOENCODING", "utf-8");
cmd.env("PYTHONUTF8", "1");
```

**Rule 2: Lossy Byte Decoding in Rust File Reader**
Never rely on strict UTF-8 string parsers for live log streams:
```rust
let bytes = std::fs::read(&log_path).map_err(|e| e.to_string())?;
let raw = String::from_utf8_lossy(&bytes);
```

---

## 2. 3-Tier Daemon Tray Architecture & Bi-Directional Event Synchronization

### Menu Structure (GUI-for-Cores Standard)
Align with proxy core managers (GUI.for.SingBox / GUI.for.Clash) using clean, icon-less, grouped menus:
```text
打开主界面
────────────────────────
内核状态：运行中 / 内核状态：已停止   (Disabled status indicator)
停止内核 / 启动内核                 (Dynamically switched)
重启内核                           (Kill, sleep 300ms, respawn)
────────────────────────
退出
```

### Bi-Directional Event Synchronization
A critical pitfall in desktop clients: actions taken in the tray context menu do NOT automatically notify the open WebView window. Users who click "启动内核" from the tray and look at the GUI see a stale "已停止" red indicator and believe the button failed.

**Solution**:
1. **Rust Event Emission**:
   ```rust
   use tauri::Emitter;
   let _ = app_handle.emit("proxy-status-changed", serde_json::json!({ "running": is_running }));
   ```
2. **Frontend Event & Focus Listeners**:
   ```javascript
   if (window.__TAURI__?.event?.listen) {
     window.__TAURI__.event.listen('proxy-status-changed', () => {
       setTimeout(checkHealth, 200);
       setTimeout(checkHealth, 800);
     });
   }
   window.addEventListener('focus', checkHealth);
   document.addEventListener('visibilitychange', () => {
     if (document.visibilityState === 'visible') checkHealth();
   });
   ```

---

## 3. IPC Command Argument Deserialization (Tauri v2)

Tauri v2 enforces camelCase argument naming by default when bridging JavaScript to Rust.
If a Rust command is defined as:
```rust
pub fn agent_configure(agent_type: String, port: u16) -> Result<String, String>
```
Invoking `invoke('agent_configure', { agent_type: 'hermes' })` from JavaScript causes runtime rejection:
`invalid args agentType for command agent_configure: command missing required key agentType`

**Best Practice**:
1. Add `#[tauri::command(rename_all = "snake_case")]` to the Rust command declaration.
2. In JS, supply both keys defensively:
   ```javascript
   invoke('agent_configure', { agent_type: 'hermes', agentType: 'hermes', port: 8787 });
   ```

---

## 4. Reverse-Engineered Model Matrices & Upstream Parameter Tuning

When translating proprietary code assistants (e.g. WorkBuddy/Copilot) into standardized OpenAI endpoints:
1. **Dynamic Model Discovery**:
   Query the provider's `/v2/enterprises/personal/models` endpoint directly using active OAuth tokens to retrieve all 28+ available models.
2. **Clean Multiplier Typography**:
   Official endpoints return varied strings (`x0.06`, `x0.51 credits`). Strip redundant `credits` wording and format via regex:
   ```javascript
   const match = raw.match(/(\d+(?:\.\d+)?)/);
   return match ? `${match[1]}x` : raw;
   ```
3. **Dynamic Reasoning Effort & Thinking Switch**:
   - Extract `reasoning.supportedEfforts` to populate dropdown options (`low`, `high`, `xhigh`, `max`).
   - For models where `canDisableThinking: true`, provide a `🚫 关闭思考` option that injects `chat_template_kwargs: {"enable_thinking": false}` into upstream requests.
