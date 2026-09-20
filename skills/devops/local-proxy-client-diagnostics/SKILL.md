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

⚠️ **探针可能与真实生成请求结论不一致**（实测同轮：台湾 probe=REGION 但 real=OK；英国 probe=PASS 但 real=REGION）。
说明「零消耗探针」与「真实生成」走到的区域检查路径不完全等价；**先用真实请求抽检一次**，
若两者在同一节点上矛盾，以真实生成请求为准，不要只看探针。

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

### ⚠️ 客户端延迟测试与「能否调用上游」是两个独立维度（实测反例）

2026-09-20 实采：Karing 列表里 🇩🇪德国-anytls-aw 显示**红三角（测速失败）**，
但同期实测该节点：零消耗探针 12/12 PASS、真实生成请求 12/12 OK。

更反直觉的是**延迟与业务速度不成正比**：

| 节点 | Karing 延迟测试 | 真实生成平均耗时 | 可用性 |
|---|---|---|---|
| 🇩🇪德国-anytls-aw | 324 ms（偏慢，曾显红三角） | **1.26 s** | 12/12 |
| 🇯🇵日本-anytls-aw | 99 ms（最快） | 1.88 s | 12/12 |

延迟最快的日本反而比德国慢 49%。典型原因：延迟测试只测 **TCP+TLS 握手**（网关可能就在入口附近），
而真实请求走的是**出口到目标服务的全程路径**，二者拓扑可能完全不同。

⇒ **不要用红三角/延迟值判定「这个节点能不能用」**，也不要据它切换节点。
⇒ 红三角多为**瞬时失败**：实测英国/德国在几分钟后重测即 10/10 全通（319~324ms）。
⇒ 判定可用性必须用**生成端点探针**（见上文）；判定速度要看**真实请求耗时**，不是握手延迟。
⇒ 若用户问「X 节点是不是挂了」，先按本节实测三个维度（TCP 可达 / 握手延迟 / 真实生成），
   不要把其中一个当成结论。

#### 红三角的两个独立成因（都要查，别只归一个）

**成因 A：阈值判定——「慢」被显示成「坏」**
Karing 的在线面板（zashboard，打包在 `D:/Karing/data/flutter_assets/assets/zashboard/`）里的阈值是
`delay:i=200` / `delay(300`：**≥300ms 显示警告色**。所以「恰好某几个节点红」通常就是它们越过了 300ms 线。
实测反例：德国 320ms / 英国 320ms 显红，其余全部 ≤205ms 显绿；同一批节点
真实生成请求 12/12 全 OK。**这是设计行为，不是故障，调什么设置都治不好**（除非线路变快）。

**成因 B：DNS 污染——「可用」被显示成「坏」**
官方博客明确列出这一故障：「节点可以用，但显示感叹号，连接超时」，根因是
**本地 DNS 把 `www.gstatic.com` 解析成了错误 IP**（默认 url-test 地址就是它）。
实测本机：系统 DNS → `120.253.253.98`（国内 IP，错）；Google DoH → `192.178.183.94`（真）。
⇒ **修法：把延迟检测 URL 换成不同提供者**（官方建议「最好替换为与原地址不同的提供者」）。
  已实测可用且延迟几乎相同（因为瓶颈是物理距离，不是目标服务器）：
  `http://cp.cloudflare.com/generate_204`（改用此项后用户红三角消失）。
  其他候选：`http://www.msftconnecttest.com/connecttest.txt`、`http://detectportal.firefox.com/success.txt`、
  `http://captive.apple.com`。
⇒ **超时建议 5s**（默认 2s 偏紧）：实测 100ms~2000ms 六档对稳定节点无影响，
  但开「解析出口 IP」或遇偶发慢包时会误判。5s 不拖慢正常测速（成功仍几百 ms 返回）。

#### `delay` vs `delay2`：UI 只显示前者，后者更接近真实体验

`/proxies/{tag}/delay` 返回两个值：`delay` = 到入口网关的握手，`delay2` = 完整 TLS 握手。
**Karing 只显示/存储 `delay`**（已有人提 issue #1535：`delay:95 / delay2:5682` 时 UI 只显 95ms，
实际那次请求花了近 6 秒）。⇒ 看到「延迟很漂亮但用起来卡」时，用 delay API 把两个值都取出来对比。

#### 「解析出口 IP」开关：默认关，不要开

开启后会额外发一次出口 IP 查询（走境外服务，比打 generate_204 慢得多）。实测额外开销：
德国 **+3.16s**、日本 **+8.83s**（后者单次查询就要 2.8s）。它还会放大超时误判 → **更多节点变红**。
仅在想确认「节点是否虚标落户地区」时才开。

