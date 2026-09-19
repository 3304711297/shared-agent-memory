---
name: local-proxy-client-diagnostics
description: "本地代理排查时必用。查配置与实时探活诊断代理客户端。Diagnose local proxy clients from config and live probes."
version: 0.1.0
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [proxy, vpn, networking, diagnostics, karing, tun]
    related_skills: [domain-intel, pinggy-tunnel]
---

# Local Proxy Client Diagnostics

Audit a desktop proxy/VPN client (Karing, Clash Verge, v2rayN, …) by reading its on-disk config, testing each listening port, and reading its service log — then deliver findings as a severity-sorted decision table. Diagnosis only: never rewrite a running client's config.

## When to Use

- User reports "代理开了但上不去" / asks whether their proxy settings have problems
- User asks for an audit or optimization list for a proxy client
- You need to prove whether a failure is routing, DNS, or a dead upstream node

Don't use for: passive recon of a remote domain (`domain-intel`), or exposing a local port publicly (`pinggy-tunnel`).

## Prerequisites

- `curl` (git-bash on Windows), `netstat`, and the client's config dir.
- Locate the config dir with `search_files(pattern='*<client>*', target='files', path='C:/Users/<user>/AppData')` — don't guess; Roaming vs Local varies per client.

## Procedure

1. **Locate config + confirm the client is running.** `search_files` for the client name under AppData; confirm the process (`tasklist //FI "IMAGENAME eq <client>.exe"`) and the listening ports (`netstat -ano | grep -E ":(<ports>)\b"`).
   *Criterion:* you have the config dir path and the set of listening ports with their owning PID.

2. **Read the config files.** Small ones with `read_file`; anything >50 KB (subscription lists) parse with `execute_code` + `json.load` and summarize — never dump raw. Capture: inbound ports, selected node, DNS mode, TUN state, auto-switch settings, subscription health.
   *Criterion:* you can state which node is selected and what the rule/final outbound is.

3. **Read the health data already on disk before testing anything.** Subscription JSON normally carries a per-node latency/error field. A node whose field is `连接超时` is already known-dead — no probe needed.
   *Criterion:* healthy-vs-total count per subscription.

4. **Live-test each listening port, isolating layers.** Run the same request through each port:
   `curl -4 -s -o /dev/null -w "code=%{http_code} ip=%{remote_ip} t=%{time_total}\n" --max-time 15 -x http://127.0.0.1:<port> https://www.baidu.com`
   and again against an external URL.
   *Criterion:* per port you know: direct works / proxy works / neither.

5. **Discriminate routing vs upstream.** If a tunnel is built but the request hangs, re-run with `-v`: `CONNECT ... 200 Connection established` followed by a timeout means routing and the client are fine and the **upstream node is unreachable**.
   *Criterion:* you can say "node dead" vs "rule wrong" with evidence.

6. **Probe the node's host:port directly** (`timeout 4 bash -c "(echo > /dev/tcp/<host>/<port>)"`) across several ports on the same hostname. All closed ⇒ the whole provider/airport is down, not one node; switching nodes inside it will not help.
   *Criterion:* single-node vs whole-provider failure distinguished.

7. **Grep the client's service log** for `ERROR` (usually a `service_core.log` next to the config) and read the last ~30 lines — it names the failing outbound tag and the dial timeouts directly.
   *Criterion:* root cause is quoted from the log, not inferred.

8. **Deliver a decision table and stop.** See below.

## Decision Table Deliverable (this user's format)

Columns: `# | 级别 | 问题 | 现状 | 为何是问题 | 建议 | 代价`. Sort by severity (🔴 严重 → 🟡 中 → 🟢 低). Every row must carry the **代价** (cost/side-effect) of the fix.

Then a short "最小修复" list — the 2–3 items that restore function — and an explicit sign-off request.

**Never auto-apply.** For config changes: list candidates + the client's official default + the cost, and wait for the user to pick. This is a standing rule for this user.

## 节点可用性筛查（判定某节点能否调用上游 AI 服务）

