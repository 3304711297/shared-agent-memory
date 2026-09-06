---
name: hermes-token-debugging
description: Use when analyzing Hermes token usage or cache behavior.
---

# 双端 Token 用量取证（2026-09-06 实证闭环）

## 数据源可信度排序
1. **网关中立账本** `D:/EasyCLIProxyAPI-v0.2.71-Windows-amd64/usage-records/usage.db`
   - 表 `usage_events`；`user_agent` 区分客户端：`OpenAI/Python*`=Hermes，`ZCode/*`=ZCode
   - `cached_tokens` ≡ `cache_read_tokens`（逐条相等，任取其一）
2. Hermes `state.db`：`session_model_usage`（`task` 字段单独记账 background_review）、`sessions`
3. ZCode `.zcode/cli/db/db.sqlite`：`model_usage` / `turn_usage`
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
改后重算同口径四指标：单次中位/均值/P90（基线 328,714/422,973/817,333）、缓存命中率（基线 95.9%）；prune 提交应呈"罕见大批次"节奏，间隔 <10min 说明触发线偏小。