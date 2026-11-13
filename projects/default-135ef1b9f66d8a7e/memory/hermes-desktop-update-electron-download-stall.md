---
name: hermes-desktop-update-electron-download-stall
description: Hermes 桌面更新卡在「Preparing Node dependencies」的根因与处置：@electron/get 默认不走代理，单连接被限速到 KB/s 且无超时无续传；含缓存预置修复法与两个启动陷阱
metadata:
  node_type: memory
  type: project
---

**Hermes 桌面更新「一直卡着」的定位与处置**（2026-11-13 实战验证，v0.23.1+1895 → +4462 期间）：

## 症状

`hermes update` 或桌面端更新跑到 `→ Preparing Node dependencies…` / 阶段 `Updating Node dependencies` 后长时间无输出、无报错，日志停在原地。更新期间网关被暂停、桌面端已退出，用户体感就是「Hermes 卡死了」。

## 根因（已用证据确认，非猜测）

1. **卡点是 Electron 二进制下载**：`node_modules/.pnpm/electron@<ver>/node_modules/electron/install.js` 走 `@electron/get` 从 GitHub Releases CDN 取 `electron-v<ver>-win32-x64.zip`（约 150MB+）。
2. **`@electron/get` 默认不使用代理**：`node_modules/@electron/get/dist/index.js` 里只有 `if (process.env.ELECTRON_GET_USE_PROXY) initializeProxy()` 才挂 `undici` 的 `EnvHttpProxyAgent`。所以哪怕 Windows 系统代理已开、桌面端也把 `HTTPS_PROXY` 注入给了更新子进程，这一步依然直连。
3. **单连接被限速且永不放弃**：实测该连接停在约 **9–13 KB/s**（每 10 秒只涨 80–130 KB），进程 IO 计数几乎不动；`@electron/get` 无读超时、不支持续传，会一直爬到几小时后才可能完成。同 URL 新开连接直连 10 MB/s、走本地代理 24 MB/s —— 说明是**连接级劣化，不是网络整体不通**，所以「等一会就好」不成立。

## 快速判定（30 秒内确认是不是这个问题）

- 握手日志阶段时间线：`%LOCALAPPDATA%\hermes\logs\desktop-update-handoff.log`（看 `stage:` 行，停在 `Updating Node dependencies` 即命中）。
- 半成品文件与增速：`%TEMP%\electron-download-*` 下的 `electron-v*-win32-x64.zip`，连续采样两次 size。
- 连接归属：`Get-NetTCPConnection -OwningProcess <node pid>` 应看到 `:443` 到 GitHub CDN 的 Established 连接，而该 node 进程 CPU 近乎 0。
- 阶段回执：`%LOCALAPPDATA%\hermes\logs\update_receipts\latest.json` 的 `outcome` / `stages`（`plan`/`apply`/`deps` 成功、无 `build` 即为卡在构建）。

## 修复：预置 Electron 缓存 + 重跑（2026-11-13 实测 4 分 53 秒完成）

缓存键 = `sha256("https://github.com/electron/electron/releases/download/v<版本>")`（`@electron/get` 的 `Cache.getCacheDirectory`：去掉 query/hash，pathname 取 dirname）。把 zip 放到
`%LOCALAPPDATA%\electron\Cache\<该哈希>\electron-v<版本>-win32-x64.zip`，installer 命中缓存后秒级解包，**不需要给更新进程注入任何代理变量**（避免污染随后重启的网关）。

1. 用代理下载 zip（`curl -x <本地 HTTP 代理> -L`），约 10 秒。
2. **必须校验**：对比该版本 `SHASUMS256.txt` 里 `electron-v<版本>-win32-x64.zip` 的 sha256，一致才用。
3. 中断卡住的链路：对更新主进程 python 执行 `taskkill /F /T /PID <pid>`（node 子进程挂在 JobObject 上，会随之全灭）。
4. 重跑 `%LOCALAPPDATA%\hermes\bin\hermes.cmd update --yes --gateway --branch main --keep-stash`。它会打印 `hermes: finishing an interrupted source update...`，Node 依赖阶段秒过，随后依次跑 TUI/Web UI/desktop 打包。
5. 收尾无需手工清理：`.hermes-update-in-progress` 标记与 `.git/hermes-update.lock` 按 **pid + 进程创建时间**判活（不是按时间老化），owner 死了自动失效；重跑结束会自行移除标记。

## 成功判据（缺一不可，别只看回执 success）

- `apps/desktop/release/win-unpacked/Hermes.exe` **时间戳必须是刚才**（打包失败时回执可能仍写 success，而 exe 还是旧的 —— 这正是「回执 success 但时间戳没变 = pack 阶段失败」的判断依据）。
- `update_receipts/latest.json`：`outcome: success` 且 `stages` 含 `build` success。
- `git -C hermes-agent log --oneline -1` 为新提交、`git status` 干净；`gateway_state.json` 里 `gateway_state: running`。

## 两个启动/收尾陷阱

1. **`ELECTRON_RUN_AS_NODE=1`**：在 Electron 宿主（WorkBuddy / 各类 Electron IDE）的子 shell 里直接 `Start-Process Hermes.exe`，会继承该变量，Hermes.exe **立刻以 exit 0 退出**、什么都不显示。重启桌面端前必须先 `Remove-Item Env:ELECTRON_RUN_AS_NODE`。
2. **误报弹窗**：用过 `taskkill` 中断更新后，下一次启动桌面端会弹出「Hermes couldn't finish updating … Update failed (exit 1)」，文案还带「You're still on the previous version」。这是 `update-handoff-report.ts` 消费 `readAndConsumeHandoffResult` 读到那次被杀的 handoff 记录的兜底文案（无 stop receipt 时 `explained === null` 就套这段通用文本），**与真实状态无关**；点 Close 即可，不要点 Try again。判断真实状态只看上面三条成功判据。

## 旁证

同一轮更新里无关紧要的噪声：`Could not refresh release history … timed out after 30 seconds`（tag 历史拉取超时，只影响版本号标签显示）、`Elevated ACL repair skipped`（未提权，跳过 junction/ACL 修复）、`Windows cua-driver refresh deferred`（需 UAC，需在交互终端手动 `hermes computer-use install --upgrade`）。
