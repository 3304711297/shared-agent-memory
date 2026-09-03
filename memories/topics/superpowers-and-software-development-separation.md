---
name: superpowers-and-software-development-separation
description: Superpowers 与 Software-Development 技能分类的同名冲突历史、去重清理与权责分工规范
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_20260903_skills_audit
---

# Superpowers 与 Software-Development 技能去重与架构分工

## 1. 历史冲突与清理背景
早期在 Hermes 中引入 `superpowers` 套件时，系统出现了跨分类同名冲突与二级目录嵌套问题：
1. **跨分类同名冲突**：`requesting-code-review`、`systematic-debugging`、`test-driven-development` 3 个核心技能同时存在于官方默认的 `software-development/` 分类和 `superpowers/` 插件套件中，导致 Hermes 技能索引产生同名冲突警告。
2. **二级同名嵌套**：早期本地解压时 `superpowers` 内部出现了多余嵌套（如 `superpowers/brainstorming/brainstorming/SKILL.md`）。
3. **清理与收拢（Commit `cddb3d5`）**：
   - 彻底移除了 `skills/software-development/` 下重复的 3 个同名旧版技能；
   - 拍平了 `skills/superpowers/` 内部的多余子目录层级；
   - 将全套方法论规范统一收归到 `superpowers/` 独立管理。

## 2. 核心架构权责分工

| 类别分类 | 核心定位与职责 | 代表技能清单 |
| :--- | :--- | :--- |
| **`superpowers/`** | **软件工程方法论与流程门禁体系**<br>指导 Agent 规范化思考、规划与实施全流程。 | `brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `test-driven-development`, `systematic-debugging`, `requesting-code-review`, `receiving-code-review`, `verification-before-completion`, `using-git-worktrees`, `finishing-a-development-branch` |
| **`software-development/`** | **具体开发工具、语言调试与底层能力**<br>提供语言级单步调试、代码库静态分析与平台 CLI。 | `github` (gh CLI), `python-debugpy` (Python DAP/pdb), `node-inspect-debugger` (Node.js CDP), `ast-grep`, `code-wiki`, `simplify-code`, `codebase-inspection`, `dogfood`, `rest-graphql-debug`, `grill-me`, `spike` |

**Why:** 消除跨分类同名冗余，使流程规范（方法论）与工程工具（具体实现工具）清晰解耦，保证 Hermes 技能索引解析 100% 唯一且高效。  
**How to apply:** 开发前强制调用 `superpowers` 引导流程；在实施、调试与交互阶段调用 `software-development` 具体工具（如 Python 调试用 `python-debugpy`，Node.js 调试用 `node-inspect-debugger`）。
