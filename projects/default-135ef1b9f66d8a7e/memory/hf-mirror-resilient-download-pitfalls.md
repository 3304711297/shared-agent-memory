---
name: hf-mirror-resilient-download-pitfalls
description: Hugging Face 权重国内镜像直连、CAS 401 拦截规避与弱网绝对断点续传实证
metadata:
  type: feedback
---

# Hugging Face 大模型国内与弱网下载排障指南

记录在 Windows、国内网络环境、移动热点与弱网 Wi-Fi 下下载 Hugging Face 几十 GB 大模型时的典型暗坑与经过实证的规避方案。

## 现象与根因

1. **`hf download` 默认 10 秒超时且崩溃删临时文件导致重头下载**：
   官方 `huggingface_hub`（及 `hf.exe` CLI）在 `huggingface_hub.constants` 中将单次 socket 数据读取超时 `HF_HUB_DOWNLOAD_TIMEOUT` 硬编码为 10 秒。在移动热点、邻里 Wi-Fi 或无线信号较弱的环境下，网络偶发抖动超过 10 秒无新 chunk 即抛 `httpcore.ReadTimeout`。更为致命的是：在 `_download_to_tmp_and_move` 的 `finally` 块中，官方设计了 `tmp_path.unlink(missing_ok=True)`。下载失败后已下载的 1~2GB `.incomplete` 文件会被直接删除，下次运行又必须从 0% 开始，形成无法续传的死循环。
2. **国内镜像 `hf-mirror.com` 专供境内直连，走海外代理被 308 拦截**：
   `hf-mirror.com` 是境内加速站。如果请求头中经过了本地代理（如 Karing 出口为海外节点），镜像站 CDN 会识别为境外访问并直接返回 `HTTP 308 Permanent Redirect`，强制重定向回 `https://huggingface.co/...`。若海外直连受阻，终端即报 `[WinError 10061 目标计算机积极拒绝]` 或超时。
3. **国内镜像对新版 XetHub/CAS 重建接口报 401 Unauthorized**：
   新版 `huggingface_hub` 默认启用基于 CAS 的 Xet 存储协议（`xet_get`）。拉取多 GB 分块权重时，客户端会访问 `https://cas-server.xethub.hf.co/v2/reconstructions/...`。国内镜像站只代理了标准 Web 与 Git-LFS 对象存储，并未代理私有 CAS 鉴权服务，导致未带专属 Token 的请求抛出 `RuntimeError: CAS Client Error: (401 Unauthorized)`。
4. **Windows 原生文件锁 `.lock` 残留与进程孤儿假死**：
   Windows 下进程因网络断开或崩溃异常退出时，其在 `.cache/huggingface/download/` 目录下创建的 `.lock` 文件无法正常释放。再次启动时 `filelock` 进入无上限轮询等待（`Still waiting to acquire lock`），控制台静止无响应。

## 规避方案与工具落地

1. **官方 CLI 标准四件套环境变量配置**：
   在 PowerShell 中使用官方 `hf download` 前，必须显式注入：
   ```powershell
   $env:HF_ENDPOINT = "https://hf-mirror.com"
   $env:HF_HUB_DISABLE_XET = "1"
   $env:HF_HUB_DOWNLOAD_TIMEOUT = "60"
   $env:HTTP_PROXY = ""; $env:HTTPS_PROXY = ""; $env:ALL_PROXY = ""
   ```
2. **通用原生断点续传工具（终极解）**：
   为彻底摆脱 10s 超时删文件陷阱，交付基于原生 HTTP 206 `Range` 头的下载脚本（见技能 `devops/hf-model-download/scripts/resilient_hf_download.py`）：
   - 写入固定的 `.part` 文件，不论手动中断（Ctrl+C）还是网络闪断，已下载字节 100% 永久留存；
   - 单次读取超时放宽至 60 秒，发生网络抖动自动等待 2 秒并无缝原地重连；
   - 自动清空代理直连国内镜像源，避免 308 重定向与节点流量消耗；
   - 显示清晰的进度百分比、已下载大小、实时网速与剩余预估时间。
3. **残留锁清理**：
   启动卡住时递归扫描清理 `*.lock` 文件：
   ```powershell
   Get-ChildItem -Path "<TARGET_DIR>" -Filter "*.lock" -Recurse | Remove-Item -Force
   ```

**Why:** 大模型权重（如 7B 达 14GB~33GB）体积庞大，在移动热点或弱网 Wi-Fi 下网络抖动是常态；官方 CLI 默认短超时与崩溃删缓存机制与弱网完全相悖，必须依赖确定的 HTTP 206 断点持久化与境内直连配置。

**How to apply:** 凡涉及从 Hugging Face 或国内镜像下载大模型，一律优先调用 `devops/hf-model-download` 技能或其内置的 `resilient_hf_download.py`；在终端执行命令前严格检查四件套环境变量，严禁走海外代理访问 `hf-mirror.com`。
