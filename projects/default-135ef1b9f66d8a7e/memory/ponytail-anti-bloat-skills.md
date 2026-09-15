---
name: ponytail-anti-bloat-skills
description: 引入 Ponytail 极简编程与反过度工程技能套件（按需 Skill 架构而非常驻 Plugin），纳入看门狗 capability-inventory.json
metadata:
  type: project
---

## 选型背景与决策（2026-09-07）

针对开源项目 `DietrichGebert/ponytail`（120k+ stars）与 `JuliusBrussee/caveman` 进行全面技术评估与落地：
1. **Caveman 评估裁定：坚决不安装**
   - **语言表达破坏**：穴居人语气在中文极客 IDE 下为生硬机翻碎语，破坏技术表达；用户系统提示词已天然具备「一问一答、直入主题、无寒暄」的高效汇报规范；
   - **Prompt 倒挂**：Skill 规则本身每轮固定消耗 1,000 ~ 1,500 input tokens，多轮对话不仅不省甚至倒赔 token；
   - **破坏 Prompt Caching**：其本地 Proxy 启发式截断历史与代码，直接破坏 Gemini 网关的 Prefix Prompt Cache，导致缓存击穿、实际成本反增。
2. **Ponytail 架构决策：收其技法（Skills），避其常驻（非 Plugin）**
   - **核心梯子（The Ladder）**：YAGNI → 代码复用 → 标准库 stdlib 优先 → 原生平台特性优先 → 现有依赖优先 → 单行解法 → 最小可用代码（代码极简，但绝不妥协 trust boundary 校验、安全与错误防护）；
   - **拒绝全局 Plugin**：避免在系统配置、运维巡检、日常检索等非代码会话中每轮污染系统上下文；
   - **按需 Skills 部署（Hermes 单端 6 项全量落地）**：
     - `ponytail`：极简实现模式
     - `ponytail-review`：diff 级过度工程审查（输出 delete / stdlib / native / yagni / shrink 清单）
     - `ponytail-audit`：全仓过度工程扫描
     - `ponytail-debt`：`ponytail:` 注释台账追踪
     - `ponytail-gain`：基准指标参考
     - `ponytail-help`：使用参考卡片
     - 宿主路径：`%LOCALAPPDATA%\hermes\skills\software-development\`（6 项；ZCode 副本已随 ZCode 于 2026-09-09 拆除移除）
3. **CI 看门狗与自动化追踪闭环**：
   - 登记至 `capability-inventory.json`，ID 为 `ponytail-skills`，类型 `gh-release` 追踪 `DietrichGebert/ponytail`；
   - 本地 `check_capability_upstream.py` 验证全项一致（0 outdated、0 skipped、has_updates=false）；
   - 每日 GitHub Actions 自动比对上游 release。

## v4.10.0 跟进结论（2026-09-15，Issue #14）

看门报 `ponytail-skills` 4.9.0 → 4.10.0。核查结论：**上游 `skills/` 子树逐字节未变，无需同步任何技能文件**。

- 比对方法：浅克隆后取两侧 `git rev-parse v4.9.0:skills v4.10.0:skills`，tree hash 均为 `d15d0642cedda91d97cd882333d2c70c564c6f52`；6 个 SKILL.md 的 blob hash 逐一相同。
- 上游本轮改动全部落在 skills 之外：`hooks/`（Cursor 原生 hooks via hooks.json、Grok Build 适配器、mode tracker/runtime 修补）、新增 `scripts/cursor-hooks.js`、各 `.xx-plugin/plugin.json` 版本号、README/docs。
- 本地保留的差异只是两类既定定制，均**不可被上游覆盖**：① frontmatter `description` 中文强触发词（6 项中 4 项仅此项不同）；② `ponytail` 正文的 `## Sub-skills` 速查表、`ponytail-audit` 正文对 tag 词表的去重引用（本地为控 token 主动瘦身，上游是重复展开）。
- 处置：仅回写清单 `installed.version`=4.10.0、`sha`=tag 提交 `1d95ff7`，并注明 skills 子树未变。**本机继续只用 skills、不装常驻 plugin**——4.10.0 的 hooks/Cursor/Grok 能力对本机（Hermes 单端 + 按需 Skill）无收益。

**This round's why:** 4.10.0 是适配器与 hooks 的发版，与「收其技法」的落地方式无关；误按版本号全量覆盖反而会冲掉本地中文触发词与正文瘦身成果。

**This round's how:** 下次 ponytail 报更新时，先跑 `git rev-parse <旧tag>:skills <新tag>:skills` 比 tree hash——相同则直接回写基线收口，不同再逐技能用 `check_skill_drift.py` 的方向判定决定是否并入。

**Why:**
AI 编码 Agent 极易产生过度封装、滥加三方库的“代码通胀病”。通过按需 Skill 可以在实现与审查阶段精准榨干代码水分，且完全不增加非代码任务的上下文负担。

**How to apply:**
1. 实现新特性或重构前，按需调用 `ponytail` 技能指导最简解法；
2. 提交前进行代码瘦身审查，调用 `ponytail-review` 审查 diff 并交出删除清单；
3. 进行工程减肥时，调用 `ponytail-audit` 扫描全仓冗余抽象与无用封装；
4. 组件升级随 `capability-inventory.json` 清单追踪，保持看门闭环。
