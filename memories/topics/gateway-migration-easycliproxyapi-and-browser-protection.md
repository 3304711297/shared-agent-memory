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

---

## 四、 Hermes 配额监控插件 (token-stats) 全面适配升级（2026-09-04）

- **旧架构缺陷**：
  - 原插件依赖已退役的 ZCode-Antigravity 私有补丁 `/v0/management/api-call` 和 `%LOCALAPPDATA%\ZCodeAntigravity\auth`。
  - 迁移至 EasyCLIProxyAPI 官方核心（7.2.149）后，官方核心无此私有接口，且使用 API Key 轮询管理接口触发了防爆破 IP 封禁。
- **全新直连架构升级**：
  - **凭据直读**：`fetch_quota.py` 重构为直接读取 EasyCLIProxyAPI 官方凭据（`D:\EasyCLIProxyAPI\auth\antigravity-*.json`），无需 DPAPI 解密，直接获取当前活跃 Google OAuth Access Token。
  - **直连 Google Quota API**：经本地代理 `127.0.0.1:3067` 毫秒级直连 Google 官方接口 `https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary`（注：必须带 `daily-` 前缀，这是 Antigravity 专有配额池，若使用通用 `cloudcode-pa` 会读取到非 Antigravity 的独立配额池导致数值不一致），精准获取：
    - Gemini 5 小时额度比例及精确重置时间戳（精确到秒与本地时间倒计时）；
    - Gemini 周额度比例及完全刷新时间；
    - 3P (Claude / GPT) 5h 及周额度状态。
  - **本地高性能微服务**：`fetch_quota.py` 自带轻量 HTTP 服务（监听 `127.0.0.1:18088/quota`），带 30s 内存防抖缓存，跨域无阻（CORS *）。
  - **前端插件对齐**：`desktop-plugins/token-stats/plugin.js` 统一请求 `http://127.0.0.1:18088/quota`，彻底与 EasyCLIProxyAPI 管理接口解耦。
  - **系统级自启动守护**：注册 Windows 计划任务 `Hermes_Quota_Service`，随用户登录无窗口静默后台自启。

---

## 五、 Hermes 提供商去重与看板视觉规范重构（2026-09-04）

### 1. 本地提供商去重清理
- **根因**：历史遗留的 `Local (127.0.0.1:18080)`（旧 ZCode 桥残留）与本次新建的 `cpa-gui` 打向同一网关，导致模型下拉列表中同一批模型出现两遍。
- **治理落地**：
  - `config.yaml` 移除 `Local (127.0.0.1:18080)`，规范化保留唯一 `cpa-gui`；
  - `auth.json` 清理 `custom:local-(127.0.0.1:18080)` 废弃凭据；
  - `MEMORY.md` 明确全系统统一使用 `cpa-gui` 标识。

### 2. 配额微件与看板 UI 现代化重构
- **消除梯田状破损背景**：识别并解决了 Hermes 原生 `<Tip>` 组件强制内联 `box-decoration-clone inline max-w-64` 导致的换行阶梯破损与词语生硬腰斩缺陷。
- **双层交互分流**：
  - **悬浮态 (Hover)**：单行克制提示，绝不换行；
  - **点击态 (Click Popover)**：展开现代深色毛玻璃仪表盘（带 Gemini 5h 与周配额动态进度条、3P 协同池状态、精确到秒与本地时刻的重置倒计时）。
- **微交互与穿透刷新**：
  - 支持 `?force=1` 穿透 30s 缓存直连 Google 官方；
  - 刷新按钮配备 SVG 顺时针旋转动效、`✓ 已刷新` 变形胶囊徽章、桌面气泡 Toast 通知及秒级同步时间戳。
- **状态栏语义化分层**：
  - 标签与语法冒号（`5h:`、`周:`）弱化为次级灰色；
  - 核心百分比数值采用等宽加粗高亮与健康度动态着色（绿色/黄色/红色），大幅提升快速扫视效率。

---

## 六、 Hermes 与 ZCode 接入 Gemini 3.8/3.7 实战配置与 7 大避坑速查

### 1. Hermes Agent 接入配置 (`~/.hermes/config.yaml`)
- **协议**：OpenAI 兼容协议 (`api_mode: chat_completions`)；
- **核心项**：
  - `model.default: gemini-3.8-flash`
  - `model.provider: cpa-gui`
  - `model.base_url: http://127.0.0.1:18080/v1`
  - `auxiliary.vision.model: gemini-3.8-flash`（配合 `cpa-gui`）
  - `agent.reasoning_effort: ultra`
  - `browser.use_real_profile: false`（防日常 Edge 扩展清空）
  - `browser.allow_private_urls: true`（支持本地与内网网页调试）

### 2. ZCode 客户端接入配置 (`~/.zcode/v2/config.json`)
- **协议**：Anthropic Messages 协议 (`kind: "anthropic"`)；
- **核心项**：
  - `provider["zcode-antigravity-local"]`: `name: "Google"`, `baseURL: "http://127.0.0.1:18080"`, `apiKey: "wY5Xr4HVPT3BZivioFX2L_3XhXdFfU8QBjT_Ff4xGJ0"`；
  - 模型字典：`gemini-3.8-flash` (优先级 200), `gemini-3.7-flash` (201), `gemini-3.1-pro-low` (203), `gemini-web-search` (204)；
  - **ZCode CLI 思考强度排查与对齐（2026-09-04）**：
    - 现象：ZCode 调用 `gemini-3.8-flash` 在 EasyCLIProxyAPI 后台显示思考强度为 `auto`，完成 Token 仅 70 余个，前端完全没有展开思考。
    - 根因：Google Gemini Flash 模型的思考逻辑为「动态自适应（Dynamic Thinking）」，当请求参数为 `auto` 时，模型根据简单 Prompt 判定无需深度思维链，返回思考 Token 为 0；此前 `v2/config.json` 配置了 `reasoning.defaultVariant: high`，但 `cli/config.json` 遗漏了 `reasoning` 节点，导致 CLI 端发起请求时默认传 `auto`。
    - 修复：在 `cli/config.json` 为 `gemini-3.8-flash`、`3.7-flash`、`3.6-flash` 补齐 `reasoning: { defaultVariant: "high", enabled: true, variants: ["low", "medium", "high"] }`，锁定 `high` 深度思考。
  - 置顶：在 `~/.zcode/v2/model-provider-display-order.json` 中将 `"zcode-antigravity-local"` 排在首位。

### 3. 全流程避坑速查（7 大血泪教训）
1. **裸构建丢凭据**：严禁本地裸 `go build` 覆盖官方二进制，发布期 ldflags 丢失会导致 500 后变 503 `auth_unavailable`；
2. **客户端探查失败**：EasyCLIProxyAPI 固定探查系统盘路径，D 盘安装需建立 NTFS 目录联接（`mklink /J`）；
3. **模型列表重复**：清理旧网关 `Local (127.0.0.1:18080)`，统一保留单实例 `cpa-gui`；
4. **扩展注册表被清**：Hermes 开启 `browser.use_real_profile: true` 会在退出时写回无扩展配置，必须设为 `false`；
5. **配额查询端点隔离**：Antigravity 专有配额必须请求 `daily-cloudcode-pa.googleapis.com`，而非通用 `cloudcode-pa`；
6. **管理端口 IP 封禁**：严禁拿普通 API Key 轮询 `/v0/management/`，触发防爆破后本地 IP 会被封禁 30 分钟；
7. **刷新交互假死感**：后端增加 `?force=1` 穿透防抖缓存，前端配备矢量旋转 Spinner、`✓ 已刷新` 胶囊变形与 Toast 弹窗反馈。



