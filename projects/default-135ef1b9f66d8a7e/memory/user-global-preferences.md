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
- **UI/状态栏审美**：高度注重界面与微交互体验——严禁简陋文本折行与单调着色；要求键值分层、核心数值等宽加粗高亮；交互必须具备加载动效、完成提示与数据变动即时反馈。
- **桌面工具内嵌化强偏好**：桌面工具与代理控制台采用完全内嵌交互——严禁后台启动反代时弹出外部黑色 CMD 终端窗口（必须默认静默无黑框）；所有 Debug 信息、运行输出与错误日志直接内嵌在控制台「实时日志」页面查看。
- 托盘偏好：系统托盘采用轻量无图标、分组分割线的现代内核管理风格（对标 GUI.for.Cores / sing-box）；倍率展示去除无意义英文单位（如 credits），保持纯净数值。
