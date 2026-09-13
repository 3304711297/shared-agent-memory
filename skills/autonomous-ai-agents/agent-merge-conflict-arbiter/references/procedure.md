## Procedure

### 1. Gather both sides

- Run via `terminal`: `git status` (confirm the conflicted state and list
  conflicted files), `git merge-base <A> <B>`, then for each side
  `git log --oneline <base>..<side>` and `git diff <base>..<side> -- <file>`
  for every conflicted file. In a halted merge, `HEAD` is one side and
  `MERGE_HEAD` is the other.
- Collect each side's intent: `hermes kanban show <task-id>` for completion
  summaries/metadata, or the PR body, or the commit messages from the log
  above. Write down one sentence of intent per side before touching any file.
- Done when: you can state both intents in your own words and have both diffs
  for every conflicted file.

### 2. Classify every conflicted hunk

- Open each conflicted file with `read_file` and locate each
  `<<<<<<<`/`=======`/`>>>>>>>` block.
- Assign each hunk exactly one class from the Quick Reference table, judging
  by the stated intents — not by which change looks nicer.
- If a single hunk contains multiple independent decisions (e.g., new logic
  that combines cleanly PLUS a styling/rounding choice both sides answered
  differently), decompose it into sub-decisions and classify each one.
- A single file often mixes classes: one hunk may be a design collision while
  a neighboring hunk is disjoint. Classify per hunk, not per file.
- Done when: every hunk has a written class and a one-line rationale.

### 3. Resolve under the impartiality contract

- Edit each hunk with `patch` (or `write_file` for whole-file rewrites):
  - disjoint-intent → merge both changes so each intent is fully served.
  - same-question-different-answer → pick the answer that best serves the
    STATED intents (e.g., an intent of "strict validation" beats "quick
    default" if the task required correctness). Never split the difference
    into a hybrid neither side asked for.
  - superseded → keep the surviving side; delete the dead premise.
- Never favor the side that spawned you. If intents genuinely tie, escalate
  (block the kanban card / report back) rather than guess.
- Change nothing outside conflict markers — no formatting, renames, or
  opportunistic fixes.
- `git add` each resolved file via `terminal`.
- Done when: `search_files` finds no `<<<<<<<` markers in the repo and every
  resolved file is staged.

### 4. Verify

- Run the project's build/tests via `terminal`; at minimum import/execute the
  touched modules. Both intents must be observable in the merged behavior
  (e.g., side A's new semantics AND side B's disjoint addition both present).
- Complete the merge: `git commit` (the default merge message plus a body
  listing hunk decisions is fine).
- Done when: verification passes and the merge commit exists.

### 5. Hand back

- Produce a completion summary naming EVERY hunk decision:
  `file:lines — class — which side(s) kept — rationale`. For every
  same-question-different-answer hunk, state the design question and the
  answer you picked so a human can veto it — never bury a design call.
- Kanban: `kanban_complete(summary=...)`. Standalone: print the summary.
- Done when: the summary is delivered and lists all hunks.
