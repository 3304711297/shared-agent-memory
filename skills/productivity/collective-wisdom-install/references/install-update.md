## Install or update

1. Use `present_wisdom_consent` with the exact skill/version, a short title, and
   explanation. The backend supplies package facts, warnings, and actions.
2. The user must click a native control or use deterministic `/wisdom consent`
   in their own CLI. A conversational "yes" prompts the control. Never apply a
   receipt through terminal, `clarify`, or another agent tool.
3. Read the result with `wisdom_inbox`. Changed bytes, local conflicts, expanded
   permissions, or stale plans require renewed review.
4. Inspect `wisdom_inspect` with `kind: installed`, the skill identity and exact
   installed version to retrieve the hash-checked setup guide and prerequisites.
   The read-only CLI equivalent is
   `hermes wisdom installed-setup <skill-id> --version <version> --json`.
   Re-inspect after an interruption or update; do not reuse an older version's
   guidance. Missing or invalid guidance requires review, not guessed commands.
   Distinguish files installed from setup completed and verification passed.
   Explain missing commands, services, permissions, and environment variable
   names without reading or displaying credential values.
5. Installing files does not authorize running setup or verification commands.
   Native Install/Update queues a setup handoff for the same private session.
   With an active session model, the idle-session worker reads the installed guide
   and proposes one step at a time, including when fixed notification copy is
   selected. Fixed copy disables unsolicited agent assessments, not requested
   installation or setup. Passed steps
   queue the next review; Not now pauses the flow without repeating the card.
   If the conversation has no active model, command preparation waits without
   spending model retries or selecting a different provider. The completed
   install/update card's Check setup control shows progress or the existing
   step's review. Select or reconnect the conversation's model and send a message
   there to resume queued work. Checking status never runs a command; expired
   approvals still require Recheck and fresh confirmation.
   Do not create a competing proposal when an existing setup control is pending.
   Propose each step through `present_wisdom_consent` with `kind: setup`, the
   exact installed identity/version, and `step: {phase, index, command}`.
   `phase: setup` selects the zero-based setup instruction; `phase: verify`
   selects the final verification step (index 0). Explain the proposed effects
   and obtain separate approval for each step.
   The native card shows the installed guidance and exact local command. The
   command does not run until the user confirms, and terminal permission rules
   still apply. Never include credential values in commands or chat.
6. For user-managed accounts, services, and permissions, use `phase: prerequisite`
   with its zero-based prerequisite index and no command. Only the user's native
   acknowledgement satisfies a manual prerequisite; it is not machine detection.
   Missing commands and environment variables must be detected again after setup.
7. Use installed inspection or the native Check progress control to read durable
   progress. A successful spawn is not command completion. If the outcome is
   unknown, stop: do not repeat or rephrase the command. The user can select
   Review interruption, check that the command and its children have stopped,
   inspect any side effects, and explicitly clear the interrupted record. A
   running command cannot be cleared. Clearing does not undo changes, verify
   setup, or authorize a retry. Recheck opens fresh native approval; never clear
   the record or claim the process has stopped on the user's behalf.
   If terminal permission was denied, no command ran; resolve permissions before
   requesting fresh review.
   After required setup, propose verification separately. Only report readiness
   when installed inspection returns `ready_to_use: true`. An update invalidates
   the previous version's setup evidence. A remote terminal is not silently
   replaced with a local terminal to run setup.

If the presentation tools are unavailable, direct the user to `/wisdom install`
or `/wisdom update` in their own session, not an agent-run confirmation bypass.
