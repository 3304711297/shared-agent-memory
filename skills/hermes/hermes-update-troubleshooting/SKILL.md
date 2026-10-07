---
name: hermes-update-troubleshooting
description: "Hermes更新失败/闪退/卡住时必用。更新交接链与看门狗排障。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [hermes, update, troubleshooting, windows, uv, handoff, watchdog]
    related_skills: [hermes-agent, windows-crash-diagnostics]
---

# Hermes 更新故障排查

## 用途与核心认知

诊断并修复 Hermes 桌面端与 CLI 的更新链路故障。三条核心认知：

1. **桌面端点「更新」时窗口关闭是设计行为，不是崩溃**——真正的故障在于更新交接链（handoff）断裂后没有人把桌面重新拉起来，用户感知为「闪退」。
2. **更新窗口长时间不输出 ≠ 卡死**。pull 之后的 pm/venv 阶段本身就有 8~15 分钟静默期，且子进程 stdout 是块缓冲、uv 无 TTY 不画进度条。必须先判“在跑”还是“死了”，再决定动不动手。
3. **终端更新为首选执行路径**：为避免 GUI handoff 静默看门狗超时或关窗失联，更新首选直接在终端执行：
   ```powershell
   hermes update --yes --branch main --keep-stash
   ```

## When to Use / 何时使用

出现以下任一情况时使用：

- 点「更新」后 Hermes 窗口消失且不再自动出现（用户常描述为“闪退”）
- **更新窗口/进度停在某一行十几分钟一动不动（最高频的“假卡死”，实际多为 uv 静默下载）**
- 更新过程中报网络错误、TLS unexpected eof 或 `exit 1` 中止
- 更新被中断后提示 `[WinError 5] 拒绝访问` 或 `another process holds the install`
- 更新退出码为 `124`（被 handoff 看门狗掐死）
- `hermes update` 报 `Unable to create '.git/shallow.lock': File exists`
- 更新提示 `⚠ Updating from fork`（假警告）或 git pack-objects BUG
- 更新完成但版本号变小（如 0.21.5 → 0.21.3），或启动时报依赖未完成

## 关键环境事实与路径

| 项目 | 位置 |
|------|------|
| HERMES_HOME（数据根） | `%LOCALAPPDATA%\hermes` |
| 代码仓库（安装根） | `%LOCALAPPDATA%\hermes\hermes-agent`（shallow clone） |
| venv | `%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\python.exe`（shim） |
| pm 运行时 | `%LOCALAPPDATA%\hermes\installs\<installId>\pm-runtime\generations\<gen>` |
| uv 缓存 | `%LOCALAPPDATA%\hermes\cache\uv`（**下载进度的最佳探针**） |
| 桌面程序 | `%LOCALAPPDATA%\hermes\hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe` |
| 桌面用户数据 | `%APPDATA%\Hermes` |
| 日志目录 | `%LOCALAPPDATA%\hermes\logs` |

关键日志与状态文件：

- `logs\desktop.log` — 桌面主进程日志，记录更新交接、venv-blocker 扫描与启动流程
- `logs\desktop-update-handoff.log` — handoff 脚本日志（含 `handoff start`、`relaunching desktop`）。**注意：`update!|` 行是子进程退出时整批落盘的（块缓冲），所有行时间戳相同，不能当作实时进度，也不能用“日志没动”判定卡死**
- `logs\update.log` — `hermes update` 输出，只覆盖到 git pull 阶段，进入 pm/uv 后不再增长
- `logs\update_receipts\latest.json` — **判断成败的唯一权威**：`outcome`、`exit_code`、`stop_reason`、`pm_steps`、`pre_update.sha`、`post_update.sha`
- `logs\update_receipts\pm_*.json` — pm 侧 sync 回执，含 `uv sync exited N` 具体报错
- `.update_exit_code` — 上一轮退出码（如 `1`），**文件 mtime = 该轮退出时刻**，是判断该轮已结束的最快线索
- `.hermes-update-in-progress` — handoff 标记文件，内容为 `<handoffPid>\n<token>`；标记存在时桌面不会被自动拉起
- `%APPDATA%\Hermes\update-check-cache.json` — 桌面端更新角标缓存。**仅缓存，读失败返回 null，可安全忽略**；真实检查走 GitHub API 比对

## 更新交接机制

