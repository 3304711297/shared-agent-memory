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
- Windows 上游已知 bug：shutdown_watchdog 用 asyncio.start_unix_server 每次启动抛非致命 AttributeError，等官方修。
- 待办（用户手动）：`hermes setup` 或 `hermes auth` 配置主模型 API key（现 provider: auto 走 OpenRouter 端点但无 key，auxiliary 报 no Nous authentication / payment error 属预期）。
- 冒烟提示：网关就绪日志（Starting Hermes Gateway / Turn machinery warmed）写入 `%LOCALAPPDATA%\hermes\logs\gateway.log`，不进 stdout，验证时看文件别盯终端。

**Why:** 安装两次失败均因 git/uv 不走系统代理，且坏了的旧 checkout 会被安装器整目录移走导致运行时丢失；记住这些可避免重复踩坑。
**How to apply:** 任何 hermes 安装/更新/克隆 GitHub 的命令前先 export 代理变量；检查 hermes 状态看 logs\gateway.log 与 gateway_state.json（进程核对 tasklist）。相关：[[user-windows-environment]]
