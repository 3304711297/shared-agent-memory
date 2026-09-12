---
name: workbuddy2api-failover-gpt-fastmode-audit
description: 2026-09-12 WorkBuddy2API 429限流避让、GPT模型11102未授权降级、快速模式(service_tier)及风控对抗审计
metadata:
  node_type: memory
  type: project
---

# WorkBuddy2API 限流避让、GPT模型降级与快速模式支持 (2026-09-12)

## 一、故障现象与根因全景

### 1. DeepSeek v4.1 flash 触发限额未自动切换账号，切号后仍报错
- **上游真实机制**：腾讯云 Copilot 后端对 `deepseek-v4.1-flash` 等高频模型施加了按账号独立的 5 小时滑动窗口频控（非 IP 级）。
- **实测证据**：
  - 账号 1（晚街）与账号 2（173...）的重置时间戳分别为 `18:32:40` 与 `18:55:18 UTC+8`，且此时其他模型（`deepseek-v4-flash`, `deepseek-v4-pro`, `glm-5.3-flash`, `kimi-k3`）两账号均 100% 正常（HTTP 200）。说明当时两账号此前均已分别打满额度。
- **转换器代码缺陷**：
  - 原 `_record_rate_limit` 强依赖汉字正则提取重置时间；当上游返回未带标准时间戳的 429 报文时直接 `return`，**未将当前账号写入 `_ACCOUNT_COOLDOWNS`**，导致后续请求无法在 `select_account` 中避开该账号；
  - 当账号池全池冷却时，`select_account` 缺少全池告警，静默反复使用当前受限账号重试。

### 2. GPT 模型不可调用（Code 11102）
- **权限边界**：`gpt-6-astra`, `gpt-5.6-luna`, `gpt-5.6-sol`, `gpt-5.3-codex` 等海外前沿模型上游属于腾讯内部 iOA 认证用户专属，个人订阅直连报错 `code 11102: model is only available for authorized users`。
- **别名缺失**：`MODEL_MAP` 原先缺少 `gpt-4o`, `gpt-4o-mini`, `gpt-4`, `o1` 等标准 OpenAI 别名映射，导致直调报 `service info not found`。

### 3. 缺少快速模式（Fast Mode / Service Tier）
- Hermes（`/fast` 开关与 `agent.service_tier`）及 Codex 在 OpenAI 协议下发 `service_tier: "priority"`（或 `"auto"`），Anthropic 协议下发 `speed: "fast"`；
- `PASSTHROUGH_BODY_KEYS` 原先过滤抛弃了 `service_tier` 与 `speed`，且未与 WorkBuddy 原生极速模型 `fast-model` 打通。

---

## 二、落地改造要点

1. **限额识别与多账号冷却加固**：
   - `_record_rate_limit` 增加 `status_code` 识别；即使上游未下发标准时间戳，只要状态码为 429 或含限频关键词，自动以 5 分钟（300s）兜底冷却写入 `_ACCOUNT_COOLDOWNS`；
   - `select_account` 与 `record_failure_and_failover` 增强全池冷却识别与告警。
2. **GPT 别名映射与 11102 平滑降级**：
   - `MODEL_MAP` 补齐常见 OpenAI 客户端别名（`gpt-4o` -> `gpt-5.6-luna`，`gpt-4o-mini` -> `fast-model`，`gpt-4` -> `deepseek-v4-pro`）；
   - 新增 `GPT_FALLBACK_MAP`：在非流式与流式请求遇到 11102 时，自动平滑降级至主力模型（`deepseek-v4-pro` / `glm-5.3` / `fast-model`）并发起 1 次补偿重试，杜绝 400 阻断会话。
3. **快速模式全链路支持**：
   - `PASSTHROUGH_BODY_KEYS` 引入 `"service_tier"`, `"speed"`, `"fast_mode"` 透传；
   - 快速模式激活时，若使用 `auto`/`default` 模型，自动路由至官方极速模型 `fast-model`（GLM-5.3-Flash，0.34 积分倍率）；
   - `/v1/models` 暴露 `fast-model`。
4. **外部审查加固（安全与风控反制）**：
   - `update.rs`：移除硬编码的个人代理 `127.0.0.1:3067`，改走系统标准环境变量代理（`HTTP_PROXY`/`HTTPS_PROXY`）或纯直连；
   - 多账号防风控抖动：在 failover 切换时增加异步随机微休眠（Jitter 0.5~1.2s），降低同设备同 IP 毫秒级突发请求关联度。
5. **Hermes token-stats 插件联动**：
   - 修复未发生限流时误报「未知」的缺陷；
   - 全景透传多账号调度策略模式与可用账号数；
   - 增加跨模型限流透视（当前模型正常时亦可提前看到其他模型的冷却时刻）。
6. **UI 动态更新（updateModelCells）修复**：
   - 修复在控制台编辑保存模型配置后，`updateModelCells()` 仍遗留渲染 `默认 (${m.default_effort})` 导致界面退化为具体档位的问题，统一为 `默认 (跟随客户端)`；
   - 单测 `test_frontend_does_not_hardcode_default_effort_as_label` 加固覆盖模板字符串形式。

---

## 三、验证与测试基线

- `workbuddy2api` 仓库：
  - `npm run build` 前端产物同步构建打包；
  - `pytest tests/`：212 passed（全量覆盖）；
  - `npm test`：32 passed（node:test）；
  - `cargo test`：24 passed。
- `token-stats` 插件：
  - 前后端本地测试全绿，Markdown 渲染与 SPA 刷新即时生效。
