---
name: claude-design
description: "做网页/落地页设计时必用。一次性HTML稿件：落地页/幻灯片/原型。Design one-off HTML artifacts (landing, deck, prototype)."
version: 1.2.0
author: BadTechBandit
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, html, prototype, ux, ui, creative, artifact, deck, motion, design-system]
    related_skills: [design-md, popular-web-designs, excalidraw, architecture-diagram]
---

# Claude Design for CLI/API Agents — Router

Produce one-off designed HTML artifacts (landing page, deck, prototype, component lab)
with Claude Design's taste but **without** hosted-UI plumbing. This file is a router.

## Skill selection (do this first)

| Skill | Use when the user wants... |
|---|---|
| **claude-design** (this) | From-scratch designed artifact, no brand/token system dictated |
| **popular-web-designs** | "make it look like Stripe / Linear / Vercel" — 54 ready-to-paste design systems |
| **design-md** | A formal machine-readable token spec file (DESIGN.md), not a rendered artifact |

They compose: `popular-web-designs` supplies vocabulary, `claude-design` drives the process.

## CLI/API mode

Ignore hosted-only concepts from source prompts: `done()`, `fork_verifier_agent()`,
`questions_v2()`, `copy_starter_component()`, `show_to_user()`, `show_html()`, `snip()`,
`eval_js_user_view()`, hosted asset review. Replace them with local file writes + verification.

## Routing table

| Need | Read |
|---|---|
| 端到端工作流（brief → 变体 → 交付） | `references/workflow.md` |
| 产出物格式与 HTML/CSS/JS 规范 | `references/artifact-rules.md` |
| 幻灯片 / 原型 / 变体规则 | `references/decks-prototypes.md` |
| AI 味检测与反 slop | `references/anti-slop.md` |
| 排版 / 配色 / 布局 / 动效 / 图像图标 | `references/visual-system.md` |
| 还原已有源码视觉 | `references/source-fidelity.md` |
| 交付前验证与响应格式 | `references/verification.md` |
| 常见坑 | `references/pitfalls.md` |

## Always-on rules

1. **Start from context, not vibes** — ask about audience/goals before drawing anything.
2. **Surface-first** — commit to a composition before touching tokens.
3. **No slop** — verify against `references/anti-slop.md` before delivering.
4. Deliverable is a **local HTML file**; verify it actually renders before claiming done.