场景：用户有多个订阅/节点，问“哪些节点能稳调 g​emini/某上游”。**核心难点是找到零配额判别器 + 排除网络假象。**

### 第一原则：区域检查只在生成路径上

实测（2026-09-20，Antigravity）——**这些端点不能用来判别**：

| 端点/思路 | 对区域受限节点 | 为何不适用 |
|---|---|---|
| `loadCodeAssist` | 返回 **200** | 不经过区域检查 |
| `countTokens` | 返回 **200** | 同上 |
| 参数校验错误（空 contents / 非法 model / 非法 topK / 非法 role） | 400，但与可用节点**结果相同** | 校验**先于**区域检查 |
| 域名级延迟测试（`delay?url=`） | 全部成功 | 只测 TCP+TLS，不触及区域门 |

曾据此误判「53/63 可用」，实际只有 8 个能真调用——**探针没走到区域检查那一层，就只是连通测试。**

**推论**：接到“帮我看哪些节点能用 XX 服务”时，先问一句「这个服务的区域/权限门到底卡在哪一层」——
把门定位到具体路径后，才能设计出“能走到那道门但不产生实际消耗”的探针。

### 零消耗判别器（首选）

**必须打生成端点，且请求体要「校验通过但不产生输出」**：

```json
POST https://daily-cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse
Authorization: Bearer <antigravity access_token>
User-Agent: antigravity/2.15.0 (windows/amd64)
{"model":"gemini-3.8-flash-high","project":"<cloudaicompanionProject>",
 "request":{"contents":[{"role":"user","parts":[{"text":""}]}],
            "generationConfig":{"maxOutputTokens":1}}}
```

| 响应 | 含义 |
|---|---|
| `400 User location is not supported for the API use.` | 🔴 区域拒绝 |
| `200` + `finishReason: MAX_TOKENS` + `promptTokenCount:1, totalTokenCount:1` | 🟢 通过（**仅 1 输入 token、零输出**） |
| 连接异常/超时 | ⚪ 网络层问题，与区域判定无关，需单独归因 |

要点：`parts:[{text:""}]` 是关键（校验通过但不生成）；必须带 `project`；model 建议带 `-high` 后缀。

### 必须多轮采样——单次结论不可信

同一节点在 PASS/REGION 间**大幅随机摆动**（实测同一批节点 10 轮内）：

| 节点 | 10轮通过率 | 若只测 3 轮会得出 |
|---|---|---|
| 日本-aw / 美国-aw / 英国-aw / 德国-aw | **10/10** | 正确 |
| 新加坡-aw | 9/10 | 正确 |
| 新加坡-fdc | 7/10 | 误判“被拒” |
| 日本-fdc | 5/10 | 误判“被拒” |
| 台湾-aw | **4/10** | 误判“稳定可用” |
| 香港-aw | **1/10** | 正确 |

⇒ **至少 10 轮统计通过率**，阈值：**≥90% 稳定 / 50~90% 高抖动 / <50% 基本不可用**。
⇒ 不要把一次成功写成“专用节点”——数分钟内状态可翻转。
⇒ 多账号交叉：同一节点对不同账号结果可能不同。

### 排除网络假象（否则会把活节点误判为“不通”）

两个坑，都会导致**系统性假阴性**（把健康节点报成不可用）：

1. **机场用动态 DNS 轮换 IP**：系统 DNS 与经代理的 DoH 返回**完全不同**的 IP 组。
   实测：系统 DNS → `13.208.*` 全部超时；DoH → `13.196.*` 全部 80~124ms 可达。
   而且**轮换很快**：几分钟前抓到的可达 IP 就会失效（实测 `15.168.173.70` 几分钟后全超时）。
   ⇒ **必须经代理 DoH 解析，且逐个 TCP 试连**，只取当前真正可达的 IP。

2. **别名节点共用同一 server 域名**：一个机场的多个节点常共用同一 hostname（仅端口不同）。
   解析一次后给所有节点填同一个 IP 是对的（IP 轮换是按域名而非按节点），
   但**若该 IP 失效，全部节点一起变“不通”**——看起来像“整个机场挂了”，其实是 IP 过期。

