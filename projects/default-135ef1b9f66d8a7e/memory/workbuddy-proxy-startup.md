---
name: workbuddy-proxy-startup
description: WorkBuddy2API 反代（127.0.0.1:8787）启动、故障排查与 venv 依赖说明
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_c9f48820-9daf-4a39-9173-ecedab6369dc
---

# WorkBuddy2API 反代运维速查

> 2026-09-11 更新：项目已由 `codebuddy2openai` 更名为 `workbuddy2api`；反代（converter.py 内核）现由 Tauri 桌面控制台托管（服务看板「启动/停止」或托盘「启动内核/停止内核/重启内核」），下述 vbs/bat 脚本属早期裸跑方式，仅作历史参考。

## 启动
- **当前推荐**：工作区 `D:/ai coding/GitRepos/workbuddy2api` → 运行 `src-tauri/target/release/workbuddy2api.exe`（或桌面快捷方式），在「服务看板」启动服务，或在托盘菜单启动内核。
- 历史方式（GUI 引入前）：`start_silent.vbs` / `start_workbuddy_proxy.bat`，用受管 venv 解释器 `%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe converter.py --port 8787 --desensitize`
- 数据目录：`%LOCALAPPDATA%\workbuddy2api`（回退兼容旧目录 `%LOCALAPPDATA%\codebuddy2openai`）

> **⚠️ vbs 重定向坑（2026-09-04 已修）**：`WshShell.Run` 不经 cmd.exe，直接写 `python.exe ... >> log 2>&1` 会导致 `>>` 被当作字面参数、CreateProcess 静默失败——双击快捷方式毫无反应（.bat 正常，因为 cmd 原生支持重定向）。vbs 内必须包一层 `cmd /c`：`WshShell.Run "cmd /c """"...python.exe"" converter.py --port 8787 --desensitize >> proxy_stdout.log 2>&1""", 0, False`。

## 健康检查
- `curl http://127.0.0.1:8787/health` → status ok、nickname「晚街」、token_expired=false 即正常
- `curl http://127.0.0.1:8787/v1/models` → 完整模型列表
- `curl http://127.0.0.1:8787/api/usage_summary` → 积分用量 `{uid,nickname,total,remain,used,is_paid_user,packages[]}`；2026-09-06 实测「晚街」remain 2779.8 / total 3700（套餐 1779.8+0+1000）；Python 访问需显式禁代理（`ProxyHandler({})`）防 3067 劫持 localhost
- 监听确认：`netstat -ano | findstr :8787`

## 排查顺序（Hermes 调 WorkBuddy 模型失败时）
1. 端口 8787 是否有进程 LISTENING（反代非自启，电脑重启/进程退出后不会自动恢复）→ 不在就双击桌面快捷方式
2. `/health` 是否 ok（检查 WorkBuddy 登录态 token 是否过期；过期会自动调 refresh 接口续期）
3. 若 venv 被 WorkBuddy 更新清除：`pip install httpx fastapi "uvicorn[standard]"` 到该 venv

## 已知事实
- 凭据源：`AppData\Local\CodeBuddyExtension\Data\Public\auth\workbuddy-desktop.info`（单账号），WorkBuddy 5.5.3 升级未破坏
- 2026-09-04 故障根因：反代未运行 + 系统缺依赖双重叠加，与 WorkBuddy 升级无关
- `~/.hermes/config.yaml` 已清理 4 个指向已卸载 Hermes Studio 的 hermes-studio-* MCP 条目（原文件备份 `config.yaml.bak-studio-20260904`），MCP 主配置在 `%LOCALAPPDATA%\hermes\config.yaml` 不受影响
