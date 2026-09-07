# Client Comparison & Endpoint Matrix

## 1. Client Architecture Comparison

| Feature / Capability | `rusty4444/hermes-android` (v2.0+) | `Hy4ri/hermes-mobile` |
| :--- | :--- | :--- |
| **Primary Transport** | Desktop Gateway JSON-RPC (HTTP/WS on 8642) | Dashboard REST + TUI WebSocket (HTTP/WS on 9119) |
| **Tool Calling & Activity** | Full real-time tool activity stream & results | Limited / Basic textual indicators |
| **Reasoning Blocks** | Collapsible native reasoning views (thinking trace) | Inline markdown text stream |
| **Execution Approvals** | Native approval dialogs (confirm dangerous commands) | Not fully integrated with desktop approvals |
| **Background Notifications** | Yes (Android turn notifications on completion) | Yes (notification inline reply) |
| **Voice Dictation & TTS** | Native STT dictation & spoken TTS responses | Text-only input |
| **Multi-Attachment Support** | Up to 10 files/images per message with sanitization | Single image attachments |
| **UI Localization (i18n)** | English only (UI strings hardcoded in English) | Native Simplified Chinese (zh) supported (v1.22.1+) |
| **Skills / Cron / Memory** | Supported via optional 9119 dashboard drawer | First-class dedicated screens |
| **Live Log Streaming** | No | Yes (live stdout/stderr stream filtering) |
| **Kanban Task Boards** | No | Yes (interactive boards) |

## 2. Gateway API Routes (Port 8642)

- `GET /health` -> Simple health check (`{"status": "ok", "platform": "hermes-agent"}`).
- `GET /v1/models` -> List available models (requires `Authorization: Bearer <API_SERVER_KEY>`).
- `POST /v1/chat/completions` -> OpenAI-compatible streaming completion endpoint.
- `GET /api/sessions` -> List active and past Hermes sessions.
- `GET /api/sessions/{id}` -> Read session transcript.
- `GET /v1/capabilities` -> Static feature flags and transport capabilities.

## 3. Dashboard Routes (Port 9119)

- `GET /api/status` -> Dashboard and agent overall status.
- `POST /auth/password-login` -> Basic Auth session token issuance.
- `GET /api/skills` -> List installed and catalog skills.
- `GET /api/cron` -> List and manage scheduled cron jobs.
- `GET /api/memory` -> Inspect long-term memories.
