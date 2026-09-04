---
name: gateway-migration-easycliproxyapi-and-browser-protection
description: 2026-09-04 网关迁移至 EasyCLIProxyAPI (Gemini 3.8/3.7) 实录与浏览器扩展清空故障根因隔离
metadata:
  type: project
---

# 网关架构迁移与浏览器扩展防护专题档案

## 一、 事件概述（2026-09-04）

### 1. Hermes `auth_unavailable` 故障复盘与根因
- **现象**：Hermes 请求 `gemini-3.7-flash` / `gemini-3.8-flash` 报 `HTTP 503: auth_unavailable: no auth available (providers=antigravity)`。
- **根因锁定**：ZCode-Antigravity 的 `cli-proxy-api.exe` 被本地裸 `go build` 覆盖，缺少了官方发布流水线中使用 `-X` ldflags 注入的 Antigravity OAuth client ID 和 secret（源码中变量默认为空，依赖构建期注入）。运行时首次请求抛出 `500 antigravity OAuth client is not configured`，该凭据被标记不可用后，后续请求均返回 `503 auth_unavailable`。
- **与 Hermes 关系**：彻底排除 Hermes 配置或环境变量问题，Hermes 仅为下游消费端。

### 2. 最终架构决策与迁移落地
- **PR 归档**：3.8 适配改动已在 fork（`3304711297/ZCode-Antigravity`）中提交并向上游 `Hhz0823/ZCode-Antigravity` 提交 PR（Commit `da11b41`）。
- **技术选型迭代**：彻底退役 ZCode-Antigravity 本地桥，转为使用官方 **EasyCLIProxyAPI**（核心版本 `7.2.149`，位于 `D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64`）。
  - 上游原生支持 `gemini-3.8-flash-high`，官方发布包自带合法内嵌 OAuth client ID/secret，彻底杜绝本地构建缺失凭据的问题。
  - 本地模型网关监听 `127.0.0.1:18080`，保留 `oauth-model-alias`，Hermes 对接配置零修改。
  - 实测验证通过：`gemini-3.8-flash` (200 / 2.3s) 与 `gemini-3.7-flash` (200 / 1.4s)。
- **清理与计划任务**：
  - 清理了临时网关守护任务，保留 `Hermes_Gateway`（Hermes CLI 登录自启动服务）。
  - 用户需要使用 Hermes 时，打开 EasyCLIProxyAPI GUI 启动核心即可。

---

## 二、 浏览器脚本与扩展消失事故复盘（深度定性）

### 1. 触发链与根因
- **错误操作**：在尝试读取外部网页时，Hermes 曾尝试调用 `browser_exec`（底层走 `tools/browser_tool.py`）。
- **底层冲突**：
  - `config.yaml` 开启了 `browser.use_real_profile: true`，且 Windows 缺少预启动的真实 Edge 调试实例。
  - `browser_tool.py` 内部使用自动化参数启动 Chromium：`--user-data-dir`、`--disable-background-networking`、`--disable-sync` 等。
  - 当该临时浏览器实例退出时，Chromium 将内存中无扩展加载的状态写回了磁盘上的 `Preferences`，导致 `extensions.settings` 注册表字段再次被清零，用户日常 Edge 中的扩展与脚本表面上全部消失。

### 2. 物理数据状态核查（100% 完好）
- **注册表被清、物理数据安然无恙**：
  - 脚本猫（ScriptCat, `liilgpjgabokdklappibcjfablkpcekh`）：`Local Extension Settings` 中 18.6 MB 数据与脚本完整无损。
  - 简约翻译（KISS Translator, `jemckldkclkinpjighnoilpbldbdmmlh`）：3.18 MB 设置完整。
  - 小电视空降助手（`khkeolgobhdoloioehjgfpobjnmagfha`）：2.03 MB 数据完整。
  - 本地解压版扩展：`D:\extensions\LimeStartPage\src`、`better-XiaoHeiHe-main` 源码完好。
- **恢复法则**：
  - 商店扩展：重新在 Edge 商店点击获取，因扩展 ID 恒定，数据立即自动接回。
  - 解压版扩展：打开 `edge://extensions` 开发者模式，重新加载原路径文件夹。

### 3. 永久防再犯军规
1. **彻底关闭 `browser.use_real_profile`**：设为 `false`，严禁任何自动化工具触碰或快照真实用户 Edge 数据目录。
2. **抓取网页工具铁律**：严禁调用任何会启动独立 Chromium 窗口的 `browser_exec`，一律使用 `smart-web-crawler`（静态直连）或通过 `chrome-devtools` MCP 挂载到用户已有的 `DevToolsActivePort` 会话。

---

## 三、 ZCode 接入 Gemini 模型与 EasyCLIProxyAPI 客户端检测适配（2026-09-04）

### 1. EasyCLIProxyAPI "未检测到客户端 / 无法启动" 根因与修复
- **现象**：在 EasyCLIProxyAPI 桌面控制台「智能体配置」中选中 ZCode 时，提示黄色警告「只检测到配置文件，未检测到客户端」，右下角按钮显示「无法启动」。
- **根因**：EasyCLIProxyAPI 在 Windows 上按固定规范路径探查客户端安装位置（`%LOCALAPPDATA%\Programs\ZCode\ZCode.exe` 与 `%ProgramFiles%\ZCode\ZCode.exe`），而用户的 ZCode 实际安装在 `D:\zcode\ZCode.exe`。
- **解决**：建立目录联接（Junction）：
  - `mklink /J "C:\Users\VOS-User\AppData\Local\Programs\ZCode" "D:\zcode"`
  - `mklink /J "C:\Program Files\ZCode" "D:\zcode"`
  使 EasyCLIProxyAPI 原生探查器能够直接定位并拉起 ZCode。

### 2. ZCode Gemini 3.8 / 3.7 / 3.6 / 3.1 矩阵接入
- **网关就绪**：本地 EasyCLIProxyAPI 核心（监听 `127.0.0.1:18080`）原生支持 Anthropic Messages 协议（`/v1/messages`），实测 `gemini-3.8-flash`（带 thinking 思考链）、`gemini-3.7-flash`、`gemini-3.1-pro-low` 均稳定返回 200 OK。
- **配置持久化**：
  - 更新全局配置 `C:\Users\VOS-User\.zcode\v2\config.json` 与工作区配置 `D:\ai coding\.zcode\v2\config.json`。
  - 在 `zcode-antigravity-local`（Google 提供商）中注入：
    - `gemini-3.8-flash`（优先级 200，支持思维链）
    - `gemini-3.7-flash`（优先级 201）
    - `gemini-3.6-flash`（优先级 202）
    - `gemini-3.1-pro-low`（优先级 203）
    - `gemini-web-search`（优先级 204）
  - 在 `model-provider-display-order.json` 中将 `zcode-antigravity-local` 置顶，确保在 ZCode 的模型下拉列表中直接展示并可供选择。
