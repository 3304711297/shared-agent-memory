---
name: ponytail-audit
description: "全库查过度工程时必用。扫全仓列可删可简化项。Whole-repo audit for over-engineering: ranked list of what to delete."
---

ponytail-review, repo-wide. Scan the whole tree instead of a diff. Rank
findings biggest cut first.

## Tags

Same tag vocabulary as `ponytail-review` — read that skill's Format section for definitions (`delete`/`stdlib`/`native`/`yagni`/`shrink`). Do not duplicate its examples here.

## Hunt

Deps the stdlib or platform already ships, single-implementation interfaces,
factories with one product, wrappers that only delegate, files exporting one
thing, dead flags and config, hand-rolled stdlib.

## Output

One line per finding, ranked: `<tag> <what to cut>. <replacement>. [path]`.
End with `net: -<N> lines, -<M> deps possible.` Nothing to cut: `Lean already. Ship.`

## Boundaries

Scope: over-engineering and complexity only. Correctness bugs, security holes,
and performance are explicitly out of scope. Route them to a normal review
pass. Lists findings, applies nothing. One-shot.
"stop ponytail-audit" or "normal mode" to revert.
