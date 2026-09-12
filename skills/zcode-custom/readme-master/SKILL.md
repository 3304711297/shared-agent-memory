---
name: readme-master
description: "写/改README时必用。项目解析与顶级自述文件生成。Use when writing, improving, or optimizing a repository README."
---

# README Master Skill

Use this skill to automatically audit a software project and generate or polish its `README.md` to top-tier open-source standards (GitHub Awesome style).

## Standard README Structure

When generating a README, analyze the codebase and structure the document into the following sections:

1. **Header & Title**
   - Project Name with clear icon/emoji.
   - One-sentence pitch: Clear, punchy description of what the project solves and who it is for.
   - Badges bar (CI status, Release version, License, Platform/Language, Stars).

2. **Key Features & Highlights (✨ Features)**
   - Bullet points with bold titles describing the most valuable capabilities.
   - Use comparison tables or feature matrices where applicable.

3. **Architecture & Workflow (📐 Architecture)**
   - Include a Mermaid diagram illustrating the data flow, module breakdown, or system architecture.

4. **Quick Start & Installation (🚀 Quick Start)**
   - Prerequisites (Node.js / Python / Go / Rust version, OS requirements).
   - Step-by-step commands (Clone -> Install dependencies -> Configure environment -> Run/Build).
   - Minimal working example code snippet with expected output.

5. **Configuration & Environment Variables (⚙️ Configuration)**
   - Table detailing key configuration options, defaults, and descriptions.

6. **Project Structure (📂 Project Structure)**
   - Clean, annotated directory tree highlighting key modules and entry points.

7. **Roadmap & Contributing (🛣️ Roadmap & 🤝 Contributing)**
   - Checkbox-style roadmap of completed and upcoming milestones.
   - Contribution guidelines and pull request flow.

8. **License & Acknowledgements (📄 License)**
   - Open source license type and credits to underlying libraries.

## Guidelines
- Write in the user's preferred language (Chinese or English, or bilingual header).
- Ensure all command examples are copy-paste ready and syntax-highlighted.

---

## Batch-Improving an Existing README (audit-driven workflow)

Use this when the task is 「改进/优化现有项目的 README」rather than writing one from scratch. Existing READMEs at 75-90 points almost always suffer from **factual drift**, not structural gaps.

### 1. Audit before writing (never rewrite blind)

Scan every repo's README against source, then classify each finding. Recurring defect classes, in order of how often they bite:

| Defect | How to catch it |
|---|---|
| **Architecture trees list files that no longer exist** | `ls Modules/` / `ls src/` and diff against the tree in the README |
| **Line counts / entry counts / item counts stale** | `wc -l`, `grep -c`, count the manifest JSON items |
| **Status text contradicts delivery**（「P1 储备」but already shipped） | grep the feature name in code, check git log |
| **Hardcoded version in a badge**（`badge/Release-v1.4.4`） | Convert to dynamic: `img.shields.io/github/v/release/OWNER/REPO` |
| **CI badge points at a tag-triggered workflow**（`release.yml`），so it never reflects real CI | Point it at the push/PR workflow（usually `ci.yml`） |
| **Project positioning stale after an ecosystem change**（a co-agent was retired） | Re-read the intro paragraph against current reality; move history to a 「沿革」 line |
| **Counts in prose vs machine-readable manifest disagree** | Cross-check the manifest/list file, not just another doc |
| **Missing standard sections**（项目结构 / FAQ / TOC） | Compare against the Standard README Structure above |

Caution: **read the source, not the translated/localized docs** — translations lag. And a number that appears in two places is a claim, not a fact; verify at the machine-readable source.

### 2. Dispatch parallel subagents — one repo per child

When improving READMEs across 3+ repos, dispatch one subagent per repo (batch 3-6, max 10). Independent repos share no writable file, so they parallelize cleanly. In each child's context include:

- **The exact list of factual corrections with verified values** (old → new). Children cannot re-derive the audit — hand it to them.
- **A hard write boundary**: 「只改 README.md 一个文件，不要动代码/测试/产物」. Without this, children wander into unrelated work (and can trip CI).
- **The repo's CI shape**, since it decides what the change triggers:
  - `paths-ignore: ['**.md']` → README-only change triggers nothing; say so, so the child doesn't wait on CI.
  - CI asserts 产物与源一致（`git diff --exit-code -- *.user.js`）→ never hand-edit the built artifact.
  - MkDocs + lychee link-check over `./**/*.md` → **do not introduce new external links**; reuse known-good ones.
- **Push fallback ladder**: `git push` → `env -u ALL_PROXY -u HTTP_PROXY -u HTTPS_PROXY git push` → `git -c http.proxy=http://127.0.0.1:3067 push`; on non-fast-forward use `git pull --rebase`, never `--force`.
- **House rules**: Pangu spacing (space between CJK and Latin/digits), full-width punctuation in Chinese sentences, no machine username / absolute disk path / token in any public repo.

### 3. Verify independently — a child's self-report is not evidence

For every repo, re-check yourself:

```bash
cd <repo> && git rev-parse --short HEAD          # local
cd <repo> && git ls-remote origin refs/heads/main # remote — must match
cd <repo> && git show --name-only --format="" HEAD | wc -l   # must be 1 (README only)
cd <repo> && git status --porcelain | wc -l       # must be 0 (clean tree)
```

Then grep the commit diff for a keyword unique to each intended fix — a commit message that claims the change is not proof the change exists.

### 4. Concurrent-writer check (when another session may be live)

If the user runs **multiple Hermes sessions against the same repos**, a commit you did not make can appear between your `git status` and your push. Before reporting a child as rogue:

```bash
cd <repo> && git reflog --date=format:"%H:%M:%S" -12   # authorship timeline
git log --format="%h | %ai | %s" -5                      # compare commit times vs your dispatch times
```

Distinguish: a commit **touching your file** means a real conflict (rebase/resolve); a commit touching **other files** is normal parallel work — confirm no overlap and move on. A child that appears to have modified 50 files usually turns out to be the user's other session; check the timeline before steering or stopping the child.

### 5. Close out

Track each repo as its own checklist item (one per repo, never 「update all READMEs」). After pushing, check the CI run **for that exact SHA** (`gh run list -R OWNER/REPO --json headSha,... --jq '.[] | select(.headSha|startswith("<sha>"))'`), not merely the repo's latest run. Queued/in-progress is a wait state — background it with `notify=true` rather than blocking, and report the real state.
