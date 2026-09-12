---
name: codebase-design
description: "模块设计/接口设计时必用。小接口深实现，防臃肿包装。Use when designing modules, interfaces, or deep modules."
version: 1.0.0
author: "Matt Pocock (mattpocock/skills) + John Ousterhout + Hermes Agent"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [software-design, deep-modules, architecture, seams, interfaces, testability]
    related_skills: [test-driven-development, systematic-debugging, simplify-code, ponytail-review]
---

# Codebase Design (深模块架构与接缝设计)

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface. 

Based on John Ousterhout's *A Philosophy of Software Design*. The core goal is **leverage for callers, locality for maintainers, and testability for all**, preventing the AI anti-pattern of shallow pass-through wrappers.

## When to Use

- Designing a new component, service, or module interface
- Refactoring bloated or tangled logic to find clean seams
- Preventing "shallow modules" (large method signatures that merely forward calls)
- Designing interfaces for testability and high caller leverage

---

## Core Concepts & Unified Vocabulary

Use these terms precisely; avoid ambiguous substitutes like "unit", "component", "service", or "boundary".

* **Module**: Anything with an interface and an implementation (function, class, package, or subsystem).
* **Interface**: Everything a caller must know to use the module correctly (type signature, invariants, ordering constraints, error modes).
* **Implementation**: What's inside the module — the actual working logic.
* **Depth**: Leverage at the interface. High depth = large amount of capability behind a tiny interface. Low depth (shallow) = interface complexity almost equals implementation complexity.
* **Seam** (Michael Feathers): A place where you can alter behaviour without modifying that exact call site.
* **Adapter**: A concrete implementor that satisfies an interface at a seam (e.g. In-Memory Fake vs Postgres Repository).
* **Leverage**: Capability gained per unit of interface learned.
* **Locality**: Bug fixes and behavior changes concentrate in one place rather than rippling across callers.

---

## Deep vs Shallow Modules

```
┌─────────────────────┐
│   Small Interface   │  ← Few methods, simple primitive params
├─────────────────────┤
│                     │
│  Deep Implementation│  ← Complex business logic hidden inside
│                     │
└─────────────────────┘
     [Deep Module - PREFERRED]

┌─────────────────────────────────┐
│       Large Interface           │  ← Many verbose methods, leaking internals
├─────────────────────────────────┤
│  Thin Implementation            │  ← Just passes through / shallow wrapper
└─────────────────────────────────┘
     [Shallow Module - REJECT]
```

### Interface Design Checklist:
- [ ] Can I reduce the number of public methods?
- [ ] Can I simplify the parameters (favor simple types over leaky structs)?
- [ ] Can I hide internal state transitions behind the seam?

---

## Engineering Principles

1. **Depth is a property of the interface, not internal lines of code.** A deep module can internally use small helper functions; they simply must not leak out of the interface.
2. **The Deletion Test**: Imagine deleting the module. If complexity vanishes completely, it was a useless pass-through wrapper. If complexity reappears across 10 callers, it was earning its keep.
3. **The Interface is the Test Surface**: Callers and tests cross the exact same seam. If tests must pierce internal private states, the interface is improperly shaped.
4. **One adapter = hypothetical seam. Two adapters = real seam.** Do not introduce interfaces/ports unless at least two concrete adapters exist (e.g., Production + Test Mock). A single-adapter seam is speculative indirection.

---

## Designing for Testability

1. **Accept dependencies, do not instantiate them internally**:
   ```typescript
   // Testable (Deep seam)
   function processOrder(order: Order, paymentGateway: PaymentGateway): Result;
   
   // Hard to test (Coupled)
   function processOrder(order: Order): Result {
     const gateway = new StripeGateway(); // coupled
   }
   ```
2. **Return values, avoid implicit side-effects**:
   ```typescript
   // Testable: pure calculation
   function calculateDiscount(cart: Cart): Money;
   ```
3. **Small surface area**: Fewer methods = fewer test variations needed.

---

## Deepening & Exploration (Fork-First subagents)

- **Deepening existing shallow clusters**: See `references/deepening.md` for dependency categorization (In-process, Local-substitutable, Ports & Adapters, True external).
- **Design It Twice (Fork-First)**: See `references/design-it-twice.md`. When designing a critical module interface, spawn 2-3 parallel subagents via `delegate_task`, each exploring distinct interface styles (Minimal entry-points vs Flexibility vs Caller ergonomics) to select the optimal seam.