```
桌面点「更新」→ 释放 venv shim、关闭后端、主动关窗（设计行为）
            → 启动 windows.ps1（handoff，位于 hermes-agent/scripts/desktop-update/）
            → handoff 用自己 pid 认领 .hermes-update-in-progress 标记
            → 运行 venv\Scripts\python.exe -m hermes_cli.main update --yes --gateway --force --branch main --keep-stash
                 └─ 该进程再转发到 .hermes-runtime\python\...、并拉起 pm\worker.py（依赖安装）
            → 成功后由 handoff 负责重启 Hermes.exe，并清理标记
```

**任一环断裂都会导致“窗口关了就不再回来”。handoff 进程是负责重启桌面的唯一角色。**

### 静默看门狗（退出码 124 的来源）

`windows.ps1` 为每个更新步骤套了私有 Windows Job + 空闲看门狗：

| 常量 | 默认值 | 含义 |
|---|---|---|
| `$script:StepIdleTimeoutSeconds` | **600 s（10 分钟）** | 连续静默多久判定卡死 |
| `$script:StepDrainGraceSeconds` | 20 s | 管道排空宽限 |
| 环境变量覆盖 | `HERMES_UPDATE_STEP_IDLE_SECONDS` | 可通过环境变量调大 |

- **判据是双静默**：子进程 stdout/stderr 无输出 **且** `logs/update.log` 的 `(Length, LastWriteTimeUtc.Ticks)` 指纹不变。
- **动作**：`TerminateAndWait($job, 124, 10000)` —— 杀掉**整棵进程树**，以 **124** 退出；若无法确认进程树静止，则以退出码 **7** 收尾（保留标记、不重启桌面）。
- 因此 `hermes update exit code: 1`（子进程自身报错）与 `retry exit code: 124`（被看门狗掐死）是两种截然不同的失败结局。

## 判定「卡死」还是「在跑」（关键前置步）

**默认假设是“在跑”**。使用三个探针交叉验证，禁止仅凭日志停更下结论：

1. **uv 缓存在涨**（最可靠）：
   ```bash
   du -sk "$LOCALAPPDATA/hermes/cache/uv"; sleep 60; du -sk "$LOCALAPPDATA/hermes/cache/uv"
   ```
   增长 = 正在下载。若直连低速（~30 KB/s），下载 150MB+ 会静默几十分钟。
2. **是否存在 `uv.exe` 进程**：
   ```bash
   wmic process where "Name='uv.exe'" get ProcessId,ParentProcessId,CreationDate /format:csv
   ```
3. **新环境目录正在生成**：`installs\<installId>\environments\` 下出现新哈希目录 = 正在编译安装 venv。

补充判据：
- 进程 `CreationDate` 晚于更新开始时刻 → 处于自动重试轮（handoff 默认失败后自动重试一次）。
- 真正的卡死特征：`cache/uv` 60 秒零增长、无 `uv.exe`、无网络连接、CPU 时间不涨。此时方可人工介入。

**估算剩余下载时间 (ETA)**：
1. 本轮总量：`grep -a -o "Downloading [a-zA-Z0-9_.-]* ([0-9.]*MiB)" logs/desktop-update-handoff.log | sed 's/Downloading //' | sort -u | awk -F'[()]' '{s+=$2} END {printf "%.1f MiB\n", s}'`
2. 已下体积：`du -sk cache/uv`
3. 采样速率：`du -sk cache/uv` 采样 100s 的增量。`剩余量 ÷ 速率 = ETA`。

## 已知深坑与机理解析

1. **更新窗口长时间不动（假卡死）**：git pull 后进入 8~15 分钟静默期（pm-runtime 代际准备与 `uv sync` 下载）。子进程块缓冲且无 TTY 进度条，窗口绝无新输出。切忌手动关窗！
2. **`NO_PROXY` 默认含 PyPI 导致 uv 直连超时**：
   - `pm/environment.py` 会将 `HTTP_PROXY/HTTPS_PROXY/ALL_PROXY/NO_PROXY` 原样透传给 uv。
   - 若系统 `NO_PROXY` 尾部包含 `pypi.org,files.pythonhosted.org`，uv 会**强制直连** PyPI。在国内网络下直连速度极慢（~30 KB/s vs 代理 ~200+ KB/s），大包下载极易踩线 `UV_HTTP_TIMEOUT=30s` 静默超时导致 `uv sync exited 1`。
   - **解决**：从用户 `NO_PROXY` 中移除 `pypi.org` 与 `files.pythonhosted.org`，并将 `UV_HTTP_TIMEOUT` 设为 300（白名单允许放行）。
3. **`UV_HTTP_TIMEOUT` 的真实语义是“静默读取超时”**：官方规范明确其为 HTTP 单次读静默超时，并非请求总时长。低速持续传输不会超时，中途 30 秒断流才会报错。白名单 `FORWARDED_UV_SETTINGS` 仅放行 `UV_HTTP_TIMEOUT`，`UV_HTTP_RETRIES` 会被 pm 丢弃。
4. **手动关闭更新窗口导致闪退**：手动关窗会直接杀掉 handoff 进程，即使后台重试成功，也没有角色负责拉起桌面。更新期间切勿关窗，也不要在中途重开桌面。
5. **pm 还原点占用与 `[WinError 5] 拒绝访问`**：
   - 机制：pm 更新工具条目时，会将旧条目重命名为 `.previous-<entry>` 作为还原点。下次更新必须先消费清除陈旧还原点；若因 DLL 锁导致删除失败，整个更新中止并报 `[WinError 5] 拒绝访问`。
   - 坑点：`pm gc` 源码中明确跳过 `.previous-*`，还原点永远不会自动清理，会一直占用磁盘（每份约 200MB+）。
   - 修复：直接将 `tools/.previous-*` 改名为 `.stale-<date>` 移开，更新通过后再物理删除。
6. **`tasklist /m` 误报**：它仅按模块文件名匹配，会把 Git 自身的 `git-remote-https.exe` 加载的 `libcrypto-3-x64.dll` 误报为占用者。
7. **`url.*.insteadOf` 导致假 fork 误报**：
   - `~/.gitconfig` 中若存在 `url."https://user@github.com/".insteadOf = https://github.com/`，`_is_fork()` 不剥离 `user@` 会与官方白名单失配，误报 `⚠ Updating from fork:`。实际拉取路径仍是官方，无功能损害。
