---
name: capability-upstream-watch
description: shared-agent-memory 仓库的每日能力组件上游看门：清单比对+自动 Issue 提醒；升级后必须回写清单推 main
metadata:
  node_type: memory
  type: project
  originSessionId: sess_888b469b-882a-4e84-aeed-8d68b401a67c
---

**能力组件上游看门**（2026-09-05 建立，位于 shared-agent-memory 仓库 main 分支，用户感知 skill/mcp/plugin/核心工具新版本的统一渠道）：

- **组成**：`capability-inventory.json`（已装版本清单）+ `scripts/check_capability_upstream.py`（纯 stdlib 比对）+ `.github/workflows/capability-upstream-watch.yml`（每天北京时间 09:00 定时 + 手动 dispatch）。
- **检查源四类**：npm registry（chrome-devtools-mcp/context7-mcp/desktop-commander）、GitHub Releases（superpowers/serena/CLIProxyAPI）、ZCode 官方市场 CDN manifest（github 插件）、claude-plugins-official 市场 pinned sha（chrome-devtools/superpowers 插件壳）。
- **Issue 语义（label `capability-watch`）**：Issue 开着 = 清单落后于上游；升级组件后**必须把清单 `installed.version` 回写为新版并推 main**，下次运行自动收口 Issue。与 hermes 分支旧 watcher 的 `upstream-watch` 标签互不干扰。
- **首轮抓出（2026-09-05，Issue #2）**：chrome-devtools-mcp 1.8.0（本地 1.7.0）、context7-mcp 4.0.5（4.0.4）、github 插件 0.1.2（0.1.1）。
- **已下架发现**：browser-use/computer-use/document-skills/skill-creator/zcode-guide 五个 ZCode 官方插件已从市场 manifest 移除（本地仍启用），无上游可查，已记入清单 notWatched。
- **脚本坑位**：npm scoped 包需全量 URL 编码（@ 和 /）且不能用 GitHub 专用 Accept 头（否则 406）；GitHub API 匿名限流需带 token；工作流建 Issue 前先确保标签存在。
- **覆盖盲区**（清单 notWatched 字段同步维护）：hermes hub 技能（hermes GUI 自带提示）、hermes-agent 与 ZCode CLI 本体（自带更新机制）、http 远端 MCP（永远最新）、zcode-custom 自有 skill（无上游）。
- **注意**：hermes 分支上的旧 `plugin-upstream-watch.yml` 因默认分支切到 main 其 schedule 已不再触发（GitHub 只跑默认分支的定时），其插件监控职责已由本看门接管；该文件保留在 hermes 分支无副作用。

**Why:** 更新源分散在 npm/GitHub/两个市场，人工逐个查不可持续；统一看门 + Issue 通知让用户及时用上新版本。
**How to apply:** 任何 Agent 升级/新装受监控组件后，顺手更新 capability-inventory.json 并推 main；新增组件时在清单登记检查源。相关：[[hermes-to-zcode-capability-sync]] [[multi-branch-memory-backup]]
