---
name: user-global-preferences
description: 用户全局铁律与偏好合集（自 Hermes USER.md 沉淀，2026-09-05 同步）：CI 跟踪、联网核实、技能优先、UI 审美、内嵌日志等
metadata:
  node_type: memory
  type: user
  originSessionId: sess_888b469b-882a-4e84-aeed-8d68b401a67c
---

用户全局偏好与铁律（原记录于 Hermes 端 USER.md，2026-09-05 经 [[hermes-to-zcode-capability-sync]] 沉淀到本共享库，两端通用）：

- 交流语言：中文为主，默认中文回复。
- **CI 全绿铁律**：代码/文档提交或推送到 GitHub 后，必须主动跟踪监控 GitHub Actions CI 至全绿（通过）后方可结束对话，严禁未等 CI 结果就提前收尾。
- **联网核实铁律**：面对不确定的技术细节、版本状态、命令参数或未完全验证的信息，必须严格优先联网检索（web_search/web_extract/API/官方文档）核实确凿事实，严禁主观臆测或输出未经实证的内容。
- **技能优先**：复杂或特定领域任务严格优先通过相关 Skills（如 [[superpowers-usage]] 流程规范、领域专业技能）引导思考和执行全过程；处理复杂任务优先调用技能与专业 MCP 工具。
- Skills 筛选偏好：偏好 100% 免费开源、无付费 API/订阅且无功能冲突的上位技能；语音转录（Whisper）明确偏好 small 模型（见 [[bilibili-video-transcription-pipeline]]）；技能安装走各 Agent 官方技能机制，严禁擅自用 pip/npm 替代原生安装。
- 上游同步看门（upstream-watch）及常规评估类 GitHub Issue：完成比对评估无须代码改动或移植后，可直接自动在 GitHub 上留言并关闭 Issue，无需每次询问确认。
- **组件更新不留本地旧版残留**（2026-09-05 明确）：升级软件/核心后无需保留旧版本备份（.bak/旧安装包），有问题直接从 GitHub Releases 重装旧版本即可；安装目录保持干净。
- 订阅与模型偏好：持有 Google 个人 Pro 订阅（非企业/开发者付费 AI Studio）；偏好高响应速度模型，主力模型走本地 EasyCLIProxyAPI 桥接的 Gemini 3.8 Flash（Ultra 思考模式），见 [[user-windows-environment]]。
- **UI/状态栏审美**：高度注重界面与微交互体验——严禁简陋文本折行与单调着色；要求键值分层、核心数值等宽加粗高亮；交互必须具备加载动效、完成提示与数据变动即时反馈；桌面端偏好沉浸式 ZCode 风格暗黑 IDE 美学（哑光深炭底色、细微描边、悬浮底栏与琥珀金点缀，已通过 desktop-plugins/zcode-theme 原生闭环）。
- **桌面工具内嵌化强偏好**：桌面工具与代理控制台采用完全内嵌交互——严禁后台启动反代时弹出外部黑色 CMD 终端窗口（必须默认静默无黑框）；所有 Debug 信息、运行输出与错误日志直接内嵌在控制台「实时日志」页面查看。
- 托盘偏好：系统托盘采用轻量无图标、分组分割线的现代内核管理风格（对标 GUI.for.Cores / sing-box）；倍率展示去除无意义英文单位（如 credits），保持纯净数值。
- **跨 Agent 协同自驱接手铁律（2026-09-05 确立）**：当需要等待 ZCode、外部长跑构建或长时间测试完成并自动接手时，**严禁口头承诺后休眠等待用户提醒**，也严禁在前台死循环阻塞会话；必须使用 `terminal(command="python C:/Users/VOS-User/AppData/Local/hermes/scripts/watch_zcode.py", background=True, notify=True)` 在后台挂起轻量守护监听脚本，退出时由 Hermes 内部进程退出信号（Process Exit Event，纯应用内事件总线，完全独立于且不受 Windows 系统通知关闭影响）自动唤醒，无缝派发多子代理接手审查推进。
- **用户个人 Telegram 频道**：拥有并运营 `@emoegg`（https://t.me/emoegg，Web 预览 https://t.me/s/emoegg，频道现用名「蛋总的圈」，曾用名「某不知名杂货铺」），专注于网络代理协议解析（SS/Trojan/VLESS等）、延迟与 RTT 深度测评、TUN 协议栈对比、GFW 与地方防火墙机制研究及实用软件/音乐定制资源。已绑定专属管理机器人 `@HermesAgentByjieBot`（ID: 8361539844，具发布/编辑/删除/置顶全套管理员权限，凭据位于 `%LOCALAPPDATA%\hermes\auth\telegram_channel.json`，CLI 脚本位于 `scripts/tg_channel.py`）。

2026-09-05 用户澄清与实测：**多仓库/多任务场景优先用并行子代理省时间**。此前「实测并发上限≈2」系 ZCode 端体验套餐 GLM-5.3-flash 模型所致；**当前 Hermes 端（Gemini 3.8 Flash + EasyCLIProxyAPI 网关）实测：**
- **模型端点并发能力**：实测并发 2、4、6、8、10、12、16、20 均 100% 成功且零 429 报错，10 以内单次延迟 1.5~2.5s；
- **子代理并发限制**：Hermes 框架 `delegation.max_concurrent_children` 默认上限为 10；实测单批并行 10 个子代理（N=10）全部同时启动并于 5 秒内全绿交付；提交 11 个会受安全门拦截；
- **排队与调度策略**：日常复杂多任务建议按 3~6 个一批并行派发（兼顾性能与调度），单批最大支持 10 个，彻底解除了旧 2 并发的限制；gh 已于 09-05 授权 delete_repo scope（可直接 gh repo delete）。

2026-09-05 教训沉淀：**用户正在执行构建（npm run tauri build/cargo build 等）时严禁改动项目工作区源文件**——增量编译可能被文件变动干扰或产生文件锁冲突；曾中途编辑 lib.rs 被用户叫停"先别修复，我还在 build 中"，需 git checkout 回滚、待用户明确"build 好了"再重新应用。同理，对用户正在操作的项目做任何修改前先确认其本地进程状态。
