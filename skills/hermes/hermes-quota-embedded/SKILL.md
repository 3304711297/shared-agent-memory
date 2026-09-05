---
name: hermes-quota-embedded
description: Hermes 配额监控内置化架构与排障路径（token-stats 后端插件替代计划任务）
---

# Hermes 配额监控内置化（token-stats）

## 架构
- 数据源：Google 官方 `daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary`，凭据读 `D:\EasyCLIProxyAPI\auth\antigravity-*.json`，经本地代理 127.0.0.1:3067。
- 服务形态：Hermes 后端**用户插件** `~/.hermes/plugins/token-stats/`，FastAPI 路由挂载在 `/api/plugins/token-stats/`（quota / health），随桌面端后端进程启停，无独立进程；并在 `__init__.py` 注册 `/quota` 会话内斜杠指令（支持 `/quota` 或 `/quota refresh`）。
- 前端：`~/.hermes/desktop-plugins/token-stats/plugin.js` 经 `ctx.rest('/quota')` 命名空间门读取，无 CORS/固定端口依赖。支持状态栏 Chip（含 Popover）、左侧导航栏 Pulse 入口（`SIDEBAR_NAV_AREA`）、独立全景看板（`ROUTES_AREA: /quota`）与命令面板（`PALETTE_AREA`）；基于 `ctx.storage` 实现时间格式（相对/绝对）本地持久化。
- 数据聚合：直连 Google Antigravity 官方配额，并集成 WorkBuddy (codebuddy2openai 8787 端口) 本地网关无感探测。

## 关键机制（排障必读）
- 用户插件后端代码被挂载的**硬性安全门**：插件名必须在 `config.yaml` 的 `plugins.enabled` 列表（GHSA-mcfc-hp25-cjv7）。漏掉 → 404。
- 插件发现：扫 `<plugins root>/*/dashboard/manifest.json`，`api` 字段必须是 dashboard 目录内相对路径；`tab.hidden: true` 可只挂 API 不出标签页。
- 前端 runtime 插件只许 import `@hermes/plugin-sdk` 和 react（lint 栅栏）；`ctx.rest` 需在 `register(ctx)` 时捕获 context。
- 改 `config.yaml` 用 python yaml 读写（patch/write_file 工具拒写该文件）；改后必须抽查关键字段完整性。
- 30s 内存缓存 + 磁盘缓存 `desktop-plugins/token-stats/direct-quota.json`；`?force=1` 穿透。

## 旧方案残留
- 计划任务 `Hermes_Quota_Service`（18088 端口 fetch_quota.py）已退役：登录触发器 Enabled=False，任务保留可手动运行作后备。
- 同批停用登录自启：`Hermes_Gateway`、`cua-driver-serve`（均为手动按需）。
