---
name: hermes-atlas-absorption
description: ksimback/hermes-ecosystem（Hermes Atlas）生态仓库吸收总账：第19号索引源、三篇蒸馏入ysk、安全红旗清单入评估技能与排除清单
metadata:
  type: project
---

# Hermes Atlas 生态仓库吸收总账（2026-09-09/10）

对社区仓库 ksimback/hermes-ecosystem（hermesatlas.com，Hermes 生态项目地图，1229★，bot 自动重建 249 项目）的完整吸收，按资产三层落账：

## 吸收落账
1. **索引型收录（不实装）**：第 19 号源写入 skill-plugin-resources.md（项目地图 + `research/` 约 70 篇研究文档按需 `web_extract` 单篇取读路径 + 25★+ 安全审查指针，5 个 WARN 需先审脚本；ECOSYSTEM.md 为 2026-04 快照星数滞后；基线 sha `bebd922`）；capability-inventory.json notWatched 登记收录理由；MEMORY.md 索引行同步（19 源=18 技能源+1 项目地图）。
2. **三篇蒸馏入 youshouldknow**（commit `cda47a4`，CI build/link-check/front-matter-check/deploy 四绿）：
   - `research/45`（@KSimback 记忆指南）→《Hermes 记忆体系三层架构与选型决策指南》：原生便签/官方 Provider/社区插件三层叠加、"80% 自动合并"（实为 prompt 指令非代码）与"Curator 管记忆"（只管技能库）两大误传源码级辟谣、8 家 Provider 架构对照、过重记忆层五条报警信号
   - `research/39` →《Hermes 技能系统机制原理：渐进式披露与程序性记忆》：Level 0/1/2 三级按需加载（本机工具池 skills_list/skill_view 实证）、事实/历史/方法三分法、SKILL.md 六要素
   - `research/28` →《Hermes 多 Profile 编队实战：从单助手到隔离的多 Agent 团队》：七类状态隔离心智模型、四角色架构、SOUL.md 定身份/AGENTS.md 定语境分界、七步落地，附本地并发上限≈2 定标修正
3. **方法论吸收**：security-review 六类安全红旗清单（混淆代码/凭据收割/typosquatting/供应链/curl-pipe-bash/挖矿/越权）+ PASS/WARN/REJECT 三级判定（WARN 不得进自动安装/更新路径）并入 skill-evaluation-and-admission 技能 Step 1.1 节（hermes 分支 `c73912a`）。

## 明确排除（评估过本体，非凭标题）
RAG 管线与检索分层策略（托管问答站形态，OpenViking+本地 bge-m3 为上位实现）、GitHub Actions bot 定时重建（与 gen-matrix.py/看门雷达同构）、community-pulse 30 天脉搏（blogwatcher+RSS 覆盖）、repos/ 星数快照（易过期）、research/38/42/43/44/29 攻略（未拍板，留按需）。

**Why:** 该仓库是 Hermes 生态唯一的项目级地图与安全审查源，`research/` 每周持续追加 release digest，长期价值在按需单篇拉取而非一次性摄入。
**How to apply:** 找 Hermes 生态成熟工具或做新技能安全评估 → 查索引库第 19 号源；需要周报细节时 `web_extract` 对应 research/ 单篇；不整装、不实装、零维护成本。
