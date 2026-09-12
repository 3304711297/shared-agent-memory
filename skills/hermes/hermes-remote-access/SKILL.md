---
name: hermes-remote-access
description: "手机/局域网连Hermes时必用。移动端与LAN接入配置。Use when configuring mobile or LAN access for Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, remote-access, mobile, gateway, dashboard, networking, android]
    related_skills: [hermes-agent, pinggy-tunnel]
---

# Hermes Remote & Mobile Access Skill

Standard procedure and hard rules for connecting mobile clients (such as `rusty4444/hermes-android` and `Hy4ri/hermes-mobile`), remote dashboards, or LAN devices to a local Hermes Agent instance.

## Client Decision Rule

When a user asks to connect or control Hermes from mobile without specifying a project, evaluate their primary objective:
- **Full Agent Control & Desktop Parity -> `rusty4444/hermes-android` (Recommended default)**: Uses Desktop Gateway JSON-RPC / API Server (port 8642). Exposes live tool activity, collapsible reasoning blocks, tool execution approvals, clarifications, and background turn completion notifications.
- **DevOps, Config & Live Admin -> `Hy4ri/hermes-mobile`**: Uses Dashboard REST & TUI WebSocket (port 9119). Exposes environment key editing, live log streaming, skills/plugins management, cron job controls, and kanban boards.

Reference `references/client-comparison-and-endpoints.md` for endpoint routes and payload schemas.

## Configuration & Deployment Procedure

### 1. Gateway API Server Setup (Port 8642)
For clients requiring Desktop Gateway or OpenAI-compatible session endpoints:
1. Inject the secret key and network bind targets into `~/.hermes/.env` (never `config.yaml` to avoid git diff churn and formatting corruption):
   ```bash
   API_SERVER_KEY=<random-hex-at-least-24-bytes>
   API_SERVER_HOST=0.0.0.0
   API_SERVER_PORT=8642
   ```
2. Restart the gateway daemon:
   ```bash
   hermes gateway restart
   ```
3. Verify process listener:
   ```bash
   netstat -ano | grep 8642
   ```

### 2. Dashboard API Setup (Port 9119, Optional / Drawer features)
When web dashboard screens, skills browsing, or cron drawer features are needed on mobile:
1. Non-loopback binds (`0.0.0.0`) enforce an authentication gate. Provide credentials via `~/.hermes/.env`:
   ```bash
   HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
   HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=<your-password>
   ```
2. Launch or verify the dashboard:
   ```bash
   hermes dashboard --host 0.0.0.0 --port 9119 --no-open
   ```

### 3. Host Firewall Inbound Rules
On Windows hosts, local loopback checks (`127.0.0.1`) succeed even when LAN inbound traffic is blocked. Explicitly permit incoming traffic:
```powershell
New-NetFirewallRule -DisplayName "Hermes Gateway API LAN" -Direction Inbound -LocalPort 8642 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Hermes Dashboard LAN" -Direction Inbound -LocalPort 9119 -Protocol TCP -Action Allow
```

### 4. End-to-End Verification Gate
Always verify with real requests before handing connection details to the user:
```bash
# 1. Health probe (must return HTTP 200)
curl -s -i http://127.0.0.1:8642/health

# 2. Bearer authentication probe (must return models list)
curl -s -H "Authorization: Bearer $API_SERVER_KEY" http://127.0.0.1:8642/v1/models

# 3. Session sync probe (must return session array containing desktop sessions)
curl -s -H "Authorization: Bearer $API_SERVER_KEY" http://127.0.0.1:8642/api/sessions
```

## Pitfalls & Operational Invariants

- **Do not edit `config.yaml` for gateway tokens**: Store `API_SERVER_KEY` and dashboard passwords strictly in `~/.hermes/.env`. `config.yaml` is reserved for permanent declarative settings; touching it causes avoidable formatting changes and requires memory repository sync.
- **`API_SERVER_KEY` length requirement**: The API server adapter silently fails to start or refuses non-loopback connections if `API_SERVER_KEY` is missing or shorter than 16 characters. Always generate keys >= 32 characters (`openssl rand -hex 24`).
- **Dashboard fails closed on `0.0.0.0`**: If `hermes dashboard --host 0.0.0.0` is run without pre-registered OAuth or Basic Auth credentials in `.env`/`config.yaml`, it aborts immediately with exit code 1.
- **Always verify IP against active Wi-Fi adapter**: Use `ipconfig` (Windows) or `hostname -I` (Linux) to get the specific IPv4 of the LAN adapter connected to the same subnet as the mobile device, not virtual/WSL adapters.
- **Desktop local serve vs gateway decoupling**: Hermes Desktop runs an internal backend process (`hermes serve` on an ephemeral port), while mobile clients connect to `hermes gateway` (8642) or `hermes dashboard` (9119). While both persist to the same `state.db`, their live in-memory sessions and WebSocket event dispatchers are independent. Messages sent from a mobile client will not trigger real-time updates in the Desktop GUI unless the Desktop app's connection mode is switched from `Local` to `Remote` pointing to the shared gateway.
- **UI language requirements**: If a Chinese interface is requested, use `Hy4ri/hermes-mobile`. `rusty4444/hermes-android` currently hardcodes all UI labels and settings in English despite supporting UTF-8 Chinese conversational exchanges.
- **Do not misinterpret ambiguous single-character user replies**: If a user submits an ambiguous number or single character while discussing multiple client options, confirm whether they are selecting a specific option or requesting an architectural evaluation before reconfiguring ports.
- **Graceful shutdown of mobile services**: When shutting down mobile gateway or dashboard exposure upon user request, use `hermes dashboard --stop` or targeted PID kill for that specific service. Never run indiscriminate process termination against Python processes or restart the core gateway without verifying active desktop sessions; killing shared runtime processes severs Hermes Desktop's backend connection (`hermes serve`), causing connection drops and repeated response interruption loops.