### 沙盒可用（修掉 IP 问题后）——但也知道它的边界

用 sing-box 重放节点配置做并行体测是**可行且已验证**的（见 `scripts/screen_nodes.py`）：
同节点沙盒路径 vs Karing 真实链路对照实测 5/6 vs 6/6，结论一致。

```
python scripts/screen_nodes.py                   # 全量，每节点 10 轮
python scripts/screen_nodes.py --filter anytls --rounds 5
```

脚本已内置：DoH 新鲜 IP + TCP 可达性预检、连通性预检（沙盒起后先验证能出网）、
区域/网络两类失败分开计（网络不可达不计入“不可用”）、自动下载对齐内核版本的 sing-box、
结束自动清理。

⚠️ **Karing 的 clash API 不能切节点**（已实测）：`/proxies/GLOBAL` 返回 404
（GLOBAL 是 `Fallback` 类型，非 Selector），PUT 任何 selector 报 `Must be a Selector`；
且 3065/3066/3067 所有本地端口都受同一个 `route.final` 控制。
**所以“逐个切换节点 + 探针”这条路走不通**，要批量测就必须自己起沙盒。

### 延迟测试只能当连通性参考

`delay?url=` 对所有节点都成功，**无法区分区域准入**。它适合快速排除“真死”的节点，
但把“延迟正常”当成“能调模型”是错的。

⚠️ 另一个易误读点：**延迟测试报“成功”，不代表能连上该服务的业务端点**——
它只测 TCP+TLS 握手（`delay` 值本身就是握手耗时），不触发任何业务层校验。

### 手写 Antigravity envelope（不走 CPA 时）

```json
{"model":"<模型名含后缀>","project":"<cloudaicompanionProject>",
 "request":{"contents":[{"role":"user","parts":[{"text":"hi"}]}],
            "generationConfig":{"maxOutputTokens":1},"sessionId":"-<16位数字>"}}
```
POST 到 `https://daily-cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse`。
project 值可从 `loadCodeAssist` 响应的 `cloudaicompanionProject` 字段取。
**缺 `project` 或缺 `request` 包裹会 404；`model` 不带 `-high`（如 `gemini-3.8-flash`）也会 404。**

## 上游内容过滤误伤（会话偶发「AI service declined」）

症状：Hermes 弹卡片 `content_policy_blocked: Sorry, I can't respond to this question.`（只给「编辑消息」，不给「重试」）；`agent.log` 记 `finish_reason=content_filter`。**先排除误判：链路是通的，不是网络/节点/代理故障。**

判别三步：
1. 反代日志 `%LOCALAPPDATA%\workbuddy2api\converter.log` 搜 `content_filter`：辅助调用（`msgs=1 | stream=False`）留 `finish=content_filter | tokens=0`；**主对话流式被客户端中止时可能只有 ▶ REQUEST 而无 ◀ RESPONSE**——“没记录”不等于“没发生”。
2. 与 `11140` 区分：`11140` 是 HTTP 400 的请求级预拦截（设计上明确不切号重试）；`content_filter` 是 HTTP 200 之后的生成级拒答。
3. 随机性验证：把被拒的同一内容原样重放几次。抽样型误伤重试即过（实测同图 6/6）；若 3/3 稳定复现才是确定性内容命中，重试无意义。

附带特性：辅助视觉被拒是**静默降级**——`computer_use` 的 `vision_analysis` 直接返回拒答文案而非报错，该文案会进入上下文。

处置：手动重发即恢复（上下文不中毒，实测下次请求即正常）；根治候选=反代侧「空拒答自动重试」，属策略判断，须用户拍板后再动。

## Pitfalls

