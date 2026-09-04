---
name: workbuddy-proxy-startup
description: codebuddy2openai 反代（127.0.0.1:8787）启动、故障排查与 venv 依赖说明
metadata:
  type: reference
---

# codebuddy2openai 反代运维速查

## 启动
- 无窗口启动（推荐）：双击桌面快捷方式 `start_silent.vbs`（日志追加到项目目录 `proxy_stdout.log`）
- 窗口模式：`start_workbuddy_proxy.bat`
- 两者均已改用受管 venv 解释器：`C:\Users\VOS-User\.workbuddy\binaries\python\envs\default\Scripts\python.exe converter.py --port 8787 --desensitize`
- 项目目录：`C:\Users\VOS-User\AppData\Local\hermes\codebuddy2openai`

> **⚠️ vbs 重定向坑（2026-09-04 已修）**：`WshShell.Run` 不经 cmd.exe，直接写 `python.exe ... >> log 2>&1` 会导致 `>>` 被当作字面参数、CreateProcess 静默失败——双击快捷方式毫无反应（.bat 正常，因为 cmd 原生支持重定向）。vbs 内必须包一层 `cmd /c`：`WshShell.Run "cmd /c """"...python.exe"" converter.py --port 8787 --desensitize >> proxy_stdout.log 2>&1""", 0, False`。

## 健康检查
- `curl http://127.0.0.1:8787/health` → status ok、nickname「晚街」、token_expired=false 即正常
- `curl http://127.0.0.1:8787/v1/models` → 完整模型列表
- 监听确认：`netstat -ano | findstr :8787`

## 排查顺序（Hermes 调 WorkBuddy 模型失败时）
1. 端口 8787 是否有进程 LISTENING（反代非自启，电脑重启/进程退出后不会自动恢复）→ 不在就双击桌面快捷方式
2. `/health` 是否 ok（检查 WorkBuddy 登录态 token 是否过期；过期会自动调 refresh 接口续期）
3. 若 venv 被 WorkBuddy 更新清除：`pip install httpx fastapi "uvicorn[standard]"` 到该 venv

## 已知事实
- 凭据源：`AppData\Local\CodeBuddyExtension\Data\Public\auth\workbuddy-desktop.info`（单账号），WorkBuddy 5.5.3 升级未破坏
- 2026-09-04 故障根因：反代未运行 + 系统缺依赖双重叠加，与 WorkBuddy 升级无关
- `~/.hermes/config.yaml` 已清理 4 个指向已卸载 Hermes Studio 的 hermes-studio-* MCP 条目（原文件备份 `config.yaml.bak-studio-20260904`），MCP 主配置在 `%LOCALAPPDATA%\hermes\config.yaml` 不受影响
