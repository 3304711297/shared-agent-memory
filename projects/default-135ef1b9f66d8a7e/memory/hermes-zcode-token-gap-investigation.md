---
name: hermes-zcode-token-gap-investigation
description: Hermes 与 ZCode 同会话 token 差距 3.34x 的全量取证结论、测量方法论与 bg-review 思考开销调查（2026-09-06 闭环，官方 issue #104116）
metadata:
  type: project
---

# Hermes vs ZCode Token 差距调查（2026-09-06 闭环）

## 最终定量结论（EasyCLIProxyAPI 网关账本，UA 区分两端）

- **同模型 gemini-3.8-flash-high 严格配对**：Hermes 单次平均上下文 **422,973**（n=3462，UA=OpenAI/Python*）vs ZCode **126,555**（n=87，UA=ZCode/*）= **3.34x**；中位 328,714 vs 124,891 = 2.63x；P90 4.87x。
- **缓存命中率不是问题**：Hermes 95.9% vs ZCode 96.6%（网关 cached_tokens 与 cache_read_tokens 两字段 3970/3970 完全一致，任取其一即可）。
- **成因分解**：①对话历史增长速度（主因）②每轮固定底座 21.7k（system prompt 28,716 chars≈8.7k tok + tools 42,894 chars≈13k tok，chat_completions 协议每轮全量重发；tool_search 桥接占 12,189 chars，但它是 123 个延迟工具 38,544 tok 的替代，净省 31k，**绝不可关**）。
- **调用次数 42 倍是样本假象**：ZCode 全库 13,000+ 请求仅 87 条走 cpa-gui/18080 网关（主力走 builtin:bigmodel GLM 等通道）。跨端比较必须限定"两端都走网关的部分"，网关 usage.db 的 `user_agent` 字段可精确区分（ZCode/0.16.x|3.11.x vs OpenAI/Python、AsyncOpenAI/Python）。

## 方法论教训（排障时必读）

- **网关 usage.db（D:/EasyCLIProxyAPI-v0.2.71-Windows-amd64/usage-records/usage.db）是两端唯一中立账本**：表 usage_events 有 input/output/reasoning/cached_tokens/cache_read_tokens/total/endpoint/user_agent/model/reasoning_effort 等字段；`total = input+output+reasoning`（逐行验证），reasoning 是独立计费项。
- **客户端 DB 口径相反**：Hermes state.db 的 input_tokens 是增量（input<cacheRead），ZCode db.sqlite 的 input_tokens 是全量（input≥cacheRead，12429 样本 0 例外）。跨端直接对表必错。
- **ZCode anthropic 协议有 cpa-gemini-carrier-v1 签名机制**：reasoning part 里挂 218B~2MB base64 签名做增量缓存（2MB 那种属异常膨胀）。
- **desktop 状态栏数字全是用户自建 token-stats 插件**（Google/Antigravity 配额监控，manifest icon=BatteryCharging）：93%=系统电量、7.1%/23.4%/电池%=插件数据，**与缓存命中率无关**，严禁解读为缓存。
- **bg-review（后台审查）**：56 次 fork/265 次调用，91% result=none 是官方设计的 save/skip 策略（issue #87250 明文）；其 90.9% 消耗是 cache_read 廉价读（62.8M/69.1M），真实新增仅 input 6.3M——**不能当"纯浪费"关掉**（enabled:false 会失去自改进闭环）。

## bg-review 思考开销与 reasoning_effort 调查（官方 issue 已提）

- 用户 config `agent.reasoning_effort: ultra` → bg-review fork 同模型路径**字节级继承**父会话 reasoning_config（`_same_model_parity_kwargs`，background_review.py:758），16 轮迭代全带 ultra 思考链。
- **`auxiliary.background_review.reasoning_effort` 在同模型路径被刻意忽略**（PR #94832：routed 分支才消费此键；同模型分支字节不变是 #30532 的缓存平价设计——thinking 字段是缓存 key 的一部分，fork-birth 请求 diverge 曾占全会话 cache_creation 的 37.7%）。
- 本地 build（desktop contentHash 92915264…）**未含 #94832 修复**，路由+effort 组合也会被静默丢弃。
- Gemini 路线实测思考开销是零头（avg 284 reasoning tok/次 vs 40 万上下文），不值得治；WorkBuddy 思考型路线（glm-5.3-flash 思考链吃光 max_tokens 配额）才是真实风险区，但治它需"更新 Hermes→路由到非思考模型→配 effort: low"三连，每步有质量/缓存代价。
- **用户拍板：全部不动**（每个改动都带缺点和纰漏，维持官方默认）。已提交官方 issue：**NousResearch/hermes-agent#104116**（docs 缺失 + 同模型路径无缓存安全的解耦方式）。

## 用户使用模式（影响任何压缩/剪枝方案设计）

- 用户习惯：**会话列表值 ≥1M 就让 AI 总结记忆然后删除会话开新聊** → idle_compact 类功能无意义；threshold_tokens 只是防失控（实测失控特例：533K tokens/1272 消息才触发压缩，压缩摘要走继承主模型 150 秒且两次中断）；proactive_prune（官方默认 0 关闭，try 48000）若将来启用是唯一核心项，min_reclaim EOQ 最优 20-30K（PR #62389 模型）。
- Hermes 官方默认配置 = 给"全价 API"设计的保守值；1M 窗口 + 0.5 阈值 = 524K 才压缩是 issue #91830 讨论的大窗口病形态。用户 config 与官方默认零偏离（仅 skills.creation_nudge_interval 放宽到 15）。

## 关键文件路径（复查入口）

- 网关账本：`D:/EasyCLIProxyAPI-v0.2.71-Windows-amd64/usage-records/usage.db`
- Hermes 会话库：`C:/Users/VOS-User/AppData/Local/hermes/state.db`（session_model_usage 表 task='background_review' 单独记账）
- ZCode 会话库：`C:/Users/VOS-User/.zcode/cli/db/db.sqlite`（model_usage 表，只读用 uri=file:...?mode=ro）
- 请求转储：`AppData/Local/hermes/sessions/request_dump_*.json`（reason= max_retries_exhausted 34 个/non_retryable 11 个）
- bg-review 日志行：`Background review complete: thread=bg-review calls=N in=N out=N cache_read=N result=none`
