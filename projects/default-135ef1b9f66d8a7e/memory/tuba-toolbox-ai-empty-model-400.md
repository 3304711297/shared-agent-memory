---
name: tuba-toolbox-ai-empty-model-400
description: 图吧工具箱 AI 服务（TubaWinUi3）指向本地反代报 400 /「连接失败」= 自定义提供商的模型列表为空，测试连接拿空模型名发出请求
metadata:
  node_type: memory
  type: feedback
---

2026-09-18，用户报告「图吧工具箱的 AI 服务配置 400 报错」。

**根因**：客户端侧**自定义提供商的模型列表为空**（`models: []`、`defaultModel: ""`），其「测试连接」按钮直接向 `<baseUrl>/chat/completions` 发 `model: ""` 的探测请求；反代把空模型名原样透传上游，上游返回 HTTP 400 `11102 model [] service info not found`（= 找不到名为空串的模型），客户端因此显示「连接失败」。地址、密钥、网络全部无关。

**证据链（复现手法，下次照做）**：
- 客户端配置在 `%LOCALAPPDATA%\TubaWinUi3\ai_providers.json`（providers 数组：baseUrl / apiKey / models / defaultModel 全在里面），同目录另有 `settings.json`。
- 反代侧看 `%LOCALAPPDATA%\workbuddy2api\converter.log`：`▶ REQUEST  | stream=False | msgs=2` → `✗ HTTP 400 |  | model [] service info not found`。**同一 rid 下出现多个不同上游 requestId = 反代内部账号重试**，不是用户点了多次。
- 直接复现：`model:""` → 400 同报文；`model:"auto"` / `"deepseek-v4.1-flash"` → 200。反代 `/v1/models` 正常 200。

**通用规则**：
- 客户端「连接失败」≠ 网络/密钥问题，先确认**探测请求实际发出的 body**（模型名是否为空）——空模型名必被上游判为不存在。
- baseUrl 填对只是第一步：**必须从反代 `/v1/models` 抄真实模型 id 填进客户端的模型列表并设为默认模型**，测试连接才会过。
- 上游只认自家模型名：教程常见的 `deepseek-chat` / `claude-sonnet-4-5` / `gpt-3.5-turbo` 实测一律 400 `11102`；`gpt-4o` 能通是内置降级映射的个例，不可当范例。

**处置（两层）**：

① **客户端侧**（即时可用，不必等反代更新）：添加模型（如 `auto` 或 `deepseek-v4.1-flash`）并设为默认，重测即通。

② **反代侧已修（2026-09-18，commit 688e362，CI run 35351335054 绿）**——这轮回溯发现反代自身有四处健壮性缺陷，全部修掉并端到端验证：

| # | 缺陷 | 旧行为 | 新行为 |
|---|---|---|---|
| P0 | 空模型名透传 | `body.setdefault("model","auto")` 只补缺键，`""`/`null`/空白照发上游 → 400 11102 | 新增 `_normalize_model_name()`，一律归 `auto`；实测旧进程 `""`→400，修复版 `""`→**200** |
| P1 | 非流式 4xx 被重发 | `except HTTPException` 在 `attempt < max_attempts-1` 时吞异常续圈，实测一次请求打上游 **3 次**（同 rid 三个不同 requestId） | 只有 failover 真正切号成功才 continue，否则直接返回 |
| P1 | 错误体形状错误 | `raise HTTPException(detail=…)` → FastAPI 包成 `{"detail":…}`，破坏 OpenAI/Anthropic 协议形状 | 新增 `_openai_error_body` / `_anthropic_error_body`，出 `{"error":{…}}` 与 `{"type":"error","error":{…}}`；中文 displayMsg 优先，原 msg 留在 `upstream_message` |
| P2 | 限流误判 | `"429" in text` / `"6004" in text` 裸子串会命中 requestId 的 hex 片段（实测 `…4290-6004-abcd…`）→ 误切号 + 假冷却 | 抽出 `_is_rate_limit_signal()`：JSON 有 code 只认 `code==6004`；无 code 只看 `msg`/`message`；仅非 JSON 文本回退整串扫。`_record_rate_limit` 与 `record_failure_and_failover` 共用同一判据 |
| P3 | Anthropic 错误 type 不分状态 | 非 400 一律 `api_error`，与官方协议不符，且与流式路径（429→`rate_limit_error`）自相矛盾 | 新增 `_anthropic_error_type()` 按官方映射（400/401/402/403/404/409/413/429/500/504/529） |
| P4 | 语义门被正则绕过 | `_record_rate_limit` 让 `_RATE_LIMIT_RE` 先行，顶层 `code=11102` 但嵌套 `details.code=6004`+重置时间结构 → 绕过语义门写假冷却 | 判定顺序反转：先过 `_is_rate_limit_signal` 门，正则只负责提取 reset 时间 |

**跨 Agent 交叉复核（本轮采用 ChatGPT 网页端协作，见 `cross-agent-collaboration` 技能的 chatgpt SOP）**：
Hermes 先交 688e362 → ChatGPT 审出 P3/P4 两条并给出最小修法 → Hermes 独立复现、TDD 修（9b18744）→
ChatGPT 再审出 P4 的变体（`_RATE_LIMIT_RE` 绕过语义门）→ 修（70456f3）→ ChatGPT 核 CI 后判 **CLOSED ✅**。
**关键经验**：外部 Agent 的指控必须**先在本地复现再修**——本轮 3 条指控全部成立，但也因此发现了它没提到的一条真实缺口
（`{"msg":"请求频率过高，请稍后再试"}` 在无 429 状态码时判不出限流）。累计变异验证 4/4 全被抓到。

同轮 UI：模型页模型 id 改为一键复制调用名（原先只能看不能取，手抄易错致 11102）；删除冗余副标题。

**通用规则**：
- 客户端「连接失败」≠ 网络/密钥问题，先确认**探测请求实际发出的 body**（模型名是否为空）。
- baseUrl 填对只是第一步：模型列表仍要从反代 `/v1/models` 抄真实 id（或直点模型页 id 复制）。
- 上游只认自家模型名：教程常见的 `deepseek-chat` / `claude-sonnet-4-5` / `gpt-3.5-turbo` 实测一律 400 `11102`；`gpt-4o` 能通是内置降级映射的个例，不可当范例。
