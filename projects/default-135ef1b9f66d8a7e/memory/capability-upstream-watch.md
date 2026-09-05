---
name: capability-upstream-watch
description: shared-agent-memory 仓库的每日能力组件上游看门：清单比对+自动 Issue 提醒；含 ZCode 市场两层架构结论与本地一键检查
metadata:
  node_type: memory
  type: project
  originSessionId: sess_888b469b-882a-4e84-aeed-8d68b401a67c
---

**能力组件上游看门**（2026-09-05 建立，位于 shared-agent-memory 仓库 main 分支，用户感知 skill/mcp/plugin/核心工具新版本的统一渠道）：

- **组成**：`capability-inventory.json`（v2 已装版本清单）+ `scripts/check_capability_upstream.py`（stdlib 比对）+ `.github/workflows/capability-upstream-watch.yml`（每天北京时间 09:00 定时 + 手动 dispatch）+ `watch-capability.cmd`（本地一键全量检查并同步 Issue）。
- **检查源五类**：npm registry、GitHub Releases、ZCode 官方市场 CDN manifest（github 插件）、claude-plugins-official 市场 pinned sha、**local-merged-marketplace（客户端本地合并清单，仅本地运行，Actions 跳过）**。
- **ZCode 插件市场两层架构（2026-09-05 实查，修正早前「已下架」错误结论）**：UI 清单 = `bundled`（随客户端构建种子分发，source=filesystem，CDN 上无 zip）+ `cdn`（在线市场）合并；UI 真源文件 = `C:/Users/VOS-User/.zcode/cli/plugins/marketplaces/zcode-plugins-official/marketplace.json`（bundled-marketplace.json + cdn-marketplace.json 合并）。browser-use/computer-use/document-skills/skill-creator/zcode-guide/restore-legacy-sessions/android-emulator/ios-simulator/zcode-cua 共 9 个内置插件随客户端更新自动换代，已作为 `zcode-bundled-plugins` 组件纳入看门（本地检查）。
- **Issue 语义（label `capability-watch`）**：Issue 开着 = 清单落后于上游；升级组件后**必须把清单 `installed.version` 回写为新版并推 main**，下次运行自动收口。Actions 有 skipped_count 防误收口（本地源未检查时不关闭 Issue）。与 hermes 分支旧 watcher 的 `upstream-watch` 标签互不干扰。
- **首轮抓出（Issue #2）**：chrome-devtools-mcp 1.8.0（本地 1.7.0，且 claude 市场 pin 已推进）、context7-mcp 4.0.5（4.0.4）、github 插件 0.1.2（0.1.1）。
- **【用户拍板 2026-09-05】hermes-agent 与 ZCode CLI 本体永久不纳入看门**（各自自带更新机制）；未安装的市场插件（cloudbase-skills/example-plugin/代码安全防护）也不监控，代码安全防护在两份清单均未见、来源待查。
- **脚本坑位**：npm scoped 包需全量 URL 编码（@ 和 /）且必须用普通 Accept 头（GitHub 专用 Accept 会 406）；GitHub API 匿名限流需带 token；工作流建 Issue 前先确保标签存在；内置插件 zip 在 CDN 上连已装版本都 404，勿再试。
- **覆盖盲区**（清单 notWatched 同步维护）：hermes hub 技能（hermes GUI 自带提示）、http 远端 MCP（永远最新）、zcode-custom 自有 skill（无上游）。

**Why:** 更新源分散在 npm/GitHub/两个市场/客户端种子，人工逐个查不可持续；统一看门 + Issue 通知让用户及时用上新版本。
**How to apply:** 任何 Agent 升级/新装受监控组件后，顺手更新 capability-inventory.json 并推 main；ZCode 客户端更新后跑 watch-capability.cmd 检测内置插件换代；新增组件时在清单登记检查源。相关：[[hermes-to-zcode-capability-sync]] [[multi-branch-memory-backup]]
