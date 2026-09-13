# 技能瘦身标准：GPT-6 Astra 六条（2026-09-13 落地）

来源：OpenAI《Rethinking skills and prompts for GPT-6 Astra》
（https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra，2026-09-11，作者 Eric Provencher）

核心命题：**规则越多，Agent 越找不到真正重要的事。** 旧模型时代为"补短板"写的手把手指令，在更强模型上是净负担。

## 六条标准（作为本地技能池的常驻审计口径）

1. **Skill 描述只写「什么时候用」** — 触发条件越窄，抢触发越少。
   - 反例："适用于处理数据库、查询、模型或持久化操作"
   - 正例："用于添加或更改迁移，或审查其部署"
2. **SKILL.md 只做路由** — progressive disclosure。主文档写清用途/触发/下一步读哪份文件；教程、案例、脚本按需加载进 `references/`。读一份 skill 就是烧一次 context。
3. **AGENTS.md 只放稳定全局规则** — 按任务分别指向文档，不要"每次编辑前读 architecture.md / database.md / deployment.md"。
4. **立刻删掉** — 重复、过宽、过时、互相冲突、只为旧模型写的 recipes。旧刹车会把新模型刹停。
5. **安全边界必须留** — 权限/隐私/生产/发布/删除/不可逆操作一律保留；但安全的本地测试要明确放出自主权（跑→修→复测，不步步请示）。
6. **提前写清完成标准** — 修改→运行→检查→修复→再验证。不定义"做完"，Astra 就会交一版就停。

## 本地量化基线（2026-09-13 审计）

| 指标 | 审计前 | 审计后 |
|---|---|---|
| 技能总数 | 94 | **89** |
| SKILL.md 总字符 | 712,400 | **623,382** |
| 描述总字符 | 8,441 | 7,989 |
| >8000 字符巨型 skill | 30 | 26 |
| 描述长度中位数 | 87（健康） | 87（保持） |

**结论：描述长度不是本地病灶**（94/94 已做中文强触发词前置）；真正的病灶是第 2 条——30 个 >8k 字符的巨石且多数无 `references/` 可按需加载。

## 已落地三批改动

### ① 删除 5 项 Ekko 生图/生视频技能
`apikey-image-gen`（8.8k）、`grok-image-to-video`、`hyperframes`、`minimax-image-to-video`、`remotion`。

- 用户偏好：**生图一律走 Gemini**（`zcode-custom/gemini-image-gen`），读图由当前会话聊天模型直接执行；Ekko 系列基本用不到。
- 视频理解保留自研 `media/agentic-video-distill`（双端实装，已在 protectedSkills 白名单）。
- 同步清 `.webui-managed-skills.json` 对应 5 项条目，避免 Web UI 重装回填。
- 物理备份：`%LOCALAPPDATA%/hermes/skills_backup_20260913-000251/`。

### ② 收窄 `superpowers/using-superpowers` 描述
- 旧："任务开始/对话开启时必用。技能自检总纲：1%相关也必须先查。"
- 新："用户提出新任务且未指定具体 skill 时必用…NOT for follow-ups already inside a skill's workflow."
- 这是全库唯一真正的过宽描述，且它是触发链入口，收益最大。

### ③ 拆分 3 个巨型 skill 为「路由主文档 + references/」
| Skill | 前 | 后 | refs |
|---|---|---|---|
| `autonomous-ai-agents/cross-agent-collaboration` | 25,482c | **1,759c** | 8 |
| `creative/c​laude-design` | 25,046c | **2,206c** | 8 |
| `research/llm-wiki` | 19,935c | **2,226c** | 4 |

内容零丢失，全部进 `references/`。`cross-agent-collaboration` 顺带删除 ZCode 退役章节（原 §1/§2 观察协议、§4 反向握手、§5 headless 探针）——2026-09-09 ZCode 拆除后已是死重。

## 扫尾（2026-09-13 接力，P0-B + P1/P2 收敛判定）

### ④ P0-B：拆剩余 20 个无 refs 巨石（全部路由化，内容零丢失）

