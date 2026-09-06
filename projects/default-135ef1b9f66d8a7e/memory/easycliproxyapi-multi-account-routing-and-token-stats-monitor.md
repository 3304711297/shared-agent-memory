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
- **状态栏 Popover 弹窗**：
  - 新增「凭据池 (N 账号) 轮询负载中」明细卡，实时显示各账号 5h / 周额度百分比，并用高亮绿色圆点标记当前活跃路由。
  - 顶部订阅方案根据活跃账号动态渲染（Pro 订阅 / 标准方案），修正原硬编码标签。
- **全景看板 (`/quota`)**：
  - 同步渲染多账号卡片网格，展示各账号详细配额与调度待机状态。

---

## 三、 辅助模型配置铁律（用户明确拍板）

- **铁律**：严禁擅自修改 `auxiliary.*` 辅助模型配置，严格保持官方默认状态：
  - `auxiliary.vision.provider: auto`
  - `auxiliary.vision.model: ''`
  - 辅助模型默认随主聊天模型动态解析/自动跟随，未经用户提议与明确拍板，严禁人工改动。

**Why:**
避免多账号环境下因优先级配置与监控单文件硬编码导致的流量倾斜认知偏差与配额监控脱节，确保轮询调度与上下文缓存兼顾，并在桌面端直观呈现真实凭据负载全貌。

**How to apply:**
新增或调整 EasyCLIProxyAPI 多账号时，必须保证同池账号优先级数值一致方可轮询；桌面端查看额度时以 token-stats 凭据池明细卡中的「● 当前活跃」账号为实际消耗准绳；辅助模型严格保持 `auto` 缺省状态。
