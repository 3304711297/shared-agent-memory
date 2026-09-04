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
   - 原先的批处理窗口与 `start_silent.vbs` 后续均可被本 GUI 客户端一键接管。
2. **多账号管理体系**：
   - 凭据存储于 `%LOCALAPPDATA%\codebuddy2openai\accounts.json`，独立管理多账号。
   - 提供 `accounts_list`、`accounts_switch`、`accounts_delete`、`accounts_refresh_token` 等完整生命周期命令。
   - 自动与外部 `workbuddy-desktop.info` 联动同步活跃凭据。
3. **内嵌资产与积分看板**：
   - 彻底将积分进度与资源包明细收拢至当前账号卡片内部，彻底消除多账号重叠与视觉污染。
   - 登录 Tab 纯粹专注扫码/手机验证码登录，不混入无关积分卡。
4. **Agent 一键配置与移除**：
   - 一键检测与写入 Hermes Agent（`config.yaml` 自动注入 `custom_providers` 与 7 个模型别名）。
   - 一键检测与写入 ZCode（`cli/config.json` 与 `v2/config.json` 自动注入 15 个模型）。
5. **接口连通性测试 (Test Chat)**：
   - 直接向本地反代（默认 8787）发送快速探测请求，实时显示延迟毫秒数与模型回答。
6. **模型速查与代码示例**：
   - 内置 15 个可用模型列表、上下文窗口规格及 Python SDK 一键复制接入代码。

**Why:** 用户要求将项目迁移至桌面统一维护，并对标 EasyCLIProxyAPI 架构补全功能，摆脱原版 WorkBuddy 依赖，提供完善的多账号、资产查询与 Agent 集成体验。
**How to apply:** 维护 `C:\Users\VOS-User\Desktop\codebuddy2openai`，后续所有跨端 Agent 配置及客户端演进均以此架构为基准。
