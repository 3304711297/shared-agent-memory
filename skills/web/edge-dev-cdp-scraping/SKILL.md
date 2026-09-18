---
name: edge-dev-cdp-scraping
description: "抓登录墙内容时必用。用已登录Edge走CDP。Use when scraping login-walled pages via signed-in Edge."
---

# 复用已登录 Edge Dev + CDP 抓取

## 环境事实（本机，2026-09-08 实证）
- Edge Dev 路径：`C:\Program Files (x86)\Microsoft\Edge Dev\Application\msedge.exe`
- 默认 profile：`%LOCALAPPDATA%\Microsoft\Edge Dev\User Data`（扩展在 `Default\Extensions`，基线 10 个）
- chrome-devtools MCP 默认连 **Chrome** 的 `DevToolsActivePort`；本机 Chrome 未运行 → "Could not connect to Chrome"。本机主力是 Edge Dev。
- 组策略 `RemoteDebuggingAllowed` / `DevToolsRemoteDebuggingAllowed` 均为 1（允许），**排除策略封锁**。

## 默认 profile 的 CDP 通道 —— 现已可用（2026-09-18 复查，推翻旧结论）
- 旧结论「默认 profile 端口起不来」**已失效**：`netstat` 有 `127.0.0.1:9222 LISTENING`，ws 直连实测通过（`Edg/155`）。根因是 `Local State` 里 `devtools.remote_debugging.user-enabled=true` —— chrome://inspect 的勾选一旦生效，重开浏览器即监听。
- `DevToolsActivePort` 内容 = `9222` + `/devtools/browser/<uuid>`。
- 仍**别做**无效尝试：给已在运行的 Edge 挂 `--remote-debugging-port`（只在冷启动生效，必须重启）；清代理变量；显式 `--user-data-dir`；`--remote-allow-origins=*`；删陈旧 `DevToolsActivePort`。

### 三个坑（实测）
1. `http://127.0.0.1:9222/json/version` 返回 **404**（Chrome 147+ 默认 profile 关闭 HTTP 发现）。**别据此判定端口不通** —— 用 `DevToolsActivePort` 的 ws 路径，或裸 `ws://127.0.0.1:9222/devtools/browser`。
2. uuid 路径偶发握手超时（瞬时抖动）；换裸 `/devtools/browser` 重试。
3. **browser-harness**：设 `BU_CDP_WS`/`BU_CDP_URL` → `CDPClient`（10s 握手死线，抖动即 fail）；不设 → `_PatientCDPClient`（`open_timeout=None` 无限等）+ 自动发现 + 自带 404→ws 回退。**结论：别设 BU_CDP_WS，零配置自己发现最稳。**
- 代理变量（`HTTP_PROXY`/`ALL_PROXY`=3067）**不阻挡** daemon→`127.0.0.1:9222` 的 ws 连接（带代理实测跑通）；只影响 `curl`/`urllib` 的 `/json/*` HTTP 请求（受 `no_proxy` 控制）。
- 每次连接会在浏览器里**新建后台标签页**（`Target.createTarget` + `setFocusEmulationEnabled`），用完 `Target.closeTarget` 关闭；用户的既有标签不受影响。

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
