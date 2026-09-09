---
name: hermes-desktop-update-exit8-false-negative
description: Hermes Desktop 在 Windows 下更新后误报 exit 8 校验失败与启动弹窗的根因、一次性消费机制与排错闭环
metadata:
  node_type: memory
  type: project
  originSessionId: sess_3af3919b-6d31-4bc8-8d18-f16a415cdd81
---

2026-09-08 Hermes Agent 桌面端（Windows 11）触发自动更新后，`hermes update` 成功退出（code 0，版本推进至 `520e63661c` / v0.21.1，cua-driver 升级至 0.24.0，网关冷启正常），但在尾声校验阶段误报 `RuntimeError: The updated Desktop executable is missing` 并以 exit 8 退出。

### 1. 现象与报错堆栈
- PowerShell 后台更新管道：
  ```
  verify!| Traceback (most recent call last):
  verify!|   File "...\hermes_cli\desktop_update_verify.py", line 77, in verify_windows_desktop_update
  verify!|     raise RuntimeError("The updated Desktop executable is missing")
  verify!| RuntimeError: The updated Desktop executable is missing
  The updated Hermes runtime or Desktop build failed verification. Repair the installation and review antivirus quarantine before retrying.
  ```
- 桌面端重新打开时弹出系统级错误框：
  `Hermes update did not finish: The updated Hermes runtime or Desktop build failed verification. Repair the installation and review antivirus quarantine before retrying. Details: ...\desktop-update-handoff.log`

### 2. 根因剖析（社区 Issue #105145 / PR #105168）
1. **工作目录脱节**：
   - 桌面端在 `apps/desktop/electron/main.ts` 中通过 `spawnUpdaterProcess` 唤起 `scripts/desktop-update/windows.ps1` 时，设定的 `cwd` 为 `HERMES_HOME`（`%LOCALAPPDATA%\hermes`），而项目源码根目录通过 `-InstallRoot` 传入。
   - `windows.ps1` 全文未调用 `Set-Location` 或 `[Environment]::CurrentDirectory`。
   - `windows.ps1:1609` 调用 Python 校验脚本：
     `verify_windows_desktop_update(Path.cwd())`
   - Python 子进程继承了父进程 CWD（即 `HERMES_HOME`），导致 `desktop_update_verify.py` 在 `HERMES_HOME/apps/desktop/release` 寻找构建产物，找不到而抛出异常，退出码判为 8。
2. **实际产物完好**：
   - 真实的 `apps/desktop/release/win-unpacked/Hermes.exe`（214MB）和 ASAR 完整无损。直接传入源码根目录运行 `verify_windows_desktop_update(Path(".../hermes-agent"))` 100% 静默通过。

### 3. 启动弹窗机制（阅后即焚）
- 后台脚本以 exit 8 失败时，会写状态文件：`%LOCALAPPDATA%\hermes\.hermes-update-result.json`。
- 桌面端冷启动时调用 `readAndConsumeHandoffResult(HERMES_HOME)`，该方法读取并**当场物理删除**该 json 文件，然后弹出 `showErrorBox`。
- **排错关键**：此弹窗为纯粹的“一次性历史通知”，点“确定”后桌面端正常进入 runtime 加载并启动后端服务（端口 3352）；再次启动绝不会重复弹出，无需重装或修复。

### 4. 社区状态与对齐
- **Issue**: [NousResearch/hermes-agent#105145](https://github.com/NousResearch/hermes-agent/issues/105145) (P1 bug，多位 Windows 用户证实；**2026-09-09 已关闭**)
- **PR**: [NousResearch/hermes-agent#105168](https://github.com/NousResearch/hermes-agent/pull/105168) (已提交，通过 `[Environment]::CurrentDirectory = $InstallRoot` 修复)
- 本地无需手动魔改仓库文件（保持 clean 以免阻碍后续 `git pull`）。

### 5. 【已治愈 2026-09-09】复发一次后随官方修复合流收口
- 09-09 更新（250 commits → `990473a79c` / v0.21.1）**再次复发同一误报**，属预期内的最后一次：hand-off 运行的是**更新前的旧脚本**（备份 ref `orphan-main-20260909-045354` 的 windows.ps1 中 `Set-InstallRootCurrentDirectory` 出现 0 次），修复代码是本次更新自己带进来的——鸡生蛋问题，无法更早生效。
- 修复已落地并实证：更新后 `windows.ps1` L1459 在起任何子进程前先 `Set-InstallRootCurrentDirectory $InstallRoot` 钉 CWD（L1647 仍调 `Path.cwd()`，但此时 cwd 已正确指向源码根），并附 `-SelfTestWorkingDirectory` 自检模式。真身 exe（`hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe`，214MB）完好，`.hermes-update-result.json` 已阅后即焚无残留。
- **结论：此后 Windows 桌面端更新不应再出现 exit 8 误报；若再遇更新失败弹窗，先查 `desktop-update-handoff.log` 确认是否同堆栈，勿盲目重装修复。**「更新时窗口卡住」体感=桌面端先退出→更新子进程静默跑数分钟（日志批量刷新）→旧脚本误报后不自动重启 GUI，属更新管线正常形态+已知 bug 叠加，非死机。
