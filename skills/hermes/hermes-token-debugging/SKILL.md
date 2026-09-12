---
name: hermes-token-debugging
description: "分析token用量/缓存时必用。Hermes token与cache行为。Use when analyzing Hermes token usage or cache behavior."
---

# 双端 Token 用量取证（2026-09-06 实证闭环）

## 数据源可信度排序
1. **网关中立账本** `D:/EasyCLIProxyAPI-v0.2.71-Windows-amd64/usage-records/usage.db`
   - 表 `usage_events`；`user_agent` 区分客户端：`OpenAI/Python*`=Hermes，`ZCode/*`=ZCode
   - `cached_tokens` ≡ `cache_read_tokens`（逐条相等，任取其一）
2. Hermes `state.db`：`session_model_usage`（`task` 字段单独记账 background_review）、`sessions`
3. ~~ZCode `.zcode/cli/db/db.sqlite`：`model_usage` / `turn_usage`~~ **[已失效 2026-09-09 — ZCode 拆除，此数据源不存在]**
4. 请求转储 `hermes/sessions/*.json`：`request.body.tools` 可直接数工具 schema

## 口径陷阱（曾三次踩坑，勿重蹈）
- **input 语义两端相反**：Hermes(chat_completions) input<cacheRead=增量口径；ZCode(anthropic-messages) input≥cacheRead=全量含缓存。跨端对比先对齐口径。
- **ZCode 主力流量不走 cpa-gui 网关**（走 builtin:bigmodel 等其他 provider）——必须按 UA 过滤后对比，否则样本严重不对称。
- **桌面状态栏 7.1%/23.4%/电池图标 = 用户自建配额插件 token-stats（Google/Antigravity 额度），不是缓存命中率**；显示器图标旁的 % = 系统电量。

## 已实证结论
- 同模型同网关：Hermes 单次上下文 ≈3.34x ZCode（423k vs 127k tok），主因=对话历史膨胀；固定底座仅 ~21.7k/轮（sysprompt 8.7k + tools 13k）且全在缓存前缀内（约 1/4 价）。
- `tools.tool_search` 净省 ~31k tok/轮（123 个延迟工具 38.5k tok 藏在 4k 目录后），**严禁建议关闭**。
- bg-review 是设计行为：90.9% 开销是 cache_read；`result=none` 正常；`enabled:false` 不影响手动 `/refine`。
- 压缩模型=继承主模型（`auxiliary.compression` 未配置时，conversation_compression.py:737）；思考型主模型（hy4/glm）跑压缩实测 150s+ 两次中断。
- glm-5.3-flash / hy4-preview 均 1M 窗口 → 0.5 阈值=52 万才压（过晚，实证 533K/1272 条才触发）。

## 优化候选（官方默认全关，需手动开）
```yaml
compression:
  proactive_prune_tokens: 48000              # 默认 0；确定性剪枝，官方建议起点
  proactive_prune_min_reclaim_tokens: 20000  # 默认 4096；EOQ 模型人类节奏最优 20-30K（PR #62389）
  threshold_tokens: 250000                   # 默认 null；1M 窗口建议 25-30 万
# auxiliary.background_review.{provider,model} 路由便宜模型 ~39x；或 memory.nudge_interval 10→30
```
- 每次 prune/压缩提交=破缓存前缀（issue #91830，不可根治；rearm 只管频率不管破坏本身）；本机已含 #92184 修复。
- 用户习惯会话 ≥1M 即删 → `idle_compact_after_seconds` 无意义，prune 是核心杠杆；订阅缓存读倍率决定 prune 净收益（倍率≈免费时 prune 费用面倒挂，余量/质量收益仍在）。

## 验证方法
改后重算同口径四指标：单次中位/均值/P90、缓存命中率；prune 提交应呈"罕见大批次"节奏，间隔 <10min 说明触发线偏小。

## 口径铁律（2026-09-08 实测纠正，勿再犯）
1. **Gateway usage.db 的 `input_tokens` 已含 `cache_read_tokens`**（全量口径）。命中率 = `SUM(cache_read)/SUM(input)`，**不是** `cr/(input+cr)`——后者会算出 48.5% 的假值，真值 94.1%。
2. **`total_tokens` ≈ `input+output`**，不含 cache 加算。
3. **usage.db 只保留 4 天**（id 从 1 连续，滚动清库）。任何跨周对比都会失真；改前/改后基线必须同库同窗口内取。
4. 2026-09-08 实测（Hermes UA，n=7848，09-04~08）：med 164,138 / mean 194,205 / P90 404,215 / cache 94.1%。**旧记录的 328,714/422,973/817,333 基线出自更早的已清库数据，不可复现，勿再引用。**
5. 归因 bg-review 效果用 `state.db` 的 `session_model_usage.task` 字段（按 task 记账），比在 usage.db 里按 UA/时间切片可靠。

