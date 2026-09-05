---
name: skill-plugin-resources
description: 用户书签 skill hub 文件夹的 6 个 Skills/插件资源站与仓库（需要技能/插件时调取下载）
metadata:
  type: reference

用户浏览器书签「skill hub」文件夹（2026-09-05 记入，用户授权后续需要时可调取/下载）：

**市场/目录类**
1. **SkillHub** — https://skillhub.cn/ （腾讯云镜像 https://skillhub.cloud.tencent.com/skills）：专为中国用户优化的 AI Skills 社区，精选 Top 50、宣称经安全审核；国内访问友好，优先从这里找。
2. **Cola Skill** — https://colaskill.com/ ：Claude/Agent skills 策展市场，中文描述+按行业打包（电商/设计/一人公司等），善用"Smart install"按需挑技能；不直接托管代码，安装前看原始仓库。
3. **Hermes Agent Skills Hub** — https://hermes-agent.nousresearch.com/docs/user-guide/features/skills （附技能目录 https://hermes-agent.nousresearch.com/docs/reference/skills-catalog ）：Hermes 官方技能系统与内置目录（装到 ~/.hermes/skills/），给 hermes-agent 装技能走这里。

**GitHub 仓库类（已验证存在，2026-09-05）**
4. **affaan-m/ECC** — https://github.com/affaan-m/ECC ：agent harness 性能优化系统（Skills/instincts/memory/security/研究优先开发），适用 Claude Code/Codex/Opencode/Cursor 等。
5. **google-gemini/gemini-skills** — https://github.com/google-gemini/gemini-skills ：Google 官方，Gemini API/SDK 与模型交互技能。
6. **zai-org/zcode-plugins** — https://github.com/zai-org/zcode-plugins ：ZCode 插件市场官方仓库（内置+社区插件），ZCode 组件升级/排查市场问题时对照它（关联 [[capability-upstream-watch]] 的两层市场架构）。

**How to apply:** 用户要找某类能力（如 PPT/SEO/安全审计技能）或 ZCode/Hermes 缺功能时，先查 1/2 的中文目录定位技能名，再回 GitHub 拿源码审读后安装；Gemini/ZCode 官方需求直接用 5/6。第三方 skill 安装前必须人工审内容（提示词注入面），不盲装。
