---
name: codebuddy2openai-tauri-gui
description: codebuddy2openai 桌面客户端对标 EasyCLIProxyAPI 重构实践与状态
metadata:
  type: project
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

**2026-09-05 ZCode 一键接入根因确认（实测）**：c2o 写 `~/.zcode/cli/config.json` 与 `v2/config.json` 的 provider.workbuddy 结构正确（与生效过的 cpa-gui provider 同构），但 **ZCode Desktop 的"模型设置"自定义供应商列表存在其内部压缩 leveldb（%APPDATA%/ZCode/session，UTF-16LE+snappy，无法程序化读写），只认 UI 添加，直接写 JSON 它不读**——写入后状态显示"已接入配置"但模型永不出现（c2o 的状态判定只是"文件里有 key"，属假阳性）。**已验证的可用路径**：Desktop 模型设置 → 添加供应商 → Chat Completions 格式 + baseURL http://127.0.0.1:8787/v1 + key `local` + 手动加模型 → 连接成功，聊天模型选择器即可选（用户已跑通）。**c2o 待改**："一键接入"对 ZCode 应改引导式（打开设置页+复制配置值），或写入后明确提示需在 Desktop UI 手动添加；现有"已接入"判定需修为真实可达性探测。ECP 官方文档亦无 ZCode 接入页（claude-code/codex/droid/grok-build/opencode/pi 有），此坑业界通用。

**Why:** 用户要求模型列表全量覆盖官方模型库，并补全 WorkBuddy 核心的倍率显示、上下文限制与思考强度调节能力。
**How to apply:** 维护 `C:\Users\VOS-User\Desktop\codebuddy2openai`，后续所有跨端 Agent 配置及客户端演进均以此架构为基准。