8. **浅克隆转完整克隆触发 Git 内核 BUG**：
   - 更新器为计算版本身份会执行 release history fetch，将浅克隆展开为完整克隆（`.git` 膨胀至 ~1.3G）。转换期间易偶发 `BUG: builtin/pack-objects.c: should_include_obj`，属一次性故障，紧接着重试即可通过。
9. **版本号 0.21.5 → 0.21.3 不是倒退**：版本号来自本地计算写入的 `install-stamp.json`，在 shallow clone 够不到 tag 时会回退到 baseline 常量。代码是否前进通过 `git merge-base --is-ancestor <preSha> <postSha>` 验证。
10. **依赖未完成时切忌启动桌面**：若更新中断导致依赖未装全，直接启动桌面会触发桌面自动补依赖，进而导致后端 `exited before port announcement (1)` 并击崩桌面。

## 标准排查与手动更新 SOP

### 1. 只读诊断与状态核查

```powershell
# 确认当前无残留的占用进程
tasklist /V /FO CSV | findstr /I "hermes uv"

# 检查权威回执与退出码
Get-Content "$env:LOCALAPPDATA\hermes\logs\update_receipts\latest.json" -Raw

# 检查残留标记与锁文件
Get-Item "$env:LOCALAPPDATA\hermes\.hermes-update-in-progress" -ErrorAction SilentlyContinue
Get-Item "$env:LOCALAPPDATA\hermes\hermes-agent\.git\shallow.lock" -ErrorAction SilentlyContinue
```

### 2. 状态清理（若上轮已死）

```powershell
# 若存在死主留下的标记，备份并清理
Remove-Item "$env:LOCALAPPDATA\hermes\.hermes-update-in-progress" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\hermes\hermes-agent\.git\shallow.lock" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\hermes\hermes-agent\.git\index.lock" -Force -ErrorAction SilentlyContinue
```

### 3. 执行标准终端更新（推荐方式）

退出所有 Hermes 桌面端与网关进程后，在终端执行：

```powershell
# 确保网络环境健康（NO_PROXY 不含 pypi.org，UV_HTTP_TIMEOUT 充足）
$env:UV_HTTP_TIMEOUT = "300"
hermes update --yes --branch main --keep-stash
```

### 4. 验证与复查

```powershell
hermes update --check
# 期望输出：✓ Already up to date.

git -C "$env:LOCALAPPDATA\hermes\hermes-agent" rev-parse HEAD
git -C "$env:LOCALAPPDATA\hermes\hermes-agent" rev-parse origin/main
# 期望：两处 commit hash 完全一致
```
验证全部通过后，即可正常启动 Hermes 桌面端。
