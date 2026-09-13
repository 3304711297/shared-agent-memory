## 12. Session Archive & Teardown Protocol (User Rule)
When the user issues a directive to delete or archive the active session, or when session consumption approaches the reset threshold (≥1M tokens):
1. **Curate High-Value Knowledge & Dual-Store Sync**:
   - Extract all critical technical decisions, verified failure root causes, configuration baseline changes, and debugging invariants discovered during the turn.
   - Commit operational facts and cross-agent invariants to the shared repository (`shared-agent-memory`, `main` branch).
   - Author or update applicable domain articles, system guides, or hardware knowledge in the `youshouldknow` (YSK) documentation repository.
2. **Physical Teardown of Ephemeral Session Artifacts**:
   - Perform an exhaustive scan of the workspace, temporary directories (`%LOCALAPPDATA%\\Temp`), and repository trees.
   - Physically delete all ephemeral test scripts (e.g. temporary `.py`, `.cjs`, `.sh` probes), scratch output logs, and transient scraper outputs generated during the conversation. Zero untracked diagnostic clutter must remain on disk.
3. **Automated Remote Push & Continuous CI Confirmation**:
   - Stage and commit all persistent knowledge updates, pushing to their authoritative remote branches (`main` for shared repositories, `hermes` for profile-local state).
   - Actively monitor and poll remote GitHub Actions workflows (`gh run watch` / `gh run list`) until 100% green (Success ✓) before completing the turn. Never conclude an archive request without remote CI verification.
4. **Batched Plan & Deferred Task Specification Preservation**:
   - When executing staged, multi-phase implementations (e.g. P0/P1/P2 task batches) and concluding a session after completing an initial phase, never treat pending subsequent batch specifications as ephemeral scratch files.
   - Any unexecuted batch items must be persisted into the shared memory or repository docs (`docs/plans/` or `topics/<project>.md`) before session teardown; wiping them forces subsequent sessions to stall and re-request the specification.
