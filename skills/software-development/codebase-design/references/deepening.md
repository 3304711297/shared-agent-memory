# Deepening (深化浅层模块)

How to deepen a cluster of shallow modules safely, given its dependencies. Assumes the vocabulary in `SKILL.md`: **module**, **interface**, **seam**, **adapter**.

## Dependency Categories

When assessing a candidate for deepening, classify its dependencies to determine testability across its seam:

### 1. In-process
Pure computation, in-memory state, no I/O. Always deepenable: merge the modules and test through the new interface directly. No adapter needed.

### 2. Local-substitutable
Dependencies that have local test stand-ins (SQLite/PGLite for database, in-memory mock filesystem). The seam is internal; no port needed at the module's external interface.

### 3. Remote but Owned (Ports & Adapters)
Your own internal services across a network boundary (microservices, RPC). Define a **port** (interface) at the seam. The deep module owns the business logic; the transport is injected as an **adapter**. Tests use an in-memory adapter; production uses an HTTP/gRPC adapter.

### 4. True External (Mock)
Third-party APIs (Stripe, GitHub, LLM gateways) outside your control. Injected port; tests use mock adapters.

## Seam Discipline
- **One adapter = hypothetical seam. Two adapters = real seam.** Don't introduce an interface unless two concrete implementations exist.
- **Internal seams vs external seams.** A deep module can have internal seams private to its implementation. Never expose internal seams through the public interface just to satisfy unit tests.

## Testing Strategy: Replace, Don't Layer
- Delete old tests on shallow wrappers once tests at the deepened interface exist.
- Tests assert on observable outcomes through the interface, not internal implementation variables.
