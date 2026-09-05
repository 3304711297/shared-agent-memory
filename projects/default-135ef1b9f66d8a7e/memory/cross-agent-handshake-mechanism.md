---
name: cross-agent-handshake-mechanism
description: Hermes×ZCode 双端互等握手机制全量方案——Hermes 等待用 watch_zcode.py+进程退出事件自动唤醒，ZCode 等待用握手文件+回合内轮询，含时序陷阱与 CLI/GUI 会话体系辨析
metadata:
  node_type: memory
  type: project
  originSessionId: sess_c9f48820-9daf-4a39-9173-ecedab6369dc
---

# Hermes×ZCode 双端互等握手机制（2026-09-06 全链路实测闭环）

## 一、Hermes 等 ZCode（✅ 已验证，标准主链路）
- 监听层：只读打开 ZCode SQLite（`sqlite3.connect(r'file:C:\Users\VOS-User\.zcode\cli\db\db.sqlite?mode=ro', uri=True)`），严禁写入（database is locked 死锁）；session 表按 `task_type != 'subagent_child'` 过滤主会话，`time_updated` 距今秒数判活跃。
- 守护层：`python C:/Users/VOS-User/AppData/Local/hermes/scripts/watch_zcode.py --timeout <秒>`（118 行，3s 轮询，15 秒滑动窗口判 settled，忽略历史遗留 step-start 子代理防假阳性）；输出 `ZCode session <id> has settled!` 且 exit 0=完工。
- 唤醒层：`terminal(background=True, notify=true)` 启动守护 → 进程退出触发 Hermes 内部 Process Exit Event（应用内事件总线，不受 Windows 系统通知开关影响）自动唤醒主对话，随即自主接手。
- 实测时间线：T+0 派 ZCode 任务 → T+2s 挂守护 → 聊天框休眠 → ZCode exit 0 → watcher settled 退出 → Hermes 自动唤醒执行接手验证，全程零用户输入。

## 二、ZCode 等 Hermes（机制成立，端到端待 GUI 实测）
- ZCode 无内置 background/notify/watch 钩子（zcode --help 全量参数核验）。
- 等价模式：ZCode 在 Bash 工具内跑前台轮询脚本（每秒检查 `%TEMP%\hermes_handshake.txt`），Hermes 完工后写入该文件 → ZCode 同回合继续执行接手任务。
- 文件机制已实测（HANDSHAKE-RECEIVED after 0.0s）；注意握手文件用 Windows 原生路径（%TEMP%），git-bash /tmp 与 Python 路径映射不一致会 TIMEOUT。

## 三、时序铁律（实测教训）
"开始盯"必须在 ZCode 施工中**单独**发出；若与"zcode已完成"合并同条消息到达，监听窗口被跳过、无守护可唤醒（实测错过 370 秒，只能事后手动验收）。

## 四、headless CLI 与 GUI 会话体系辨析（严禁混用）
- 落点：`zcode.cjs -p --cwd "D:/ai coding"` → project_id=`proj_d-ai-coding`；GUI 主区目录 `D:\ai coding\.zcode\workspace\default` → `proj_d-ai-coding-.zcode-workspace-default`；GUI 任务列表只显示后者，headless 会话全部"隐身"。
- 模型体系：CLI 只认 `.zcode/cli/config.json`（providers 仅 cpa-gui→18080）；GUI 走 v2/setting.json 与 provider family OAuth；两套模型选择与额度池互不相通。
- 故障链：18080 网关未启动 → CLI 报 ECONNREFUSED（重启 EasyCLIProxyAPI 即愈）；Gemini 配额触顶 → CLI 全挂 RESOURCE_EXHAUSTED。
- **用户拍板（09-06）**：严禁 headless CLI 代开测试会话；跨端验证由用户在 GUI 手动建会话，Hermes 只做 db.sqlite 只读监听与验收；CLI 撞 429 不得擅自改 ZCode 配置（Desktop 自定义供应商只认 UI 内添加）。

**How to apply:** 用户令"等 ZCode 跑完接手"→ 立即 `terminal(background=True, notify=true)` 挂 watch_zcode.py → 休眠 → 被唤醒后先审 ZCode 产出再接手；反向等待走握手文件模式；任何跨端测试前先确认会话落点与模型体系归属。