### ⚠️ 主导变量是「时间」不是「规模」——通过率随时间窗大幅漂移

**先前结论已推翻**（2026-09-20 自查）：曾以为「沙盒里放多少出口」会压低通过率，
后续三个独立实验证明那是巧合——**真正的自变量是时间窗**。

同一批 7 个 anytls 节点、**完全相同**的参数与账号，四次运行结果：

| 运行时刻 | 香港-aw | 台湾-aw | 日本-aw | 美国-aw | 英国-aw | 新加坡-aw | 德国-aw |
|---|---|---|---|---|---|---|---|
| 11:47 筛选跑 ① | 0% | 80% | **100%** | 90% | **100%** | 100% | 100% |
| 12:00 筛选跑 ② | 20% | 80% | **100%** | 100% | **100%** | 100% | 100% |
| 约 13:0x 筛选跑 ③ | 0% | **30%** | **90%** | **0%** | **10%** | **70%** | 100% |
| 全量 63 节点跑 | 0% | 0% | 0~20% | 0~10% | 0~60% | 10~50% | 100% |

**推翻「规模混淆」的证据**：
- 在**同一份 63 出口配置**里只单独测日本-aw 15 轮 → **53%**（若规模是自变量，应仍为 0%）。
- 用**仅 2 出口**的配置对日本-aw 连测 40 轮 → **50%**（与 63 出口配置下的 53% 一致）。
- ⇒ 出口数量与通过率**无关**；先前看到的相关性来自「全量跑开始得早、筛选跑开始得晚」。

**速率限制假设也已被否证**：单节点连续 40 轮（无间隔）序列
`RPRRRRRPRRPRPPRPRPRPRRRPPPPRRPPPPPPRPRRP` 前 20 轮 40% / 后 20 轮 60%，
趋势 FLAT（无衰减）⇒ **不是「打得多了被封」，而是每请求独立随机 + 长周期基线漂移**。

⇒ **正确用法：结论必须带时间戳，且不可跨时间窗复用**。
   要判断「某节点能不能用」，就在**当下**跑一次 10 轮；
   两次跑结果矛盾时不需解释——那就是上游的随机门在漂。
⇒ **唯一在本轮所有运行中都稳定 100% 的节点是 🇩🇪 德国-aw**
   （跨 4 次运行 + 单独 40 连轮全 PASS）；其余节点均曾出现过 0%。
⇒ 长时间跨度（数小时）的「稳定性」需要**多次重测取交集**，不能拿一次 10 轮的 100% 盖章。

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

处置：手动重发即恢复（上下文不中毒，实测下次请求即正常）；根治=**反代侧「空拒答同账号重试」**（已于 2026-09-20 在 workbuddy2api 交付：
`converter.py` 的 `_is_blank_refusal()` + 三端点 + `_safe_stream_upstream` 共四条路径）。

### 两个必须记住的实测事实（否则修复会静默失效）

1. **拒答文案确实在 `content` 里**（实测 `Sorry, I can't respond to this question.`），
   所以判据绝不能用「`not content`」——它永远不成立。要用「正文长度上限」（拒答实测 38 字符）。
   证据：`%LOCALAPPDATA%\workbuddy2api\usage\snapshots.jsonl` 的 `resp` 字段原文。
2. **上游下发的是下划线 `content_filter`**，而历史代码只比对连字符 `content-filter`
   → 真实命中从未被识别。同时旧的字节扫描（在 payload 里搜「敏感」「审核」字样）
   会把**模型正文**里的这些字样当命中——实测 8 次该标签**全是假阳性**（均为成功的
   tool_calls 响应，tokens 从 1.9 万到 32 万不等）。
   ⇒ 判据必须：归一化拼写（去空白+小写+连字符转下划线）+ **只按结构化字段判定**，
   不要复用字节扫描。

### 判据要 Fail-Closed，别信"零 token"字面值

`total_tokens == 0` 但 `prompt_tokens`/`completion_tokens`/`reasoning_tokens` 非零是
**自相矛盾报文**（如 total=0 而 prompt=100）——此时「零 token」这个证据本身不可信，
必须判否（不重试）。任何一项明细非零都不得重试，否则会把有实质产出的响应再发一次。

## 配置层审计：全局开关会静默覆盖订阅声明

**这一类问题的共同形状**：客户端全局设置不仅“补默认”，还会**覆盖订阅源已声明的值**，
导致排查时“看订阅文件”与“看运行态”得出相反结论。**必须两个都读再 diff。**

### 实例：TLS 跳过证书验证的全局覆盖（2026-09-20 实测）

