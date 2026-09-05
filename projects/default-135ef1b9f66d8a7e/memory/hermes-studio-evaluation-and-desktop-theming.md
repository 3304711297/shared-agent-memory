---
name: hermes-studio-evaluation-and-desktop-theming
description: 第三方客户端 hermes-studio 深度评估结论与 Hermes 桌面端 ZCode 沉浸式暗黑 IDE 主题落地
metadata:
  type: project
---

# Hermes Studio 评估结论与 ZCode 桌面端主题落地

## 一、第三方客户端 hermes-studio 深度评估（2026-09-05）
用户反馈官方 Hermes 桌面端较朴素，希望评估 `EKKOLearnAI/hermes-studio`（Vue 3 + Naive UI）是否值得换用。

### 评估结论：强烈反对作为日常主力客户端替换官方端
1. **桌面插件体系（`@hermes/plugin-sdk`）彻底失效**：
   - Studio 是纯 Vue 3 Web 应用，未实现 Hermes 官方基于 React 的桌面插件运行时；
   - 现行落地的 `token-stats`（状态栏实时电池 Chip、Popover、左侧 Pulse 导航与 `/quota` 全景看板）换用后**直接全部报废**。
2. **会话数据库“裂脑”（Split-Brain Database）**：
   - Studio 采用自建 SQLite 会话库，官方 `state.db` 在 Studio 中仅为只读历史源，全局搜索（Ctrl+K）完全不索引官方会话；跨端会话无法双向无缝读写，数据发生永久割裂。
3. **双重代理架构与延迟/超时风险**：
   - 官方端直接经 Gateway 直连 EasyCLIProxyAPI（18080 端口）；
   - Studio 强行插入 Node.js Koa BFF + Socket.IO + Python Agent Bridge（占用 18765/18780 端口），在 Windows 下易出现端口冲突与 `HERMES_AGENT_BRIDGE_STARTUP_TIMEOUT` 启动超时，内存与系统开销成倍翻倍。
4. **商业限制与强制登录摩擦**：
   - 采用 BSL-1.1 商业源码协议（非 MIT），核心用于推销 Ekko Agent 生态与付费移动 App 鉴权，且带默认登录锁（`.login-lock.json`）与密码认证，增加单机个人使用负担。

## 二、官方桌面端原生美化方案：ZCode Dark 主题落地
针对用户对 ZCode 现代化 Agentic IDE 视觉风格的明确诉求，通过官方原生的 `THEMES_AREA` 和桌面样式覆盖插件完美 1:1 复刻，零功能损失、零会话割裂。

### 1. 插件落地位置
`%LOCALAPPDATA%\hermes\desktop-plugins\zcode-theme\plugin.js`

### 2. 核心设计语言与还原细节
- **三层哑光深炭底色（Matte Charcoal Palette）**：
  - 侧边栏：冷炭石墨色（`#131518`），搭配微弱内敛分割线；
  - 会话主区：哑光冷灰（`#181a1f`），柔和护眼、消解纯黑生硬感；
  - 卡片与输入框：微浮起暗灰（`#1f2228` / `#14161b`）。
- **极细微描边（Subtle Borders）**：
  - 全界面剔除粗硬边框，使用 `1px solid rgba(255, 255, 255, 0.08)`，轻盈深邃。
- **悬浮式底栏卡片（Floating Dock Input）**：
  - 输入框转为 `14px` 圆角、带 `0 10px 32px` 漫反射深色阴影的悬浮卡片；
  - 聚焦时带有 ZCode 标志性的**琥珀金微光晕（Amber Gold Ring: `rgba(229, 169, 60, 0.45)`）**。
- **去气泡化扁平工单流**：
  - 用户提问弱化为扁平克制的暗灰矩形（`#20242c`）；
  - 行内代码使用 `#f59e0b` 琥珀金点缀；滚动条收缩为 5px 微型暗色轨道。
- **双字体系统**：
  - 正文采用 `Inter` / `PingFang SC`；
  - 代码、路径与终端输出强制使用 `JetBrains Mono` / `Cascadia Code` 等宽字体。

### 3. 生效与切换
桌面端自动热重载，按 `Ctrl+K` 输入 `ZCode` 即可随时重新应用；与 `token-stats` 配额监控完美融合。
