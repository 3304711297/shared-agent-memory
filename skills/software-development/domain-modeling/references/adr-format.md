# ADR Format

ADRs live in `docs/adr/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`, etc.
Create the `docs/adr/` directory lazily: only when the first ADR is needed.

## Template

```markdown
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

That's it. An ADR can be a single paragraph. The value is in recording *that* a decision was made and *why*, not in filling out bureaucratic sections.

## Optional Sections (Only when adding genuine leverage)

- **Status** frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`)
- **Considered Options**: Only when rejected alternatives are critical to remember.
- **Consequences**: Only when non-obvious downstream side-effects must be documented.

## When to Offer an ADR (Strict Three-Gate Rule)

All three must be true:
1. **Hard to reverse**: The cost of changing later is meaningful.
2. **Surprising without context**: A future developer will wonder why it wasn't done the standard way.
3. **The result of a real trade-off**: Genuine alternatives were weighed.

### What Qualifies:
- **Architectural shape**: Monorepo layout, CQRS / Event-sourcing, DB write/read separation.
- **Integration boundaries**: Domain events vs synchronous REST between subsystems.
- **High lock-in technology choices**: Auth providers, core ORM/query engine, database.
- **Deliberate deviations**: "Manual SQL instead of ORM because of query latency". Stops future agents from "fixing" deliberate design choices.
