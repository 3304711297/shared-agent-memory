---
name: openviking-lazy-gateway-and-local-bge-m3
description: OpenViking 语义层级检索架构、本地 CUDA BGE-M3 向量加速与 Serverless 按需唤醒休眠静默网关落地全貌
metadata:
  type: reference
---

# OpenViking 语义层级检索与本地模型工作台落地全貌

本文档详细记录 2026-09-06 在 Windows 11 本机上，为 Hermes Agent 和 ZCode 双端共享记忆库接入 OpenViking 智能语义检索层、本地 llama.cpp CUDA 硬件加速引擎及 Serverless 按需唤醒/休眠静默网关的技术全貌与运维规范。

## 一、架构拓扑与分层原则

```text
       shared-agent-memory (Git main 分支 —— 唯一物理真源 SSOT)
                         │
        ┌────────────────┴────────────────┐
 [即时驱动] post-commit / post-merge   [探活校准] HEAD SHA 对比
        │                                 │
        └────────────────┬────────────────┘
                         ↓ (单向注入，严禁反向覆盖 Git)
       本地 BGE-M3 (RTX 4070 Laptop, CUDA 加速, 端口 18082, 1024维向量)
                         +
       本地 Gemini 3.8 Flash (端口 18080, 秒级 L0/L1 摘要提炼)
                         │
                         ↓
       OpenViking 核心服务 (HTTP 127.0.0.1:1934, 独立 venv)
       虚拟文件系统: viking://resources/shared-memory/
                         │
                         ↓
       Serverless 懒加载网关 (HTTP 127.0.0.1:1933)
       - 按需自动唤醒 18082 与 1934
       - 2 分钟空闲自动终止进程、100% 释放 GPU 显存
                         │
                         ↓
       Hermes 原生 Memory Provider (openviking 插件, 保守召回策略)
```

## 二、关键技术细节与突破

### 1. 存储空间治理：NTFS Junction 彻底释放 C 盘
Hermes 客户端默认将模型与运行时下载至 `AppData\Local\hermes\`。通过 Windows NTFS 目录联接（Junction）实现透明物理重定向：
- `C:\Users\VOS-User\AppData\Local\hermes\models` ➔ `D:\HermesModels`
- `C:\Users\VOS-User\AppData\Local\hermes\runtimes` ➔ `D:\HermesRuntimes`
写入与下载对 C 盘空间损耗为 0 字节，全部落入 D 盘（可用空间 145+ GB）。

### 2. 本地推理引擎与模型矩阵
- **RTX 4070 (8GB VRAM) 显存适配黄金法则**：模型体积 ≤ 5.5GB（留 2.5GB 供 KV Cache），实现 100% 显存满血加速；大参数优先选 MoE 架构（如 Qwen3-Coder-30B-A3B，激活仅 3B）。
- **已部署就位模型**（全部存放在 `D:\HermesModels`）：
  - `bge-m3-Q8_0.gguf` (605 MB)：1024 维高精度向量嵌入模型，llama-server 纯本地 GPU 加速；
  - `Qwen3.5-9B-Q4_K_M.gguf` (5.3 GB)：满血本地通用推理模型，带思考链；
  - `DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf` (4.4 GB)：纯显存满血深度逻辑推演模型。

### 3. llama-server 向量批处理陷阱规避
OpenViking 摄入长 Markdown 文档时输入常超过 2000 tokens。llama-server 默认 batch size (512) 会报错 `input too large to process`。
必须配置扩展参数：
`-c 8192 -b 8192 --ubatch-size 8192 -ngl 99`

### 4. Serverless 懒人网关与 Agent 退出自动清理（Agent Guard 闭环）
脚本位于 `C:\Users\VOS-User\AppData\Local\hermes\scripts\openviking_lazy_gateway.py`。
依用户指令（2026-09-06）：
1. **解除开机自启**：已从 `Startup` 移除 `OpenVikingGateway.vbs`；
2. **全自动退出清理（方案 A）**：部署 `scripts/agent_guard.py`（开机启动项 `Startup/AgentGuard.vbs`，经 `.openviking\venv\Scripts\pythonw.exe` 驱动，占用 ~18MB 内存，CPU 0%）。静默监控 `Hermes.exe` 与 `ZCode.exe`：
   - 当检测到所有 Agent GUI 均已关闭后，防抖 2.5 秒，自动连根清除 MCP 孙子孤儿进程（`chrome-devtools-mcp`、`desktop-commander`、`context7-mcp`、`serena`）、残留后台 Python 进程，并自动执行 `openviking_service.py stop` 完全释放 GPU 显存与内存；
3. **桌面快捷辅助**：
   - `启动 OpenViking.lnk`（点击后台静默开启 1933 懒网关）；
   - `停止 OpenViking.lnk`（点击一键杀掉网关与模型进程）；
   - `清理孤儿进程.lnk`（一键手动强制清扫孤儿进程）。
4. **运行环境严格隔离**：必须使用 OpenViking 独立虚拟环境 `C:\Users\VOS-User\.openviking\venv\Scripts\pythonw.exe` 驱动，严禁借用 `hermes-agent\venv`，规避 Windows 文件锁拦截 Hermes 桌面更新。
- 平时状态：0% GPU、0 MB 显存、0% CPU；
- 收到提问时：自动在后台 5~6 秒内静默拉起 18082 与 1934，无任何黑框终端弹出；
- 连续 2 分钟无请求：自动 taskkill 终止推理进程，100% 归还 800MB 显存。

### 5. Hermes 保守召回策略
在 Hermes `config.yaml` 与 `.env` 中锁定：
- `OPENVIKING_ENDPOINT=http://127.0.0.1:1933`
- `OPENVIKING_RECALL_LIMIT=3`
- `OPENVIKING_RECALL_SCORE_THRESHOLD=0.35`
- `OPENVIKING_RECALL_PREFER_ABSTRACT=true`（优先只召回 L0 极短摘要，防止长文档污染 Gemini 3.8 Flash 注意力）
- `OPENVIKING_RECALL_RESOURCES=true`
- `OPENVIKING_RECALL_TIMEOUT_SECONDS=15.0`

