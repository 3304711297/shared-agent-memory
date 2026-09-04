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
4. **Agent 一键配置与修复**：
   - 一键检测与写入 Hermes Agent：已将首选路径固定为真正的 `C:\Users\VOS-User\AppData\Local\hermes\config.yaml`（已配置 WorkBuddy 供应商与 7 个模型别名，状态正常显示为「已接入配置」绿色徽章）。
   - 一键检测与写入 ZCode：自动在 `cli/config.json` 与 `v2/config.json` 注入 15 个模型。
5. **内嵌 Debug 与运行日志查看器 (核心新增)**：
   - **完全告别外部黑框**：后端服务（FastAPI/Uvicorn/Converter）的标准输出与错误流自动重定向至本地 `%LOCALAPPDATA%\codebuddy2openai\proxy_stdout.log`；
   - **左侧独立「实时日志」Tab**：内置深色终端风格的代码阅读器，支持每 2 秒自动同步追加最新日志、支持手动「刷新日志」与「一键清空日志」，启动、请求流与报错信息在客户端内一目了然。
6. **系统托盘与关闭策略设置**：
   - 支持关闭窗口转为系统托盘后台运行（托盘左键切换显隐、右键托盘菜单打开/退出）。
   - 设置面板中提供两档选择：「最小化到系统托盘（后台继续提供 API 服务）」与「直接退出程序（自动停止服务释放端口）」，配置持久化于 `%LOCALAPPDATA%\codebuddy2openai\settings.json`。
7. **自述文件全面重写**：
   - `README.md` 已全面重写，剔除上游原作者内容，更新为你专属的架构设计、特性列表、Mermaid 流程图、多模型表格及客户端调用示例。

**Why:** 用户要求将 Debug 信息直接内嵌在控制台界面中查看，摆脱外部黑色终端窗口。
**How to apply:** 维护 `C:\Users\VOS-User\Desktop\codebuddy2openai`，后续所有跨端 Agent 配置及客户端演进均以此架构为基准。
