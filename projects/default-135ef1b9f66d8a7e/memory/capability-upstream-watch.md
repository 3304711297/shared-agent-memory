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
- **检查源六类**：npm registry、GitHub Releases、ZCode 官方市场 CDN manifest（github 插件）、claude-plugins-official 市场 pinned sha、**local-merged-marketplace（客户端本地合并清单，仅本地运行，Actions 跳过）**、**github-commits-path（hermes hub 技能库 skills/ 目录提交基线，repo=NousResearch/hermes-agent）**。
- **ZCode 插件市场两层架构（2026-09-05 实查，修正早前「已下架」错误结论）**：UI 清单 = `bundled`（随客户端构建种子分发，source=filesystem，CDN 上无 zip）+ `cdn`（在线市场）合并；UI 真源文件 = `C:/Users/VOS-User/.zcode/cli/plugins/marketplaces/zcode-plugins-official/marketplace.json`（bundled-marketplace.json + cdn-marketplace.json 合并）。browser-use/computer-use/document-skills/skill-creator/zcode-guide/restore-legacy-sessions/android-emulator/ios-simulator/zcode-cua 共 9 个内置插件随客户端更新自动换代，已作为 `zcode-bundled-plugins` 组件纳入看门（本地检查）。
- **Issue 语义（label `capability-watch`）**：Issue 开着 = 清单落后于上游；升级组件后**必须把清单 `installed.version` 回写为新版并推 main**，下次运行自动收口。Actions 有 skipped_count 防误收口（本地源未检查时不关闭 Issue）。与 hermes 分支旧 watcher 的 `upstream-watch` 标签互不干扰。
- **首轮差异（Issue #2，2026-09-05 当日全部落地并收口）**：chrome-devtools-mcp 1.8.0（双端 MCP 钉版已改、claude 市场插件重装至 pin 45f187b1、保护参数 `--ignore-default-chrome-arg=--disable-extensions` 已补回插件）；github 插件 0.1.2（CDN zip sha256 校验换装）；context7-mcp 确认为远端托管（http mcp.context7.com + npx 未钉版）自动最新，移出监控。
- **【重大事故复盘 2026-09-05】cli/config.json 的 provider.npm 字段导致整份用户配置被 CLI 静默丢弃**：桌面端/第三方工具写入的 provider 条目含 `npm` 键，而捆绑 CLI（zcode.cjs 0.16.5）的 zod schema 定义 `npm: g.never()`——出现即 parse 失败→配置回退空对象（无任何诊断输出）。症状：marketplace 来源插件（github/claude 市场系）全部显示 disabled、GUI 开关点击弹回、更新徽章异常；bundled 内置插件因走 officialPluginsEnabledByDefault 默认启用列表而看似正常，极具迷惑性。修复=删掉 provider 各条目的 `npm` 键（其他字段 passthrough 全兼容）。排查路径：CLI `plugins list --json` 状态矛盾 → 沙盒复刻（USERPROFILE 重定向+junction plugins 目录+二分 config 段落→字段）。**教训：cli/config.json 是 schema 强校验文件，手工/第三方工具写入前必须过 CLI `plugins list` 冒烟验证**。
- **无 CLI 的 ZCode 插件手工更新法（复刻安装器行为，已两次实操验证）**：下载 zip/tarball → 校验 sha256/来源 → 解压到 cache 新版本目录（zip 需剥离顶层前缀）→ installed_plugins.json 定向更新 version/installPath/updatedAt/source.sha（勿动 cacheTransactionId 等其余字段）→ 删旧版本目录（.git 只读 pack 需先 chmod -R u+w）→ 本地跑脚本验证全绿。注意 python 脚本内不可用 /tmp 路径（MSYS 虚拟路径，Windows python 看不到）。
- **GUI「可更新」徽章与开关的两个坑（2026-09-05）**：①徽章比对源是客户端本地市场快照 `plugins/marketplaces/claude-plugins-official/.claude-plugin/marketplace.json`（8 月快照、非 git 不会自更新）——手工换装后 pin ≠ 已装 sha 会误报可更新，定向补丁该文件的 sha 字段即可；②客户端运行中内存注册表不感知手工换装，启用开关会因校验旧路径（已删目录）失败而弹回，重启客户端即恢复（enabledPlugins 真值存 cli/config.json 未丢）。
- **【用户拍板 2026-09-05】hermes-agent 与 ZCode CLI 本体永久不纳入看门**（各自自带更新机制；注意 hermes-agent 仓库的 skills/ 子目录提交监控属于技能库不属于本体）；未安装的市场插件（cloudbase-skills/example-plugin/代码安全防护）也不监控，代码安全防护在两份清单均未见、来源待查。
- **脚本坑位**：npm scoped 包需全量 URL 编码（@ 和 /）且必须用普通 Accept 头（GitHub 专用 Accept 会 406）；GitHub API 匿名限流需带 token；工作流建 Issue 前先确保标签存在；内置插件 zip 在 CDN 上连已装版本都 404，勿再试。
- **覆盖盲区**（清单 notWatched 同步维护）：hermes hub 技能（hermes GUI 自带提示）、http 远端 MCP（永远最新）、zcode-custom 自有 skill（无上游）。

**Why:** 更新源分散在 npm/GitHub/两个市场/客户端种子，人工逐个查不可持续；统一看门 + Issue 通知让用户及时用上新版本。
**How to apply:** 任何 Agent 升级/新装受监控组件后，顺手更新 capability-inventory.json 并推 main；ZCode 客户端更新后跑 watch-capability.cmd 检测内置插件换代；新增组件时在清单登记检查源。相关：[[hermes-to-zcode-capability-sync]] [[multi-branch-memory-backup]]
