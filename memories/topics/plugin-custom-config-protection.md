---
name: plugin-custom-config-protection
description: 本地核心插件 Windows 环境适配与静默配置保护规范，严禁上游直接覆盖
metadata:
  node_type: memory
  type: project
  originSessionId: sess_20260903_plugin_upstream_protection
---

# 本地核心插件定制配置保护规范

## 1. 定制背景与核心配置项
本地安装的 4 大核心插件针对 Windows 11 宿主系统与 Hermes Agent 进行了深度适配与静默化改造：

1. **`serena`**（`plugin.yaml` 与 `.mcp.json`）：
   - **静默化参数**：必须包含 `--enable-web-dashboard false --open-web-dashboard false --enable-gui-log-window false`，杜绝桌面弹窗与浏览器自动弹出；
   - **启动命令**：使用 `cmd /c uvx --from serena-agent serena ...`。
2. **`context7`**（`plugin.yaml`）：
   - **启动命令**：使用 `cmd /c npx -y @upstash/context7-mcp` 适配 Windows 下 Node 执行环境。
3. **`desktop-commander`**（`plugin.yaml`）：
   - **启动命令**：使用 `cmd /c npx -y @wonderwhy-er/desktop-commander@latest`。
4. **`superpowers`**（`plugin.yaml`）：
   - 精简技能路径为 Hermes 单层兼容路径，移除嵌套子目录。

## 2. 严禁盲目覆盖原则 (Anti-Overwrite Invariant)
- **上游更新模式**：GitHub Actions 仅检测并发布 Issue 通知（附带 Diff 对比），**严禁在 CI 或脚本中执行盲目的全局覆盖式 pull/copy**；
- **同步更新规则**：
  1. 仅拉取上游源码与上层技能更新；
  2. `plugin.yaml`、`.mcp.json`、`plugin.json` 等受保护文件必须保留本地 Windows / 静默化定制字段；
  3. 如上游配置文件结构发生重大升级，必须通过局部 Patch 手工/精确合入，确保 Windows 启动命令与静默参数不丢失。

**Why:** 盲目覆盖会把 Windows `cmd /c` 和 Serena 静默参数冲掉，导致 MCP 进程启动崩溃或每次调用频繁弹窗。  
**How to apply:** 收到上游更新 Issue 后，先检查受保护配置文件列表，仅增量合入核心逻辑与技能，保留 Windows 与静默参数配置。
