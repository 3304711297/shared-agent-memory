---
name: skill-evaluation-and-admission
description: Use when evaluating new agent skills, tools, or repos, or when user asks "值得安装吗", "评估技能", "新技能评估". Five-step audit SOP.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, evaluation, admission, prompt-caching, trigger-design, watchdog]
    related_skills: [writing-skills, hermes-agent-skill-authoring]
---

# Skill Evaluation and Admission

A class-level operating procedure for evaluating, auditing, admitting, and triggering external AI agent skills, plugins, and toolkits.

## When to Use

- User presents a GitHub repository, URL, or proposal for a new agent skill/plugin and asks "值得安装吗" (is this worth installing?) or requests an evaluation.
- Deciding whether to adopt a new capability as an on-demand Skill vs an always-on Plugin.
- Diagnosing and fixing "Agent ignores installed skills and answers with bare model memory".

---

## 1. Five-Step Evaluation & Admission Procedure

When evaluating candidate skills, toolkits, or repos provided by user, execute this audit sequentially:

### Step 0: Upstream Registry & Duplicate Defense Gate (Pre-Evaluation)
- **Check Resource Index First**: Prioritize searching the shared registry `skill-plugin-resources.md` and `capability-inventory.json` before starting audit.
- **De-duplication Check**: If the user submits a repo or skill set that was already evaluated or admitted (e.g. `cangjie-skill`), immediately notify the user with existing evaluation/admission records, preventing redundant duplicate cycles.
- **Index Admission Judgment**:
  - If a submitted library or tool is deemed **valuable** (whether adopted directly or cataloged as reference material), formally append it to `skill-plugin-resources.md` under its appropriate category so all future agent turns can prioritize indexing from it.
  - If deemed **unworthy / disqualified**, do NOT add to `skill-plugin-resources.md`, but explicitly record its technical disqualification reason under `capability-inventory.json`'s `notWatched` array, explaining why to prevent repeat evaluations if re-submitted later.

### Step 1: Core Value & Pain-Point Penetration
- Identify the exact failure mode the tool claims to address (e.g. LLM code bloat, runaway verbosity).
- Strip away marketing and meme framing to assess the actual mechanism (a prompt rule ladder vs AST rewriting vs a local proxy).
- Distinguish between real engineering solutions and superficial prompt wrapping.

### Step 2: Architecture, Cache & Token Audit (Crucial)
- **Prompt Caching Compatibility**: Does the tool alter context dynamically (e.g. heuristic log truncation, AST stripping)? If a proxy modifies historical turns or tool output dynamically, it breaks Prefix Prompt Caching (e.g. Gemini/Claude prefix caching), causing real billing to spike dramatically.
- **Prompt Overhead / Token Inversion**: Calculate the fixed input token penalty per turn. If a skill injects 1k–1.5k input tokens on every turn just to save 50 output tokens, multi-turn sessions will result in negative savings (costing more money).
- **Runtime & Network Compatibility**: Audit OS and network constraints (e.g. local proxy loops, Windows path handling, BSL commercial license limitations, telemetry).

### Step 3: Deployment Form Factor: On-Demand Skill vs Always-On Plugin
- **Reject Always-On Plugins by Default**: A plugin with lifecycle hooks (`UserPromptSubmit`, `PreToolUse`) injects rules into every turn regardless of whether the task is coding, sysadmin, writing, or retrieval. This pollutes baseline attention and triggers unhelpful pushback on non-coding tasks.
- **Enforce On-Demand Skills**: Wrap the proven ruleset, review checklists, and audit commands as on-demand skills. They cost zero baseline tokens and are summoned only when the task requires them.

### Step 4: Survival of the Fittest (Deduplication)
- Compare the candidate against existing local tools and skills.
- If an existing native tool or mature skill already covers the need with better aesthetics or integration, reject the redundant tool. Only admit items that provide distinct, verifiable leverage.

