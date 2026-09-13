---
name: hermes-agent-skill-authoring
description: "写仓库内技能时必用。SKILL.md结构与frontmatter规范。Author in-repo SKILL.md files: frontmatter and structure."
version: 2.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, authoring, hermes-agent, conventions, skill-md]
    related_skills: [requesting-code-review]
---

# Authoring Hermes-Agent Skills — Router

In-repo skill authoring: tier decision, frontmatter hardlines, body structure, workflow.
This file is a router only.

## Routing table

| Need | Read |
|---|---|
| Tier 决策（bundled vs optional） | §Decide the Tier First（本文件下方） |
| frontmatter / description / author / related_skills 硬规则 | `references/frontmatter-rules.md` |
| 正文结构 + 写作质量原则 | `references/body-structure.md` |
| 新建/编辑工作流 + 测试文档要求 | `references/workflow.md` |
| 常见坑 + 验证清单 | `references/pitfalls-verify.md` |

## Decide the Tier First: Bundled vs Optional

- **Bundled**：所有会话高频刚需、无外部依赖、体积小。
- **Optional**：领域专用、有外部依赖或体积大——按需加载，不进默认池。
