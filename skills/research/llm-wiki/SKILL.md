---
name: llm-wiki
description: "建知识库/Karpathy wiki时必用。互链markdown KB构建查询。Karpathy's LLM Wiki: build/query interlinked markdown KB."
version: 2.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, rag-alternative]
    category: research
    related_skills: [obsidian, arxiv]
---

# Karpathy's LLM Wiki — Router

Build and maintain a persistent, compounding knowledge base as interlinked markdown files.
Based on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Unlike RAG (which rediscovers knowledge per query), the wiki compiles knowledge once and
keeps it current: cross-references already exist, contradictions are already flagged.

**Division of labor:** the human curates sources and directs analysis; the agent summarizes,
cross-references, files, and maintains consistency.

## Wiki location

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"   # WIKI_PATH 可在 ${HERMES_HOME:-~/.hermes}/.env 配置
```

## Architecture: three layers

```
wiki/
├── SCHEMA.md      # Conventions, structure rules, domain config
├── index.md       # Sectioned catalog with one-line summaries
├── log.md         # Chronological action log (append-only)
├── raw/           # L1: immutable sources (articles/ papers/ transcripts/ assets/)
├── entities/ concepts/ comparisons/ queries/   # L2: synthesized pages
└── ...
```

## Resuming an existing wiki (do this every session)

Before any wiki work, orient with:

```bash
cat "$WIKI/SCHEMA.md"
cat "$WIKI/index.md"
tail -50 "$WIKI/log.md"
```

Skip this only when initializing a brand-new wiki.

## Routing table

| Need | Read |
|---|---|
| 初始化新 wiki / SCHEMA·index·log 模板 | `references/schema-templates.md` |
| Ingest / Query / Lint / 批量导入 / 归档 | `references/operations.md` |
| Obsidian（含 headless 同步） | `references/obsidian-sync.md` |
| 常见坑 | `references/pitfalls.md` |

## Always-on rules

- Every synthesized page carries frontmatter + `[[wikilinks]]`; append to `log.md` after any mutation.
- Never edit `raw/` — it is immutable source material.
- New pages go to `entities/` (things), `concepts/` (ideas), `comparisons/` (A vs B), `queries/` (Q&A).
