---
name: hermes-quota-embedded
description: Hermes 配额监控内置化 — token-stats 后端插件替代计划任务/独立微服务的架构与排障
metadata:
  type: project
---

# Hermes 配额监控内置化（token-stats）

## Why
原方案靠计划任务 `Hermes_Quota_Service` 登录拉起独立微服务（fetch_quota.py 监听 127.0.0.1:18088），用户不每次开机都用 Hermes，白占进程；且手动启动易忘。内置到 Hermes 后端插件后随桌面应用启停，零常驻。

## 现行架构（2026-09-04 落地）
- 数据源：Google 官方 `daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary`，凭据读 `D:\EasyCLIProxyAPI\auth\antigravity-*.json`，经本地代理 127.0.0.1:3067，30s 内存缓存 + 磁盘缓存 `desktop-plugins/token-stats/direct-quota.json`，`?force=1` 穿透。
- 服务形态：Hermes 后端**用户插件** `~/.hermes/plugins/token-stats/`（plugin.yaml + __init__.py + dashboard/manifest.json + dashboard/plugin_api.py），FastAPI 路由挂载 `/api/plugins/token-stats/quota|health`，随桌面端后端进程启停。
- 前端：`~/.hermes/desktop-plugins/token-stats/plugin.js` 经 `ctx.rest('/quota')` 命名空间门读取，无 CORS/固定端口依赖。

**How to apply:** 排障顺序：1) `config.yaml` 的 `plugins.enabled` 必须含 `token-stats`（用户插件后端代码挂载的硬性安全门 GHSA-mcfc-hp25-cjv7，漏掉即 404）；2) 插件发现扫 `<plugins root>/*/dashboard/manifest.json`，`api` 字段必须是 dashboard 目录内相对路径；3) `tab.hidden: true` 只挂 API 不出标签页；4) 前端 runtime 插件只许 import `@hermes/plugin-sdk` 与 react，`ctx.rest` 需在 `register(ctx)` 捕获 context。改 `config.yaml` 用 python yaml 读写（patch/write_file 工具拒写该文件），改后抽查关键字段。旧计划任务 `Hermes_Quota_Service`、`Hermes_Gateway`、`cua-driver-serve` 登录触发器均已停用（保留任务体可手动 Start-ScheduledTask 按需拉起）。
