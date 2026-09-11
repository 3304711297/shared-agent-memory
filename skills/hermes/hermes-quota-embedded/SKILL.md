---
name: hermes-quota-embedded
description: Hermes 配额监控内置化架构与排障路径（token-stats 后端插件替代计划任务）
---

# Hermes 配额监控内置化（token-stats）

## 架构
- 数据源：Google 官方 `daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary`，凭据读 `D:\EasyCLIProxyAPI\auth\antigravity-*.json`，经本地代理 127.0.0.1:3067。
- 服务形态：Hermes 后端**用户插件** `~/.hermes/plugins/token-stats/`，FastAPI 路由挂载在 `/api/plugins/token-stats/`（quota / health），随桌面端后端进程启停，无独立进程；并在 `__init__.py` 注册 `/quota` 会话内斜杠指令（支持 `/quota` 或 `/quota refresh`）。
- 前端：`~/.hermes/desktop-plugins/token-stats/plugin.js` 经 `ctx.rest('/quota')` 命名空间门读取，无 CORS/固定端口依赖。支持状态栏 Chip（含 Popover）、左侧导航栏 Pulse 入口（`SIDEBAR_NAV_AREA`）、独立全景看板（`ROUTES_AREA: /quota`）与命令面板（`PALETTE_AREA`）；基于 `ctx.storage` 实现时间格式（相对/绝对）与左侧导航栏配额入口开关持久化（默认隐藏侧栏入口，避免误认为 Hermes 原生自带，用户可在状态栏 Popover 底部或看板一键启闭并热生效）。
- 多账号与待机账号重置监控（2026-09-07 升级）：多账号凭据池在 Popover 列表和 /quota 看板卡片均直接内联展示各个账号（包括非活跃/待机轮询账号）独立的 5h 滚动与周配额重置倒计时（支持 compact 紧凑与相对/绝对格式），并支持点击任意账号卡片将核心指标大卡（进度条、绝对时刻）切换为该账号的待机聚焦预览。
- 数据聚合：直连 Google Antigravity 官方配额，并集成 WorkBuddy (workbuddy2api 8787 端口) 本地网关无感探测。

## 降级模式（2026-09-07 修复）
- 根因链：EasyCLIProxyAPI 网关(18080)未运行 → auth/*.json 的 access_token 无人续期（1h 有效期，字段 `expired`）→ retrieveUserQuotaSummary 401 → 旧代码整体退回磁盘缓存，WorkBuddy 积分被冻结在旧快照且 force=1 也刷不动。
- 现行为：Google 拉取全败时返回 `status=degraded`（非 error），Google 数字=磁盘缓存快照并附 `degradedReason`；WorkBuddy 8787 积分独立实时探测，与 Google 成败解耦；降级时清内存缓存，恢复后自动回到全实时。
- 前端 plugin.js 接受 ok|degraded 两态，Chip 呼吸灯/看板徽章转琥珀色并出横幅。
- 改 plugin_api.py / plugin.js 后必须重启桌面端进程才生效（模块级加载，无热重载）。

## WorkBuddy 上游频率限制监控（2026-09-08 新增）
- 腾讯 CodeBuddy 上游免费模型限流报文：HTTP 429 + `{"code":6004,"msg":"您的使用量已超出频率限制，将在 <YYYY-MM-DD HH:MM:SS> UTC+8 重置…"}`；报文自带精确重置时刻，冷却窗口不定长（实测触发点浮动：hy4-preview 5h 滚动 46~212 次请求 / 9.3M~20.3M tokens 均出现过，与未触发区间重叠，**腾讯未公开固定阈值**，严禁前端推算剩余百分比）。
- 数据链路两级：① 新版 converter.py（commit 03d600b）在流式/非流式两条上游错误路径记录 6004，自曝 `GET /api/rate_limit`（含 resetAt/resetLocal/remainingSec + usage.jsonl 滚动用量 + 账号昵称，只读零配额消耗）；② 旧版反代无该端点时，插件后端回退扫 Hermes 自身 `logs/errors.log(.1)` 尾部 4MB 的 6004 报文（纯被动）。`_workbuddy_rate_limit()` 优先①回退②，20s 内存缓存，挂在 `/quota` 的 workbuddy.rateLimit 与独立 `/api/plugins/token-stats/rate_limit`。
- 前端：Chip Popover WorkBuddy 卡内 `RateLimitRow` 紧凑行（limited=红点呼吸+冷却倒计时 `⏳3h12m @22:11:33`，正常=绿点+5h请求数）；/quota 看板独立卡片（原始报文、5h 请求/tokens/429 次数/最近一次 429 四宫格、数据源标注）。倒计时按绝对值 resetAt 每渲染重算，不依赖后端快照 remainingSec。
- 当前聊天模型与被限模型可能不同（用户切模型避限）：当前模型无 6004 记录时报「最近被限的模型」，字段 `model` 如实标注。
- 观测数据源：`%LOCALAPPDATA%\workbuddy2api\usage\usage.jsonl`（ts/model/ok/input_tokens/output_tokens/error），SQLite 不涉及。旧目录 `codebuddy2openai` 已弃用（插件后端仍保留回退读取）。

## 关键机制（排障必读）
- 用户插件后端代码被挂载的**硬性安全门**：插件名必须在 `config.yaml` 的 `plugins.enabled` 列表（GHSA-mcfc-hp25-cjv7）。漏掉 → 404。
- 插件发现：扫 `<plugins root>/*/dashboard/manifest.json`，`api` 字段必须是 dashboard 目录内相对路径；`tab.hidden: true` 可只挂 API 不出标签页。
- 前端 runtime 插件只许 import `@hermes/plugin-sdk` 和 react（lint 栅栏）；`ctx.rest` 需在 `register(ctx)` 时捕获 context。
- 改 `config.yaml` 用 python yaml 读写（patch/write_file 工具拒写该文件）；改后必须抽查关键字段完整性。
- 30s 内存缓存 + 磁盘缓存 `desktop-plugins/token-stats/direct-quota.json`；`?force=1` 穿透。

## 旧方案残留
- 计划任务 `Hermes_Quota_Service`（18088 端口 fetch_quota.py）已退役：登录触发器 Enabled=False，任务保留可手动运行作后备。
- 同批停用登录自启：`Hermes_Gateway`、`cua-driver-serve`（均为手动按需）。
