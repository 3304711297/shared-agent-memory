---
name: serena-mcp-silent-config
description: Serena 插件（MCP）静默运行配置（禁用 Dashboard 与 GUI 日志弹窗，离线快速启动）
metadata:
  node_type: memory
  type: project
  originSessionId: sess_e9f64bdf-b2b7-44d6-8d98-2141892c8505
---

## Serena 插件静默配置与弹窗禁用机制（2026-09-03）

### 1. 弹窗问题与根因
- 原 Serena 插件启动时会默认开启图形化 Web Dashboard / 系统托盘 / GUI Log Window，导致每次调用 MCP 工具时桌面都会弹窗并需手动关闭。
- 原 `.mcp.json` 使用 `--from git+https://github.com/oraios/serena`，每次启动均尝试网络检查与 git fetch，因未显式带代理易引发连接超时和进程重启。

### 2. 静默与离线快速启动配置
1. **全局配置静默化**（`~/.serena/serena_config.yml`）：
   - `gui_log_window: false`（关闭 GUI 日志窗口）
   - `web_dashboard: false`（禁用 Web Dashboard）
   - `web_dashboard_open_on_launch: false`（禁止启动弹窗/浏览器）
2. **MCP 启动参数优化**（`.mcp.json`，包括 cache 与 marketplaces 对应路径）：
   - 使用本地已预装好的 `uvx --from serena-agent serena start-mcp-server`，避免每次启动联网 git fetch。
   - 显式附加 CLI 参数保证绝对静默：
     `--enable-web-dashboard false --open-web-dashboard false --enable-gui-log-window false`
3. **本地预编译工具**：已通过 `uv tool install git+https://github.com/oraios/serena` 预装至本地 uv tool cache。

**Related:** [[user-windows-environment]]
