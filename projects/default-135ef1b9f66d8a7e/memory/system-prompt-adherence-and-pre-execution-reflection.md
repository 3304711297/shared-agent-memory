---
name: system-prompt-adherence-and-pre-execution-reflection
description: 为什么 AI 会无视 soul.md、前置推理门禁自检机制（Reflection Protocol）与核心提示词/记忆全英文铁律（2026-09-24 治理复盘）
metadata:
  type: feedback
---

# 提示词执行力衰减根因、前置推理反射协议与核心记忆全英文治理

## 背景与问题（Why）

2026-09-24 用户质询：「为什么还是很多时候，AI 并没有按照这个 soul.md 执行？」
在此前的会话中，尽管 `SOUL.md` 明确规定了「技能优先（Skill-First）」、「3步以上必用 todo_list」、「先检索再造轮子」等铁律，Agent 依然高频出现跳过技能直接改代码、用纯文本打列表敷衍、或在终端中违规使用 `cat/find` 的现象。

深入排查后，发现并不仅是「提示词语气不够强」，而是存在深层次的模型认知、提示词语言以及体系架构矛盾。

---

## 核心根因剖析（Root Causes）

1. **软提示词缺乏运行时硬门禁（概率采样 vs 确定性 Hook）**：
   `SOUL.md` 里的「必须第一步」、「严禁」、「铁律」，在自回归 LLM 视角下只是先验偏置，不是操作系统的内核拦截器。当模型拥有直接调用 `read_file`/`patch` 的权限时，在 greedy/temperature 采样下很容易直接出手。
2. **基底对齐惯性（RLHF Inertia）的反向对抗**：
   大模型在预训练与对齐阶段被深度强化为「热情详尽、迅速给出代码、讨好用户」。而 `SOUL.md` 要求「冷淡极简、一句话问题一句话答、先查技能再写代码」，是在处处逆着基底概率分布走。
3. **上下文膨胀与注意力稀释（Attention Dilution）**：
   全量上下文包含 `SOUL.md`、51 个工具定义、上百个技能名称描述、`MEMORY.md`、`USER.md` 与多轮历史，达数万 Token。用户的即时提问引力极强，位于前部的系统规则极易陷入「Lost in the Middle」。
4. **「第一步」规则过多导致的逻辑踩踏（Priority Deadlock）**：
   `SOUL.md` 里同时规定了多个「首要动作」（Skill-First、Todo-First、Fork-First）。当一个复杂多步任务同时触发多条规则时，缺乏强类型的仲裁分支，模型陷入混乱后往往退化回无规则的默认直觉。
5. **双语混杂与中英文注意力损耗**：
   此前 `SOUL.md` 为英文基底但包含中文附录，`USER.md` 和 `MEMORY.md` 半中半英，且带有大量历史编辑截断的破损残句。前沿模型在解析系统级指令时，频繁切换中英上下文会造成 Attention 分散与 Token 成本膨胀。
6. **技能层工具映射反向误导**：
   `skills/superpowers/using-superpowers/references/hermes-tools.md` 中竟然将「按文件名找文件」映射为 `terminal with find`，且使用了虚构的 `delegate_task` 参数，导致模型查阅技能后直接被误导去调用违规命令。

---

## 解决方案与全链路落地（How to apply）

### 1. 结构化前置推理反射协议 (Pre-Execution Reflection Protocol)
在 `SOUL.md` 顶部插入布尔门禁自检，强制要求模型在内部 CoT（Thinking Process）中以结构化清单完成判定：
```markdown
# Pre-Execution Reflection Protocol
Before executing ANY tool call or producing a final response, you MUST complete the following boolean gate checks inside your thinking process. When multiple gates trigger, resolve strictly in this priority order:
1. [Skill Gate | Skill-First]: Code/bug/planning task? -> FIRST action MUST be skill_view(name).
2. [Todo Gate | Todo-First]: >= 3 steps? -> FIRST tool call MUST be todo_list.
3. [Fork Gate | Fork-First]: >= 2 independent asks? -> delegate_task parallel subagents.
4. [Lookup Gate | Lookup-Before-Build]: Hand-rolling parser/glue? -> STOP, search first.
5. [Verification Gate | Verification-Before-Completion]: Claiming completion? -> Present real tool output evidence.
```
**原理**：自回归生成在思考链中写出 `1. [Skill Gate] YES -> invoking skill_view` 后，后续 Attention 被自我生成的 Token 强行锚定，大幅提升真实动作遵循率。

### 2. 核心指令与常驻记忆全英文铁律 (Strict English Invariant)
- **铁律**：`SOUL.md`、`memories/USER.md` 与根 `memories/MEMORY.md` 必须**严格使用纯英文维护**。严禁任何 Agent 擅自使用中文或中英混杂格式写入。
- **收益**：前沿模型对纯英文 Prompt 的指令遵循度最高；字符与 Token 密度提升，大幅节省上下文空间；仅面向用户的最终答复正文使用中文。

### 3. 记忆分层与冗余彻底剥离
- 清理 `USER.md` 历史坏账残句，剔除与 `SOUL.md` 重复的系统条款，专注于用户个人偏好与工作区构建约束；
- 将 `MEMORY.md` 中的工具级源码细节（输出预算、三坑）沉淀至 `hermes-agent` 技能正文，常驻记忆由 88% 顶格降至 55%，消除溢出风险。

### 4. 技能工具映射纠偏
- 修正 `superpowers/using-superpowers/references/hermes-tools.md`：
  - `find files by name` 映射纠偏为 `search_files(pattern="...", target="files")`；
  - `delegate_task` 纠偏为真实 `tasks=[{"goal": "...", "context": "..."}]` 结构；
  - 任务追踪纠偏为 `todo_list`。

### 5. 关键实操纪律固化
- **零调试残留（Zero-Residual）**：收尾前物理删除临时测试脚本与探针，严禁遗留 `.bak`/`.backup`（Git 本身即版本历史）；
- **ysk 门禁**：未经用户明确勾选，严禁擅自向 `youshouldknow` 写入内容；
- **看门 Issue 自动闭环**：确认无须改动时，直接留言评估结论并自动关闭 Issue，无需二次请示用户。
