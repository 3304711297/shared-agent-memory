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
- **检查源六类**：npm registry、GitHub Releases、ZCode 官方市场 CDN manifest（github 插件）、claude-plugins-official 市场 pinned sha、**local-merged-marketplace（客户端本地合并清单，仅本地运行，Actions 跳过）**、**github-commits-path（hermes hub 技能库 skills/ 目录提交基线，repo=NousResearch/hermes-agent）**。2026-09-05 起系统级 CLI 工具也纳入：gh/cli、git-for-windows、PowerShell、lychee（共 12 组件），gh-release 检查支持 `tag_strip` 剥离 tag 前缀（如 lychee-v）。
- **ZCode 插件市场两层架构（2026-09-05 实查，修正早前「已下架」错误结论）**：UI 清单 = `bundled`（随客户端构建种子分发，source=filesystem，CDN 上无 zip）+ `cdn`（在线市场）合并；UI 真源文件 = `C:/Users/VOS-User/.zcode/cli/plugins/marketplaces/zcode-plugins-official/marketplace.json`（bundled-marketplace.json + cdn-marketplace.json 合并）。browser-use/computer-use/document-skills/skill-creator/zcode-guide/restore-legacy-sessions/android-emulator/ios-simulator/zcode-cua 共 9 个内置插件随客户端更新自动换代，已作为 `zcode-bundled-plugins` 组件纳入看门（本地检查）。
- **Issue 语义（label `capability-watch`）**：Issue 开着 = 清单落后于上游；升级组件后**必须把清单 `installed.version` 回写为新版并推 main**，下次运行自动收口。Actions 有 skipped_count 防误收口（本地源未检查时不关闭 Issue）。与 hermes 分支旧 watcher 的 `upstream-watch` 标签互不干扰。
- **首轮差异（Issue #2，2026-09-05 当日全部落地并收口）**：chrome-devtools-mcp 1.8.0（双端 MCP 钉版已改、claude 市场插件重装至 pin 45f187b1、保护参数 `--ignore-default-chrome-arg=--disable-extensions` 已补回插件）；github 插件 0.1.2（CDN zip sha256 校验换装）；context7-mcp 确认为远端托管（http mcp.context7.com + npx 未钉版）自动最新，移出监控。
- **第二轮跟进与自动化收口闭环（Issue #3 & #4，2026-09-06 彻底收口归零）**：
  - **Issue #3（hermes-hub-skills 上游技能库同步）**：上游 `NousResearch/hermes-agent` skills 引入 `reddit-reading` 与 `rss-feeds`（commit `ee5b5ec2`）。Hermes 本地与 ZCode `~/.zcode/skills/` 均已同步迁入（总计 89 副本），清单基线更新为 `ee5b5ec2`。同时修补 `.github/workflows/capability-upstream-watch.yml`：移除 `skipped_count == '0'` 限制（防止云端 Actions 因跳过本地种子检查项而阻止自动关单），清单对齐后 Actions 自动留言并收口 Issue #3。
  - **Issue #4（desktop-commander / serena / context7 上游小更新评估）**：上游变动仅为 codespell 修正、LSP 内部坐标返回与文档补充；鉴于四大核心插件本地具有 Windows 平台定制保护规范（严禁盲目全量覆盖），评估无需改动并规范留言关单。
  - **hermes 分支 watcher 加固**：`plugin-upstream-watch.yml` 补齐 `Ensure upstream-watch label exists` 步骤（commit `a7c5875`），消除标签缺失红灯隐患。
  - **4 仓总盘点结案（2026-09-06）**：`youshouldknow`（外链超时自愈/Pages绿）、`huggingface-chinese-plus`（单测与规则基线对齐/CI绿）、`make-bilibili-great-together`（check/release 双 Job 隔离无缓存报错/Release绿）、`shared-agent-memory`（双分支看门与单测全绿，Issue 全收口），全面达成 0 故障、0 红点、0 遗留 Issue、0 待办 PR。
