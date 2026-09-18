# Edge Dev 复用已登录 Profile + CDP 抓取（2026-09-08 实证·历史归档）

> ⚠️ **方案升级与归档说明（2026-09-17）**：
> 本文记录的「独立 Profile + 命令行 CDP 抓取」妥协方案及 `edge-dev-cdp-scraping` 技能已正式废弃归档。
> 现已由 **Tencent/BrowserSkill**（基于 Edge 官方扩展 + 本地 bsk CLI/Daemon，免 CDP 远程调试弹窗，独立 Agent Window 隔离运行，原生复用日常 Profile 登录态）全面替代。
>
> **⚠️ 后续更正（2026-09-18）**：
> ① 技能文件已于本日**实际删除**（此前 09-17 记为已删但执行遗漏）；两块独有知识已迁移——X/Twitter 抓取通道表 → `browser-skill` 技能；Edge 扩展被物理删除的高危坑 → `cross-agent-collaboration/references/browser-boundary.md`。
> ② 本文「核心结论」整节**已失效**：Edge Dev 默认 Profile 的 9222 CDP 端口**现已可用**（实测 `Edg/155` ws 直连通过）。根因是 `Local State` 的 `devtools.remote_debugging.user-enabled=true` 已持久化——在 `edge://inspect` 勾选过一次后，重开浏览器即监听。2026-09-08 的失败结论不再成立，勿据此判断。
> ③ 扩展基数为 **13**（非本文所记的 10），且计数需排除 Edge 自建的 `Temp` 空目录。

## 环境事实

| 项 | 值 |
|---|---|
| Edge Dev 可执行文件 | `C:\Program Files (x86)\Microsoft\Edge Dev\Application\msedge.exe` |
| 默认 profile | `%LOCALAPPDATA%\Microsoft\Edge Dev\User Data` |
| 扩展目录 | `Default\Extensions`（本机基线 **13** 个；计数须排除 Edge 自建 `Temp` 目录） |
| chrome-devtools MCP | 默认连 **Chrome** 的 `DevToolsActivePort`；本机 Chrome 未运行 → `Could not connect to Chrome`。主力是 Edge Dev |
| 组策略 | `RemoteDebuggingAllowed` / `DevToolsRemoteDebuggingAllowed` 均为 `1`（允许）→ **排除策略封锁** |

## 核心结论：默认 profile 挂不上调试端口 —— **本节已失效，见顶部更正 ②**

- 给**已运行**的 Edge 加 `--remote-debugging-port` 无效，该参数只在冷启动生效，必须重启浏览器。
- 冷启动带 `--remote-debugging-port=9222` **端口仍不监听**：`netstat` 无 LISTENING，`DevToolsActivePort` 文件也不更新（残留旧 GUID）。
- 已排除的四条路径，全部失败，勿重复：
  1. 清空代理变量（`HTTP_PROXY`/`HTTPS_PROXY`/`ALL_PROXY`）+ `--proxy-bypass-list=<-loopback>`
  2. 显式 `--user-data-dir` 指向默认 profile
  3. 追加 `--remote-allow-origins=*`
  4. 删除陈旧 `DevToolsActivePort` 后重启

**规律：新建独立 `user-data-dir` 时端口正常；用户默认 profile 时端口起不来。**
因此「拿登录态」这条路当前不通，动手前必须先问用户。

## 退而求其次：无登录态能拿到的

1. 建标签页：`curl -X PUT "http://127.0.0.1:<port>/json/new?<url>"`（GET 返回 405）
2. `pip install websocket-client` → `websocket.create_connection("ws://.../devtools/page/<id>")`
3. `Runtime.evaluate` 取 `document.body.innerText`

## X/Twitter 通道优先级

| 通道 | 主文 | 回复 |
|---|---|---|
| `api.fxtwitter.com/<user>/status/<id>` | ✅ 含完整元数据（views/likes/replies/bookmarks） | ❌ |
| `api.vxtwitter.com/<user>/status/<id>` | ✅ 精简 JSON | ❌ |
| 独立 profile CDP 直开 x.com | ✅ | ⚠️ 未登录只渲染前 3 条 |
| `zamantika.com/profile/<user>` 镜像 | ✅ 时间线含部分回复 | ⚠️ 部分 |
| nitter 各实例 / xcancel | ❌ 全部挂掉或 anti-bot | ❌ |
| `cdn.syndication.twimg.com` | ❌ 空 | ❌ |

- 未登录态下 "See all the replies" 是 `<h2>` 元素，**合成 MouseEvent 与 CDP `Input.dispatchMouseEvent` 均被忽略**。

## 操作铁律（不碰用户浏览器）

1. 需要登录态 → **先问用户**，明确告知会重启浏览器并打断当前标签页。
2. 关闭只用 `CloseMainWindow()` 优雅退出（让 Edge 保存会话），**严禁 `Stop-Process -Force`**。
3. 操作前后各统计一次 `Default\Extensions` 子目录数并比对，异常立即停止并报告。
4. 恢复启动带 `--restore-last-session`。
5. 临时 profile 放 `%TEMP%` 且目录名以 `edge-cdp-` 开头；收尾按命令行精确匹配 PID 清理：

```powershell
Get-CimInstance Win32_Process -Filter "name='msedge.exe'" |
  Where-Object { $_.CommandLine -match 'edge-cdp' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

`wmic process where "name='msedge.exe'" get ProcessId,CommandLine /value` 常返回空 CommandLine（权限限制），**必须用 `Get-CimInstance` 替代**。

6. 失败即停，**连续重试不超过 2 次**；第 3 次前必须回头问用户。

## 关联

- ~~本机技能：`edge-dev-cdp-scraping`（Hermes 侧）~~ → **已于 2026-09-18 删除**。现行方案：`browser-skill`（bsk）；读页面加速：`bsk-compact-page-read`
- 相关教训：抓取连撞 2 次防爬即停手问用户，不得穷举镜像或擅起新浏览器（X 通道表已迁入 `browser-skill`）
