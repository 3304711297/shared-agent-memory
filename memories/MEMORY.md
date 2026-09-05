Hermes 主力模型 gemini-3.8-flash，经 EasyCLIProxyAPI（D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64，网关 18080，provider=cpa-gui）桥接 Antigravity；vision 辅助=cpa-gui+gemini-3.8-flash。
§
WorkBuddy 经本地 codebuddy2openai 反代（已迁移至桌面 C:\Users\VOS-User\Desktop\codebuddy2openai，fork=3304711297/codebuddy2openai，Release 桌面快捷方式 CodeBuddy2OpenAI.lnk）暴露 OpenAI 兼容端点 http://127.0.0.1:8787/v1。Tauri v2 客户端已对标 EasyCLIProxyAPI 重构闭环：支持全量 28 官方模型矩阵、纯净倍率（去除 credits）、自定义上下文上限、思考强度调节/关闭、多账号切换管理、内嵌积分看板与实时 Debug 日志（UTF-8 容错、无黑框后台静默）；右键托盘对标 GUI.for.Cores 风格（内核状态/启停/重启/退出并双向事件广播）；Hermes/ZCode 配置一键写入（兼容驼峰与下划线）。旧批处理与 vbs 已删。venv=C:\Users\VOS-User\.workbuddy\binaries\python\envs\default。
§
Windows 运行环境：本地代理 127.0.0.1:3067；GitHub CLI 账号 3304711297；浏览器接管 Edge Dev + chrome-devtools MCP；4 大插件（context7/desktop-commander/serena/superpowers）有 Windows 定制，upstream-watch 巡检严禁全量覆盖。ysk 四篇双端协同专题已落库（09-06，0e1378b，CI 33978995549 全绿），详见共享记忆库 cross-agent-handshake-mechanism.md（1560d9f）。
§
ScriptCat Edge154 全脚本失效已修复闭环（SW 内 registerContentScripts 补注册），复发用 hermes/scripts/cdp_live.py；issue scriptscat/scriptcat#1724。
§
Hermes 配额监控内置化（09-05）：token-stats 插件（Pulse 导航、/quota 看板、WorkBuddy 8787 探测）；zcode-theme+14 暗黑主题。WorkBuddy 积分链路 09-06 闭环：converter.py 加 /api/usage_summary（5b4381c）→插件对接（cd652b7）双端验证通过；另打通 ZCode SQLite 实时毫秒级进度、CoT 与子代理状态监听。
§
Telegram 频道 @emoegg（蛋总的圈）已绑定专属管理员机器人 @HermesAgentByjieBot（ID: 8361539844），本地凭据见 auth/telegram_channel.json，通过 scripts/tg_channel.py 经 127.0.0.1:3067 代理实现发帖、改帖与管理。
§
子代理模型路由（09-05 用户拍板）：delegate_task 默认继承聊天模型；用户会随机变换聊天模型与子代理模型组合，通常会主动告知子代理模型，未告知=子代理与聊天模型同模型；严禁固定 delegation.provider/model（已从 config.yaml 撤回固定项）；单任务定制走 kanban per-task override；改 config.yaml 用 python yaml。
§
ZCode 跨端测试规范（09-05 用户拍板）：严禁用 zcode.cjs headless CLI 代开测试会话——①会话落 proj_d-ai-coding，GUI 主区是 -.zcode-workspace-default，用户看不见；②CLI 与 GUI 模型体系分离，CLI 只认 cli/config.json；③跨端验证由用户在 GUI 手动建会话，Hermes 只做 db.sqlite 只读监听与验收；④CLI 撞 429 时不得擅自改 ZCode 配置。
§
Hermes 桌面 token 双口径：会话列表数字=该会话累计消耗（input+output 按轮累加，缓存读不计入）；状态栏 xk/1M=当前上下文占用（下一轮 prompt，压缩阈值看它）。多轮后左侧必然≥状态栏，100k vs 38k 属正常。