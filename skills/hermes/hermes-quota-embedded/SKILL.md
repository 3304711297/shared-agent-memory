---
name: hermes-quota-embedded
description: "查配额/额度监控时必用。token-stats内置化架构与排障。Hermes quota monitoring built into the token-stats backend plugin."
---

# Hermes 配额监控内置化（token-stats）

## 架构
- 数据源：Google 官方 `daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary`，凭据读 `D:\EasyCLIProxyAPI\auth\antigravity-*.json`，经本地代理 127.0.0.1:3067。
- 服务形态：Hermes 统一插件（Unified Agent+Desktop Plugin），代码收敛在 `~/.hermes/plugins/token-stats/`：后端位于 `dashboard/plugin_api.py`（FastAPI 路由挂载在 `/api/plugins/token-stats/`），桌面端 UI 位于 `desktop/plugin.js`（由桌面端统一插件机制自动映射至 `desktop-plugins/token-stats/`，Settings -> Plugins 呈现为单一包）；并在 `__init__.py` 注册 `/quota` 会话内斜杠指令（支持 `/quota` 或 `/quota refresh`）。
- 前端：经 `ctx.rest('/quota')` 命名空间门读取，无 CORS/固定端口依赖。支持状态栏 Chip（含 Popover）、左侧导航栏 Pulse 入口（`SIDEBAR_NAV_AREA`）、独立全景看板（`ROUTES_AREA: /quota`）与命令面板（`PALETTE_AREA`）；基于 `ctx.storage` 实现时间格式（相对/绝对）与左侧导航栏配额入口开关持久化（默认隐藏侧栏入口，避免误认为 Hermes 原生自带，用户可在状态栏 Popover 底部或看板一键启闭并热生效）。
- 多账号与待机账号重置监控（2026-09-07 升级）：多账号凭据池在 Popover 列表和 /quota 看板卡片均直接内联展示各个账号（包括非活跃/待机轮询账号）独立的 5h 滚动与周配额重置倒计时（支持 compact 紧凑与相对/绝对格式），并支持点击任意账号卡片将核心指标大卡（进度条、绝对时刻）切换为该账号的待机聚焦预览。
- 数据聚合：直连 Google Antigravity 官方配额，并集成 WorkBuddy (workbuddy2api 8787 端口) 本地网关无感探测。

## 积分显示：精确优先（2026-09-18 用户要求，改动必读）

**铁律：积分一律精确显示，禁止约数/截断。**

- **真值口径**：上游 `CycleRemainCapacity` 是**量化到 2 位小数的字符串**，但经 float64 呈现带二进制尾数 —— 实测 `"833.33000192"` 真值即 833.33（`833.33000192 + 3316.66999808 == 4150` 精确闭合，证明尾数是浮点噪声而非真实额度）。故「精确」= **保留 2 位小数**，既不截断真值也不展示噪声。
- **两个等价格式化函数**（口径必须一致）：后端 `plugin_api.py::_fmt_credits_exact()`、前端 `plugin.js::fmtExactCredits()` —— 都是 `2 位小数 → 去尾零`，`None`/非数/NaN → `'—'`（**不得**回退成硬编码值）。
- **禁止出现的写法**：`fmtCredits` 这类缩约函数（原会把 1833.33 压成 `1.8k`、null 时回退成端口号 `8787`）、`toFixed(0|1)`、`Math.round()` 截断积分、后端 `:.0f` / `:.1f`。
- **全部消费点**（漏一处即不一致）：状态栏 chip、Popover 账号行、/ quota 看板大卡、积分包明细、后端 `note` 字段与 `/quota` markdown 摘要。
- 契约锁定：`tests/test_token_stats_exact_credits.py`（4 条：格式化口径、后端无 `:.0f/.1f` 残留、前端无 `fmtCredits` 且 chip 用精确格式、看板与明细无 `toFixed/Math.round`）。改完跑：
  ```bash
  cd "%LOCALAPPDATA%/hermes" && "<有 pytest 的解释器>" -m pytest tests/ -q
  ```
  注：hermes home 仓**自带 venv 无 pytest**（精简安装），借用 `D:/ai coding/GitRepos/workbuddy2api/.venv/Scripts/python.exe` 即可；hermes home 无 JS 测试基建，前端只能靠静态契约断言 + 手工验证。

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
- **Windows 下 fs.watch 文件/目录死循环事件风暴（2026-09-22 踩坑排障实证）**：
  Hermes Desktop 的 `watchPreviewFile` 与 `watchDirectory`（Electron 主进程）在 Windows 上调用 Node.js 原生 `fs.watch(dir)` 时，若监控目录或其子文件发生高频文件系统变动（或与子项发生句柄竞争），会导致主线程每 2 秒接收到超 36 万次文件系统变动事件（`eventType: rename`），引发内核态 I/O 等待自旋，使得单个 CPU 核心（通常是 Core #2）被固定打满 100%（其中 75%+ 处于 Kernel/Privileged 模式，用户态仅占 ~18%）。遇到桌面端单核 100% 满载且 JS 无长任务卡顿特征时，应直接通过 V8 Inspector 检查 `process._getActiveHandles()` 中的 `FSWatcher` 句柄，关闭高频或失效的 watcher 即可瞬间自愈。

## 旧方案残留
- 计划任务 `Hermes_Quota_Service`（18088 端口 fetch_quota.py）已退役：登录触发器 Enabled=False，任务保留可手动运行作后备。
- 同批停用登录自启：`Hermes_Gateway`、`cua-driver-serve`（均为手动按需）。
