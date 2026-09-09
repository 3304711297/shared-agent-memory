---
name: edge-dev-cdp-scraping
description: Use when scraping login-walled pages via signed-in Edge.
---

# 复用已登录 Edge Dev + CDP 抓取

## 环境事实（本机，2026-09-08 实证）
- Edge Dev 路径：`C:\Program Files (x86)\Microsoft\Edge Dev\Application\msedge.exe`
- 默认 profile：`C:\Users\VOS-User\AppData\Local\Microsoft\Edge Dev\User Data`（扩展在 `Default\Extensions`，基线 10 个）
- chrome-devtools MCP 默认连 **Chrome** 的 `DevToolsActivePort`；本机 Chrome 未运行 → "Could not connect to Chrome"。本机主力是 Edge Dev。
- 组策略 `RemoteDebuggingAllowed` / `DevToolsRemoteDebuggingAllowed` 均为 1（允许），**排除策略封锁**。

## 已知阻塞（未解决，勿重复试）
- 给**已在运行**的 Edge 挂 `--remote-debugging-port` 无效：该参数只在冷启动生效，必须重启浏览器。
- 冷启动带 `--remote-debugging-port=9222` **端口仍不监听**（netstat 无 LISTENING，`DevToolsActivePort` 也不更新）。已试且全部失败：
  1. 清代理变量（HTTP_PROXY/HTTPS_PROXY/ALL_PROXY 置空）+ `--proxy-bypass-list=<-loopback>`
  2. 显式 `--user-data-dir` 指向默认 profile
  3. 加 `--remote-allow-origins=*`
  4. 删除陈旧 `DevToolsActivePort` 后重启
  → **结论：独立 profile（新建 user-data-dir）端口正常；用户默认 profile 端口起不来。** 需要登录态时此路不通，先问用户再动手。

## 生效的做法（无登录态可拿到的部分）
1. `curl -X PUT "http://127.0.0.1:<port>/json/new?<url>"` 建标签页（GET 会 405）
2. `pip install websocket-client` → `websocket.create_connection(ws://.../devtools/page/<id>)`
3. `Runtime.evaluate` 取 `document.body.innerText`

## X/Twitter 抓取通道优先级
| 通道 | 主文 | 回复 |
|---|---|---|
| `api.fxtwitter.com/<user>/status/<id>` | ✅ 含完整元数据 | ❌ |
| `api.vxtwitter.com/...` | ✅ 精简 JSON | ❌ |
| 独立 profile CDP 直开 x.com | ✅ | ⚠️ 未登录只渲染前 3 条 |
| `zamantika.com/profile/<user>` 镜像 | ✅ 时间线含部分回复 | ⚠️ 部分 |
| nitter 各实例 / xcancel | ❌ 全挂 / anti-bot | ❌ |
| `cdn.syndication.twimg.com` | ❌ 空 | ❌ |

- X 未登录态下 "See all the replies" 是 `<h2>` 元素，**合成 MouseEvent 与 `Input.dispatchMouseEvent` 均被忽略**，必须登录。

## 铁律：不碰用户浏览器
1. 需要登录态 → **先问用户**，说清要重启浏览器（会打断当前标签页）。
2. 关闭只用 `CloseMainWindow()` 优雅退出（让 Edge 保存会话），**禁止直接 `Stop-Process -Force`**。
3. 启动/关闭前后各数一次 `Default\Extensions` 子目录数量并比对；异常立即停止并报告。
4. 恢复时带 `--restore-last-session`。
5. 临时 profile 必须放 `%TEMP%` 且以 `edge-cdp-` 开头，收尾按命令行精确匹配 PID 清理：
   ```powershell
   Get-CimInstance Win32_Process -Filter "name='msedge.exe'" |
     Where-Object { $_.CommandLine -match 'edge-cdp' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
   ```
   `wmic ... get ProcessId,CommandLine /value` 常返回空 CommandLine（权限限制），**改用 `Get-CimInstance`**。
6. 失败即停，**连续重试不超过 2 次**；第 3 次前必须回头问用户。
