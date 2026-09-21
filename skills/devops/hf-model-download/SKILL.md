---
name: hf-model-download
description: "下载HF大模型/断点续传时必用。国内镜像直连与弱网抗抖动断点续传。Download Hugging Face models resiliently via domestic mirrors."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [huggingface, model-download, breakpoint-resume, mirror, domestic, network, comfyui]
    category: devops
    related_skills: [local-llm-ops, creative:comfyui]
---

# HF Model Download — Resilient Domestic Pipeline

在 Windows、国内网络环境、移动热点与弱网 Wi-Fi 下下载 Hugging Face 几十 GB 大模型的抗抖动绝对断点续传工程管线。

## 核心痛点与破解法则

1. **绝对断点续传（拒绝从零开始）**：
   官方 `hf download` 在下载失败后会清除临时文件导致进度归零。本方案通过原生 HTTP 206 `Range` 头将分块持久化至 `.part` 文件，网络中断或手动 Ctrl+C 后下次运行 100% 原地续传。
2. **强制国内镜像直连（避开 308 拦截）**：
   `hf-mirror.com` 专供境内直连，如果走了海外节点会被 308 重定向踢回官网；必须显式屏蔽本地代理直连。
3. **禁用 XetHub CAS 协议（避开 401 报错）**：
   国内镜像站未代理私有 CAS 接口，拉取大文件必抛 401；必须设置 `HF_HUB_DISABLE_XET=1` 退回 Git-LFS 直链。
4. **放宽超时至 60 秒（抗无线网络抖动）**：
   官方默认 10 秒读取超时（`HF_HUB_DOWNLOAD_TIMEOUT`），在热点或慢 Wi-Fi 抖动时必崩；脚本放宽至 60s 并自动指数退避重试。

## 详细排错手册

- 详细机制与四大暗坑（401 / 308 / 10s 超时 / 文件锁）参见：`references/network-pitfalls.md`。

## 快速使用指令

### 1. 推荐：使用本技能自带的抗抖动断点续传脚本（最稳妥）

脚本路径：`scripts/resilient_hf_download.py`

```bash
# 下载指定仓库的单个大文件（例如 Qwen-Image-2.1 的 transformer 权重）
python "%LOCALAPPDATA%/hermes/skills/devops/hf-model-download/scripts/resilient_hf_download.py" \
  --repo "Qwen/Qwen-Image-2.1" \
  --file "transformer/diffusion_pytorch_model-00001-of-00002.safetensors" \
  --local-dir "D:/ai coding/ComfyUI/ComfyUI/models/diffusion_models/Qwen-Image-2.1"

# 全量下载整个仓库（逐个文件执行断点续传）
python "%LOCALAPPDATA%/hermes/skills/devops/hf-model-download/scripts/resilient_hf_download.py" \
  --repo "Qwen/Qwen-Image-2.1" \
  --local-dir "D:/ai coding/ComfyUI/ComfyUI/models/diffusion_models/Qwen-Image-2.1"
```

### 2. 官方 CLI 标准四件套环境变量配置

如果在 PowerShell 中直接使用官方 `hf download`，必须预先注入以下变量：

```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
$env:HF_HUB_DISABLE_XET = "1"
$env:HF_HUB_DOWNLOAD_TIMEOUT = "60"
$env:HTTP_PROXY = ""; $env:HTTPS_PROXY = ""; $env:ALL_PROXY = ""

hf download <REPO_ID> <FILE_PATH> --local-dir "<TARGET_DIR>"
```

### 3. Windows 残留锁文件清理

若启动提示 `Still waiting to acquire lock`：

```powershell
Get-ChildItem -Path "<TARGET_DIR>" -Filter "*.lock" -Recurse | Remove-Item -Force
```