### 6. Hermes 客户端「本地运行时」常驻内存陷阱与关闭规范
Hermes 桌面端「提供方 → 本地模型」下的「已安装 llama.cpp 运行时」开关（对应 `local_runtime.enabled`）属于**全量加载本地聊天大模型（如 Qwen/DeepSeek）**，一旦开启会常驻霸占 **2.9 GB ~ 5 GB 物理内存与显存**。
- **定位分工原则**：对话模型由用户按需随时切换（严禁固定主力模型）；客户端「已安装 llama.cpp 运行时」开关必须显式保持关闭（`local_runtime.enabled: false`），杜绝常驻吞噬 3GB 内存；
- **解耦独立**：向量嵌入（BGE-M3）完全交由上述 2 分钟 Serverless 懒加载网关托管，绝不通过常驻客户端大模型吃内存。


## 三、双驱动防漂移机制
- **即时驱动**：在 `C:\Users\VOS-User\.zcode\cli\memories\.git\hooks\post-commit` 与 `post-merge` 挂载自动同步脚本 `scripts/sync_shared_memory_openviking.py`；
- **探活对比**：记录 `C:\Users\VOS-User\.openviking\last_synced_commit.txt`，对比 HEAD SHA，重复提交秒级跳过，新提交触发增量重扫。

## 四、常用维护命令
- 查看守护状态：`python C:/Users/VOS-User/AppData/Local/hermes/scripts/openviking_service.py status`
- 强制启停后端：`python C:/Users/VOS-User/AppData/Local/hermes/scripts/openviking_service.py [start|stop|restart]`
- 强制全量同步：`python C:/Users/VOS-User/AppData/Local/hermes/scripts/sync_shared_memory_openviking.py --force`
- 语义检索验证：`C:/Users/VOS-User/.openviking/venv/Scripts/ov.exe find "<query>"`

[[shared-agent-memory]] [[hermes-shared-memory]] [[user-windows-environment]] [[hermes-agent-install]]
