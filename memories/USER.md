User communicates in Chinese; reply in Chinese by default.
§
用户主用 Hermes Agent 作为日常主力 AI 编码与操作系统助手（ZCode 处于备用/不常用状态）；记忆库 shared-agent-memory（GitHub 仓库 3304711297/shared-agent-memory）默认主分支为 hermes，变动自动静默推送到 GitHub hermes 分支。
§
用户铁律：记忆库 shared-agent-memory（GitHub 仓库 3304711297/shared-agent-memory）默认主分支为 hermes；后续任何记忆变动（新增、修改）必须在当轮结束前自动静默提交并推送到 GitHub（hermes 分支），严禁遗漏或等待用户提醒。优先使用技能/插件提升执行效率。
§
用户偏好：对于上游同步看门（upstream-watch）及常规评估类 GitHub Issue，完成比对评估无须代码改动或移植后，可直接自动在 GitHub 上留言并关闭 Issue，无需每次额外询问确认。
§
用户偏好：关于 Skills 安装与管理，优先通过 Hermes 官方技能机制（桌面侧边栏一键点击安装或 `hermes skills install`），严禁擅自用 pip/npm 替代原生技能安装。筛选技能时偏好 100% 免费开源、无付费 API/订阅且无功能冲突的上位技能；语音转录场景（Whisper）明确偏好使用 small 模型。处理复杂任务优先调用技能与专业 MCP 工具。
§
持有 Google 个人 Pro 订阅（非企业/开发者付费 AI Studio）；偏好高响应速度模型，主力模型使用本地 ZCode Antigravity 桥接的 Gemini 3.7 Flash（Ultra 思考模式）。
§
用户偏好：高度认可并要求在面对复杂或特定领域任务时，严格优先通过相关 Skills（如 superpowers 流程规范、领域专业技能）引导思考和执行全过程。
§
用户铁律：面对不确定的技术细节、版本状态、命令参数或未完全验证的信息，必须严格优先联网检索（web_search/web_extract/API/官方文档）核实确凿事实，严禁主观凭空臆测或输出未经实证的内容。