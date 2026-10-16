---
name: hermes-update-workflow-and-benchmarks
description: Hermes Agent 两检出双端同步与预检预热流水线：部分克隆 blob:none 延迟拉取 120s 超时机理、20 个启动关键文件定向预热实测（0.07s）、积压 >1500 提交条件全量预热、去 --keep-stash 与 desktop 源码 pack 闭环
metadata:
  node_type: memory
  type: project
---

# Hermes Agent 更新流水线与定量基准 (2026-10-16 定案)

## 架构：两个独立检出双端对齐

NousResearch/hermes-agent 在本机由两个独立的检出构成，各自跟踪官方 `main` 分支：

| 检出路径 | 角色与定位 | Git 克隆形态 | 构建/运行方式 |
|---|---|---|---|
| `%LOCALAPPDATA%\hermes\hermes-agent` | CLI 与 Agent 托管运行时（`hermes` 核心） | `blob:none` 部分克隆（promisor=true） | 由 `hermes update` 自身维护更新与 venv |
| `%USERPROFILE%\hermes-agent-src` | Electron 桌面端（GUI）源码构建树 | 完整克隆（full clone，无 promisor） | `npm --prefix apps/desktop run pack` 产出 `apps\desktop\release\win-unpacked\Hermes.exe` |

**重要定位铁律**：`%USERPROFILE%\hermes-agent-src` 是当前桌面应用的原生运行与快速重建位置（2.8GB，含完整 node_modules、.cache、build、dist）。快捷方式直接指向其 `release\win-unpacked\Hermes.exe`，必须完整保留该目录与构建缓存，**严禁主动清理或提议瘦身**。

---

## 更新假死与 120s 超时的底层根因

### 1. 现象
长期不更新（如积压数千个提交）或偶发大版本升级时，执行 `hermes update` 报：
```
Command '['git', ..., 'cat-file', 'batch']' timed out after 120 seconds
```
但退出后工作区干净，`pre_update.sha == post_update.sha`，安装本身完好无损。

### 2. 根因链
1. 安装目录 `%LOCALAPPDATA%\hermes\hermes-agent` 是 **`blob:none` 部分克隆**（`.git/config` 中包含 `remote.origin.promisor = true` 与 `partialclonefilter = blob:none`）。
2. 在 `git fetch` 拉取新提交后，更新器进入拉取后语法预检阶段，需要读取新远端提交（`origin/main`）上的启动关键文件。这些 blob 对象本地完全不存在，触发 Git 按需延迟拉取（lazy fetch）。
3. **关键缺陷**：`git cat-file --batch` **完全不合并 promisor 请求**！每个缺失的对象都会单独 fork 并 spawn 一次 `git fetch --filter=blob:none --stdin` 以及一次 `git index-pack --promisor`。
4. **硬编码超时死线**：`hermes_cli/update_cmd_commit.py:500` 对预检调用硬编码了 `timeout=120`，而正常网络 fetch 阶段使用的是 `update_cmd.py:224 NETWORK_GIT_TIMEOUT_SECONDS = 300`。
5. 当缺失对象存在冷启动（首个缺失对象按需拉取冷启动耗时高达 22.6s~71.4s）或缺失对象较多时，必定瞬间撞死在 120 秒超时线上。

---

## 关键定量实测事实（实跑取证）

| 测量项 | 实测性能与数据 | 说明与结论 |
|---|---|---|
| 单个缺失对象按需拉取（**冷启动**） | **22.6s / 71.4s** | 取决于网络代理与首次 promisor 握手开销 |
| 单个缺失对象按需拉取（热态） | ~1.2s – 1.6s | 每次依然新起子进程，耗时线性累加 |
| 100 个缺失对象走 `cat-file --batch` | 164s（**100 次 fetch**） | 完全不并发、不合并，1.6s/对象 |
| 缺口对象规模（落后 4200+ 提交时） | **184,679 个 blob** | 占可达对象的 35%，若全靠懒加载需 80+ 小时，**根本无法自然收敛** |
| `git cat-file --batch-check` 是否触发拉取 | **会触发拉取**（pack 数 4→5） | 只输出元数据文本、不吐二进制，极适合管道预热 |
| `rev-list --objects --missing=print origin/main` | 3.9s 热 / **41.9s 冷** | 遍历 52.8 万全量对象树，耗时较长 |
| `rev-list --count HEAD..origin/main` | **0.05s** | 仅统计提交拓扑距离，不遍历对象树，极速判定 |
| 定向预热 20 个启动关键文件（全在本地时） | **0.07s** | 消除 120s 超时的最轻量关键杠杆 |

