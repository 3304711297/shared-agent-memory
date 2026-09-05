User communicates in Chinese; reply in Chinese by default.
§
用户主用 Hermes Agent 作为日常主力 AI 编码与操作系统助手（ZCode 处于备用/不常用状态）；记忆库 shared-agent-memory（GitHub 仓库 3304711297/shared-agent-memory）自 2026-09-05 起为三分支架构：默认主分支 main=双端共享记忆库唯一真源（本 Agent 的 memories/topics 是指向它的 junction，读写字同一份），zcode/hermes 分支各放 Agent 专属内容。
§
用户铁律：记忆库 shared-agent-memory（GitHub 仓库 3304711297/shared-agent-memory）main 分支=共享真源；后续任何共享记忆变动（topics/ 下新增、修改）必须在当轮结束前自动静默提交并推送到 GitHub main 分支，Hermes 专属内容（USER.md/根 MEMORY.md 等）推 hermes 分支，严禁遗漏或等待用户提醒。优先使用技能/插件提升执行效率。
§
用户偏好：对于上游同步看门（upstream-watch）及常规评估类 GitHub Issue，完成比对评估无须代码改动或移植后，可直接自动在 GitHub 上留言并关闭 Issue，无需每次额外询问确认。
§
用户偏好：关于 Skills 安装与管理，优先通过 Hermes 官方技能机制（桌面侧边栏一键点击安装或 `hermes skills install`），严禁擅自用 pip/npm 替代原生技能安装。筛选技能时偏好 100% 免费开源、无付费 API/订阅且无功能冲突的上位技能；语音转录场景（Whisper）明确偏好使用 small 模型。处理复杂任务优先调用技能与专业 MCP 工具。
§
持有 Google 个人 Pro 订阅（非企业/开发者付费 AI Studio）；偏好高响应速度模型，主力模型使用本地 EasyCLIProxyAPI 桥接的 Gemini 3.8 Flash（Ultra 思考模式）。
§
用户偏好：高度认可并要求在面对复杂或特定领域任务时，严格优先通过相关 Skills（如 superpowers 流程规范、领域专业技能）引导思考和执行全过程。
§
用户铁律：面对不确定的技术细节、版本状态、命令参数或未完全验证的信息，必须严格优先联网检索（web_search/web_extract/API/官方文档）核实确凿事实，严禁主观凭空臆测或输出未经实证的内容。
§
用户高度注重界面/状态栏的审美排版与微交互体验：严禁简陋文本折行与单调着色，要求键值分层、核心数值等宽加粗高亮；交互操作必须具备加载动效、完成提示与数据变动即时反馈。
§
用户铁律：代码/文档提交或推送到 GitHub 后，必须主动跟踪监控并确认 GitHub Actions CI 全绿（通过）后方可结束对话，严禁未等 CI 结果就提前收尾。
§
- 用户强偏好桌面工具与代理控制台采用完全内嵌化的交互设计：严禁后台启动反代时弹出外部黑色 CMD 终端窗口（必须默认静默无黑框）；所有 Debug 信息、运行输出与错误日志必须直接内嵌在控制台应用界面的「实时日志」页面中查看。
- 偏好系统托盘采用轻量无图标、分组分割线的现代内核管理风格（对标 GUI.for.Cores / sing-box）；大模型倍率展示严格去除无意义英文单位（如 credits），保持纯净数值倍率。
- 用户个人 Telegram 频道：拥有并运营 Telegram 频道 @emoegg（https://t.me/emoegg，Web 预览 https://t.me/s/emoegg，频道现用名「蛋总的圈」，曾用名「某不知名杂货铺」），专注于网络代理协议解析、延迟/RTT 测评、TUN 协议栈、GFW/地方防火墙机制研究及实用软件定制资源。已绑定专属管理机器人 @HermesAgentByjieBot（ID: 8361539844，具备发布、编辑、删除与置顶等完整管理员权限，配置位于 %LOCALAPPDATA%\hermes\auth\telegram_channel.json，专用脚本为 scripts/tg_channel.py）。
§
用户工作偏好：全面优先使用并发进行工作以最大化效率；多任务/多仓库/大批量检查修复场景优先调度并行子代理（当前 Hermes + Gemini 实测单批最高支持 10 并发，日常推荐 3~6 个一批并行推进，彻底解除旧 2 并发限制）。