## 已兑现效果（2026-09-08 实测）
- **background_review 关闭确实生效**：最后一条记录停在 09-07 23:53（禁用后），09-08 全天为 0，无 fail-open 复活。
- 其历史占比：calls 17.8%、input 28.8%、cache_read **37.5%**；每调用均值 133,781 cache_read vs 主流量 49,999（2.7x）。剔除后每调用均值 71,201→54,957（**-22.8%**）。
- **proactive_prune 至今仍是 `proactive_prune_tokens: 0`（从未开启）** —— 最大的那个杠杆一分钱没兑现。

## 思考爆炸与中英重复归因（2026-09-10 实证，deepseek-v4.1-flash@codebuddy/8787）

- **体量实测**：两深调研会话 reasoning 占 output token 约 90%（327K/362K、809K/901K）；单条 trace 中位 1.7万~2.7万字符、最大 10.6 万；单会话合计 1.4M~6.0M 字符。
- **主因排序（A/B 实测，非猜测）**：
  1. **`agent.reasoning_effort: ultra` → wire 实发 `max`**：高 effort 调用 rtok 主体 5k~10k、时延 35~56s（探针观察）。**但档位差异不可靠**：同日 20+ 轮对照（temp=0 同形任务）显示同批内 max 明显重于 medium（5.9k~10.2k vs 0.4k~1.6k），但跨批 medium 复测达 3.3k~6.7k——区间重叠、无稳定单调，**该后端没有实现可靠的努力阶梯，单跑结论不可采信**。
  2. 模型结构性过思考（文献：步级冗余 61~93%，outcome-only reward 下无有限最优停止，属训练属性非 bug）。
  3. 双语复述：英文主导 CoT + 结尾中文成稿（Reply in Chinese 目标语言），同一结论第二遍表述。
- **rc 回传的定位（2026-09-10 二次修正，勿引用旧结论）**：Hermes 的 `_REASONING_ECHO_RULES` 确实对 model 名含 `deepseek` 的链路做全部历史 rc 回传（dump 实测单请求 281K 字符）；但**本链路（codebuddy/8787 → 上游）实测 rc 字段既不改变 prompt_tokens 也不能被模型引用**（带/不带 7000 字符 rc，prompt_tokens 均为 335/2216 不变；暗号可见性测试 3 组全 FAIL）。早期“rc 放大 7x”观测是 temperature 未固定造成的假象；temp=0 复测 rc=T 与 rc=F 无显著差异（同档位）。**结论：rc 回传是 token 带宽浪费，但不是思考膨胀的加速器**；真正放大器是 effort 档位。
- **该后端 reasoning 语义实测（腾讯 copilot.tencent.com，2026-09-10）**：`reasoning_effort` **缺位 → 不思考**（5 轮 rtok=0）；**在位（含 `none`）→ 思考**（none 3 轮 3.7k~5.6k rtok——"关"关不掉）；档位值对长度影响不可靠（见上）。输入 `reasoning_content` 被静默丢弃。`chat_template_kwargs` 不在反代透传白名单 `PASSTHROUGH_BODY_KEYS`，客户端直传会被丢弃（早前 ct 探针因此无效）；仅反代控制台 disable 路径自注入（效果未验证）。
- **归属判决（2026-09-10，用户认同）**：语义紊乱 + rc 丢弃 = **腾讯后端对新模型的适配滞后**（V4.1 Flash 当日 12:00 才发布，552B MoE 新架构；官方称模型对 DeepSeek Harness v0.1.5 的运行配置专项训练，第三方 harness/后端行为易漂移）。反代 workbuddy2api 忠实透传、Hermes 忠实执行档位——两段皆无过。**用户拍板：保留 ultra 档、反代不加翻译层、等腾讯适配；全局 `agent.reasoning_effort: ultra` 严禁改动。**
- **非诱因排除**：receiving-code-review 等 skill 无因果（未加载该 skill 的共时会话思考量更大 5x）；show_reasoning 类显示开关不影响生成。
- **排查入口**：`state.db` 的 `messages.reasoning` / `sessions.reasoning_tokens`；`sessions/request_dump_*.json` 查 rc 回传实况。
- **备注**：本链路调档收益不稳；用户明确要 ultra 质量档（全局默认勿动）。若日后确需压时延：优先换非 deepseek 链路/模型，而非调档。