中文交流，默认中文回复；主力 Hermes（ZCode 备用）；共享库 shared-agent-memory（3304711297/shared-agent-memory）main=双端共享真源（topics 挂 junction 直通），变动当轮必自动推 main，Hermes 专属推 hermes 分支。
§
Skill-First 反射门禁铁律：凡涉及新功能编写、Bug修复、代码审查/重构、架构方案与复杂多步任务，在执行任何编辑（patch/write）或终端操作前，第 1 动作必须先执行技能匹配自检；只要命中相关技能（如 TDD、systematic-debugging、ponytail、writing-plans 等），必须坚决先调用 skill_view(name) 加载工作流规范，严禁凭大模型裸脑惯性直接写代码；未命中时方可直接操作。
§
持 Google 个人 Pro 订阅；EasyCLIProxyAPI 与 WorkBuddy 双网关切模型；Exa 独享检索；Skills 官方机制且开源免费优先；Whisper 偏好 small；watch Issue 无需改动直接关。
§
铁律：技术细节不确定必严格优先联网实证（官方文档/知识库），严禁臆测；代码/文档推 GitHub 后必盯 Actions CI 全绿方能收尾，严禁未等 CI 提前结束。
§
跨 Agent 接手铁律：等 ZCode/外部长跑任务完成必须 terminal 后台跑 watch_zcode.py(notify=True) 监听，严禁口头承诺后休眠；用进程退出信号唤醒并派并发子代理接手。
§
UI：重微交互、桌面工具内嵌化（无黑框）、托盘 GUI.for.Cores 风格、纯暗黑极客 IDE 美学（深炭底/细描边/琥珀金），已配 zcode-theme。
§
并发优先最大化效率（Fork-First 铁律）：多任务/多仓库/多独立需求（如一边修代码一边巡检上游），首轮动作必须坚决直接派并行子代理（单批 3~6 并发，上限 10），严禁在主会话单线程串行试探；主会话永远保持清爽响应，严禁中间数据与长跑任务（如 CI 轮询）阻塞主聊天。WorkBuddy 思考型模型测试需给足 max_tokens 或读 reasoning 字段；用户正在构建时严禁修改工作区源文件。
§
本地模型：对话模型随时切换不固定；llama.cpp 运行时保持关闭（local_runtime.enabled: false）。
§
工具调用效率规范（2026-09-06 用户纠偏）：读文件用 read_file、小改用 patch（严禁 python 全量重写导致格式重排）、搜索用 search_files（ripgrep）、看目录用 search_files files 模式；python 仅留给真需逻辑的批量任务（进程树审计、跨库合并、签名算法、SQLite 分析），严禁把 python -c 当读改文件的默认手段。
§
Hermes 配置自同步铁律（2026-09-06）：用户通知改设置时，主动读取 config.yaml 识别最新配置附带 Git SHA 指纹，脱敏后自动更新共享记忆库 hermes-config-baseline-and-sync-protocol.md 与 hermes-config.yaml 并推 main。改 config.yaml 须用 python ruamel.yaml。
§
会话归档与清理闭环铁律（2026-09-06 用户拍板）：日常普通会话模式；若用户要求删除/归档当前会话或累计 ≥1M tokens，必须严格执行三步收尾闭环 SOP——① 提炼记忆上传 shared-agent-memory 共享库；ysk 内容严禁擅自写入，必先列出包含理由的候选清单供用户勾选拍板；② 彻底物理清理本会话全部无用临时文件（测试脚本/探针/日志）；③ 自动提交推送并盯 Actions CI 全绿收尾。
§
技能与看门联动铁律（2026-09-07 用户纠偏）：技能变动与看门狗绝对同步——凡新装、升级、裁撤或评估否决，当轮必本能同步 capability-inventory.json（基线/已装数/notWatched 排除）并推 main 跑 CI，严禁改完技能漏看门、严禁等用户提醒补漏；新技能评估严格执行五步 SOP（穿透本质/审计缓存与倒挂/拒常驻 Plugin/优胜劣汰/闭环）；裁撤物理删除不留残余；找工具优先 Edge Dev 9k+ 本地书签。