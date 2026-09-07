---
name: ponytail-anti-bloat-skills
description: 引入 Ponytail 极简编程与反过度工程技能套件（v4.9.0，按需 Skill 架构而非常驻 Plugin），纳入看门狗 capability-inventory.json
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
   - **双端按需 Skills 部署（6 项全量落地）**：
     - `ponytail`：极简实现模式
     - `ponytail-review`：diff 级过度工程审查（输出 delete / stdlib / native / yagni / shrink 清单）
     - `ponytail-audit`：全仓过度工程扫描
     - `ponytail-debt`：`ponytail:` 注释台账追踪
     - `ponytail-gain`：基准指标参考
     - `ponytail-help`：使用参考卡片
     - 宿主路径：Hermes `AppData/Local/hermes/skills/software-development/`（6 项）+ ZCode `~/.zcode/skills/`（6 项副本）。
3. **CI 看门狗与自动化追踪闭环**：
   - 登记至 `capability-inventory.json`，ID 为 `ponytail-skills`，类型 `gh-release` 追踪 `DietrichGebert/ponytail`；
   - 本地 `check_capability_upstream.py` 验证 19 项全部一致（0 outdated、0 skipped、has_updates=false）；
   - 每日 GitHub Actions 自动比对上游 release。

**Why:**
AI 编码 Agent 极易产生过度封装、滥加三方库的“代码通胀病”。通过按需 Skill 可以在实现与审查阶段精准榨干代码水分，且完全不增加非代码任务的上下文负担。

**How to apply:**
1. 实现新特性或重构前，按需调用 `ponytail` 技能指导最简解法；
2. 提交前进行代码瘦身审查，调用 `ponytail-review` 审查 diff 并交出删除清单；
3. 进行工程减肥时，调用 `ponytail-audit` 扫描全仓冗余抽象与无用封装；
4. 组件升级随 `capability-inventory.json` 清单追踪，保持看门闭环。
