---
name: hermes-bots-mode-team-practice
description: Hermes Desktop Bot Mode 实践落地——channel-ops、devops、researcher 三专业智能体构建、专属 SOUL.md 人设与共享记忆库无缝链接
metadata:
  type: project
---

# Hermes Desktop Bot Mode 团队实践落地（2026-09-06）

## 一、 实践背景与目标
- 用户在 Hermes Desktop 启用官方 `Hermes Bots` 插件（Bot Mode）；
- 将通用单一环境按核心业务拆分为三个专有 Bot（Profile），降低上下文杂质与提示词稀释，实现多 Agent 模块化协同。

## 二、 三大专业 Bot 架构清单

| Bot 标识 (Profile) | 核心定位与职责 | 关键纪律与约束 | 协同角色 (Handoffs) |
| :--- | :--- | :--- | :--- |
| **`channel-ops`** | Telegram 频道 `@emoegg`（蛋总的圈）运维 | 严格走 `127.0.0.1:3067` 代理与 `tg_channel.py` 脚本；纯暗黑等宽加粗排版风格；保护密钥凭据 | 接收 researcher 调研结论与 devops 发版简报，转为频道速递 |
| **`devops`** | 五大开源项目看门与 GitHub Actions CI 闭环 | **CI 全绿方能收尾（铁律）**；TDD 测试驱动实证；常规提交中文规范；tag-only 自动发版 | 项目发版后交接 channel-ops；架构选型向 researcher 咨询 |
| **`researcher`** | 技术前沿调研与严谨事实核查 (Fact-checking) | **零幻觉与联网真源（铁律）**；三级核查（Confirmed / Unverified / Contradicted）；严谨出处引用 | 向 channel-ops 输出干货速报；向 devops 提供依赖安全性与兼容性评估 |

## 三、 底层工程实现与记忆共享保证
1. **Profile 自动化创建**：
   - 经 `hermes profile create --clone-from default <name> --description "..."` 快速构建；
   - 继承默认环境变量、API 密钥与网关配置（`gemini-3.8-flash` / 18080 与 8787 反代）。
2. **共享记忆物理真源贯通**：
   - 针对各 Profile 隔离目录（`AppData\Local\hermes\profiles\<name>\memories\topics`），全部建立 NTFS Junction 软链接，直通 `C:\Users\VOS-User\.zcode\cli\memories\projects\default-135ef1b9f66d8a7e\memory\`；
   - 确保三个 Bot 与 default 共享同一份知识库与项目记录，同时各自保持独立的会话上下文。
3. **专属 SOUL.md 落地**：
   - 编写结构化人设与交付契约（Identity, Mandates & Rules, Cross-Bot Collaboration & Handoffs, Shared Memory Protocol）。

**Why:** 将用户的三大核心使用场景具象化为专职智能体，实现提示词隔离、精简工具集与结构化协同。
**How to apply:** 在 Hermes Desktop 侧边栏的 Bots 面板中直接选择对应 Bot 开展专项工作，或通过 `@channel-ops`、`@devops`、`@researcher` 实现跨智能体协作。
