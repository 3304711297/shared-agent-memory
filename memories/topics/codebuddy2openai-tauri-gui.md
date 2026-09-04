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
5. **服务启动静默与 Debug 控制台灵活切换 (新增)**：
   - **默认行为**：启动反代服务时传入 Windows `CREATE_NO_WINDOW (0x08000000)` 标志，**彻底静默无黑框弹出**。
   - **设置控制**：在「服务设置」中提供「启动服务时显示 Debug 黑色控制台窗口」开关（默认关闭），勾选后启动即可显示前台 CMD。
   - **即时查看**：在「服务设置」中提供「立即弹出前台 Debug 调试窗口」按钮，点击可随时单独唤出前台 CMD 查看实时 Python 日志。
6. **系统托盘与关闭策略设置**：
   - 支持关闭窗口转为系统托盘后台运行（托盘左键切换显隐、右键托盘菜单打开/退出）。
   - 设置面板中提供两档选择：「最小化到系统托盘（后台继续提供 API 服务）」与「直接退出程序（自动停用服务释放端口）」，配置持久化于 `%LOCALAPPDATA%\codebuddy2openai\settings.json`。
7. **自述文件全面重写**：
   - `README.md` 已全面重写，剔除上游原作者内容，更新为你专属的架构设计、特性列表、Mermaid 流程图、多模型表格及客户端调用示例。

**Why:** 用户要求修复 Hermes Agent 状态检测路径（修正为 AppData 真实有效文件），默认隐藏启动反代时的黑框窗口并增加调试窗口开关与即时弹出按钮。
**How to apply:** 维护 `C:\Users\VOS-User\Desktop\codebuddy2openai`，后续所有跨端 Agent 配置及客户端演进均以此架构为基准。
