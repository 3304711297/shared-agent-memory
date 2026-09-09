---
name: prompt-language-token-cost
description: 实测结论——中文系统提示词/记忆库比英文贵约 1.34x token；改英文需先压内容，因内置库按字符限额而成本按 token 计
metadata:
  type: reference
---

注入系统提示词与内置记忆库的语言直接影响每轮 token 成本。2026-09-09 双分词器实测：G​emini 真值 1.10x，O​penAI o200k_base 1.34x。

## 实测数据（2026-09-09 双分词器对照）

### G​emini 真值（countTokens 实测，`gemini-3.8-flash`）

走 Antigravity `v1internal:countTokens` 实测（**零配额消耗**，只计数不生成）：

| 样本 | 中文字/token | 英文字/token | 倍率 |
|---|---|---|---|
| Fork-First 规则 | 140 / 94 | 361 / 82 | 1.15x |
| 记忆架构段 | 175 / 107 | 374 / 103 | 1.04x |
| 混合配置（含大量英文术语） | 174 / 86 | 181 / 77 | 1.12x |
| 短指令 | 10 / 7 | 24 / 6 | 1.17x |
| **合计** | **499 / 294** | **940 / 268** | **1.10x** |

**结论：G​emini 下中文 = 英文的 1.10x token**，中文约 0.59 token/字，英文约 0.29 token/字符。

### O​penAI o200k_base（对照，第三方基准）

- 同一句 Fork-First：中文 140 字符 = **104 token**；英文同义 361 字符 = **80 token**（1.30x）。
- 中文只占 37–41% 的字符数，却多花 34–55% 的 token——汉字几乎不产生词合并。
- 6 组配对基准：中文 1.06–1.55x，平均 **1.34x**；日文 1.73x。旧 `cl100k_base` 下中文达 2.08x。

### 关键教训

**厂商不可外推**：G​emini 1.10x vs O​penAI 1.34x，差 22%。G​emini 对 CJK 明显比 O​penAI 友好。要准数必须调对应厂商的 `count_tokens`——用 tiktoken 估 G​emini 会高估约 20%。

### 零成本实测方法（可复用）

Antigravity 的 countTokens 需 `{"request": {...}}` 包装（直接给 model/contents 会 400）：

```
POST https://daily-cloudcode-pa.googleapis.com/v1internal:countTokens
Authorization: Bearer <antigravity access_token>
{"request": {"model": "models/gemini-3.8-flash",
             "contents": [{"role": "user", "parts": [{"text": ...}]}]}}
```

返回 `{"totalTokens": N}`。该端点**不消耗生成配额**，适合在额度紧张时做分词器基准。注意 `v1beta`/`v1` 标准路径返回 404，只有 `v1internal` 通。

## 关键陷阱：限额按字符，成本按 token

Hermes 内置库限额是 `memory.memory_char_limit` / `user_char_limit`（默认 3000/2000 **字符**）。同样 3000 字符预算：全中文 ≈ 2490 token，全英文 ≈ 615 token。**英文版表达同样信息需要约 2.5 倍字符**，所以直接翻译会撑爆限额——必须先把内容压掉约 60%（低频条目迁 OpenViking）再译。

## 落地结果（2026-09-09）

SOUL.md / MEMORY.md / USER.md 三文件全量译英 + 压缩，每轮注入合计 **3430 → 2004 token**（按 o200k 计）。

**注意**：3430 与 1426 的差额是按 o200k_base 估的。按 G​emini 真值 1.10x 重算，实际节省约 **200 token/轮**（而非 1426）。保留英文版的真正理由不是省下的绝对量（相对 21.7k 底座约 0.9%），而是**限额空间**——同样预算下英文能塞进更多事实；且回滚需再次破坏 cache 前缀并 revert 两个已推 commit。

| 文件 | token 变化 | 字符限额 |
|---|---|---|
| SOUL.md | 826 → 797 | 无 |
| MEMORY.md | 1525 → 740 | 2769/3000 |
| USER.md | 1079 → 464 | 1996/2000 |

**Why:** 这三份随系统提示词全量注入每一轮，是最高频复现的开销；中文在其中占比达 49%（MEMORY.md）。

**How to apply:** 想省钱先做减法再谈换语言；改完必须实测字符数确认未超限。另外 SOUL.md 位于 cache 前缀最头部，改动会失效其后整段前缀一次，属一次性成本，不值得为几十 token 反复改。输出语言是另一本账——用户若不擅长英文，输出侧保持中文的体验收益大于 token 成本。
