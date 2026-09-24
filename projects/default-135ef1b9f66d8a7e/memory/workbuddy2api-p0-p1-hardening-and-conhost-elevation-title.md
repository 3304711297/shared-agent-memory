# WorkBuddy2API P0/P1 Hardening and Windows ConHost Elevation Title Invariant

## Context
During cross-agent collaborative auditing with ChatGPT Thinking mode on `workbuddy2api` (commits `812bd33`, `9437160`, `f79ddea`, `d31dec9`), several critical race conditions and platform gotchas were resolved.

## Hardening Ledger

### 1. Token Refresh UID Binding (P0)
- **Problem**: When a token refresh was in-flight and a user switched active accounts in the GUI, `CredentialManager._save_tokens` dynamically read the global `active_uid` from disk upon writeback, erroneously overwriting account B's credentials with account A's newly refreshed token.
- **Fix**: Bound the target session UID directly into the refresh invocation, ensuring writes target only the originating account.

### 2. OpenAI Responses API Context Fork Defense (P1)
- **Problem**: When a client supplied `previous_response_id` that was evicted or missing from the local FIFO response cache, the server silently skipped history restoration, continuing the request as an empty prompt (Silent Context Forking).
- **Fix**: Aligned with the official OpenAI Responses API specification. Throws `PreviousResponseNotFoundError` and returns an immediate HTTP 400 with `error.code = "previous_response_not_found"`.

### 3. Anthropic Messages Thinking Sidecar (P1)
- **Problem**: Multi-turn requests from clients like Claude Code passed back `thinking` (with encrypted signatures) or `redacted_thinking` blocks. Stripping them broke agent continuity, while sending them to OpenAI/Tencent upstreams caused schema validation failures.
- **Fix**: Implemented an internal opaque sidecar (`_anthropic_original_content` and `_anthropic_signature`) on assistant message objects. Added `strip_anthropic_sidecar` before upstream egress to preserve internal structure while maintaining upstream cleanliness.

### 4. Credential Readiness Gate & Single-Flight Refresh (P1)
- **Problem**: Accounts with expired access tokens but earlier asset expiration dates were scheduled ahead of instantly ready accounts, introducing multi-second latency spikes in the hot path. Concurrent failovers also fired duplicate token refresh requests against upstream.
- **Fix**: 
  - Classified account readiness into 3 tiers: `READY_INSTANT` (0), `READY_REFRESHABLE` (1), and `UNREADY` (2). `AccountRotator.get_candidate_uids_tiered` sorts by `(readiness, day_key, exp)`.
  - Added per-UID single-flight locking (`_get_uid_refresh_lock`) in `CredentialManager._refresh_session_tokens` to ensure only one network call runs per account at any time.

### 5. Frontend Settings Serial Queue (P1)
- **Problem**: Concurrent rapid setting toggles caused Lost Update races when reading stale disk snapshots.
- **Fix**: Added module-level `saveChain = Promise.resolve()` in `src/settings.js` to serialize all setting persistence operations.

## Windows ConHost Elevation Title Invariant

### Mechanism
- When a process running under elevated Administrator privileges invokes `cmd.exe /d /s /c start "Title" /min pwsh.exe ...`, the Windows Console Host (`conhost.exe`) initializes the console window.
- Out of security and anti-phishing tracking design in Windows 10/11, elevated ConHost forcibly pins the title bar of the new console window to the physical path of the initial spawning shell (e.g. `Administrator:  C:\Windows\system32\cmd.exe`), regardless of the internal process (`pwsh.exe`) or initial `start "Title"` arguments.
- Process table inspection (`tasklist /v` or `Get-CimInstance Win32_Process`) proves the running process is 100% `pwsh.exe` with zero `cmd.exe` active.

### Operational Rule
- Never guess or attempt ad-hoc script hacks when diagnosing OS/platform quirks. Search official MSDN / Microsoft Learn documentation first (Search-Before-Guess rule).
