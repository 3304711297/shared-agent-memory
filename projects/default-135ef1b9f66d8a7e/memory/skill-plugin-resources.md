---
name: skill-plugin-resources
description: 技能/插件索引库：19 个 Skills/插件/Agent 资源站与仓库（需新技能时在此按需检索，已装技能的漂移检查走 check_skill_drift.py）
metadata:
  type: reference
---

用户浏览器书签「skill hub」文件夹（2026-09-07 实查本地 Edge Dev 书签，全量 10 项）：

**市场/目录类**
1. **SkillHub** — https://skillhub.cn/ （腾讯云镜像 https://skillhub.cloud.tencent.com/skills）：专为中国用户优化的 AI Skills 社区，精选 Top 50、宣称经安全审核；国内访问友好，优先从这里找。
2. **Cola Skill** — https://colaskill.com/ ：Claude/Agent skills 策展市场，中文描述+按行业打包（电商/设计/一人公司等），善用"Smart install"按需挑技能；不直接托管代码，安装前看原始仓库。
3. **Hermes Agent Skills Hub** — https://hermes-agent.nousresearch.com/docs/user-guide/features/skills （附技能目录 https://hermes-agent.nousresearch.com/docs/reference/skills-catalog ）：Hermes 官方技能系统与内置目录（装到 ~/.hermes/skills/），给 hermes-agent 装技能走这里。

**GitHub 仓库类（已验证存在，2026-09-07 全量对齐）**
4. **affaan-m/ECC** — https://github.com/affaan-m/ECC ：agent harness 性能优化系统（Skills/instincts/memory/security/研究优先开发），适用 Claude Code/Codex/Opencode/Cursor 等。
5. **google-gemini/gemini-skills** — https://github.com/google-gemini/gemini-skills ：Google 官方，Gemini API/SDK 与模型交互技能。
6. **zai-org/zcode-plugins** — https://github.com/zai-org/zcode-plugins ：ZCode 插件市场官方仓库（内置+社区插件），ZCode 组件升级/排查市场问题时对照它（关联 [[capability-upstream-watch]] 的两层市场架构）。

**Anthropic 官方仓库**
7. **anthropics/skills** — https://github.com/anthropics/skills ：Agent Skills 官方公共仓库（Claude 系技能的源头真源）。
8. **anthropics/claude-plugins-official** — https://github.com/anthropics/claude-plugins-official ：Anthropic 官方管理的高质量 Claude Code 插件目录。
9. **anthropics/knowledge-work-plugins** — https://github.com/anthropics/knowledge-work-plugins ：面向知识工作者的开源插件集（主要供 Claude Cowork 使用）。

**前沿 Agent 架构类（2026-09-07 书签最新实查扩充）**
10. **TokenRhythm/opensquilla** — https://github.com/TokenRhythm/opensquilla ：OpenSquilla，高 Token 效率与高智能密度 Agent 框架，具有前沿 Session 隔离与任务裁决机制。

**高价值方法论与技能蒸馏元生态类（2026-09-07 评审评估收录）**
11. **kangarooking/cangjie-skill** — https://github.com/kangarooking/cangjie-skill ：仓颉技能蒸馏母机（9.2k Stars，RIA-TV++ 体系），将书籍、长视频字幕、播客转写提炼为原子化、可执行的 Agent技能包；已提炼母机为本地按需技能 `cangjie-distill`（排除上百个衍生包，杜绝技能通胀）。
12. **mattpocock/skills** — https://github.com/mattpocock/skills ：Matt Pocock 工程师实战技能集（247k Stars，Skills for Real Engineers）；精选采纳 `domain-modeling`（防术语漂移）与 `codebase-design`（深模块设计哲学），排除与外部任务书重叠的 PM 切票类工具。

**权威科研数据域雷达（2026-09-09 评审收录，按需单拉不整装）**
13. **google-deepmind/science-skills** — https://github.com/google-deepmind/science-skills ：GDM 官方科研技能库（2659 Stars，Apache 2.0），40 个 skill 覆盖基因组学/结构生物学/化学信息学/文献检索/本体通路/临床数据，脚本经 PEP 723 + `uv run` 直连 40+ 权威数据源（UniProt/Ensembl/PDB/PubChem/ChEMBL/ClinVar/gnomAD/PubMed/OpenAlex/arXiv 等）。**不整装**（会冲破二八瘦身铁律），需要时**只拉单个 skill 目录**审读后放入 skills/。免 key 可直接用的优先项：`pubmed_database`、`uniprot_database`、`pubchem_database`、`pdb_database`、`clinical_trials_database`、`literature_search_arxiv`（与本地 research/arxiv 重叠，二选一）、`gnomad_database`、`string_database`。需 key 才完整：alphagenome(2 项) 与 openalex 必需，clinvar/dbsnp/ncbi/pubmed/openfda 加 NCBI_API_KEY 提频。**⛔ 禁用 `predictingthepast`**：其 run_inference.py 用 `pickle.load` 反序列化 GCS 下载的 .pkl 检查点，属远程代码执行面，且强依赖 jax。基线 sha `28b8482`（2026-09-08）。

