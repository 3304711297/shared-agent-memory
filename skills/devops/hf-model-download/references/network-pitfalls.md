# Hugging Face 大模型国内与弱网下载排障指南

记录在 Windows、国内网络环境、移动热点与弱网 Wi-Fi 下下载 Hugging Face 几十 GB 大模型时的典型深坑与经过实证的规避方案。

---

## 坑位 1：`hf download` 默认 10s 超时在弱网必崩，且删除临时文件致进度清零

* **根因与机制**：
  官方 `huggingface_hub`（及 `hf.exe` CLI）在 `huggingface_hub.constants` 中将单次 socket 数据读取超时 `HF_HUB_DOWNLOAD_TIMEOUT` 硬编码为 **10 秒**（`_as_int(os.environ.get("HF_HUB_DOWNLOAD_TIMEOUT")) or 10`）。
  在移动热点、邻里 Wi-Fi 或信号较弱的环境下，一旦网络偶发抖动超过 10 秒没有收到下一个 chunk，就会抛出 `httpcore.ReadTimeout`。
  更为致命的是：在 `_download_to_tmp_and_move` 的 `finally` 块中，官方设计了 `tmp_path.unlink(missing_ok=True)`。这意味着下载失败后，已下载的 1~2GB `.incomplete` 文件会被**直接删除**，下次运行又必须从 0% 开始，形成无法续传的死循环。
* **规避与修复**：
  1. 临时环境变量：必须设置 `$env:HF_HUB_DOWNLOAD_TIMEOUT = "60"` 放宽超时。
  2. 彻底解法：对于数 GB 的核心 safetensors 权重，改用本技能自带的 `resilient_hf_download.py` 脚本，基于 HTTP 206 `Range` 头写入固定的 `.part` 文件，不论手动中断还是网络超时，已下载字节 100% 永久留存，下次执行自动接续。

---

## 坑位 2：国内镜像 `hf-mirror.com` 专供境内直连，走海外代理被 308 拦截

* **根因与机制**：
  `hf-mirror.com` 是公益性质的境内加速站。如果请求头中经过了本地代理（如 Karing `127.0.0.1:3067` 出口是海外节点），镜像站的 CDN 会识别为境外访问，并直接返回 `HTTP 308 Permanent Redirect`，强制将请求重定向回 `https://huggingface.co/...`。
  这会导致：用户以为走了国内镜像，其实瞬间被踢回了官方外网，如果在外网直连受阻，终端就会报 `[WinError 10061 目标计算机积极拒绝]` 或超时。
* **规避与修复**：
  在下载窗口中，必须显式清空代理变量直连：
  ```powershell
  $env:HTTP_PROXY = ""; $env:HTTPS_PROXY = ""; $env:ALL_PROXY = ""
  ```
  在 Python 脚本中，直接使用 `urllib.request.build_opener(urllib.request.ProxyHandler({}))` 绕过系统与环境变量代理。

---

## 坑位 3：国内镜像对新版 XetHub/CAS 重建接口报 401 Unauthorized

* **根因与机制**：
  新版 `huggingface_hub` 默认启用了基于 CAS（Content Addressable Storage）的 Xet 存储下载协议（`xet_get`）。当尝试拉取多 GB 的分块权重时，客户端会访问 `https://cas-server.xethub.hf.co/v2/reconstructions/...`。
  由于国内镜像站只代理了标准的 Web 资源和 Git-LFS 对象存储，并未代理该私有 CAS 鉴权服务，导致未登录或未配置专属 Token 的请求直接遭遇 `RuntimeError: CAS Client Error: (401 Unauthorized)`。
* **规避与修复**：
  必须显式禁用 Xet 协议，强制客户端退回标准的 HTTP Git-LFS 直链下载：
  ```powershell
  $env:HF_HUB_DISABLE_XET = "1"
  ```

---

## 坑位 4：Windows 原生文件锁 `.lock` 残留与进程孤儿假死

* **根因与机制**：
  在 Windows 平台下，当下载进程因网络断开、控制台崩溃或用户强退时，其在 `.cache/huggingface/download/` 目录下创建的 `.lock` 文件可能来不及清理。下一次启动时，`filelock` 会在启动阶段进入无限等待：
  ```text
  Still waiting to acquire lock on .../model.safetensors.lock (elapsed: 120.0 seconds)
  ```
  此时终端看起来完全静止，没有进度条，误以为是卡死。
* **规避与修复**：
  重新启动前，扫描目标目录清理所有孤立的 `*.lock` 文件：
  ```powershell
  Get-ChildItem -Path "D:\..." -Filter "*.lock" -Recurse | Remove-Item -Force
  ```