**结论**：120s 超时的真凶是**首次按需拉取的冷启动开销**。预检最多只读取 20 个启动关键文件，但只要首个文件未命中，就会在 120s 预算内被吃掉数十秒冷启动时间。因此，**在执行更新前预先将这 20 个文件的 blob 取到本地**，即可把冷启动完全移出 120s 预算之外。

---

## 历史更新命令审查与避坑要点

1. **`npm run package` 根本不存在**：
   - `apps/desktop/package.json` 的 scripts 仅有 `pack`、`dist`、`builder`、`payload`、`dist:bundled`、`dist:win`，**绝无 `package` 指令**。
   - 过去使用 `npm run package` 会直接报错，导致打包实际上从未执行；换为 `npm --prefix apps/desktop run pack` 才能真正刷新 `release/win-unpacked/`。
2. **`npm run build` 冗余**：
   - `pack` 的定义即为 `npm run build && npm run builder -- --dir --publish never`，单独跑 `npm run build` 纯属重复构建。
3. **分号 `;` 掩盖错误致双端错配**：
   - 若用 `;` 拼接命令，当 `hermes update` 失败（exit 1）时后续的 `git pull` 与桌面构建依然会继续跑，导致 CLI 停在旧 commit，而桌面源码推进到新 commit，出现静默版本错配。必须使用 `&&` 或在 PowerShell 中通过 `$LASTEXITCODE -ne 0` 显式 `throw` 中断。
4. **手动更新严禁使用 `--keep-stash`**：
   - `--keep-stash` 是 Hermes 桌面端自动更新交接（desktop updater handoff）的专属参数（源码注释：`leave edits parked rather than re-apply silently`）。手动在终端执行更新时若带 `--keep-stash`，会导致安装目录原有的任何本地改动在更新后被静默遗留在 stash 中而不还原。手动终端更新应去除该参数。
5. **`.git/hermes-pack-tidy.lock` 是内核锁**：
   - `git_pack_tidy.py:343` 内部使用的进程互斥锁，持有进程退出即自动释放，**不是**陈旧死锁文件，切勿随意手工删除。

---

## 权威更新流水线脚本 (PowerShell)

在 PowerShell 终端（`pwsh`）中执行以下标准化流水线：

```powershell
$R = "$env:LOCALAPPDATA\hermes\hermes-agent"
git -C $R fetch --no-tags origin "+refs/heads/main:refs/remotes/origin/main"

# 积压过大时才全量预热（判断只要 0.05 秒）
if ([int](git -C $R rev-list --count HEAD..origin/main) -gt 1500) {
    Write-Host "积压过多，全量预热中（约 3 分钟）..."
    git -C $R fetch --no-tags --refetch --filter=blob:limit=100m origin "+refs/heads/main:refs/remotes/origin/main"
}

# 提前把预检要读的 20 个启动关键文件取到本地（全在本地时 0.07 秒）
$crit = 'pyproject.toml','hermes_bootstrap.py','hermes_cli/_parser.py','hermes_cli/_launchers.py',
        'hermes_cli/_early_recovery.py','hermes_cli/update_lock.py','hermes_cli/update_custody.py',
        'hermes_cli/update_handoff.py','hermes_cli/venv_sync.py','pm/__init__.py','pm/environments.py',
        'hermes_cli/main.py','hermes_cli/config.py','hermes_cli/__init__.py','hermes_cli/web_server.py',
        'cli.py','run_agent.py','model_tools.py','toolsets.py','hermes_constants.py'
($crit | ForEach-Object { "origin/main:$_" }) | git -C $R cat-file --batch-check | Out-Null

hermes update --yes --branch main
if ($LASTEXITCODE -ne 0) { throw "hermes update 失败，已中止" }

Set-Location "$env:USERPROFILE\hermes-agent-src"
git pull
if ($LASTEXITCODE -ne 0) { throw "git pull 失败，已中止" }
npm --prefix apps/desktop run pack
```

### 关键细节说明
- `$crit` 清单来源为上游 `hermes_cli/update_cmd.py` 的 `_UPDATE_CRITICAL_FILES`（20 个）。即使上游偶有增删，该预热依然保护绝大多数关键入口，不会恶化或阻塞。
- `throw` 会立即截断批处理后续语句，`Set-Location` 不会覆盖前面的 `$LASTEXITCODE`。
- 构建完成后，桌面快捷方式直接启动 `release\win-unpacked\Hermes.exe` 即可。

**Why:** 根治 `blob:none` 部分克隆下长期不更新导致的 120s 语法预检死锁，消除错误更新参数与冗余构建步骤，确保 CLI 运行时与桌面源码构建树严格原子同步。
**How to apply:** 凡需更新 Hermes，严格执行上述 PowerShell 脚本；更新异常时参考本文定量指标排查 promisor 延迟拉取状态。