| 批次 | Skill | 前 → 后 | refs |
|---|---|---|---|
| P0-A | `computer-use` | 15,758 → **1,186** | 5 |
| P0-A | `rest-graphql-debug` | 15,564 → **1,206** | 6 |
| P0-A | `simplify-code` | 14,650 → **979** | 4 |
| P0-B | `hermes-agent-skill-authoring` | 14,610 → **1,007** | 4 |
| P0-B | `python-debugpy` | 13,365 → **918** | 4 |
| P0-B | `node-inspect-debugger` | 10,909 → **944** | 4 |
| P0-B | `docker-management` | 10,416 → **888** | 3 |
| P0-B | `skill-evaluation-and-admission` | 9,625 → **890** | 3（纯路由化，SOP 语义零改动） |
| P0-B | `adversarial-ux-test` | 8,921 → **736** | 2 |
| P0-B | `spike` | 8,632 → **836** | 2 |
| P0-B | `publish-site` | 8,626 → **767** | 2 |
| P0-B | `finishing-a-development-branch` | 7,724 → **564** | 3 |
| P0-B | `agent-merge-conflict-arbiter` | 7,622 → **661** | 2 |
| P0-B | `receiving-code-review` | 7,420 → **658** | 5 |
| P0-B | `collective-wisdom-install` | 7,238 → **638** | 2 |
| P0-B | `readme-master` | 6,780 → **443** | 2 |
| P0-B | `using-git-worktrees` | 6,690 → **495** | 2 |
| P0-B | `blogwatcher` | 6,235 → **768** | 2 |
| P0-B | `inspecting-hermes-desktop-dom` | 6,207 → **742** | 3 |
| P0-B | `dispatching-parallel-agents` | 6,045 → **502** | 2 |

累计：技能数保持 **89**，SKILL.md 总体积 623,892 → **446,812** 字符（再降 177,080，-28%）。
`>6000c 无 refs` 残余仅 1 项：`ponytail` 主文档 6,264c——系常驻 discipline（ACTIVE EVERY RESPONSE），有意保持自包含，不拆。
其余 24 个 `>6000c` 均已有附属文件（上游 prompts/scripts/templates 或已路由化），不动。

### ⑤ P1/P2 收敛判定（经作者归属核查后修正执行）

- **P1a ponytail 家族**：原计划 6→1 物理合并**已否决**——主文档是常驻 discipline（必须常驻加载），5 个子技能全是 one-shot（help 速查卡本身就是路由器），当前 factored 状态正是 progressive disclosure 的正确形态；且整族被 `ponytail-skills` 看门（gh-release DietrichGebert/ponytail）跟踪，物理合并会断上游同步。实际执行：主文档加 Sub-skills 路由表；`ponytail-audit` 的 Tags 重复段改为指向 `ponytail-review` 的指针（-6 行）。
- **P1b 审查类**：`simplify-code`（已路由化）/ `ponytail-review`（diff 臃肿一行一条）/ `grill-me`（动手前对抗性质询）/ `receiving-code-review`（已路由化）/ `requesting-code-review`（结构化送审报告）——触发词已正交，**无需合并**。
- **P2**：`systematic-debugging` / `test-driven-development` 为上游 superpowers 套件成员（看门 gh-release 跟踪），**禁止删除**；`diagnosing-probe-false-failures`（本地自研 v0.1.0，探针真伪判定）与 `dogfood`（Web 探索性 QA）/ `adversarial-ux-test`（敌意 UX persona）触发词均正交，**保留**。

### ⑥ 看门语义补丁

`check_skill_drift.py` 无白名单机制，路由化后 7 个有上游同名者会被永久报告为「上游大幅改写」。已逐项核对上游最后提交（obra/superpowers 四项 07-24/08-12、hermes-agent 三项 07-24/08-30，均早于基线），确认为路由化人为差值，已在 `capability-inventory.json` → `notWatched` 首条写入「路由化冻结」声明：禁止用上游覆盖路由主文档，跟进上游增量时只并入 `references/`。

## 后续待办（本轮未做）

- ~~**P1 合并**~~（已判定：保持现状，见⑤） / ~~**P2 删除**~~（已否决） / ~~**P0 剩余**~~（已清零，见④）。
- 新事项：上游若对 7 个已路由技能有实质更新，需人工把增量并入 `references/`（看门误报已屏蔽语义，需主动 `gh api .../commits?path=` 抽查）。

## 复用要点

- 拆 skill 的机械流程：提取正文 H2 分节 → 按主题写入 `references/*.md` → 主文档重写为「frontmatter + 路由表 + 5 条 always-on 不变式」。主文档目标 <2.5k 字符。
- 拆完必跑 `python scripts/check_skill_drift.py`，确认本地增强（中文 description）仍被识别为"禁止被上游覆盖"。
- 改完技能**必须同轮**更新 `capability-inventory.json` + `skills-provenance.json` 并推 main，否则看门狗会误报。
