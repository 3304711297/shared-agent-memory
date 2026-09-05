User communicates in Chinese; reply in Chinese by default.
§
主力为 Hermes Agent（ZCode 备用）；记忆库 shared-agent-memory（3304711297/shared-agent-memory）main 分支为双端共享真源（topics 挂 junction 直通），变动当轮必自动推 main，Hermes 专属推 hermes 分支。复杂任务严格优先由相关 Skills（如 superpowers）及专业 MCP 引导全过程。
§
组件偏好：持 Google 个人 Pro 订阅，主力走本地 EasyCLIProxyAPI 桥接的 Gemini 3.8 Flash（Ultra 思考）；Skills 走官方机制安装、100% 免费开源上位；Whisper 偏好 small；上游 watch 类 Issue 评估无需改动可直接留言关闭。
§
铁律：不确定技术细节必严格优先联网检索（官方文档/知识库）实证事实，严禁凭空臆测；代码/文档推送到 GitHub 后必主动跟踪监控 Actions CI 全绿后方可结束对话，严禁未等 CI 提前收尾。
§
跨 Agent 协同自驱接手铁律（2026-09-05 确立）：当需要等待 ZCode 或外部长跑任务完成并接手时，严禁口头承诺后休眠等待用户提醒，也严禁前台死循环阻塞；必须使用 terminal(command="python C:/Users/VOS-User/AppData/Local/hermes/scripts/watch_zcode.py", background=True, notify=True) 在后台挂起轻量守护监听，退出时由系统事件通知唤醒，自动无缝派发多子代理接手审查与推进。
§
UI与审美偏好：注重微交互，要求键值分层、数值等宽加粗、加载动效与即时反馈；桌面工具完全内嵌化（严禁黑框终端，日志内嵌）；托盘对标 GUI.for.Cores 风格；桌面端偏好纯暗黑极客 IDE 美学（ZCode 哑光深炭底色、细微描边、悬浮圆角底栏、琥珀金点缀，排斥日间浅色，已装配 zcode-theme 及 14 款暗黑主题）。
§
个人 Telegram 频道：运营 @emoegg（蛋总的圈，专注网络代理协议、延迟测评、TUN 与防火墙审查），已绑定专属管理员 Bot @HermesAgentByjieBot 自动化发帖管理；主号因多次风控受限禁言。
§
用户工作偏好：全面优先使用并发进行工作以最大化效率；多任务/多仓库/大批量检查修复场景优先调度并行子代理（当前 Hermes + Gemini 实测单批最高支持 10 并发，日常推荐 3~6 个一批并行推进，彻底解除旧 2 并发限制）。
