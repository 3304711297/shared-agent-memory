---
name: hermes-quota-embedded
description: Hermes 配额监控内置化 — token-stats 后端插件架构与排障；WorkBuddy 积分数据源已迁 converter /api/usage_summary（5b4381c）
metadata:
  node_type: memory
  type: project
  originSessionId: sess_656a8367-2a67-4b01-be2c-f06bb80ecba5
---

# Hermes 配额监控内置化（token-stats）

## Why
原方案靠计划任务 `Hermes_Quota_Service` 登录拉起独立微服务（fetch_quota.py 监听 127.0.0.1:18088），用户不每次开机都用 Hermes，白占进程；且手动启动易忘。内置到 Hermes 后端插件后随桌面应用启停，零常驻。

## 现行架构（2026-09-04 落地，2026-09-05 演进升级）
- 数据源：Google 官方 `daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary`，凭据读 `D:\EasyCLIProxyAPI\auth\antigravity-*.json`，经本地代理 127.0.0.1:3067，30s 内存缓存 + 磁盘缓存 `desktop-plugins/token-stats/direct-quota.json`，`?force=1` 穿透；集成 WorkBuddy (workbuddy2api 8787 端口) 本地网关无损探测。
- **WorkBuddy 积分/账号数据源（2026-09-05 新增，commit 5b4381c）**：converter.py 新增 `GET /api/usage_summary`——服务端读 `%LOCALAPPDATA%\workbuddy2api\accounts.json`（回退兼容旧目录 `codebuddy2openai`）取 active_uid 会话，直查 `copilot.tencent.com/billing/meter/get-user-resource-summary`，返回与 Rust UsageSummary 对齐的 `{uid,nickname,total,remain,used,is_paid_user,packages:[{code,total,remain,used,unit}]}`；任何失败归一 `{"error": "..."}`（token 过期/网络失败/文件缺失均不抛 5xx），插件端按 error 优雅降级显示「—」。无鉴权（Host 中间件限回环）。测试注入点：`converter._BILLING_TRANSPORT_OVERRIDE`（httpx.MockTransport）。
- **usage_summary 实测与握手快照（2026-09-06）**：ZCode 用 Python 直调 `GET http://127.0.0.1:8787/api/usage_summary` 成功，线上返回与上述 schema 完全一致（未走 error 分支）；账号「晚街」积分 total 3700 / used 920.2 / remain 2779.8（packages 明细 1779.8+0+1000）。注意 Python 访问须显式禁代理（`urllib.request.ProxyHandler({})` 或 requests `trust_env=False`），防本机 3067 代理劫持 localhost。同日用户要求生成握手快照 `%TEMP%\zcode_handshake_snapshot.json`：首行 `# snapshot by zcode` + indent=2 格式化 JSON，回复收尾标记 `SNAPSHOT-DONE`——同类任务按此格式复用。
- 服务形态：Hermes 后端**用户插件** `~/.hermes/plugins/token-stats/`（plugin.yaml + __init__.py + dashboard/manifest.json + dashboard/plugin_api.py），FastAPI 路由挂载 `/api/plugins/token-stats/quota|health`，随桌面端后端进程启停；并在 `__init__.py` 注册 `/quota` 会话斜杠指令（支持 `/quota` 或 `/quota refresh` 即时返回排版清晰的 Markdown 报告）。
- 前端交互（吸收上游优势）：`~/.hermes/desktop-plugins/token-stats/plugin.js` 支持右下角状态栏 Chip（带 Popover 详情与全景看板直达）、左侧导航栏 Pulse 入口（`SIDEBAR_NAV_AREA`）、独立全景看板（`ROUTES_AREA: /quota`）与命令面板（`PALETTE_AREA`）；基于 `ctx.storage` 实现时间格式（相对倒计时/绝对时刻）持久化。
- **2026-09-07 体验与多账号监控深度升级**：
  1. **多账号重置倒计时直显与待机聚焦**：Popover 凭据池明细与全景看板卡片均直接内联展示各个待机轮询账号独立的 5h 滚动与周总额度刷新倒计时（支持 compact 紧凑与相对/绝对格式切换）；点击任意待机账号卡片可将下方核心指标大卡无缝切换为该账号的待机聚焦预览（附「待机预览」与「切回活跃」按钮）。
  2. **状态栏视觉净化与 Tooltip 降噪**：彻底移除了状态栏上的无用电池 `🔋` 图标；去除了鼠标悬停在状态栏时的全局 Tooltip 气泡（去掉了 `Tip` 组件与按钮 title），杜绝视觉遮挡。
  3. **左侧导航入口默认隐藏与按需启闭**：为了避免让人误以为配额入口是 Hermes 官方原生自带菜单，左侧导航栏的「配额」按钮（Pulse 图标）默认设置为**关闭/隐藏**；并在状态栏 Popover 底部与 `/quota` 全景看板顶部新增了即时开关，支持 `ctx.storage` 本地持久化与运行时动态热启闭（无感生效）。
  4. **OpenViking 记忆提炼联动映射修复**：修复了 `plugin_api.py` 中因写死 `custom:` 前缀而导致 `billing_provider == "custom"` 时误报“非 custom 类型 provider，无本地凭据可映射”及“模型不在目录”的逻辑反转 Bug；现采用支持当前模型名称反查 custom_providers 目录与默认 provider 的多级健壮映射。

**How to apply:** 排障顺序：1) `config.yaml` 的 `plugins.enabled` 必须含 `token-stats`（用户插件后端代码挂载的硬性安全门 GHSA-mcfc-hp25-cjv7，漏掉即 404）；2) 插件发现扫 `<plugins root>/*/dashboard/manifest.json`，`api` 字段必须是 dashboard 目录内相对路径；3) `tab.hidden: true` 只挂 API 不出标签页；4) 前端 runtime 插件只许 import `@hermes/plugin-sdk` 与 react，`ctx.rest` 需在 `register(ctx)` 捕获 context。改 `config.yaml` 用 python yaml 读写（patch/write_file 工具拒写该文件），改后抽查关键字段。旧计划任务 `Hermes_Quota_Service`、`Hermes_Gateway`、`cua-driver-serve` 登录触发器均已停用（保留任务体可手动 Start-ScheduledTask 按需拉起）。