- **schedule 时线（2026-09-05 会话归档时状态）**：workflow 文件当日 03:26 UTC 才建到 main，此前仅手动 dispatch（当日 6 次：1 失败=Issue 创建前标签不存在，已由 `fix(watch): Issue 创建前先确保 capability-watch 标签存在` 自愈，其后全绿）；**首次 schedule 触发预计 2026-09-06 UTC 01:00（北京 09:00），归档时待验证**。
- **【重大事故复盘 2026-09-05】cli/config.json 的 provider.npm 字段导致整份用户配置被 CLI 静默丢弃**：桌面端/第三方工具写入的 provider 条目含 `npm` 键，而捆绑 CLI（zcode.cjs 0.16.5）的 zod schema 定义 `npm: g.never()`——出现即 parse 失败→配置回退空对象（无任何诊断输出）。症状：marketplace 来源插件（github/claude 市场系）全部显示 disabled、GUI 开关点击弹回、更新徽章异常；bundled 内置插件因走 officialPluginsEnabledByDefault 默认启用列表而看似正常，极具迷惑性。修复=删掉 provider 各条目的 `npm` 键（其他字段 passthrough 全兼容）。排查路径：CLI `plugins list --json` 状态矛盾 → 沙盒复刻（USERPROFILE 重定向+junction plugins 目录+二分 config 段落→字段）。**教训：cli/config.json 是 schema 强校验文件，手工/第三方工具写入前必须过 CLI `plugins list` 冒烟验证**。
- **无 CLI 的 ZCode 插件手工更新法（复刻安装器行为，已两次实操验证）**：下载 zip/tarball → 校验 sha256/来源 → 解压到 cache 新版本目录（zip 需剥离顶层前缀）→ installed_plugins.json 定向更新 version/installPath/updatedAt/source.sha（勿动 cacheTransactionId 等其余字段）→ 删旧版本目录（.git 只读 pack 需先 chmod -R u+w）→ 本地跑脚本验证全绿。注意 python 脚本内不可用 /tmp 路径（MSYS 虚拟路径，Windows python 看不到）。
- **GUI「可更新」徽章与开关的完整闭环（2026-09-05 终版）**：①开关失效根因=provider.npm 配置丢弃事故（详见下条），修复后恢复；②徽章比对源是本地市场快照 + **GUI 自己的 IndexedDB 安装记录（记装机时版本，感知不到任何 GUI 之外的变更）**——手工换装后徽章误报，点 GUI「更新」可消除；③**实测 GUI「更新」会按陈旧记录降级重装**（1.8.0→1.7.0，且不读已手工更新的市场快照文件）——降级后终态=活动插件目录 1.7.0、其 plugin.json 的 args 已补保护参数并钉 `chrome-devtools-mcp@1.8.0`、孤儿 1.8.0 目录已删；后续 GUI 再提示更新时须检查是否又降级并重补参数。已向 zai-org/feedback 提交 issue #527（含配置静默丢弃/开关弹回/徽章不感知/更新降级四案）。
- **ZCode 插件市场真源仓库（2026-09-05 用户发现）**：`zai-org/zcode-plugins`（官方内置+社区插件，17 个，CDN cdn-zcode.z.ai 是其镜像）——看门的 zcode-marketplace 检查已切换为优先拉取该仓库 raw marketplace.json、CDN 作回退；`zai-org/feedback`=官方用户反馈收集仓库（CLI 静默丢弃非法配置零诊断的行为值得去报一个）。
- **【用户拍板 2026-09-05】hermes-agent 与 ZCode CLI 本体永久不纳入看门**（各自自带更新机制；注意 hermes-agent 仓库的 skills/ 子目录提交监控属于技能库不属于本体）；未安装的市场插件（cloudbase-skills/example-plugin/代码安全防护）也不监控，代码安全防护在两份清单均未见、来源待查。
- **脚本坑位**：npm scoped 包需全量 URL 编码（@ 和 /）且必须用普通 Accept 头（GitHub 专用 Accept 会 406）；GitHub API 匿名限流需带 token；工作流建 Issue 前先确保标签存在；内置插件 zip 在 CDN 上连已装版本都 404，勿再试。
- **覆盖盲区**（清单 notWatched 同步维护）：hermes hub 技能（hermes GUI 自带提示）、http 远端 MCP（永远最新）、zcode-custom 自有 skill（无上游）。

**Why:** 更新源分散在 npm/GitHub/两个市场/客户端种子，人工逐个查不可持续；统一看门 + Issue 通知让用户及时用上新版本。
**How to apply:** 任何 Agent 升级/新装受监控组件后，顺手更新 capability-inventory.json 并推 main；ZCode 客户端更新后跑 watch-capability.cmd 检测内置插件换代；新增组件时在清单登记检查源。相关：[[hermes-to-zcode-capability-sync]] [[multi-branch-memory-backup]]