### Step 5: Lifecycle & Watchdog Synchronization (Strict Atomicity)
Any change to skills (admission, version upgrade, pruning, or evaluation rejection) must be treated as an atomic transaction with the capability watchdog:
1. **Dual-Agent Alignment**: Deploy or prune skill copies across all active agent runtimes (e.g., Hermes and ZCode).
2. **Trigger Optimization**: For newly admitted skills, enforce the 57-Character Rule + Chinese colloquial aliases in frontmatter description.
3. **Inventory & Baseline Sync**: Immediately update `capability-inventory.json` in the same turn:
   - Admitted: register upstream repo/release under `checks` and record installed version/SHA.
   - Upgraded: advance `installed.version` and `sha` to the target release.
   - Pruned: adjust installed copy counts (e.g., `hermes-hub-skills`) and clean out orphaned checks.
   - Rejected: record explicit technical disqualification reason under `notWatched` to prevent repeat re-evaluations.
4. **CI Verification**: Execute `check_capability_upstream.py` locally, commit and push to remote `main`, and verify remote GitHub Actions pass 100% green before concluding.

---

## 2. Solving "Agent Ignores Skills" (Invocation Discipline)

When agents bypass installed skills in favor of bare model generation, apply these three countermeasures:

### 1. The Skill-First Reflex Gate
Enforce an explicit gate in the agent's core instructions:
- Before executing any file edits (`patch`/`write_file`) or shell commands on coding, debugging, planning, or review tasks, the agent's **FIRST action MUST be checking the skill pool and calling `skill_view(name)`**.
- Making the decision step mandatory and observable breaks the model's subconscious urge to rush into code generation.

### 2. The 57-Character Rule & Colloquial Trigger Aliases
- Models prioritize matches within the first 57 characters of a skill's description.
- Start with `Use when...` followed immediately by common colloquial phrases and intent verbs the user actually speaks (e.g. "帮我看下代码", "修bug", "做个需求", "代码瘦身", "最简解法").
- Contrast:
  - ❌ *Bad*: `Code review focused exclusively on over-engineering and dead flexibility...` (abstract, never matches casual user requests).
  - ✅ *Good*: `Use when user asks to review diff, simplify, or says "帮我看看代码", "太臃肿了", "代码瘦身". Hunts dead code...`

### 3. The 80/20 Skill Pool Diet (Noise Reduction)
- Maintaining >100 skills in the prompt creates attention dilution (haystack effect).
- Ruthlessly prune long-tail toys, unused MLOps frameworks, and platform-incompatible tools. Keep the active pool compact (~30–50 high-leverage skills). Lower catalog noise yields higher retrieval accuracy for core disciplines.

---

## Verification & Pitfalls

- **Pitfall: Decoupled Skill Modifications and Watchdog Tracking**: Never modify, install, prune, or reject a skill in the filesystem without atomically updating `capability-inventory.json` and verifying CI in the very same turn. Modifying skills while forgetting the watchdog causes baseline drift, breaks daily automated upstream checks, and requires manual user intervention to fix.
- **Pitfall: Builtin Skill Curator Auto-Archiving Managed Skills**: When skills are version-controlled via Git or audited by capability watchdogs, explicitly disable the background skill curator (`curator.enabled: false` in `config.yaml`). The curator uses binary categorization where any skill absent from `.bundled_manifest` or `.hub/lock.json` is treated as disposable scratchwork, silently demoting (`stale`) or moving (`.archive/`) low-frequency domain skills after 30–90 days of inactivity, which corrupts local repository baselines and trips watchdog CI alarms.
- **Pitfall: Deceptive Single-Shot Benchmarks**: Never accept an external tool's self-reported benchmark without auditing its baseline. Many tools test against a verbose unprompted conversational model rather than an agentic baseline, artificially inflating reported savings.
- **Pitfall: Dynamic Modifiers Breaking Prompt Cache**: Reject proxies or interceptors that heuristically truncate logs, code, or context turns on the fly. Dynamic prompt mutation continuously breaks provider prefix cache hashes, causing downstream API costs to spike despite theoretical token reductions.
