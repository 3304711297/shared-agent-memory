---
name: karing-gemini-node-test
description: Karing 测 Gemini 各节点地区封锁的完整方法论（暂停待续）：节点来源、Clash API 坐标、判定逻辑、自建 sing-box 测试环境与坑
metadata:
  node_type: memory
  type: project
  originSessionId: sess_1fbcffe3-2cf3-43db-a794-42103d6b105a
---

用户想测 Karing 里 liangxin.xyz（59 节点，订阅 `https://liangxin.xyz/api/v1/liangxin?OwO=f71d26b69311146a74cdad980c62e354`）和搅局者（11 节点，订阅 `https://sub.jjz127ab.top/subscribe/0decc9d3b551b762595cb37ece94b977`）两组节点哪些能用 Gemini——普通节点访问 generativelanguage.googleapis.com 返回「地区不支持」。**2026-09-06 用户拍板暂停，以后再研究。**

**Why:** 全量 70 节点逐个切+测太慢（每节点 >20s，总耗时 20+ 分钟），用户等不了主动叫停。

**How to apply（恢复研究时直接按此执行，全部已验证可用）：**

1. **判定逻辑（无需真 key）**：请求 `https://generativelanguage.googleapis.com/v1beta/models?key=test`——403 且 body 含 "location is not supported" = 地区被封；400 API_KEY_INVALID = 地区放行。看状态码即可区分。

2. **Karing 内部坐标（已实测）**：
   - Clash API：`127.0.0.1:3057`，secret `91777b8aba027172`（在 `%APPDATA%\karing\karing\service_core.json` 的 experimental.clash_api 和 service.json 里）。注意：**Karing 未连接（红叉状态）时核心进程不跑，3057/3065/3066/3067 全部不监听**，先让用户在界面点连上（绿勾）。
   - 混合代理端口：3065(直连)/3066(proxy)/3067(规则分流，系统代理用的就是它)。日志证实 Karing 自己的测速也走 3057 的 `/proxies/{name}/delay` 接口。
   - `127.0.0.1:8614` 是 Karing GUI 心跳端口，只回固定字节，不是代理也不是 API，别浪费时间去探测。
   - Clash API 里只有 `GLOBAL`(Fallback 型) 和 `urltest_out` 两个组，**Fallback 不能 PUT 切换**——程序化切节点要自建 selector（见下）。
   - Karing 切节点本质是改 `karing_subscribe_use.json` 的 select_default + 重启核心，无干净程序化接口。

3. **订阅拉取坑**：liangxin 订阅默认被 Cloudflare 盾拦（403），**带 UA `Karing/1.2.24; sing-box 1.13.19` 即可 200**，返回 sing-box JSON；搅局者订阅返回 base64（含 anytls/hysteria2 分享链接，需自行解码转 sing-box outbound；anytls 格式 `anytls://password@host:port?sni=xx#tag`）。

4. **自建测试环境（不碰用户 Karing 状态，推荐方案）**：下载官方 sing-box（GitHub v1.13.19 走 3067 代理），生成配置：全部节点做 outbound + 顶部加一个 `type:selector` 的 `sel` 组 + mixed 入站 `127.0.0.1:3167` + clash_api `127.0.0.1:3168`（避开 Karing 的 3057-3067）。跑起来后循环：PUT `/proxies/sel` 切节点 → sleep 0.5-1s → 走 3167 请求 Gemini 看状态码。sing-box check -c 校验配置后再 run。

5. **测试脚本两大坑（已踩）**：① 环境变量残留 `http_proxy=127.0.0.1:3067`，所有 curl/python 必须显式 `--noproxy '*'` 或 `ProxyHandler({'http':'http://127.0.0.1:3167',...})`，否则请求全撞死在死端口；② Python heredoc 里 Windows 路径别写 `t+'\'+f`（转义坑），用 `os.path.join`。

6. **加速思路（未验证，恢复时可先试）**：瓶颈在每节点连接建立+TLS 握手。可并行化：起 N 个 sing-box 实例各绑不同入站端口分段承包节点；或先用 Karing 自带测速剔除死节点再测 Gemini；或对 CONN_FAIL 的节点直接跳过不重试。

相关：[[user-windows-environment]]（3067 代理端口规范）、[[edge-dev-cdp-mcp-setup]]
