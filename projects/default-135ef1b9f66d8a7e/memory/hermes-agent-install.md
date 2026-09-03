---
name: hermes-agent-install
description: hermes-agent v0.21.0 重装完成（2026-09-02）：路径、代理依赖、Studio 已弃、待用户配 API key
metadata:
  node_type: memory
  type: project
  originSessionId: sess_76a3a301-0dc5-444b-9b1a-8b0802281a9c
---

NousResearch hermes-agent v0.21.0 于 2026-09-02 23 时重装完成并验证（doctor --fix 已跑、网关冒烟通过：Turn machinery warmed 8.4s + housekeeping + kanban dispatcher 均正常）。

- 代码：`%LOCALAPPDATA%\hermes\hermes-agent`（git checkout）；数据主目录 HERMES_HOME（用户环境变量）= `%LOCALAPPDATA%\hermes`；旧 `~\.hermes` 里 memories/sessions 为空、无有效数据，仅留作参考（其 config.yaml 含已失效的 4 个 hermes-studio MCP 条目，勿复制）。
- 安装/更新必须走本地代理 `127.0.0.1:3067`：git 克隆与 uv 下载 Python 默认不走系统代理，需 export HTTP(S)_PROXY 后再跑 install.ps1 / hermes update；PowerShell 的 Invoke-WebRequest 走系统代理所以 ZIP 回退能成功，属误导性假象。
- Hermes Studio（D:\hermes studio）已不存在，用户当时拒绝了 AppData 迁移；暂不装，CLI/TUI 即主用法。
- 主模型已接 ZCode-Antigravity 桥（[[user-windows-environment]]）：config.yaml `model: default gemini-3.7-flash / provider custom / base_url http://127.0.0.1:18080/v1 / api_key 取桥接 config.yaml 的 api-keys`；2026-09-02 `hermes -z` 一次性提问真机验证通过。使用前提：cli-proxy-api.exe 桥接进程须在运行。可换模型：claude-sonnet-4-6、gemini-3.6-flash 等（`hermes model`）。auxiliary 仍走 Nous/OpenRouter 未配置，其警告无害。
- **用户偏好 GUI 而非 TUI/CLI，桌面端界面语言已于 2026-09-02 切换为简体中文**：官方 Electron 桌面端已构建并跑通——`hermes desktop` 首跑自动 npm 构建（需代理环境变量），产物稳定路径 `hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe`；桌面快捷方式已改指此 exe（原 CLI 版启动方式作废）。`hermes dashboard` 是浏览器版配置管理页，`hermes serve` 是其无头后端。
- Windows 上游已知 bug：shutdown_watchdog 用 asyncio.start_unix_server 每次启动抛非致命 AttributeError，等官方修。
- **⚠ chrome-devtools-mcp 默认 --disable-extensions（2026-09-03 事故已修复）**：MCP 亲自拉起 Edge 时带 `--disable-extensions`，Edge 退出时把 Preferences 的 extensions.settings 清零 → 用户扩展/脚本"全消失"（数据未删：ScriptCat 数据目录 liilgpjgabokdklappibcjfablkpcekh 18MB 完整、解压版源目录都在）。**修复参数：`--ignore-default-chrome-arg=--disable-extensions`，ZCode 与 hermes 两边 MCP 配置均已加**。恢复：edge://extensions 开发者模式→从原路径重载解压版（ID 按路径哈希，同路径=同 ID=数据自动接回）：D:\extensions\extension(BewlyCat)、better-XiaoHeiHe-main(小黑盒)、LimeStartPage\src(青柠)、Desktop\make-bilibili-great-together\packages\extension\dist(mbgt)。ScriptCat 解压源目录已不存在，需重新下载后做数据迁移（改目录名 liilgp→新ID，涉及 Local/Sync Extension Settings + IndexedDB + Extension State）。
- ~~桌面快捷方式指 CLI~~（已改为 GUI，见上条）。
- **浏览器控制（2026-09-03 定案）**：hermes 挂载 ZCode 同款 chrome-devtools MCP 驱动**日常 Edge**——config.yaml `mcp_servers.chrome-devtools: command cmd + args [/c, npx, -y, chrome-devtools-mcp@1.7.0, --autoConnect, --user-data-dir=<Edge Dev User Data>]`，真机验证通过（开 example.com 取标题）。Windows 下 MCP 命令用 `cmd`+`/c` 包装最稳。每个 Edge 会话浏览器内可能需点一次「允许」。**勿走 CDP 端口路线**：Chromium 136+ 对默认配置目录硬禁 --remote-debugging-port，HKCU/HKLM 的 RemoteDebuggingAllowed 与 DevToolsRemoteDebuggingAllowed=1 均解不开（已实测勿重试；策略残留注册表无害）；Edge 快捷方式补丁已还原；browser.use_real_profile 路线已弃。
- 冒烟提示：网关就绪日志（Starting Hermes Gateway / Turn machinery warmed）写入 `%LOCALAPPDATA%\hermes\logs\gateway.log`，不进 stdout，验证时看文件别盯终端。
- **Edge 起不来=锁占用排查法（2026-09-03 实战）**：hermes 测试中断曾遗留 ①孤儿 chrome-devtools-mcp node 进程群、②无头 Playwright Chromium（进程名 chrome.exe、带真实 Edge User Data，Get-Process msedge 扫不到！）占住 `Edge Dev\User Data\lockfile` → Edge 静默秒退无窗口。修复：杀 ms-playwright/chrome-devtools-mcp 相关进程 → 删 lockfile 与 DevToolsActivePort → 重启 Edge。定位占用者用 handle.exe（live.sysinternals.com 下载，已存 D:\temp\handle.exe）。
- **ZCode 插件与 MCP 全量生态打通（2026-09-03）**：
  - Hermes 原生智能体插件（`%LOCALAPPDATA%\hermes\plugins\`）规范化接入：`desktop-commander`, `superpowers`, `serena`, `context7` 4 个插件全部就绪且由 Hermes 插件系统集中管理生命周期（GUI「插件」设置页直接可视化控制）。
  - Skills 结构化分类管理（`superpowers` 11 项、`zcode-custom` 7 项；移除冗余散装 github 技能，直接使用 Hermes 内置全功能 `software-development/github` 技能）。Hermes 与 ZCode 完全共享同等工具与方法论能力。

**Why:** 安装两次失败均因 git/uv 不走系统代理，且坏了的旧 checkout 会被安装器整目录移走导致运行时丢失；记住这些可避免重复踩坑。
**How to apply:** 任何 hermes 安装/更新/克隆 GitHub 的命令前先 export 代理变量；检查 hermes 状态看 logs\gateway.log 与 gateway_state.json（进程核对 tasklist）。相关：[[user-windows-environment]]
