Hermes 主力模型 gemini-3.8-flash，经 EasyCLIProxyAPI（D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64，网关 18080，provider=cpa-gui）桥接 Antigravity；vision 辅助=cpa-gui+gemini-3.8-flash。
§
WorkBuddy 经本地 codebuddy2openai 反代（已迁移至桌面 C:\Users\VOS-User\Desktop\codebuddy2openai，fork=3304711297/codebuddy2openai，Release 桌面快捷方式 CodeBuddy2OpenAI.lnk）暴露 OpenAI 兼容端点 http://127.0.0.1:8787/v1。Tauri v2 客户端已对标 EasyCLIProxyAPI 重构闭环：支持全量 28 官方模型矩阵、纯净倍率（去除 credits）、自定义上下文上限、思考强度调节/关闭、多账号切换管理、内嵌积分看板与实时 Debug 日志（UTF-8 容错、无黑框后台静默）；右键托盘对标 GUI.for.Cores 风格（内核状态/启停/重启/退出并双向事件广播）；Hermes/ZCode 配置一键写入（兼容驼峰与下划线）。旧批处理与 vbs 已删。venv=C:\Users\VOS-User\.workbuddy\binaries\python\envs\default。
§
Windows 运行环境：本地代理 127.0.0.1:3067；GitHub CLI 账号 3304711297；浏览器接管 Edge Dev + chrome-devtools MCP；4 大插件（context7/desktop-commander/serena/superpowers）有 Windows 定制，upstream-watch 巡检严禁全量覆盖。
§
ScriptCat Edge154 若复发：用 scripts/cdp_live.py 排查（scriptscat#1724，registerContentScripts 补注册）。
§
token-stats=用户自建配额插件（Pulse导航、/quota看板、8787积分端点、18080额度）；已集成 /ovlm 提炼动态跟随（真源读 state.db 最新会话写 ov.conf 并踢 1934 懒后端），彻底解决切模型后后台仍慢漏 Gemini 配额。
§
Telegram 频道 @emoegg（蛋总的圈）已绑定专属管理员机器人 @HermesAgentByjieBot（ID: 8361539844），本地凭据见 auth/telegram_channel.json，通过 scripts/tg_channel.py 经 127.0.0.1:3067 代理实现发帖、改帖与管理。
§
子代理路由：delegate_task 默认继承聊天模型；未告知=同聊天模型；严禁固定 delegation.provider/model（已撤回）；单任务定制走 kanban per-task override；改 config.yaml 用 python yaml。
§
ZCode 跨端测试规范（09-05 用户拍板）：严禁用 zcode.cjs headless CLI 代开测试会话——①会话落 proj_d-ai-coding，GUI 主区是 -.zcode-workspace-default，用户看不见；②CLI 与 GUI 模型体系分离，CLI 只认 cli/config.json；③跨端验证由用户在 GUI 手动建会话，Hermes 只做 db.sqlite 只读监听与验收；④CLI 撞 429 时不得擅自改 ZCode 配置。
§
Hermes 桌面 token 双口径：会话列表数字=该会话累计消耗（input+output 按轮累加，缓存读不计入）；状态栏 xk/1M=当前上下文占用（下一轮 prompt，压缩阈值看它）。多轮后左侧必然≥状态栏，100k vs 38k 属正常。
§
Hermes 检索与抽取全量接管为 Exa 独享（EXA_API_KEY 已入库 .env，web.backend/search_backend/extract_backend=exa，避开公共免密限流）；EasyCLIProxyAPI(18080) 的 gemini-web-search 仅为 gemini-3.1-flash-lite 别名无实时搜索（无 Grounding 工具），不可作搜索源；已卸载冗余社区技能 duckduckgo-search 与 searxng-search。
§
本机硬件：RTX 4070 Laptop (8GB 显存) + 24GB 内存；C 盘空间紧张 (~50GB)，Hermes 本地模型与运行时已建立 NTFS Junction 映射至 D 盘（models -> D:\HermesModels，runtimes -> D:\HermesRuntimes）；OpenViking 独立虚拟环境位于 C:\Users\VOS-User\.openviking\venv。
§
OpenViking 智能记忆检索已全面闭环（09-06）：物理真源 shared-agent-memory (main) 唯一；D:\HermesModels 挂载本地 BGE-M3 + 动态跟随 VLM 提炼；已依用户要求移除开机自启（Startup/OpenVikingGateway.vbs 已撤），改为桌面快捷方式/openviking_service.py 按需启停；1933 懒网关与守护严格使用 .openviking\venv 独立环境防锁更新，2分钟闲置休眠；配套 cleanup_agent_orphans.py 治理深层 MCP 孤儿进程。
§
会话习惯：Hermes 会话列表累计 ≥1M 时让 AI 总结记忆后删会话、开新聊。配置改动流程：先列候选+官方默认+代价清单，等用户拍板再动手，严禁擅自改。
§
桌面推理块（09-06 收尾）：show_reasoning 对桌面 write-only（gateway 无条件发 reasoning.delta）；真实桌面开关=外观「默认折叠推理过程」；上游 bug 已在 hermes-agent#49664 留言根因（comment-5557680014），修复 PR #103379 流转中勿再提新 issue；用户已恢复 true。详见 OpenViking 桌面推理块机制考证。