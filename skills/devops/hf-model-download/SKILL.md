---
name: hf-model-download
description: "下载HF大模型/断点续传/国内镜像时必用。镜像直连与弱网抗抖动断点续传，含 ModelScope 备选。Download Hugging Face models resiliently via domestic mirrors, with ModelScope fallback."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [huggingface, model-download, breakpoint-resume, mirror, domestic, network, modelscope, comfyui]
    category: devops
    related_skills: [local-llm-ops, creative:comfyui]
---

# HF Model Download — Resilient Domestic Pipeline

在 Windows、国内网络环境、移动热点与弱网 Wi-Fi 下下载 Hugging Face 几十 GB 大模型的抗抖动绝对断点续传工程管线。
支持双源：`--provider hf`（hf-mirror.com，默认）与 `--provider modelscope`（魔搭，镜像站也挂时的备选，带 sha256 强制校验）。

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

### 0. 动手前先确认是哪种故障（避免用错方案）

先跑一次无副作用的探测，再决定用哪个方案：

```bash
# 直连 HF（会暴露 schannel/TLS 握手被掐）
curl -sS --noproxy "*" --max-time 20 -o /dev/null -w "code=%{http_code}\n" \
  "https://huggingface.co/api/models/<org>/<name>"
```

症状对照表：

| 症状 | 含义 | 对应方案 |
|---|---|---|
| `[SSL: UNEXPECTED_EOF_WHILE_READING]` 或 `Cannot send a request, as the client has been closed` | TLS 链路被掐，`urlopen` / `hf download` / `curl` 三者都会中招 | 本技能四件套（镜像 + 禁 Xet + 清代理 + 放宽超时） |
| `curl` 报 `schannel: failed to receive handshake` | 同上，确认是链路层而非凭据层 | 同上 |
| `401` on large files | 镜像站未代理 XetHub CAS | `HF_HUB_DISABLE_XET=1` |
| `308` 重定向回 huggingface.co | 走了海外节点 | 清空所有 proxy 变量 |

**关键区分（容易误判）**：PyPI 通道正常 **不代表** HF 通道正常 —— 二者是不同的 CDN。
实测中 `pip install` 全程稳定（150–400 KB/s）的同时，HF 与 hf-mirror 都是握手即断。
拿 pip 的成功当 HF 的判据会浪费大量时间。

### 0.1 备选方案：ModelScope（镜像站也挂时才用）

**ModelScope 对两类文件的 Range 行为不同，必须分清**（实测 2026-09-21）：

| 文件类型 | 路径 | Range 行为 |
|---|---|---|
| **LFS 大文件（模型权重）** | `302` → `cdn-lfs-cn-1.modelscope.cn` 直链 | ✅ 真 `206 Partial Content` + `Accept-Ranges: bytes`，**续传正常** |
| 普通小文件（README / config 等） | 网关直接返回 | ⚠️ 不规范：回 `200`（非 206）但带 `Content-Range` 头；对开放式尾部 Range `bytes=N-` 会声明错误的 `Content-Length`（实测声明 200 却发 627 字节）→ `IncompleteRead` |

**结论**：实际要下的模型权重全是 LFS，**续传可用**；小文件建议一次性下完，不要指望断点。
脚本已对“200 + 已有断点”做保守退化（丢弃断点改整文件重下），不会写出损坏文件。

脚本支持 ModelScope（无需另写）：

```bash
python "%LOCALAPPDATA%/hermes/skills/devops/hf-model-download/scripts/resilient_hf_download.py" \
  --provider modelscope \
  --repo "Comfy-Org/Qwen-Image-2.1" \
  --file "vae/qwen_image_2.1_vae_bf16.safetensors" \
  --local-dir "D:/ai coding/ComfyUI/ComfyUI/models/vae"
```

**额外优势：ModelScope 的 CDN 重定向 URL 里直接嵌 sha256**，形如
`.../lfs-objects/bb/21/<sha256>?filename=...`，脚本会自动从列表接口或重定向链提取并
**下载后强制校验**（失败则把文件退回 `.part` 并报错，不会静默通过）。

手写 curl 的等价形式（`FilePath` 中的斜杠必须编码成 `%2F`，缺了会 404）：

```bash
curl -L -o "<dest>" \
  "https://modelscope.cn/api/v1/models/<org>/<name>/repo?Revision=master&FilePath=vae%2F<file>.safetensors"
```

列表接口可拿 sha256 与 Size 做人工核对（注意：**列表只列真实存在的文件，不要凭想象拼文件名**）：

```bash
curl -sS "https://modelscope.cn/api/v1/models/<org>/<name>/repo/files?Revision=master&Root=vae"
```

**踩坑**：请求 URL 指向仓库中不存在的文件时，ModelScope 不返回 404，而是返回 `200` +
JSON 错误体（`{"Code":10990101007,...,"Success":false}`）。若把它当数据存下，会得到一个
看似成功的垃圾文件。脚本已识别此模式并设了重试上限；手工 curl 时务必用列表接口先核对文件存在。

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
