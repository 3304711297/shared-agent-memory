---
name: skill-lifecycle-governance
description: 技能生命周期治理闭环：发现（索引库）→ 准入（评估 SOP）→ 维护（漂移检查）→ 同步（看门清单），三库分工与铁律
metadata:
  type: project
---

**技能生命周期治理闭环**（2026-09-09 确立，取代此前「看门发现新技能」的错误语义）：

## 三库分工（严禁越界）

| 环节 | 负责组件 | 职责 | 不负责 |
|---|---|---|---|
| **发现** | `skill-plugin-resources.md` 索引库 | 18 个源、约 1467 个可拉取技能，需要新能力时**按需检索** | 不主动推送、不自动安装 |
| **准入** | 新技能评估 SOP（五步 + Step 0 查重） | 审质量/架构/缓存影响/重叠/端到端落地 | 不做日常维护 |
| **维护** | `scripts/check_skill_drift.py` | 已装技能 vs 上游同名技能**内容比对**，判是否落后 | 不发现新技能 |
| **同步** | `capability-inventory.json` + `skills-provenance.json` | 记录已装版本与出处 | 不判定更新 |

**关键分界**：看门（`check_capability_upstream.py`）的 `github-commits-path` 分支**永不计入 outdated**，仅展示 HEAD/基线信息（2026-09-09 语义变更）。「上游仓库有 N 笔新提交」不构成更新信号——它可能改的是你没装的技能。

## 漂移检查三层判定（check_skill_drift.py）

1. **行尾归一哈希**：CRLF/LF、行尾空白、BOM 归一后比对，消除跨平台噪声
2. **差异方向**：本地多 = `local_extra`（本地增强，忽略）／上游多 = `upstream_extra`（需评估）／双向 = `both_changed`（人工判定）
3. **仅 description 差异特判**：正文一致、仅 frontmatter `description` 不同 → 判为本地中文强触发词定制，**禁止被上游覆盖**

## 铁律

- **本地增强禁止覆盖**：`hermes-agent`（UI 消歧/禁止假称并行铁律）、superpowers 13 项（中文强触发词）等本地定制，同步上游会毁掉 2026-09-07 的 57 字符截断优化成果
- **上游缩小支持范围不跟进**：如 `python-debugpy` 上游把 `platforms` 改为 `[linux, macos]` 去掉 windows，本地保留 windows 才正确
- **技能变动与看门绝对同步**：新装/升级/裁撤/否决，当轮必同步 `capability-inventory.json` 与 `skills-provenance.json` 并推 main
- **二八瘦身**：技能池控制在 30-50 项，索引库 1467 个技能按需单拉，严禁整装（ECC 898 项整装会冲破铁律）
- **安装前人工审读**：第三方 skill 是提示词注入面，不盲装；⛔ `science-skills/predictingthepast`（pickle.load 远程代码执行面）

**Why:** 旧机制按仓库提交数报更新，无法区分「上游新增你没装的技能」与「你装的技能变了」，导致误导性同步——轻则丢失本地定制，重则丢失平台支持。

**How to apply:** 需要新技能 → 查索引库 → 走评估 SOP → 装后登记出处与版本 → 定期跑 `watch-skill-drift.cmd` 看是否落后。已装技能坏了要重装 → 查索引库 14-18 项溯源。
