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
本地模型使用偏好：对话模型由用户随时按需切换，严禁在设定中固定死主力对话模型；Hermes 客户端「已安装 llama.cpp 运行时」开关必须显式保持关闭（local_runtime.enabled: false），严禁常驻吃 3GB+ 内存；模型与运行时存 D 盘；记忆向量（BGE-M3）仅由 2 分钟空闲自动休眠网关按需拉起。
§
Hermes 配置自同步铁律（2026-09-06）：用户通知改动设置时，模型须自行读取 C:\Users\VOS-User\AppData\Local\hermes\config.yaml 识别最新配置，附带当前 Hermes 构建版本与 Git Commit SHA 指纹，脱敏后自动更新共享记忆库 hermes-config-baseline-and-sync-protocol.md 与 hermes-config.yaml 并推 main。