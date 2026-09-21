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

## 隔离实例端到端验证（改动只在真实上游才能看清时用）

想在不动主服务（8787）的前提下打真实上游：把 `LOCALAPPDATA` 指到一个临时目录再起内核，
端口换 8799。**目录层级必须与生产完全一致**——这是最容易白跑一轮的坑：

```
$ISO/workbuddy2api/accounts.json      ← 必须在这一层！放 $ISO/ 根目录等于没放
$ISO/workbuddy2api/settings.json      ← 同上；放错层会让 model_list_mode 退回默认 all
$ISO/workbuddy2api/model_availability.json   ← 内核自己写
$ISO/CodeBuddyExtension/Data/Public/auth/*.info   ← 仅作回退，优先 accounts.json
```

- `accounts.json` 放错层级的连锁反应：`_accounts_file()` 找不到 → `_active_uid()` 返回空
  （而 `_read_all_accounts()` 也读到空）→ 凭据模块回退去读 `.info`，**拿到的是另一个账号**。
  症状是记账落到了非预期 uid、清单过滤怎么都不生效，看起来像功能坏了，其实是布局错了。
- `settings.json` 是**按 mtime+size 热读**的，改完立刻生效、不必重启内核。
- 起停：`LOCALAPPDATA=<iso> <venv>/python.exe converter.py --port 8799 --log <iso>/conv.log`；
  验完 `netstat -ano | grep -E ':8799' | grep -c LISTENING` 应为 0（TIME_WAIT 残留不算），
  再 `rm -rf $ISO`。收尾顺手 `curl 127.0.0.1:8787/health` 确认主服务没被牵连。
- 判断「这是既有行为还是我这轮引入的回归」：`git show HEAD:converter.py > head.py` 起一个
  对照实例（另一端口），同一请求打两边比状态码。实测流式 11102 两边都返回
  `200 + SSE 带内错误`（已发头无法改状态码），据此排除回归。

## 排查顺序（Hermes 调 WorkBuddy 模型失败时）
1. 端口 8787 是否有进程 LISTENING（反代非自启，电脑重启/进程退出后不会自动恢复）→ 不在就双击桌面快捷方式
2. `/health` 是否 ok（检查 WorkBuddy 登录态 token 是否过期；过期会自动调 refresh 接口续期）
3. 若 venv 被 WorkBuddy 更新清除：`pip install httpx fastapi "uvicorn[standard]"` 到该 venv

## 已知事实
- 凭据源：`AppData\Local\CodeBuddyExtension\Data\Public\auth\workbuddy-desktop.info`（单账号），WorkBuddy 5.5.3 升级未破坏
- 2026-09-04 故障根因：反代未运行 + 系统缺依赖双重叠加，与 WorkBuddy 升级无关
- `~/.hermes/config.yaml` 已清理 4 个指向已卸载 Hermes Studio 的 hermes-studio-* MCP 条目（原文件备份 `config.yaml.bak-studio-20260904`），MCP 主配置在 `%LOCALAPPDATA%\hermes\config.yaml` 不受影响