- **The session shell exports `ALL_PROXY`/`HTTP_PROXY`/`HTTPS_PROXY` (= `http://127.0.0.1:3067`), so a bare `curl` is a *proxied* request.** Unset them for the true direct path: `env -u ALL_PROXY -u HTTP_PROXY -u HTTPS_PROXY curl …`. Labeling a proxied failure as "direct" inverts the entire diagnosis.
- **`3065` force-direct failing against a CN-blocked target (google) is the port working correctly, not a fault.** Probe force-direct with a domestic URL (`baidu.com`), exactly as the split test above does — otherwise a correct result reads as a dead client.
- **A vendor-wide, self-healing failure is a transient upstream, not a bad rule.** Signature: every subdomain of one vendor returns `000` through the rule port, with `curl: (35) schannel: failed to receive handshake` immediately after `CONNECT … 200 Connection established`, while unrelated domains — even on the same CDN — return 200. An upstream node/route blip presents exactly like a broken rule set. Retest 2–3 times over a few minutes before touching any config; in the observed case it healed on its own within minutes.
- **Always pass `-4` and `--max-time N` to curl on Windows.** Resolution returns AAAA first; a dead upstream then makes curl sit for the full 60 s default, which reads as "the proxy is broken" when the node is simply unreachable.
- **`CONNECT ... 200` followed by a hang is an upstream failure, not a routing one.** Don't start editing rule sets until you've seen this.
- **Never write a running client's config file.** It auto-saves and overwrites your edit, or drops it silently. Recommend the GUI path and name the menu location instead.
- **Use the client's split ports to isolate layers** rather than reasoning from the rule file: rule port, force-proxy port, force-direct port. If force-direct works and force-proxy fails, the node is dead regardless of what the rules say.
- **Don't run a latency sweep to find dead nodes** — the subscription JSON already has per-node latency/error. Sweeping hundreds of nodes is slow and re-tests known failures.
- **A free/public subscription with zero healthy nodes is noise, not a backup:** it slows list load and auto-switch. Recommend disabling rather than keeping "just in case".
- **Custom rule groups are usually evaluated before the built-in region fallback** (geosite:cn / geoip:cn / private-IP). Fine until someone adds a domestic domain to a proxy group — then the cn fallback can't catch it. Flag the ordering; don't silently reorder.
- **A health-check timeout of 2 s misjudges healthy overseas nodes from inside CN** and floods the list with false timeouts. Raise to 5–8 s.
- **A local AI client wired to a loopback reverse proxy (127.0.0.1:8787) that shows 「连接失败」 may simply be sending an empty model name.** Its "test connection" button POSTs `/v1/chat/completions` with no model; the proxy forwards that upstream, which answers HTTP 400 `11102 model [] service info not found`. Looks like auth/network, is actually a config gap — the client's provider entry has `models: []` and `defaultModel: ""`. Fix = add the upstream's real model id in the client (e.g. `auto`, `deepseek-v4.1-flash`). Public generic ids (`deepseek-chat`, `gpt-4o`, `claude-...`) also 400: such proxies only accept their own upstream's model names, so tutorial-default names are the wrong thing to paste.
- **Triage client 400s from the proxy side first, not from the client.** Match the failed request's message count in the proxy's structured log (`%LOCALAPPDATA%/workbuddy2api/converter.log`): a 2-message request whose model column is empty is the test button, not a real chat turn; the same rid repeating = proxy-internal retries, not repeated user clicks. Client-side config lives at `%LOCALAPPDATA%/TubaWinUi3/ai_providers.json` (图吧工具箱 AI 服务 / custom providers) — read it before touching VPN/proxy/keys.

## Verification

- Every 🔴/🟡 row is backed by a quoted log line, a curl result, or a config value — no row rests on inference.
- At least one domestic URL and one external URL were actually fetched through the proxy.
- The report ends with a sign-off question; no config file was modified.

## References

- `references/karing-windows.md` — Karing on Windows: config paths, port map, key setting fields, rule-order note.
- `scripts/screen_nodes.py` — 节点可用性筛查（零配额）。DoH 新鲜 IP + sing-box 沙盒 + 零消耗判别器，
  自动分区域/网络两类失败，自动清理。仅改运行时内存对象，不碰 Karing 配置。
