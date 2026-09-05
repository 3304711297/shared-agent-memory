---
name: codebuddy2openai-tauri-gui
description: codebuddy2openai 桌面客户端对标 EasyCLIProxyAPI 重构实践与状态
metadata:
  node_type: memory
  type: project
  originSessionId: sess_91c8484d-0d81-48d1-89e3-b7d52ed11653
---

# CodeBuddy2OpenAI 桌面端架构 (对标 EasyCLIProxyAPI)

## 架构对齐与实现成果 (2026-09-04)
1. **项目路径规范**：
   - 遵照用户使用习惯，项目源码已完整从临时路径迁移至桌面：`C:\Users\VOS-User\Desktop\codebuddy2openai\`。
   - 桌面已创建独立 Release 版快捷方式 `CodeBuddy2OpenAI.lnk`（指向 `src-tauri\target\release\codebuddy2openai.exe`）。
   - 原先的批处理窗口与 `start_silent.vbs` 等脚本已彻底删除并下线，完全由桌面 GUI 控制台接管生命周期。
2. **多账号管理体系**：
   - 凭据存储于 `%LOCALAPPDATA%\codebuddy2openai\accounts.json`，独立管理多账号。
   - 提供 `accounts_list`、`accounts_switch`、`accounts_delete`、`accounts_refresh_token` 等完整生命周期命令。
   - 自动与外部 `workbuddy-desktop.info` 联动同步活跃凭据。
3. **内嵌资产与积分看板**：
   - 彻底将积分进度与资源包明细收拢至当前账号卡片内部，彻底消除多账号重叠与视觉污染。
   - 登录 Tab 纯粹专注扫码/手机验证码登录，不混入无关积分卡。
4. **全量 27+ 模型矩阵与深度参数定制**：
   - **云端全量同步**：直连 WorkBuddy 官方后端 `/v2/enterprises/personal/models`，自动拉取包含 `glm-5.3`、`glm-5.3-flash`、`hy4-preview`、`hy3-x`、`kimi-k3-1`、`minimax-m3`、`deepseek-v4-pro` 等全量 28 个可用模型；
   - **干净倍率显式展示**：彻底核实并去除后端历史遗留的冗余 `credits` 英文单词，统一遵循官方前端规范格式化为纯净的等宽倍率徽章（如 `0.06x`、`0.51x`、`1.62x`、`免费 (0.00x)`）；
   - **上下文窗口自由调节**：支持为每个模型单独输入自定义上下文 Token 限制并持久化保存，Python 反代转发时自动做上下文保护截断；
   - **思考强度 (Reasoning Effort) 调节与关闭**：对支持思考的模型提供强度档位切换（如 `low` / `high` / `max` / `xhigh`），并支持「🚫 关闭思考」，无缝注入 `chat_template_kwargs.enable_thinking: false`，彻底还原 WorkBuddy 官方 Agent 体验。
5. **Agent 一键接入参数契约修复**：
   - 修复了 Tauri v2 默认将 `agent_type` 映射为驼峰 `agentType` 导致的命令调用参数丢失报错（双向契约兼容 snake_case 与 camelCase），一键写入与移除现已顺畅执行。
5. **内嵌 Debug 与运行日志查看器**：
   - **完全告别外部黑框**：后端服务标准输出与错误流自动重定向至本地 `%LOCALAPPDATA%\codebuddy2openai\proxy_stdout.log`；
   - **跨编码容错与全链路 UTF-8**：Rust 端读取日志改用 `String::from_utf8_lossy` 容错解码，彻底根治 Windows 默认 GBK 导致的 `stream did not contain valid UTF-8` 报错；同时为 Python 进程注入 `PYTHONIOENCODING=utf-8` 与 `PYTHONUTF8=1` 环境变量，确保日志输出全链路中文原生合规。
   - **左侧独立「实时日志」Tab**：内置深色终端风格的代码阅读器，支持自动追加、手动刷新与清空。
6. **系统托盘与内核右键菜单 (对标 GUI.for.Cores / sing-box 交互风格)**：
   - 托盘右键菜单完全按照网络代理内核标准重构，包含三段式分组：
     1. **打开主界面**
     2. *(横向分割线)*
     3. **内核状态：运行中 / 已停止**（作为只读状态项展示）
     4. **停止内核 / 启动内核**（根据实时内核运行态动态切换文案与操作）
     5. **重启内核**（快速重启释放端口）
     6. *(横向分割线)*
     7. **退出**
   - **双向即时联动机制**：
     - 在托盘点击「启动/停止/重启内核」时，Rust 端通过 `app_handle.emit("proxy-status-changed")` 全局广播事件；
     - 前端控制台实时监听该事件，并在窗口获得焦点（从托盘切回控制台）时瞬间自动触发 `checkHealth()`，将状态轮询频率由 15 秒优化至 3 秒，彻底解决托盘点击后界面不刷新的问题。
   - 托盘左键点击：快速在主窗口显示与隐藏之间无缝切换；
   - 设置面板支持两档选择：「最小化到系统托盘（后台继续提供 API 服务）」与「直接退出程序」，配置持久化于 `%LOCALAPPDATA%\codebuddy2openai\settings.json`。
7. **Agent 一键接入**：
   - Hermes Agent：一键检测并注入 `AppData\Local\hermes\config.yaml`。
   - ZCode：一键检测并注入 `cli/config.json` 与 `v2/config.json`。

**2026-09-05 安全与健壮性批次（全账号审计产出，均已推送）**：
- `2020b4b` 日志查看器 UTF-8 边界 panic 修复（中文日志 80KB 截断对齐 char boundary）；
- `c9da638` 开发机硬编码路径全量环境变量化：集中工具区 env_nonempty/local_appdata/user_home + `C2O_PYTHON`/`C2O_CONVERTER`/`HERMES_HOME`，原 VOS-User 路径仅剩最终兜底（本机行为不变）；**Agent 路径检测已核实通用**：Hermes 候选=官方 Windows 默认 %LOCALAPPDATA%\hermes + HERMES_HOME + ~/.hermes（官方文档三 者 皆 认），ZCode=~/.zcode/cli（官方约定），他人机器可正常检测；
- `b23c2d5` /health 收窄为 {status, authenticated} 并新增 LocalHostOnlyMiddleware（Host 头校验防 DNS rebinding，[::1]:port 方括号解析已处理）；前端昵称改走 accounts_list 并移除硬编码"晚街"；
- `d79fd4f` 补基础 CI（windows-latest：npm ci+vite build+cargo check --locked+rust-cache，timeout 30min，首跑 4m26s 绿）+ dependabot.yml（npm+cargo）；
- 已知存量风险（未修，设计内）：accounts.json 明文 token（与桌面端同级）、converter --api-key 默认空时零鉴权（GUI 不传 key）、proxy_stop 按命令行匹配可能误杀其他 converter.py 进程、脱敏功能=绕过上游合规词检测（合规风险用户自担）。

**2026-09-05 ZCode 一键接入根因确认（实测）**：c2o 写 `~/.zcode/cli/config.json` 与 `v2/config.json` 的 provider.workbuddy 结构正确（与生效过的 cpa-gui provider 同构），但 **ZCode Desktop 的"模型设置"自定义供应商列表存在其内部压缩 leveldb（%APPDATA%/ZCode/session，UTF-16LE+snappy，无法程序化读写），只认 UI 添加，直接写 JSON 它不读**——写入后状态显示"已接入配置"但模型永不出现（c2o 的状态判定只是"文件里有 key"，属假阳性）。**已验证的可用路径**：Desktop 模型设置 → 添加供应商 → Chat Completions 格式 + baseURL http://127.0.0.1:8787/v1 + key `local` + 手动加模型 → 连接成功，聊天模型选择器即可选（用户已跑通）。**c2o 待改→已完成（`18c3e00`，同日）**：configure_zcode 改引导式（不再写文件，返回 JSON 引导信息；前端复制到剪贴板+展开步骤文本框+按钮改「复制接入配置」）；agent_detect 加 loopback_port_open（TcpStream 800ms 探测）真实可达性探测，徽章改报「服务在线·可接入/服务离线」，假阳性消除；remove_zcode 保留文件清理并提示 Desktop 内条目需手动删。用户 rebuild 后需 developerPrivate 无关——Tauri 应用需重新构建安装包或 cargo tauri dev 生效。ECP 官方文档亦无 ZCode 接入页（claude-code/codex/droid/grok-build/opencode/pi 有），此坑业界通用。

**2026-09-05 tauri dev 环境三个坑（用户 `npm run tauri dev` 实测连环发现，均已修）**：① package.json 原本无 `tauri` script 且未装 @tauri-apps/cli → 已装 tauri-cli 2.11.4 + scripts 加 `"tauri": "tauri"`（`ba1e26c`）；② tauri.conf.json 的 build 段缺 `beforeDevCommand`/`beforeBuildCommand` → `tauri dev` 不会自启 vite，卡死在 "Waiting for your frontend dev server to start on http://localhost:5173/"（netstat 见 SYN_SENT）→ 已补 `"beforeDevCommand": "npm run dev"` + `"beforeBuildCommand": "npm run build"`（`da5a94d`）；③ vite chokidar 监视整个项目目录，cargo 编译写 `src-tauri/target/debug/deps/*.exe` 时文件被 Windows 锁定 → chokidar 抛 `EBUSY: resource busy or locked, watch ...codebuddy2openai.exe` 把 vite 进程干崩（beforeDevCommand 非零退出）→ 已在 vite.config.js 加 `server.watch.ignored: ['**/src-tauri/target/**']`（`ca29709`）——Tauri+Vite on Windows 经典坑，官方模板默认带此排除。现 `npm run tauri dev`（首跑编译 Rust 数分钟）与 `npm run tauri build` 均为标准一键流程。**④ tauri build 的 MSI/WiX 打包环境性失败（WixTools314 light.exe 挂，exe 本体已成功）→ bundle targets 从 "all" 固化 `["nsis"]`（`4a45660`），NSIS 一次成功**；产物：`src-tauri/target/release/codebuddy2openai.exe`（绿色直跑）与 `bundle/nsis/codebuddy2openai_0.1.0_x64-setup.exe`（安装包）；用户已产出新版，用于验证 Agent 引导式接入与真实探测徽章。**注意：用户该次 build 基于 `f140398`，含「页面加载即弹空窗」的 hidden 覆盖 bug（修复在 `cf96ead`），main 此后另有 04d7457/README 更新等提交——用户下次使用前需重新 `npm run tauri build`**。

**2026-09-05 模型矩阵表格三轮 UI 迭代 + ZCode 引导面板重构（用户审美反馈驱动，均已推送 CI 绿）**：
- 表格三轮收敛：① 列宽规划（table 加 `models-table` 类：各列 nowrap、输入框/下拉定宽、min-width 740、section-title-row 按钮 flex-shrink:0+nowrap 防折行飘移，`c1fdebe`）；② 用户建议改"点击弹窗编辑"——上下文/思考强度单元格变只读展示按钮（cell-edit 类），点击弹居中模态框集中编辑（**保持 `ctx-<id>`/`effort-<id>` 元素 id 不变以复用 saveModelConfig**），删除模型描述列（用户："完全无用"）、列头简化为"模型"/"标签"（`6430db6`）；③ 用户建议两列合一——上下文+思考强度合并单列"参数（上下文 / 思考）"竖排两个值按钮、空操作列整列删除、min-width 480（`f140398`/`bd79468`）；
- **弹窗 hidden 覆盖坑**：`.modal-overlay { display:flex }` 会覆盖 HTML hidden 属性的 display:none → 页面加载即弹空窗且取消/保存"无反应"（hidden=true 同样被压）→ 必须补 `.modal-overlay[hidden] { display:none !important; }`（`cf96ead`）；
- ZCode 引导面板按用户要求重构（`ce33862`）：按钮改「如何接入配置」，取消整块 textarea，改结构化面板——Base URL/API 格式/API Key 独立字段行（键值分层等宽加粗、点击值即复制、成功变绿 1.5s+toast）、模型列表渲染 15 个可点击芯片（点击复制单个模型名 + 「复制全部模型」芯片），clipboard API 带 execCommand 兜底；
- Emitter 未使用导入清理（`04d7457`）：emit 调用全在 commands.rs 且函数内局部 `use tauri::Emitter`，lib.rs 顶部导入为死代码，删除后构建零警告；
- **操作纪律教训：用户在跑 npm run tauri build/cargo 构建时严禁改动工作区源文件**（曾中途改 lib.rs 被用户叫停"先别修复"，git checkout 回滚，待 build 完成后再应用）。

**2026-09-05 前端迭代与 Tauri 工程坑（会话归档批次，提交 ce33862→bd79468/da5a94d/ca29709/4a45660/cf96ead/04d7457）**：
- 模型矩阵表格改只读单元格+弹窗编辑（ctx/effort 合并为单列"参数"，点击弹居中 modal，保存后行内值即时更新）；模型描述列删除；列头简化；操作列删除。
- **Tauri+Vite on Windows 三坑**：① `tauri.conf.json` 必须配 `beforeDevCommand: "npm run dev"`，否则 tauri dev 干等 5173；② vite 的 `server.watch.ignored` 必须排除 `**/src-tauri/target/**`，否则 cargo 写 exe 被 Windows 锁定时 chokidar 抛 EBUSY 崩掉 beforeDevCommand；③ Windows 打包用 `bundle.targets: ["nsis"]`（WiX light.exe 在本机环境性失败，NSIS 一次成功）。
- **CSS 坑**：`.modal-overlay { display:flex }` 会覆盖 `hidden` 属性的默认 display:none——弹窗加载即显示且"取消"失效；必须补 `.modal-overlay[hidden] { display:none !important; }`。
- `Emitter` 死导入已清（emit 全在 commands.rs 且函数内局部 use），构建零警告；`package.json` 补 @tauri-apps/cli 与 `tauri` script。
- README 已同步：模型列表改"自动获取 WorkBuddy 支持的模型"动态说明、架构 mermaid 折叠 details、ZCode 引导式接入描述。
- 用户拍板保留 ysk《本地回环服务的暴露面与防护》页（本会话唯一新增 ysk 内容）。

**Why:** 用户要求模型列表全量覆盖官方模型库，并补全 WorkBuddy 核心的倍率显示、上下文限制与思考强度调节能力。
**How to apply:** 维护 `C:\Users\VOS-User\Desktop\codebuddy2openai`，后续所有跨端 Agent 配置及客户端演进均以此架构为基准。
