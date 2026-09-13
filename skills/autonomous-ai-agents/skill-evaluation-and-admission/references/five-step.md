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
