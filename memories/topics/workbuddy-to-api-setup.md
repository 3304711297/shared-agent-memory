---
name: workbuddy-to-api-setup
description: 本地部署的 WorkBuddy 模型桥接服务与 Hermes Agent 接入配置（支持 hy4-preview、glm-5.3、kimi-k3 等模型）
metadata:
  node_type: memory
  type: project
  originSessionId: sess_424dd893-22b5-42eb-93ba-cc52bfa2fdda
---

## 项目与服务概况
- **WorkBuddy 客户端路径**：`D:\workbuddy\WorkBuddy.exe`
- **CLI 核心与配置**：`D:\workbuddy\resources\app.asar.unpacked\cli\product.json`
- **桌面端登录凭据位置**：`%LOCALAPPDATA%\CodeBuddyExtension\Data\Public\auth\workbuddy-desktop.info`

## 桥接方案 1：Hermes 专用直连适配器（codebuddy2openai，8787 端口）
- **代码目录**：`C:\Users\VOS-User\AppData\Local\hermes\codebuddy2openai`
- **监听端点**：`http://127.0.0.1:8787/v1`（OpenAI 兼容协议，原生支持 Tool Calling / 流式 SSE）
- **核心原理**：直接读取本地登录态凭据透传至腾讯后端 `copilot.tencent.com/v2/chat/completions`，无需付费版 Web API Key。
- **启动脚本**：
  - 后台静默启动：`C:\Users\VOS-User\AppData\Local\hermes\codebuddy2openai\start_silent.vbs`
  - 终端运行脚本：`C:\Users\VOS-User\AppData\Local\hermes\codebuddy2openai\start_workbuddy_proxy.bat`
- **Hermes 接入状态**：
  - `custom_providers` 已注册 `WorkBuddy (127.0.0.1:8787)`
  - 模型别名：`/model workbuddy`（自动）、`/model hy4-preview` / `/model hy4`（混元4代）、`/model hy3`、`/model workbuddy-glm53`、`/model workbuddy-kimi3` 等。
- **已实测验证可用模型（15个）**：`auto`、`hy4-preview`、`hy3`、`glm-5.3`、`glm-5.3-flash`、`glm-5.2`、`glm-5.1`、`glm-5v-turbo`、`kimi-k3`、`kimi-k2.7`、`kimi-k2.6`、`kimi-k2.5`、`deepseek-v4-pro`、`deepseek-v4-flash`、`minimax-m3`。

## 桥接方案 2：通用代理（workbuddy_to_api，3000 端口）
- **仓库位置**：`D:\ai coding\workbuddy_to_api`
- **监听端口**：`http://127.0.0.1:3000/v1`（OpenAI）、`http://127.0.0.1:3000`（Anthropic）
- **管理面板**：`http://127.0.0.1:3000/admin`（Key: `local`）

**Why:** 用户希望在 Hermes Agent 及 ZCode 等多工具中无缝复用 WorkBuddy 订阅的大模型与编程能力。
**How to apply:** 在 Hermes 中直接使用 `/model hy4-preview` 或切换至 `WORKBUDDY (127.0.0.1:8787)` 分组；确保 `converter.py` 后台进程运行（开机可执行 `start_silent.vbs`）。
