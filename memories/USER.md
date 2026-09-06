中文交流，默认中文回复。
§
主力 Hermes（ZCode 备用）；共享库 shared-agent-memory（3304711297/shared-agent-memory）main=双端共享真源（topics 挂 junction 直通），变动当轮必自动推 main，Hermes 专属推 hermes 分支；复杂任务严格优先 Skills（superpowers 等）+专业 MCP 引导。
§
持 Google 个人 Pro 订阅；本地具备 EasyCLIProxyAPI 与 WorkBuddy 双网关，聊天与子代理模型根据任务随时动态切换；检索主力走 Exa 独享，排斥需绑定外币信用卡的海外商业服务；Skills 官方机制安装、100% 免费开源上位；Whisper 偏好 small；上游 watch 类 Issue 评估无需改动可直接留言关闭。
§
铁律：技术细节不确定必严格优先联网实证（官方文档/知识库），严禁臆测；代码/文档推 GitHub 后必盯 Actions CI 全绿方能收尾，严禁未等 CI 提前结束。
§
跨 Agent 接手铁律（2026-09-05）：等 ZCode/外部长跑任务完成并接手时，必须 terminal(command="python C:/Users/VOS-User/AppData/Local/hermes/scripts/watch_zcode.py", background=True, notify=True) 挂后台轻量守护监听，严禁口头承诺后休眠等用户提醒、严禁前台死循环阻塞；Hermes 内部进程退出信号（Process Exit Event，应用内事件总线，独立于且不受 Windows 系统通知关闭影响）自动唤醒，无缝派多子代理接手审查推进。
§
UI：重微交互（键值分层、数值等宽加粗、加载动效与即时反馈）；桌面工具内嵌化（严禁黑框终端，日志内嵌）；托盘对标 GUI.for.Cores 风格；纯暗黑极客 IDE 美学（ZCode 哑光深炭底、细微描边、悬浮圆角底栏、琥珀金点缀），排斥日间浅色，已配 zcode-theme+14 款暗黑主题。
§
TG 频道 @emoegg（蛋总的圈：网络代理协议、延迟测评、TUN 与防火墙审查），绑定管理员 Bot @HermesAgentByjieBot 自动化发帖管理；主号多次风控已禁言。
§
并发优先最大化效率；多任务/多仓库/批量检查修复优先并行子代理（Hermes+Gemini 实测单批上限 10 并发，日常 3~6/批，已解除旧 2 并发限制）；2026-09-05 深夜：WorkBuddy glm-5.3-flash 实测（max_tokens≥300、10 并发 6.61s、15 并发 4.07s 全绿）无 429；该模型属思考型，max_tokens<100 思考链吃光配额致 content=null（测试须给足 max_tokens 或读 reasoning 字段）。
§
本地模型与后台偏好：对话模型由用户随时按需切换，严禁在设定中固定死主力对话模型；Hermes 客户端「已安装 llama.cpp 运行时」开关必须显式保持关闭（local_runtime.enabled: false），严禁常驻吃 3GB+ 内存；模型与运行时存 D 盘；OpenViking 记忆服务已依偏好移除开机自启，由 Hermes 插件按需自动唤醒懒网关（2 分钟空闲自动休眠退显存，桌面无冗余快捷方式）；Agent 客户端关闭后由 agent_guard 守护（Startup 自启，.openviking\venv pythonw 驱动）自动清扫 MCP 孤儿进程（Node/Python）并联动停 OpenViking 释放显存。
§
MCP 精简终态（2026-09-06 双端拍板）：Hermes 端 MCP 仅留 chrome-devtools（用户定制：扩展保护参数 + 驱动真实 Edge Dev，原生 browser 不支持 Dev 渠道且 use_real_profile=false，系不可再生能力）与 deepwiki（远端零进程）；context7/serena 双端物理裁撤（Hermes 全程 0 调用、ZCode 仅初始化 8 次），desktop-commander 退出 Hermes 端（原生 terminal/patch/read_file 全覆盖）但 ZCode 端保留（205 次高频调用）；四大 MCP 已配 lazy:true + idle_timeout_seconds:60（不调用零进程，调用冷启 1~2s，闲置 60s 自动回收）。
§
工具调用效率规范（2026-09-06 用户纠偏）：读文件用 read_file、小改用 patch（严禁 python 全量重写导致格式重排）、搜索用 search_files（ripgrep）、看目录用 search_files files 模式；python 仅留给真需逻辑的批量任务（进程树审计、跨库合并、签名算法、SQLite 分析），严禁把 python -c 当读改文件的默认手段。
§
Hermes 配置自同步铁律（2026-09-06）：用户通知改动设置时，模型须自行读取 C:\Users\VOS-User\AppData\Local\hermes\config.yaml 识别最新配置，附带当前 Hermes 构建版本与 Git Commit SHA 指纹，脱敏后自动更新共享记忆库 hermes-config-baseline-and-sync-protocol.md 与 hermes-config.yaml 并推 main。注意：config.yaml 是安全敏感文件，patch/write_file 工具会被拒，须走 python ruamel.yaml（preserve_quotes=True）写入；ZCode 的 config.json 修改后必须 node zcode.cjs plugins list --json 冒烟防 schema 静默丢弃。
§
会话模式习惯（2026-09-06）：日常明确只用普通会话模式（default profile 一体化），不常驻维护多 profile/Bot Mode；工作流集中统一，会话累计 ≥1M tokens 时总结记忆后重建新会话。