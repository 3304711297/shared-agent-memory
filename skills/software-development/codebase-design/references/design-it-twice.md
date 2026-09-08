# Design It Twice (Fork-First 并行接口探索)

When designing a critical module interface or deepening candidate, use parallel subagents via `delegate_task`. Based on John Ousterhout's principle: *Your first design idea is rarely your best.*

## Process

### 1. Frame the Problem Space
Before delegating, summarize:
- The core constraints and domain requirements.
- Existing caller dependencies and category (see `deepening.md`).
- A quick ground-truth code sketch (not the final interface).

### 2. Spawn Subagents (Fork-First)
Spawn 2-3 subagents in parallel via `delegate_task`. Give each agent a distinct design bias:
- **Agent 1 (Minimal Surface)**: Aim for 1-2 entry points maximum. Push maximum complexity behind the seam.
- **Agent 2 (Flexibility & Extension)**: Design with clean lifecycle hooks and extensible options without leaking internals.
- **Agent 3 (Caller Ergonomics)**: Make the 90% default use-case a one-liner with zero configuration.

Each subagent returns:
1. Proposed interface (signatures, inputs, return types, error invariants).
2. Usage example at call sites.
3. What complexity is hidden behind the seam.
4. Trade-offs (where leverage is high vs where it is limited).

### 3. Compare and Recommend
Compare designs on:
- **Depth**: Leverage at the interface.
- **Locality**: Where changes and bugs concentrate.
- **Seam placement**: How natural it is to test and mock.

Synthesize the strongest elements or pick the clear winner before writing code.
