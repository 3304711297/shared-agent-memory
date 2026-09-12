# README 批量治理与技能描述全库改造（2026-09-12）

## 一、11 仓库 README 批量治理
- 范围：GitRepos 全部 10 仓 + openviking-backup，修事实错误 + 补标准模块（结构树/FAQ/恢复步骤），全部推送且 CI 绿。
- 修掉的硬伤：tweakbyjie 架构树 3 个不存在文件（Core/EfiLock/Vbs.ps1 → 实为 Registry.ps1 与 Virtualization.ps1）；ysk 覆盖口径 44→48 项；workbuddy2api「P1 储备」实已交付；shared-agent-memory 定位改 Hermes 单一真源；steamdb/mbt 徽章写死版本或指向不触发的工作流。
- 方法论已沉淀 readme-master 技能（审计驱动 + 一仓一子代理 + 独立验收 + 并发写手排查）。commits：profile 8542111 / hf e1e185d / mbt 7e9ff99 / or 60bf53a / sdb 7194b03 / ysk 0bbbfdd+5dd083e / sess 5ccea54 / tweak 5fce57f / w2a d1d2c65 / mem d76622b / ovb 4086b90。

## 二、93 技能描述全库中文触发词前置改造
- 根因（源码级）：agent/skill_utils.py `SKILL_PROMPT_DESC_LIMIT = 60`，超长描述截为「前 57 字+...」入系统提示词；33 个零调用技能多为英文长描述触发条件不可见。
- 改造：93/93 统一「中文高频触发词前置（前 35 字符内）+ 英文原文补充」；端到端用 Hermes 自带解释器跑 extract_skill_description() 验证；仅改 frontmatter description，正文零改动。
- 交付：Hermes home `59ebdab`（hermes 分支）；provenance 86→93 补登 7 个 webui/hub 技能（`c9abd45`，CI 绿）；漂移检查确认 14 个 superpowers 全部判「本地中文触发词定制禁上游覆盖」。
- 运维要点：改技能后须重命名 `.skills_prompt_snapshot.json` 快照缓存，新会话生效；机制详情见 OpenViking「Hermes 技能描述截断机制与全库改造记录」。

## 教训
- 批量改 frontmatter 的脚本必须按 `\n---\n` 定界切分并原样保留其余字节（首版把 `---` 与 `name:` 粘连，靠严格验证层当场抓住，从备份还原重做）。
- 多会话并发期：本会话与用户另一会话（20260911_205620_219d54）同时写 youshouldknow/shared-agent-memory，靠 reflog 时间线区分归属，零冲突收场。
