# Provider Quirks: Google AI Studio vs. Local Antigravity Bridge & OpenCode Free Relay

## 1. Google Gemini: AI Studio API Key vs. Consumer Pro / Antigravity Bridge

- **AI Studio API Key limitations**:
  - Direct API requests to `generativelanguage.googleapis.com` with AI Studio API keys strictly enforce geographical whitelisting. Requests from unsupported IP locations (e.g. mainland China/Hong Kong proxy exit nodes) fail with:
    `400 FAILED_PRECONDITION: User location is not supported for the API use.`
  - AI Studio API keys require developer/enterprise billing projects and do NOT automatically inherit consumer Google One AI Premium / Gemini Pro subscriptions.
- **Consumer Google Pro via Antigravity Bridge (`127.0.0.1:18080`)**:
  - Bridges the user's logged-in Google account OAuth token (`antigravity-*.json`) to a local OpenAI-compatible endpoint.
  - Automatically handles upstream OAuth tokens and bypassing API-level geographical barriers, exposing models like `gemini-3.7-flash` (supporting Ultra reasoning effort) with zero incremental API token cost.

## 2. Non-interactive `hermes auth add` syntax

- When invoking `hermes auth add` non-interactively in shell/scripts, **both `--api-key` and `--label` must be provided**:
  ```bash
  hermes auth add gemini --label "my-label" --api-key "API_KEY_HERE"
  ```
  If `--label` is omitted, the CLI attempts an interactive `input()` for label and throws `EOFError: EOF when reading a line` in non-PTY subprocesses.

## 3. OpenCode Free Keyless Relay (`https://opencode.ai/zen/v1`) Availability

- **Keyless Architecture**: The relay expects an empty or omitted `Authorization` header. Sending an unrecognized Bearer token returns `401 Unauthorized`.
- **Concurrency & Rate Limits (429)**:
  - High-demand models (`muse-spark-1.3-contributor-free`, `deepseek-v4-flash-free`, `mimo-v2.5-free`, `ling-3.0-flash-fin-free`) frequently return `HTTP 429 Too Many Requests` during peak global usage.
  - `laguna-s-2.1-free` is designated as the primary high-availability, low-latency free fallback model with consistent uptime.