| 来源 | `insecure=true` | `insecure=false` |
|---|---|---|
| 订阅源自己声明（`karing_subscribe.json`） | 23 个节点 | **40 个节点** |
| 运行态实际（`service_core.json`） | **63 个** | **0 个** |

⇒ 全局 `tls.enable_insecure=true` 把 40 个“本应校验证书”的节点一起降级了。
⇒ 排查命令：从 `service_core.json` 数 `outbounds[].tls.insecure`，与订阅里声明的逐项对比。

**但这不一定是缺陷，取决于用户取舍**——本机用户是**故意**全局关闭的：

> 用户明确表述：“我不在乎网络安全，要的只有可用性和延迟还有网速。”

⇒ **在本用户的场景下，全局 insecure 是合理选择，不要反复劝其开启校验。**
⇒ 但**仍要告知代价与范围**（本题：40 个额外节点被降级），让取舍是知情的。
⇒ 判断能否关：先测证书链有效性（`ssl.create_default_context()` 直连节点 SNI）。
   实测 27 个不同 SNI 里 24 个证书有效（另 3 个失败是 DNS 解析问题，非证书问题）。

### 实例二：EDNS Client Subnet 的“预期收益”实测为零

直觉认为 ECS（把用户网段告知 DNS，帮助 CDN 选址）能提升速度。**实测否定**：
对手工构造的 DNS 报文开启/关闭 ECS，`www.baidu.com` / `www.taobao.com` /
`cdn.jsdelivr.net` / `www.bilibili.com` 返回的都是**同一批 IP，仅顺序不同**（轮询）。
⇒ 大网段广播/anycast 型 CDN 不依赖 ECS 选址；开着不提升速度，只多送隐私。
⇒ 但**也不影响可用性/速度**，故按用户标准无需改动。

（手工构造带 ECS 的 DNS 报文：OPT RR type=41 + OPTION-CODE 8，
 RDATA = FAMILY(1=IPv4) + SOURCE-PREFIX + SCOPE-PREFIX + 截断 IP。
 常见错误：把 ECS option 字段写进 OPT 的 RDLEN 里当裸结构——会收到 FORMERR(rcode=1)。）

### 实例三：明文 UDP DNS vs DoH 的实测代价

| 方式 | 实测耗时 | 解析结果 | 谁能看到查询内容 |
|---|---|---|---|
| 明文 UDP:53（经代理） | **67 ms** | 103.235.46.102/115 | 本地 ISP 看不到；**节点运营方能看到** |
| DoH（经代理） | **698 ms** | 同一批 IP | 仅能看到“连了 8.8.8.8” |

⇒ DoH 走代理要额外建 HTTPS 连接，**慢 10 倍**，解析结果相同。
⇒ 对“可用性/延迟/网速优先”的用户，**明文 UDP 是更优选择**，不是安全隐患。

## 用户取舍原则（本机基线，别再劝）

本用户对代理客户端的选择标准是**可用性 / 延迟 / 网速 优先**，不是安全：

| 项 | 用户选择 | 用户理由 | 处置 |
|---|---|---|---|
| TLS 跳过证书验证 | **全局开** | 只要可用性/延迟/网速 | 不改。已告知范围（额外 40 节点降级）后尊重选择 |
| 更新通道 | **beta** | 喜欢体验新东西 | 不改 |
| EDNS Client Subnet | 开 | （默认） | 不改（实测零收益也零损害） |
| DNS | 明文 UDP:53 | — | 不改（实测比 DoH 快 10 倍） |

⇒ **不要把自己的安全偏好当默认建议反复上提**。告知代价 → 尊重决定 → 不再重复。
⇒ 提建议时要把“安全风险”与“对本用户实际指标（可用/延迟/带宽）的影响”分开陈述——
   后者才是他会采纳的依据。

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
- **Triage a node's red triangle in this order, not by switching nodes.** ① clash API `history` — empty means the UI never测成功 (suspect DNS/config); a value means it did succeed and just crossed the display threshold. ② Take both `delay` and `delay2` from the delay API. ③ Compare system DNS vs proxied DoH for the `url_test` hostname. ④ Only then suspect the node. Two independent causes produce the same red triangle — a **threshold** (zashboard warns at ≥300 ms) and **DNS poisoning** of the test URL — and only the second is fixable by config.
- **A settings change the user reports as "fixed it" still needs the mechanism named.** 实测：用户改 URL+超时后红三角消失，真因是绕开了被污染的 `www.gstatic.com`（系统 DNS 返回国内 IP），不是超时变宽——同一批实测中 100 ms~2000 ms 六档对稳定节点结果一致。把功劳归给错的那个参数，下次复发时会去调错的旋钮。
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
