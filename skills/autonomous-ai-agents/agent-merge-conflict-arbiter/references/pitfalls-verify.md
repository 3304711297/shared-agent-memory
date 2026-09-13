## Pitfalls

- **Self-favoring**: if you were spawned by one of the conflicting agents,
  you are structurally biased — state this and weigh the other side's intent
  deliberately. Prefer the third-profile shape so this never arises.
- **Splitting the difference** on a design collision produces a hybrid nobody
  designed; pick one answer and surface it.
- **Per-file classification**: files usually mix hunk classes; classifying a
  whole file as one class silently drops a disjoint change.
- **Drive-by edits** make the merge unreviewable and steal decisions from the
  original agents.
- **Missing intents**: commit messages alone can be thin; prefer kanban
  completion summaries or PR bodies. If neither side's intent is recoverable,
  escalate instead of guessing.
- **Repeat offenders**: repeated conflicts on the SAME file across rounds are
  a hotspot signal, not routine reconciliation work — flag it (e.g. a
  `hotspot: <path> — <reason>` kanban comment) so the orchestrator decomposes
  that file, rather than serially reconciling every new collision on it.

## Verification

- `git status` shows a clean tree on the target branch with a merge commit.
- No conflict markers remain (`search_files` pattern `<<<<<<<`).
- Build/tests pass; both sides' intents are demonstrably present or the
  dropped one is explicitly named in the summary.
- The hand-back summary enumerates every hunk with class and rationale.
