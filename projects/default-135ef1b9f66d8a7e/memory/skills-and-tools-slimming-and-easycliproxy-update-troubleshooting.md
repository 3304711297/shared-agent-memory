---
name: skills-and-tools-slimming-and-easycliproxy-update-troubleshooting
description: EasyCLIProxyAPI 更新内核与 GUI 报错根因诊断与双端 (Hermes & ZCode) 技能库深度精简归档规范
metadata:
  type: project
---

# EasyCLIProxyAPI 更新报错诊断与双端技能库精简归档

## 一、EasyCLIProxyAPI 更新启动报错排查复盘（2026-09-07）

### 1. 现场诊断与排错结论
用户在 EasyCLIProxyAPI 客户端手动更新内核与 GUI 端后，启动报出错误。经排查 `D:\EasyCLIProxyAPI\auth\logs\main.log` 与 Tauri 客户端源码，明确了以下三个核心事实：

1. **核心报错根因（网络代理握手瞬间拒绝）**：
   - 重启瞬间（00:10:31），内核 `cli-proxy-api.exe` 尝试经由配置的本地代理 `http://127.0.0.1:3067` 刷新 Google OAuth 凭据及拉取 Antigravity 版本清单。
   - 报错信息：`dial tcp 127.0.0.1:3067: connectex: No connection could be made because the target machine actively refused it.`
   - 根因在于客户端重启瞬间本地代理（3067）短时不可达或网络中断，导致启动探活直接抛错。
2. **上游服务断连（EOF 与单账号冷却）**：
   - 主账号 `antigravity-jimygod114514@gmail.com.json` 此前已因配额耗尽进入 104 小时冷却；
   - 更新前后备用号 `antigravity-2964251404@qq.com.json` 短暂遭遇 Google 上游接口断连（`err=Post "https://daily-cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse": EOF`），从而抛出 500/503 错误。
3. **便携版更新机制与单实例锁**：
   - 便携版通过临时目录 `EasyCLIProxyAPI-updater.exe` 就地替换 `EasyCLIProxyAPI.exe`、`core-version.txt` 和 `portable-app.json`；外层安装目录名保持旧名 `D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64` 属于正常现象；
   - 若旧主进程未完全退出即拉起新 exe，会碰撞命名互斥锁 `Local\EasyCLIProxyAPI-instance-{hash}` 或 18080 端口占用提示。

### 2. 当前运行现状
- **实际已成功更新**：内核已生效为 **7.2.152**（Commit `c76dfd4e`），GUI 记录为 **0.2.75**。
- **服务状态平稳**：18080 端口监听正常，后续请求均已恢复 200 响应。当前严禁改动任何配置或重启，保持通信稳定。

---

## 二、双端 (Hermes & ZCode) 技能库精简与归档方案

### 1. 精简动机与效率瓶颈
121 个 Skills 的名称、分类和描述在每次 Agent 会话启动时全量注入系统 Prompt，不仅白白消耗数千 tokens 的固定开销，还在意图分发时引入歧义与迟滞。

### 2. 归档而非物理删除原则
为保证安全可回溯，所有被剔除的技能不使用 `rm` 彻底销毁，而是移动到各自的备用归档目录：
- **Hermes 归档目录**：`C:\Users\VOS-User\AppData\Local\hermes\skills-archived\`
- **ZCode 归档目录**：`C:\Users\VOS-User\.zcode\skills-archived\`
未来若有特定极端开发场景需要恢复，只需将文件夹从 `skills-archived/` 移回 `skills/` 即可秒级复活。

### 3. 精简归档技能分类清单

| 类别 | 归档技能 | 归档原因与更优替代 |
| :--- | :--- | :--- |
| **网络抓取类** | `smart-web-crawler`<br>`scrapling` | 依赖本地 requests/Playwright，在复杂代理环境下极易被 Cloudflare / 验证码风控阻断；**更优替代**：配置已全量接管为 Exa 独享（`web_search` / `web_extract`），云端清洗免密，速度与成功率高数倍。 |
| **本地重型/大显存 MLOps 类** | `llama-cpp`<br>`comfyui`<br>`audiocraft-audio-generation`<br>`nemo-curator`<br>`huggingface-tokenizers`<br>`huggingface-hub`<br>`segment-anything-model`<br>`dspy`<br>`qdrant` | 用户配置明确 `local_runtime.enabled: false`，本机 8GB 显存无法支撑重型本地大模型运行，长期 0 触发；向量检索由 OpenViking 智能感知与 2 分钟闲置休眠全权接管。 |
| **无本地凭据 SaaS 工具类** | `airtable`<br>`box`<br>`notion`<br>`google-workspace`<br>`teams-meeting-pipeline`<br>`himalaya`<br>`1password` | 本机未配置对应 CLI / OAuth 授权，保留会导致模型误以为具有调用能力而产生试探报错。 |
| **冗余外部 Agent CLI 类** | `claude-code`<br>`codex`<br>`opencode` | 本机无对应后台 CLI 服务；多任务严格优先原生 `delegate_task` 并发子代理与双端跨 Agent 握手。 |

### 4. 优化成果
- **Hermes 端**：由 **121 个** 技能精简至 **102 个**（剔除 19 项 / 21 个子目录）。
- **ZCode 端**：由 **92 个** 技能精简至 **75 个**（剔除 17 个子目录）。
- **核心保留**：Superpowers 研发纪律套件（14个）、`shared-agent-memory`、`hermes-agent`、`telegram-channel-ops`、`ast-grep`、`frontend-design`、`chinese-copywriting` 等核心能力 100% 完整保留。

**Why:** 降低系统 Prompt 的 Token 损耗与意图匹配噪音，杜绝无凭据/低效爬虫工具对模型的误导。
**How to apply:** 日常对话与研发中，网页抓取一律使用原生 Exa 驱动的 `web_extract` / `web_search`；多任务优先 `delegate_task` 并发；若遇小众需求需临时找回旧技能，直接在 `skills-archived` 查验复制。
