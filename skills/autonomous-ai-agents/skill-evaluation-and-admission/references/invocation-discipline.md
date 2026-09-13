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