**已在本地实装的上游源（2026-09-09 出处盘点回补，供漂移检查与重装定位）**
14. **obra/superpowers** — https://github.com/obra/superpowers ：开发纪律套件（283k Stars），本地 14 项全量实装，正文与上游一致、仅 description 做了中文强触发词改造（**禁止被上游覆盖**）。
15. **DietrichGebert/ponytail** — https://github.com/DietrichGebert/ponytail ：代码极简与反过度工程套件（132k Stars），本地 6 项实装。注意其仓库同时存在 `.openclaw/skills/` 与 `skills/` 两份副本，以 `skills/` 为准。
16. **NousResearch/hermes-agent** — https://github.com/NousResearch/hermes-agent ：Hermes 本体仓库的 `skills/` + `optional-skills/`（合计 199 个 SKILL.md），本地 27 项实装。注意 `optional-skills/` 与 `skills/` 存在重名（如 rss-feeds/reddit-reading 已迁至 optional），映射时优先取较短路径。
17. **BadTechBandit/skills** — https://github.com/BadTechBandit/skills ：本地 `c​laude-design` 与 `architecture-diagram` 的可能来源（4 Stars，2026-04 后停更，**已停维护**，仅作溯源用）。
18. **JulienTant/blogwatcher-cli** — https://github.com/JulienTant/blogwatcher-cli ：本地 `research/blogwatcher` 的上游（31 Stars，2026-05 后停更，仅作溯源用）。

**Hermes 专用生态地图类（2026-09-09 评审收录，按需检索不实装）**
19. **ksimback/hermes-ecosystem（Hermes Atlas）** — https://github.com/ksimback/hermes-ecosystem （站点 https://hermesatlas.com ）：社区维护的 Hermes 生态项目地图（1229 Stars，bot 自动重建，全量 249 个项目、质量过滤收录 80+，分 12 类：Core/GUI 工作台/技能库/插件/记忆/多智能体/部署/集成/开发工具/领域应用/指南）。亮点：对 25★+ 仓库做过安全审查（`repos/security-review.md`，5 个 WARN：hermes-CCC 与 vessel-browser 有 curl-pipe-bash 安装器、gladiator 有硬编码凭据，使用前先审脚本）；找"某类 Hermes 工具是否存在/哪个成熟"先查它。注意：ECOSYSTEM.md 是 2026-04 快照（星数滞后），实时数据看网站 API；`data/repos.json` 为活数据。基线 sha `bebd922`（2026-09-09）。

**索引库规模（2026-09-09 实查）**：15 个 GitHub 技能源合计约 **1,467 个可拉取 SKILL.md**（ECC 898 / hermes-agent 199 / knowledge-work-plugins 212 / science-skills 40 / mattpocock 37 / claude-plugins-official 31 / anthropics 20 / ponytail 13 / gemini-skills 3 等），全部可访问、无归档或禁用；本地实装 84 项，采撷率约 5.7%，符合二八瘦身铁律（技能池控制在 30-50 项为宜，按需从本索引单拉）。第 19 号源 Atlas 为项目地图（不含 SKILL.md），不计入技能源计数。

**How to apply:** 用户要找某类能力（如 PPT/SEO/安全审计技能）或 ZCode/Hermes 缺功能时，先查 1/2 的中文目录定位技能名，再回 GitHub 拿源码审读后安装；Claude 系官方技能/插件直接用 7/8/9（源头真源，优先于第三方转译）；Gemini/ZCode 官方需求直接用 5/6；Token 优化与架构借鉴看 10；长文/长视频方法论提炼看 11；领域建模与深模块架构看 12；科研数据库（蛋白/基因/化合物/文献/临床）查文献需求看 13（按需单拉，不整装）；**已装技能的溯源与重装查 14-18**；找 Hermes 生态里的成熟工具/插件/集成项目（含安全审查结论）看 19。第三方 skill 安装前必须人工审内容（提示词注入面），不盲装。
