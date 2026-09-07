---
name: browser-automation-and-ego-lite-evaluation
description: 真实浏览器接管/自动化技术路线评估与 ego-lite 调研记录（批量脚本降 Token、跨平台 Skill 选型、Edge Dev 安全边界）
metadata:
  type: reference
---

# 真实浏览器接管/自动化技术路线评估与 ego-lite 调研记录

## 一、 ego-lite 核心机制与评估结论（2026-09-07）

- **技术定位**：CitroLabs 出品的专为 AI Agent（Codex、Claude Code、DSH 等）设计的 Chromium 衍生浏览器（GitHub: `citrolabs/ego-lite`）。
- **核心特色**：
  1. **无感凭证克隆**：首次启动读取 Chrome 数据（Cookie、LocalStorage、系统钥匙串），免去重复登录。
  2. **Spaces 虚拟空间隔离**：Agent 在后台独立 Spaces 执行自动化，不抢占前台焦点，不污染用户主标签页。
  3. **Heredoc 批量脚本执行（对齐 PTC 范式）**：摒弃传统 Agent “看一眼→调一步” 的交互式 REPL 循环，一次性下发包含等待、选择器定位、DOM 操作与数据清洗的完整 Node/Playwright 脚本，实测节约约 21.6% Token 消耗，速度提升 35%。
- **当前局限与用户适配性**：
  - **操作系统限制**：当前正式版**仅支持 macOS**，Windows 与 Linux 尚在官方路线图中。用户主力机为 Windows 11（机械革命极光 X），现阶段无法直接运行。
  - **安全与环境敞口**：直接读取个人主凭据存在潜在注入与泄漏风险；且用户此前已有自动化工具自启真实 profile 导致扩展被 Edge 垃圾回收的血泪教训（见 [[edge-dev-cdp-mcp-setup]]），不宜再随意接入第三方未隔离浏览器。

## 二、 社区已有/开箱即用的浏览器自动化 Skill 选型

为避免每次从头编写 CDP/Puppeteer 脚本浪费大量 Token，社区已有数个高成熟度的现成 Skill：

| Skill 名称 | 来源仓库 | 平台支持 | 核心亮点与执行机制 |
| :--- | :--- | :--- | :--- |
| **dev-browser** | `SawyerHood/dev-browser` | **Windows** / macOS / Linux | 专为 Coding Agent 打造，支持 `--connect` 自动发现并挂接运行中的 Chrome/Edge；支持 Heredoc 批量脚本在 QuickJS 沙箱执行；内置 `page.snapshotForAI()` 生成专为 LLM 压缩的语义快照，官方测试 Token 费用降至 $0.88（对比 MCP 的 $1.45+）。 |
| **attach-to-browser-skill** | `cskwork/attach-to-browser-skill` | **Windows** / macOS / Linux | 包装 `dev-browser --connect`，专攻复用用户已登录的真实会话（SSO/2FA），附带严格的安全准则（禁自动提交/买单/改密）。 |
| **faster-chrome-devtools-skill** | `zeke/faster-chrome-devtools-skill` | 跨平台 (Node.js) | 极轻量，基于原生 WebSocket 直连 CDP 端口；提供高内聚 CLI 命令与压缩 a11y 树快照，无 Playwright 等重依赖。 |
| **ego-browser** | `citrolabs/ego-lite` | 仅 macOS | 官方配套技能（`npx skills add citrolabs/ego-lite`），强绑定 ego-lite 桌面端，依赖其底层定制内核。 |

## 三、 用户环境落地方案与降 Token 实践原则

1. **信息获取分流原则**：
   - **公开网页/文章提取**：坚决走 Exa 独享（`web_search` / `web_extract`），耗时秒级且完全免除浏览器开销。
   - **个人书签与历史**：走本地 `search_bookmarks.py`（10ms）与 OpenViking 向量检索，不走浏览器界面。
   - **真实登录态/复杂后台操作**：唤起 Edge Dev（`chrome-devtools` MCP 直连），或在需要复杂交互时引入 `dev-browser` Skill。
2. **浏览器自动化防 Token 浪费铁律（PTC 思维）**：
   - 严禁“截屏一次→大模型推理一步→再点击一次”的漫长往返。
   - 优先通过 `mcp__chrome_devtools__evaluate_script` 或 `dev-browser` 批量脚本，在页面上下文跑完轮询选择器与数据清洗，仅将结构化 JSON 返回大模型。
3. **安全红线**：
   - 严格维持 `chrome-devtools` 的 `--autoConnect` 纯挂接模式，严禁带 `--user-data-dir` 触发孤儿自启；
   - 严防清空用户 Edge Dev 的扩展目录（`D:\extensions`）与凭证。

相关记忆：[[edge-dev-cdp-mcp-setup]] [[user-windows-environment]] [[hermes-search-provider-exa-and-cleanup]]
