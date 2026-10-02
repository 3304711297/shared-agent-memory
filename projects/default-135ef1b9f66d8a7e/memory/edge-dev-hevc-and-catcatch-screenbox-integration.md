# Edge Dev HEVC Decode Breakdown and Cat-Catch Screenbox Protocol Integration

## 1. Edge Dev (Chromium 150+) HEVC Decoder Disconnect

### Root Cause & Diagnostics
- Video stream encoded in HEVC / H.265 (Main Profile, NVENC) fails playback in Edge Dev on Windows with:
  ```json
  {"code": 3, "message": "PipelineStatus::PIPELINE_ERROR_DISCONNECTED"}
  ```
- **Architectural divergence**:
  - **Edge on Windows**: Relies on `MediaFoundationVideoDecoder` -> Windows MFT (`MediaFoundationServiceBroker`). When AppX license validation fails (or during Chromium preview IPC regressions), the media broker process fails to attach or drops the pipe unexpectedly, causing `PIPELINE_ERROR_DISCONNECTED`.
  - **Chrome on Windows**: Utilizes `D3D11VideoDecoder` calling D3D11VA (DXVA) directly to GPU hardware decoders (NVDEC), completely bypassing Windows Media Foundation and Microsoft Store license checks.
  - **UWP / LibVLC Players (e.g. Screenbox)**: Package their own FFmpeg / LibVLC decode pipeline and hardware render paths, immune to Edge browser sandbox restrictions.

## 2. Cat-Catch (猫抓) Protocol Invocation Pitfall

### Navigation Parameter Invariant
- In the cat-catch extension, `.invoke` triggers:
  ```javascript
  const url = templates(G.invokeText, data);
  chrome.tabs.update({ url: url });
  ```
- **Strict Single-Line Constraint**: `G.invokeText` must evaluate to a valid URI string. Introducing newlines (`\n`) creates an invalid URL that Chromium silently rejects, rendering the invoke button completely unresponsive.
- **Two Distinct Action Entrypoints in Cat-Catch**:
  1. **Preview / Player (`G.Player`)**: Configured under "Other Settings" (`anchorOtherSettings`) -> "Preview Mode" / `Player`. Triggers when the user clicks the `▶` Play button next to any media entry.
  2. **External Tool Invoke (`G.invokeText`)**: Configured under "Invoke App" (`anchorInvokeApp`) -> `invokeText`. Triggers when the user clicks the `🚀` / computer invoke button (used for download tools such as `N_m3u8DL-RE`).

## 3. Screenbox Custom URL Protocol Integration (`screenbox:`)

### Architecture
- Screenbox (`18496Starpine.Screenbox_rm8wvch11q4my!App`) is a packaged UWP application without native CLI URL stream arguments.
- A custom Windows protocol handler `screenbox:` was registered in `HKCU\Software\Classes\screenbox`:
  - Shell command executes `%LOCALAPPDATA%\hermes\tools\python-...\pythonw.exe "%LOCALAPPDATA%\hermes\scripts\invoker\screenbox_invoker.py" "%1"`
  - `screenbox_invoker.py`:
    1. Unquotes and extracts the pure video stream URL.
    2. Writes the URL to the Windows system clipboard via Win32 `OpenClipboard`/`SetClipboardData`.
    3. Finds and restores the Screenbox UWP window (`ShowWindow(hwnd, SW_RESTORE)` + `SetForegroundWindow(hwnd)`) or launches `shell:appsFolder\18496Starpine.Screenbox_rm8wvch11q4my!App`.
    4. Displays a lightweight Windows Toast notification confirming stream readiness.
- In cat-catch, setting `G.Player` to `screenbox:${url}` provides seamless single-click transition from browser media sniffing to full hardware-accelerated playback in Screenbox.
