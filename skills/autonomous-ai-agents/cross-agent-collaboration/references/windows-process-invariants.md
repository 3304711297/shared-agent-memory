## 9. Windows MCP Process Tree, Lazy Startup & Orphan Teardown Invariant
In Windows, Agent GUIs (Hermes Desktop / ZCode) spawn stdio MCP servers through deep process trees:
`Agent GUI -> cmd.exe -> npx/uvx -> node.exe / serena.exe`.
Because Windows does not cascade process termination to grandchildren upon GUI window close without an explicit Windows Job Object, grandchildren become orphaned background zombies (CPU 0%, but holding 300MB~500MB RAM across multiple restarts).

### Dual-Tier Defense Architecture
1. **Tier 1: Hermes Native On-Demand Lazy Connect & Idle Recycle (In-App Hygiene)**:
   Never run heavy stdio MCP servers in persistent eager mode. In Hermes `config.yaml` (`mcp_servers.<name>`), configure:
   - `lazy: true`: Enables cold-on-demand start. Hermes registers tools at startup from its local schema cache (`cache/mcp_schema_cache.json`) with **zero subprocesses spawned** (0 Node, 0 Serena, 0 Python), achieving instant boot and zero idle RAM. The process is spawned only on the first actual tool call.
   - `idle_timeout_seconds: 60`: If no tool calls occur for 60 seconds, Hermes automatically triggers a clean `recycle`, terminating the stdio subprocess and freeing all memory/handles until the next call.
2. **Tier 2: System-Level Targeted Whitelist Reaper & Agent Guard (Exit Failsafe)**:
   When cleaning up or automating post-exit shutdown, never blindly `taskkill /IM node.exe` (which kills user web servers, Vite, Next.js). Target exclusively verified MCP signatures:
   - Node MCPs: `commandline` matching `chrome-devtools-mcp`, `desktop-commander`, `context7-mcp`.
   - Python MCPs: `serena.exe` and `cmdline` containing `serena`.
   - Implementation: canonical safe reaper at `%LOCALAPPDATA%/hermes/scripts/cleanup_agent_orphans.py`, orchestrated by background daemon `%LOCALAPPDATA%/hermes/scripts/agent_guard.py` (2.5s debounce after all Agent GUIs close).
- **OpenViking Automated Demand-Wake & Zero-Focus-Steal Invariant**:
  - OpenViking is the shared dual-agent memory service, completely decoupled from OS auto-start (`Startup/OpenVikingGateway.vbs` removed) and free of desktop shortcut clutter.
  - **Native GUI PATH Shim**: Hermes' OpenViking plugin runs `shutil.which("openviking-server")` on 1933 connection drops. A compiled Go binary with `-H=windowsgui` PE subsystem header at `%USERPROFILE%/.openviking/shim-bin/openviking-server.exe` (placed first on User PATH) intercepts the call and transparently boots the full lazy-gateway stack without spawning `cmd.exe` or flashing console windows.
  - **Zero Console-Allocation / Zero Focus-Steal (CRITICAL)**: In background supervisor or auto-sleep routines running under `pythonw.exe` (such as `openviking_lazy_gateway.py` or `agent_guard.py`), NEVER invoke console executables (`netstat.exe`, `taskkill.exe`) without `CREATE_NO_WINDOW = 0x08000000`. On Windows, running console apps from a windowless process forces the OS to allocate a transient `conhost.exe` host window; even a 10ms transient console creation steals foreground input focus, disrupting active typing and destroying uncommitted IME candidate buffers. Always terminate processes via native `psutil` (`proc.kill()` / Win32 `TerminateProcess`) and query ports via `psutil.net_connections()`.
  - **Tri-phase Lifecycle**: Demand-wake on first memory access -> 2-minute idle auto-sleep (100% VRAM release) -> automatic termination upon Agent GUI close via `agent_guard`.
