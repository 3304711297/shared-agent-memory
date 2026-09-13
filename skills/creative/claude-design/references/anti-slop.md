## Content Discipline

Do not add filler content.

Every element must earn its place.

Avoid:

- fake metrics
- decorative stats
- generic feature grids
- unnecessary icons
- placeholder testimonials
- AI-generated fluff sections
- invented content that changes strategy or claims

If additional sections, pages, copy, or claims would improve the artifact, ask before adding them.

When copy is necessary but not final, mark it as draft or placeholder.

## Anti-Slop Rules

Avoid common AI design sludge:

- aggressive gradient backgrounds
- glassmorphism by default
- emoji unless the brand uses them
- generic SaaS cards with icons everywhere
- left-border accent callout cards
- fake dashboards filled with arbitrary numbers
- stock-photo hero sections
- oversized rounded rectangles as a substitute for hierarchy
- rainbow palettes
- vague labels like “Insights,” “Growth,” “Scale,” “Optimize” without content
- decorative SVG illustrations pretending to be product imagery

Minimal is not automatically good. Dense is not automatically cluttered. Choose intentionally.

## Slop Diagnostic: Score Before You Fix

AI design slop has a tiny, predictable failure distribution — designers asked to label AI UIs collapse the "this is AI" signal down to about ten tells. Before polishing or repairing an artifact, run this as an explicit self-audit and write a short report. **Diagnose first, treat second** — auditing and fixing in one breath fails, because the model's prior outweighs the instruction and it repeats the mistake (recolors when it needed re-layout, polishes type on a composition problem).

The ten tells (presence of each = one point of slop; lower is better):

1. **Tech gradient** — blue/violet/indigo glossy gradient on everything.
2. **Generic tech hue** — the default accent is indigo/violet (not chosen for the brand, just the model's favorite).
3. **Feature-tile grid** — icon + heading + sentence × 3, all equal weight, nothing prioritized.
4. **Accent rail** — a colored left strip on cards: decoration pretending to be organization.
5. **Unearned blur** — glassmorphism with no real depth/elevation system behind it.
6. **Monument stat** — oversized numbers filling space that should carry product story.
7. **Icon topper** — a rounded-square icon centered above every heading (Tailwind-template filler).
8. **Center stack** — everything centered because no real composition was committed to.
9. **Default type** — Inter (or system-ui) used by default rather than chosen.
10. **Wrong surface** — the composition doesn't match the surface (e.g. a hero on a Monitor surface). This is the root cause behind most of the others.

How to run it:

- Score the artifact out of 10 (10 = maximum slop). State the score and list which tells fired, in one short report.
- Treat the report as **context, not a to-do list** — it tells you *where* to spend repair effort, it does not dictate edits.
- Then repair, matched to the diagnosis:
  - tells 3, 8, 10 → **re-layout / re-compose** (revisit the surface choice — do not recolor).
  - tells 1, 2, 9 → **recolor / re-typeset** (palette and type are genuinely the problem here).
  - tells 4, 5, 6, 7 → **remove the decoration**; replace it with real hierarchy (scale, weight, spacing).
- Re-score after repairing. Do not declare done while compositional tells (3, 8, 10) are still firing — those are causes, the rest are usually symptoms.

The point of separating diagnosis from treatment: let the audit complain first, then fix only what it complained about, in the register the complaint calls for.
