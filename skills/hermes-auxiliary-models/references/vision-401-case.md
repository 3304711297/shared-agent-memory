# Worked case: vision_analyze 401 while chat worked (2026-09-03)

## Symptom

`vision_analyze` on a local image failed with
`401 Invalid API key`, while the chat session (model
`muse-spark-1.3-contributor-free` via `opencode-free`) worked fine.

## Diagnosis (in order)

1. `hermes config get auxiliary.vision` → `provider: auto`, `model: ''`.
   `auto` finds no key-backed provider → 401.
2. `hermes auth list` → only `copilot` and
   `custom:local-(127.0.0.1:18080)` hold credentials. No `opencode-free`
   entry: the desktop chat's OAuth credential is session-scoped and
   invisible to auxiliary calls.
3. `custom_providers:` in config showed the local proxy serves
   `gemini-3.7-flash` (+ `gemini-pro-agent`, `gemini-3.1-pro-low`,
   `gpt-oss-120b-medium`).

## Attempts and results

| Route | Result |
|---|---|
| local proxy + `muse-spark-1.3-contributor-free` | `400 unknown provider for model` — id not served by proxy |
| `opencode-free` + `muse-spark-1.3-contributor-free` | `401 Invalid API key` — no credential on auxiliary path |
| local proxy + `gemini-3.7-flash` | **Success** — image parsed |
| `hermes auth add opencode-free --no-browser` | Prompts `Paste your API key:` — key-type provider, no browser-OAuth path; killed, user declined to paste key |

## Follow-up (same day): keyless-provider findings

- `opencode-free` is KEYLESS by design (provider source pins an empty
  `Authorization` header; the Zen relay 401s any bearer). Adding the
  user's api-key credential did NOT fix vision — same 401 — and had to
  be removed (`hermes auth remove opencode-free 1`) to restore keyless.
  The "add an opencode key" alternative from the first session is now
  tested and disproven for the vision path.
- Direct `/models` probe of the local proxy (key from config, never
  printed) enumerated 13 servable ids — Gemini family, `claude-opus-4-6
  -thinking`, `claude-sonnet-4-6`, `gpt-oss-120b-medium`. No
  `muse-spark`: vision cannot run the chat model anywhere.
- Negative-control probe: vision model `probe-xyz-123` → error echoed
  `unknown provider for model probe-xyz-123`, proving the configured
  value reaches the wire verbatim. Restored `gemini-3.7-flash`, success.
- `auth add` stdin piping (`echo |`, `printf |`) hangs — the prompt
  reads the TTY. `--api-key` flag works non-interactively.
- Profile default unified to chat model: `model.default =
  muse-spark-1.3-contributor-free`, `model.provider = opencode-free`,
  `model.base_url` unset (falls back to provider default). New sessions
  start on it; already-running sessions keep their startup model.

## Final state

Chat default: `muse-spark-1.3-contributor-free · opencode-free`.
`auxiliary.vision` stays `custom:local-(127.0.0.1:18080)` +
`gemini-3.7-flash` (verified working) — full unification is impossible:
no provider serving muse-spark accepts auxiliary vision calls.
