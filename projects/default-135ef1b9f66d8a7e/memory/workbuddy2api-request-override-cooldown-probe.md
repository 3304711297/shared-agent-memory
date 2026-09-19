---
name: workbuddy2api-request-override-cooldown-probe
description: 2026-09-19 WorkBuddy2API 吸收 9router 特性：请求级控制头、全冷却自愈熔断单飞探针与 Streaming 响应头时序闭环
metadata:
  node_type: memory
  type: project
---

# WorkBuddy2API 请求级旁路控制与全冷却自愈单飞探针 (2026-09-19)

**背景**：在对开源网关 decolua/9router 评估并裁定不整体采用后，提炼其高价值特性（Per-Request Header 控制、账号熔断与状态机）吸收进 WorkBuddy2API。通过 BrowserSkill 接管 Edge 与 ChatGPT 进行多轮深度思考对抗式代码审查，完成最终架构收敛与 CLOSED 验收。

## 一、核心特性实现全景

### 1. 请求级控制头（Per-Request Header Control）
- **请求头规范**：
  - `X-WorkBuddy-Account: <uid 或 alias>`（单次强制指定路由账号）；
  - `X-WorkBuddy-Strategy: direct | round_robin | expire_priority | failover`（单次临时覆盖调度策略）；
- **Fail-Open 与安全隔离铁律**：
  - 指定账号处于冷却、未启用或重名别名歧义时，Fail-Open 放弃账号覆盖，但**绝不清除同请求中合法的 Strategy 覆盖**（契约修正 A）；
  - 请求级账号覆盖**严禁调用 `switch_active_account()`**，零全局副作用，不干扰并发其他会话；
  - 非法策略取值安全回退全局配置。

### 2. 全冷却 Half-Open 单飞探针（Single-Flight Probe）与防惊群
- **有效账号池交集**：全池冷却时，必须从「当前有效可用账号池 ∩ 冷却字典」中选取剩余冷却时间最短的账号，绝不挑选已删除/禁用的残留账号（契约修正 C）。
- **单飞探针门禁（Single-Flight）**：
  - 维护 `_PROBE_INFLIGHT: set[tuple[str, str]]` 内存互斥集合；
  - 仅放行 1 个请求作为探针，且探针期间不修改全局 `active_uid`；
  - 并发涌入的其他请求若全池仍在冷却且探针在途，严格阻断并返回 503 `all_accounts_cooldown`，**100% 杜绝任何并发穿透打向冷却账号**。
- **并发状态反转保护（State Inversion Protection）**：
  - `_clear_account_cooldown(uid, model, req_start_ms)` 携带请求启动时间戳；若限流时间 `lastSeenMs > req_start_ms`，禁止迟到成功覆盖新限流。
- **Monotonic 内部单调时钟**：内部冷却优先由 `time.monotonic()` 驱动，免疫系统时钟回拨或 NTP 跳变；外部展示继续保留 `resetAtMs`。

### 3. Streaming 响应头时序闭环（`DeferredHeaderStreamingResponse`）
- **根因解决**：传统 `StreamingResponse` 启动时即发送 `http.response.start` 固化 Header，导致流式握手 429 发生 failover 切号后，响应头中的 `X-WorkBuddy-Active-Account` 仍为旧 UID。
- **设计**：实现 `DeferredHeaderStreamingResponse`，延迟挂起 `http.response.start` 直到流式生成器吐出首个 chunk。结合 `_stream_upstream` / `_safe_stream_upstream` 的 `on_account_switched` 回调，确保 HTTP 响应头准确反映最终生效账号。覆盖 Chat、Messages、Responses 全部流式协议端点。

---

## 二、测试验证与 CI 交付证据

- **自动化契约单测**：`tests/test_header_override_and_cooldown_probe.py`（16 条完整契约用例，含 20 协程真实 `asyncio.gather` 并发防穿透测试、时钟跳变测试、流式 failover 响应头测试与 `/api/rate_limit` 三态契约锁定）。
- **全量四门禁**：
  - Python pytest：**460 passed**
  - 禁网隔离运行器 `tests/run_isolated_tests.py`：**460 passed**（LF/CRLF 零网依赖）
  - 前端 Node 契约：**207 passed**
  - Rust 后端：**85 passed**
- **远端 GitHub Actions CI**：
  - 提交 SHA：`7e9ff2a` 与文档同步 `d7c539e`
  - CI Run ID：`35373501139`（Linux & Windows 双环境全部 completed success）。
- **ChatGPT 验收结论**：`✅ CLOSED`（经 4 轮严格对抗式代码级与 Actions 日志对拍审查后签发）。
