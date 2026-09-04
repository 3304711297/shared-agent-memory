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
   - **左侧独立「实时日志」Tab**：内置深色终端风格的代码阅读器，支持自动追加、手动刷新与清空。
6. **系统托盘与关闭策略设置**：
   - 支持关闭窗口转为系统托盘后台运行（托盘左键切换显隐、右键托盘菜单打开/退出）。
   - 设置面板中提供两档选择：「最小化到系统托盘（后台继续提供 API 服务）」与「直接退出程序（自动停止服务释放端口）」，配置持久化于 `%LOCALAPPDATA%\codebuddy2openai\settings.json`。
7. **Agent 一键接入**：
   - Hermes Agent：一键检测并注入 `AppData\Local\hermes\config.yaml`。
   - ZCode：一键检测并注入 `cli/config.json` 与 `v2/config.json`。

**Why:** 用户要求模型列表全量覆盖官方模型库，并补全 WorkBuddy 核心的倍率显示、上下文限制与思考强度调节能力。
**How to apply:** 维护 `C:\Users\VOS-User\Desktop\codebuddy2openai`，后续所有跨端 Agent 配置及客户端演进均以此架构为基准。
