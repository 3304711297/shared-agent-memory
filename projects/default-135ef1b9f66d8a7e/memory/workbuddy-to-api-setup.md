---
name: workbuddy-to-api-setup
description: 本地部署的 workbuddy_to_api 桥接服务（将 D:\workbuddy 的模型转换为 OpenAI/Anthropic 兼容 API）
metadata:
  node_type: memory
  type: project
  originSessionId: sess_424dd893-22b5-42eb-93ba-cc52bfa2fdda
---

## 项目与服务概况
- **仓库位置**：`D:\ai coding\workbuddy_to_api`（源于 `https://github.com/yxxawa/workbuddy_to_api`）
- **WorkBuddy 客户端安装路径**：`D:\workbuddy\WorkBuddy.exe`
- **CLI 核心脚本**：`D:\workbuddy\resources\app.asar.unpacked\cli\bin\codebuddy`
- **本地配置文件**：`D:\ai coding\workbuddy_to_api\.env`

## API 服务参数
- **监听端口**：`http://127.0.0.1:3000`
- **OpenAI 兼容 Base URL**：`http://127.0.0.1:3000/v1`
- **Anthropic 兼容 Base URL**：`http://127.0.0.1:3000`
- **API Key**：`local`
- **支持模型**：共 49 个模型，包括 `auto`（智能推荐）、`glm-5.3`、`kimi-k3-1`、`minimax-m3`、`deepseek-v4-pro`、`glm-5v-turbo` 等。
- **管理面板**：`http://127.0.0.1:3000/admin`（输入 API Key `local` 解锁，支持签到、额度查看、倍率表与调用日志）。

## 服务控制命令
- **后台启动**：`cd "D:\ai coding\workbuddy_to_api"; python .\workbuddy_to_api.py --background`
- **查看状态**：`cd "D:\ai coding\workbuddy_to_api"; python .\workbuddy_to_api.py --status`
- **停止服务**：`cd "D:\ai coding\workbuddy_to_api"; python .\workbuddy_to_api.py --stop --api-key local`

**Why:** 用户希望在 ZCode 及各种 AI 编程工具中无缝使用 WorkBuddy 的模型能力。
**How to apply:** 只要用户需要使用 WorkBuddy 模型，确保后台服务在 3000 端口运行，客户端填入 `http://127.0.0.1:3000/v1`，API Key 填 `local`，模型填 `auto` 即可。
