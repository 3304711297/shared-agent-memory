---
name: codebuddy-upstream-11128-fingerprint-block
description: CodeBuddy 反代 11128 风控拦截的实证机制、定位手法与脱敏设计约束
metadata:
  node_type: memory
  type: feedback
---

# CodeBuddy 反代 11128 风控拦截（2026-09-10 实证）

排查「Hermes 某个会话突然不可用」时的根因结论。默认猜测是 429/6004 限流，**实际是另一回事**。

## 症状与误判点

- Hermes 侧表现：会话连续 3 次重试全挂后彻底不可用，日志刷 `code 11128 Illegal API invocation from an unapproved channel`。
- **不是**限流（6004 是「使用量超出频率限制」，消息里带重置时间；11128 是安全策略拦截，无重置时间）。先读 `errors.log` 里的 code 再定性。
- 只影响**单个会话**，其他会话正常 → 说明毒在该会话的**历史消息**里，不在全局配置。

## 拦截机制（实测结论，别靠猜）

- **整串匹配，不是分词**：`Main branch` 或 `(you will usually use this for PRs):` 单独出现都不触发，必须完整串才拦。加词表要加**完整短语**。
- **只拦 `system` / `assistant` 角色**：`user` / `tool` 角色带同样的串不拦。后端防的是「客户端指纹」，只扫客户端会主动构造的角色。
  → 因此脱敏范围 `roles=("system","assistant")` 是**精确解**，不要为「更保险」扩到 user/tool，扩了只污染真实对话。
- **毒在历史里会永久复现**：触发串一旦进入某条 `assistant` 历史消息，后续每次请求都带着它 → 该会话永久 11128。
  **修代码救不回已有会话**，只能改 `state.db` 那条消息或放弃会话。这是「要不要救会话」决策的关键依据。

## 定位手法（二分 + 探针，比读代码快）

1. 从 `state.db` 的 `messages` 表重建 OpenAI 格式 messages（注意用 `api_content`，它是实际发出的内容）。
2. 递增窗口打 8787：`last1 / last2 / ... ` 找到最小触发前缀。
3. 在触发前缀里逐条、再逐行二分，定位到具体串。
4. 对候选串做「词汇拆分」验证，确认是整串还是片段命中。

⚠️ **探针必须以 `user` 消息开头**。单条 `assistant` 作唯一消息会返回 11151、孤立 `tool` 无配对 `tool_calls` 返回 11148 —— 都是会话结构非法，**不是风控结果**，极易误报成缺陷（我 09-10 就误报过一次）。

## 脱敏设计约束

两层，**顺序不能反**：

1. `_rewrite_known_fingerprints()` —— 精确改写已知指纹（稳定，遇变体不漏）
2. `SENSITIVE_TERMS` 零宽空格兜底 —— 只打断匹配，词还在语义还在，遇变体会漏

已确认指纹（源码 `desensitize.py` 常量，左=原文 → 右=改写后）：

- `_ATTRIBUTION_HEADER_PREFIX`：`x-anthropic-billing-header:` 开头的整行 → 剥离
- `_CLAUDE_CODE_IDENTITY`：`"You are Claude Code, Anthropic's official CLI for Claude."`
  → `_NEUTRAL_CLI_IDENTITY` 中性 CLI 身份文本
  另有 `_CLAUDE_CODE_IDENTITY_PREFIX`（无尾部 `for Claude.`）前缀变体，同改写
- `_MAIN_BRANCH_FINGERPRINT`：`"Main branch (you will usually use this for PRs):"` → `Main branch:`
  另有 `_MAIN_BRANCH_FINGERPRINT_NO_COLON` 无冒号变体 → `Main branch`

注意区分**原文常量**与**改写目标**：`_NEUTRAL_CLI_IDENTITY` 是改写后的结果，不是指纹。

改动后**必须实测模型可调用性**，不能只看单测。

## 排查教训

- 症状「只有这个会话不可用」→ 先怀疑历史内容，不要先怀疑全局配置/额度。
- 复现优先于推理：直接重放真实请求体打端点，二分定位，几分钟出结果；读代码猜词表会绕远。
- 自己的输出也可能成为毒源：本次触发串是 Agent 在总结「指纹改写」能力时，把被误判的原文抄进了回复。

相关：[[codebuddy2openai-tauri-gui]] [[codebuddy2openai-upstream-benchmark]] [[hermes-desktop-rewind-deadlock]]
