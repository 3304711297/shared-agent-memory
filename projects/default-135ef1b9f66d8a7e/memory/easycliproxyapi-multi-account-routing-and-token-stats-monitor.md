---
name: easycliproxyapi-multi-account-routing-and-token-stats-monitor
description: EasyCLIProxyAPI 多账号轮询调度机制、优先级桶实测闭环与 token-stats 插件多凭据池动态监控升级
metadata:
  type: project
---

# EasyCLIProxyAPI 多账号轮询调度与 token-stats 监控升级 (2026-09-06)

## 一、 EasyCLIProxyAPI 多账号调度与会话粘性机制

### 1. 优先级桶与轮询规则（实测排查结论）
- **现象复盘**：在 EasyCLIProxyAPI 控制台开启「轮询 (Round Robin)」后，系统仍持续将所有请求分发给 `jimygod114514@gmail.com`，而 Pro 账号 `2964251404@qq.com` 额度完全未动。
- **内核机制剖析**：
  - EasyCLIProxyAPI 内核（`selector.go`）在执行 `RoundRobinSelector` 时，**优先级（Priority）是第一维度的硬分组（Priority Bucket）**。
  - 调度器仅在**当前最高优先级的凭据池**内执行轮询。之前 `jimygod` 优先级为 `10`，`2964251404` 优先级为 `9`。由于 `10 > 9`，最高优先级池中仅有单个凭据，导致轮询退化为单号单打。
  - **解决方案**：在 `D:\EasyCLIProxyAPI\auth\antigravity-2964251404@qq.com.json` 中将 `priority` 同步调高至 `10`，使两账号平级并存入同一轮询池。

### 2. 轮询分流与会话粘性（Session-Affinity）联动
- **配置基准**：
  - `routing.strategy: round-robin`（轮询）
  - `routing.session-affinity: true`（开启会话粘性，TTL: 1h）
- **端到端实测验证**：
  - **新会话轮询**：发起独立新会话时，网关触发 `session-affinity: LCP cache miss, new binding`，分别交替绑定 `jimygod114514@gmail.com` 与 `2964251404@qq.com`。
  - **会话粘性命中**：同一会话后续多轮对话触发 `session-affinity: LCP cache hit`，请求牢牢锁定在初始选定的凭据上，最大化命中 Google Prompt/KV Cache，保障首字延迟与生成吞吐。

---

## 二、 token-stats 配额监控插件全面升级

### 1. 历史缺陷
- 原 `fetch_quota.py` 及 `plugin_api.py` 采用 `os.listdir` 按文件名升序盲取首个 `antigravity-*.json`，导致状态栏 Popover 弹窗永远只显示排在首位的 `2964251404@qq.com`（99.8% 假象），无法反映底层网关实际调用 `jimygod`（周额度已消耗至 2.4%）的真实状况。

### 2. 后端核心重构 (`plugins/token-stats/dashboard/plugin_api.py`)
- **动态活跃路由感知**：
  - 引入 `_find_usage_db()` 与 `_get_active_email()`，直读 EasyCLIProxyAPI 的 SQLite 数据库 `usage.db`（`SELECT source FROM usage_events WHERE source != '' ORDER BY id DESC LIMIT 1`），并辅以 `logs/main.log` 尾部匹配。
  - 秒级感知当前真正承接调用的活跃凭据，不再受文件名顺序干扰。
- **凭据池并发查询**：
  - 采用 `ThreadPoolExecutor` 并发遍历 `D:\EasyCLIProxyAPI\auth` 下所有有效凭据，直连 Google 官方 `retrieveUserQuotaSummary` 接口拉取额度与重置时间。
  - 聚合输出 `accounts` 列表与各账号的 `isActive` 状态。
- **交互式指令增强**：
  - `/quota`（及 `/quota refresh`）支持格式化输出多账号全量明细与 `● 当前活跃` 徽章。

