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

## 后续待办（本轮未做）

- **P1 合并**：生图/生视频 7→1、ponytail 家族 6→1（主文档改路由表）、代码审查类 4→2。
- **P2 删除**：`systematic-debugging` / `test-driven-development` / `diagnosing-probe-false-failures` 对"跑测试/自查"的强调重复（官方第 4 条：旧刹车）。
- **P0 剩余**：`computer-use`(15.8k)、`rest-graphql-debug`(15.6k)、`simplify-code`(14.7k)、`hermes-agent-skill-authoring`(14.6k)、`python-debugpy`(13.4k) 等 23 个无 refs 的 >6k 巨石，按同一模板拆。

## 复用要点

- 拆 skill 的机械流程：提取正文 H2 分节 → 按主题写入 `references/*.md` → 主文档重写为「frontmatter + 路由表 + 5 条 always-on 不变式」。主文档目标 <2.5k 字符。
- 拆完必跑 `python scripts/check_skill_drift.py`，确认本地增强（中文 description）仍被识别为"禁止被上游覆盖"。
- 改完技能**必须同轮**更新 `capability-inventory.json` + `skills-provenance.json` 并推 main，否则看门狗会误报。
