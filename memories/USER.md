中文交流，默认中文回复；主力 Hermes（ZCode 备用）；共享库 shared-agent-memory（3304711297/shared-agent-memory）main=双端共享真源（topics 挂 junction 直通），变动当轮必自动推 main，Hermes 专属推 hermes 分支；复杂任务严格优先 Skills（superpowers 等）+专业 MCP 引导。
§
持 Google 个人 Pro 订阅；EasyCLIProxyAPI 与 WorkBuddy 双网关切模型；Exa 独享检索；Skills 官方机制且开源免费优先；Whisper 偏好 small；watch Issue 无需改动直接关。
§
铁律：技术细节不确定必严格优先联网实证（官方文档/知识库），严禁臆测；代码/文档推 GitHub 后必盯 Actions CI 全绿方能收尾，严禁未等 CI 提前结束。
§
跨 Agent 接手铁律：等 ZCode/外部长跑任务完成必须 terminal 后台跑 watch_zcode.py(notify=True) 监听，严禁口头承诺后休眠；用进程退出信号唤醒并派并发子代理接手。
§
UI：重微交互、桌面工具内嵌化（无黑框）、托盘 GUI.for.Cores 风格、纯暗黑极客 IDE 美学（深炭底/细描边/琥珀金），已配 zcode-theme。
§
并发优先最大化效率：多任务/多仓库/批量检查优先并行子代理（单批上限 10 并发，日常 3~6/批）；WorkBuddy 思考型模型测试需给足 max_tokens 或读 reasoning 字段；用户正在构建时严禁修改工作区源文件。
§
本地模型：对话模型随时切换不固定；llama.cpp 运行时保持关闭（local_runtime.enabled: false）。
§
工具调用效率规范（2026-09-06 用户纠偏）：读文件用 read_file、小改用 patch（严禁 python 全量重写导致格式重排）、搜索用 search_files（ripgrep）、看目录用 search_files files 模式；python 仅留给真需逻辑的批量任务（进程树审计、跨库合并、签名算法、SQLite 分析），严禁把 python -c 当读改文件的默认手段。
§
Hermes 配置自同步铁律（2026-09-06）：用户通知改设置时，主动读取 config.yaml 识别最新配置附带 Git SHA 指纹，脱敏后自动更新共享记忆库 hermes-config-baseline-and-sync-protocol.md 与 hermes-config.yaml 并推 main。改 config.yaml 须用 python ruamel.yaml。
§
会话归档与清理闭环铁律（2026-09-06 用户拍板）：日常普通会话模式；若用户要求删除/归档当前会话或累计 ≥1M tokens，必须严格执行三步收尾闭环 SOP——① 提炼记忆上传 shared-agent-memory 共享库；ysk 内容严禁擅自写入，必先列出包含理由的候选清单供用户勾选拍板；② 彻底物理清理本会话全部无用临时文件（测试脚本/探针/日志）；③ 自动提交推送并盯 Actions CI 全绿收尾。
§
技能与资源偏好（2026-09-07）：裁撤技能物理删除不留本地残余；视 Edge Dev 9k+ 个人书签为核心资源库，找工具/推荐优先本地检索（search_bookmarks/OpenViking）；能力看门狗严格去重防重复 Issue，非 GitHub 爬虫异常优雅降级不误报。