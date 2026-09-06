---
name: hermes-to-zcode-capability-sync
description: 2026-09-05 Hermes→ZCode 能力全量同步记录：87 skills 迁入、deepwiki MCP 新增、去重与跳过清单、记忆库补差
metadata:
  node_type: memory
  type: project
  originSessionId: sess_888b469b-882a-4e84-aeed-8d68b401a67c
---

2026-09-05 执行 Hermes→ZCode 能力同步（用户指令：复制全部 skill/mcp/工具集/plugin，跳过重复与 Hermes 专有）：

**Skills（复制 87 个到 `~/.zcode/skills/`，扁平化，零重名冲突）**：creative 22、research 12、productivity 11、software-development 10、autonomous-ai-agents 5、devops 5、mlops 5、security 4、media 3、web-development 3、email 2、mcp 2（fastmcp/mcporter）、note-taking 1（obsidian）、social-media 1（xurl）、web 1（blocked-page-recovery）。新 skill 下次 ZCode 会话生效。
- **2026-09-06 增量迁入**：上游 `NousResearch/hermes-agent` skills 引入 `reddit-reading` 与 `rss-feeds`（HEAD@`ee5b5ec2`），同步优化 `competitor-news-monitor` 与 `grounded-citations`；已完整同步至 `~/.zcode/skills/`，ZCode 技能副本增至 89 个。
- **2026-09-06 闲置退役**：双端卸载清理 `antigravity-cli`（本地未安装 `agy` 独立 CLI 二进制，编程工作流已由底层工具链及子代理闭环，保留属冗余空置）。Hermes 端经 `hermes skills uninstall` 移除，ZCode 端同步删除 `~/.zcode/skills/antigravity-cli` 目录，ZCode 迁入技能副本收敛至 88 个。

**跳过-重复**：zcode-custom 6 项（与 ZCode 现有逐字节一致）；superpowers 14 项（ZCode 插件同为 obra/superpowers v6.3.0，含相同 14 skills）；productivity 的 docx/pdf/powerpoint/xlsx（document-skills 插件已有）；software-development/github（github 插件已有）；autonomous-ai-agents/computer-use（computer-use 插件已有，且重名会遮蔽插件 skill）。

**跳过-Hermes 专有**：hermes/hermes-quota-embedded、hermes-auxiliary-models、dogfood/adversarial-ux-test、software-development/{dogfood,hermes-agent-skill-authoring,inspecting-hermes-desktop-dom}、autonomous-ai-agents/hermes-agent、zcode-custom/shared-agent-memory（hermes 读共享库的入口协议）、apple（仅 DESCRIPTION.md 无实体 skill）、token-stats 插件（hermes 配额监控后端）。

**MCP**：仅 deepwiki 为 ZCode 缺口，已加 `~/.zcode/cli/config.json` mcp.servers：`{"type":"http","url":"https://mcp.deepwiki.com/mcp","enabled":true}`（重启 ZCode 生效）。chrome-devtools/desktop-commander/serena/context7 ZCode 均已以插件形式存在，不重复加裸 MCP。hermes 的 platform_toolsets 为 hermes 内部概念，无可迁内容。

**记忆库补差**（方向 hermes 分支→ZCode 共享库）：提取 7 个缺失文件（codebuddy2openai-tauri-gui、gateway-migration-easycliproxyapi-and-browser-protection、hermes-quota-embedded、hermes-skills-and-mcp-optimization-2026-09-03、plugin-custom-config-protection、superpowers-and-software-development-separation、workbuddy-proxy-startup）；合并 5 个分叉文件（bilibili-great-together-project 补 Issue#9/upstream-watch 幂等修复、desktop-projects-tweak-youshouldknow 补 Kiwi-Tweaks/Atom-Tool-Box 吸收、hermes-agent-install 补 token-stats 服务与更新弹窗锁、user-windows-environment 换 EasyCLIProxyAPI 新架构并保留 ZCode skills 清单、youshouldknow-bios-knowledge-series 推进到 d0fc852/EP15）；USER.md 偏好沉淀为 [[user-global-preferences]]。

**Why:** 两端能力对齐防漂移；记录去重边界避免后续重复迁移或误删。
**How to apply:** 后续 hermes 装新 skill 时按同样规则评估单向增量迁移；勿把 Hermes 专有项再搬过来；验证 skill 生效看新会话技能列表。相关：[[hermes-agent-install]] [[multi-branch-memory-backup]]