### 3. 前端界面升级 (`desktop-plugins/token-stats/plugin.js`)
- **状态栏 Popover 弹窗与多账号交互**：
  - 新增「凭据池 (N 账号) 轮询负载中」明细卡，实时显示各账号 5h / 周额度百分比与独立重置倒计时（支持 compact 紧凑与相对/绝对切换），并用高亮绿色圆点标记当前活跃路由。
  - 交互式待机聚焦：点击任意待机账号卡片，下方核心指标区（5h 大进度条、周总额度、3P 协同池）即刻切换为该账号的待机聚焦预览（附「待机预览」与「切回活跃」按钮）。
  - 顶部订阅方案根据活跃账号动态渲染（Pro 订阅 / 标准方案），修正原硬编码标签。
- **状态栏去繁就简**：彻底去除无用电池 `🔋` 图标与鼠标悬停 Tooltip 气泡（去除了 `Tip` 组件），杜绝遮挡干扰。
- **全景看板 (`/quota`) 与侧栏入口控制**：
  - 同步渲染多账号卡片网格，展示各账号详细配额、重置时间与调度待机状态。
  - 侧栏入口防混淆（默认隐藏）：左侧导航栏的「配额」按钮（Pulse 图标）默认关闭/隐藏（避免误认为 Hermes 原生功能），并在状态栏 Popover 底部与看板顶部提供热生效开关（`ctx.storage` 本地记忆）。

---

## 三、 辅助模型配置铁律（用户明确拍板）

- **铁律**：严禁擅自修改 `auxiliary.*` 辅助模型配置，严格保持官方默认状态：
  - `auxiliary.vision.provider: auto`
  - `auxiliary.vision.model: ''`
  - 辅助模型默认随主聊天模型动态解析/自动跟随，未经用户提议与明确拍板，严禁人工改动。

---

## 四、 3067 链路断流与 CPA 冷却假死机制辨析与改进储备（2026-09-07 沉淀，暂不改动）

- **故障现象复盘**：偶发 `503 auth_unavailable: no auth available (providers=antigravity)` 且伴随 event-loop stall。
- **底层物理根因**：
  1. 真正首发的异常是底层 Windows Socket `wsasend / wsarecv` 被远端强制断开（`WSAECONNRESET 10054`）或 TLS 超时，发生在 `18080 → 3067 (Karing) → daily-cloudcode-pa.googleapis.com` 链路上。
  2. **网关冷却放大机制（关键真凶）**：CPA 核心配置 `transient-error-cooldown-seconds: 0`（官方默认值代表 60 秒冷却封锁）。当底层发生一次短暂断流时，CPA 误将网络瞬态抖动判定为凭据故障，将当前 Antigravity 凭据封锁 60 秒（blackout window）；当两个轮询账号均遭遇抖动，整个凭据池全被拉黑，后续请求全部被 CPA 直接阻断并返回 `503 auth_unavailable`，造成长达数分钟的“假死”。
- **后续可选改进方案（用户拍板：暂不改动，留作储备）**：
  1. *CPA 冷却解绑*：将 CPA `config.yaml` 的 `transient-error-cooldown-seconds` 设为 `-1`（禁用瞬态错误冷却）或 `disable-cooling: true`，网络恢复后请求秒级放行，杜绝假死。
  2. *代理协议优化*：CPA `proxy-url` 由 HTTP CONNECT 改为纯 4 层 TCP 隧道的 `socks5://127.0.0.1:3067`，规避 HTTP 状态机断流重置。
  3. *Hermes 容灾兜底*：在 `config.yaml` 配置 `fallback_providers` 接入本地直连的 WorkBuddy (GLM-5.3-flash)。

**Why:** 明确区分底层网络断流与网关冷却假死机理，为后续链路稳定性优化提供事实储备，严禁擅自改动。
**How to apply:** 保持现有配置现状不变；当用户明确需要治理代理断流假死时，按上述储备方案逐步推进。
