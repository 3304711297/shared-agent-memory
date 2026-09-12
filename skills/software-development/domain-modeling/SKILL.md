---
name: domain-modeling
description: "统一领域模型/定术语时必用。消概念漂移，建通用语言与ADR。Use when unifying domain models or defining shared terminology."
version: 1.0.0
author: "Matt Pocock (mattpocock/skills) + Hermes Agent"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [domain-driven-design, context, adr, ubiquitous-language, terminology, alignment]
    related_skills: [grill-me, requesting-code-review, writing-plans]
---

# Domain Modeling (统一领域建模与概念对齐)

Actively build and sharpen the project's domain model as you design. This is the **active** discipline: challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise.

(Merely *reading* `CONTEXT.md` for vocabulary is not this skill: that's a basic habit. This skill is for when you're shaping or altering the model, not just consuming it.)

## When to Use

- User discusses project domain concepts, terminology, or ambiguous naming
- Writing or editing a project's `CONTEXT.md` (domain dictionary)
- Evaluating or recording a major architectural decision (ADR) in `docs/adr/`
- When multiple agents (Hermes & ZCode) or developers use conflicting terminology for the same entity

## File Structure

Most repos have a single context:

```
/
├── CONTEXT.md                    ← Domain glossary (definitions only, NO implementation details)
├── docs/
│   └── adr/                      ← Key architectural decision records
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple bounded contexts pointing to respective sub-directories:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                      ← System-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

**Lazy Creation**: Only create files when there is concrete content. If no `CONTEXT.md` exists, create one when the first term is formally resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

---

## Operating Discipline

### 1. Challenge Against the Glossary (核对既有词典)
When the user or another agent uses a term that conflicts with `CONTEXT.md`, call it out immediately:
> *"Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"*

### 2. Sharpen Fuzzy Language (击碎模糊代称)
When the user uses vague or overloaded terms, propose a precise canonical term:
> *"You're saying 'account': do you mean the Customer or the User? Those are distinct entities."*

### 3. Discuss Concrete Scenarios (用具象场景压测边界)
When domain relationships are discussed, stress-test them with concrete edge cases:
> *"What happens if an order is partially refunded before shipping? Does it stay in 'Processing' or move to 'PartiallyRefunded'?"*

### 4. Cross-Reference With Code (实证代码实现)
When assertions are made about business logic, inspect the code directly (`search_files` / `read_file`):
> *"The code currently allows single-tenant isolation, but you stated this service is multi-tenant. Which is the target truth?"*

### 5. Update CONTEXT.md Inline (即时沉淀，严禁堆积)
When a domain term is resolved, update `CONTEXT.md` immediately. 
* See `references/context-format.md` for exact formatting.
* `CONTEXT.md` must be **totally devoid of implementation details**. It is a glossary and boundary map, not a scratchpad or tech spec.

### 6. Offer ADRs Sparingly (审慎提出 ADR)
Only offer to create an ADR when **ALL THREE** criteria are met:
1. **Hard to reverse**: The cost of changing your mind later is substantial.
2. **Surprising without context**: A future developer will look at the code and ask *"Why on earth was it built this way?"*
3. **The result of a real trade-off**: Genuine alternatives were evaluated and rejected for specific, verifiable reasons.

If any criterion is missing, skip the ADR. See `references/adr-format.md`.
