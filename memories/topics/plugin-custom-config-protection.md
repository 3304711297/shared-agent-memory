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

---

## 附：ScriptCat 全脚本静默失效事件（2026-09-04，已闭环 ✅）

- **现象**：Edge Dev 154.0.4251.0 + 脚本猫 1.4.0，所有用户脚本不注入（弹窗静态匹配仍显示「运行 (1/1)」，极具迷惑性）。
- **根因**：`chrome.scripting` 动态注册的 `scriptcat-scripting`（isolated world 广播者）丢失（`getRegisteredContentScripts()=[]`）；SW 的 `registerUserscripts()` 早退守卫（REGISTER_DONE + scriptcat-inject 存在 → return）导致永不补注册 → 三层握手（scripting.js 广播 broadcastEventFlag → inject/content 双 ack → 脚本清单下发 .slc/.elc）永不发生。
- **修复**：SW 上下文 `registerContentScripts` 补注册（`persistAcrossSessions: true`）。
- **验证（Hermes 复核 2026-09-04 晚）**：重启 Edge 后注册幸存（persistAcrossSessions 生效）；实测 GitHub（标题「我的仓库」）、Hugging Face（「模型」）、OpenRouter 汉化全部生效。
- **复发处置**：重跑 `C:\Users\VOS-User\AppData\Local\hermes\scripts\cdp_live.py`（`check-register` / `fix-register`）。技术要点：Edge 154 的 CDP HTTP 发现端点全 404，须从 `DevToolsActivePort` 文件读 WS 地址直连 + `suppress_origin=True`；MV3 SW 约 30s 休眠，需先开 options 页唤醒。WorkBuddy 侧同款工具在 `C:\Users\VOS-User\WorkBuddy\2026-09-04-16-45-23\`（cdp.py / fix_register.py / handshake_test.py）。
- **上游隐患**：Edge 154 isolated world 中 `chrome.extension` = undefined，脚本猫 scripting.js 顶层读 `chrome.extension.inIncognitoContext` 存在崩溃风险，建议向 scriptscat/scriptcat 反馈（连同早退守卫不校验 getRegisteredContentScripts 的问题）。
