# Karing on Windows — config map

## 延迟检测 / 测速设置（`karing_setting.json` 顶层键）

| Key | 含义 | 默认 | 建议 |
|---|---|---|---|
| `url_test` | 延迟检测 URL | `https://www.gstatic.com/generate_204` | 被 DNS 污染时换成**不同提供者**（`http://cp.cloudflare.com/generate_204`）——见 SKILL.md 【成因 B】 |
| `url_test_timeout` | 单节点超时（秒） | `2` | **改 5**：2s 对跨境节点偏紧，且开「解析出口IP」时必不够 |
| `latency_check_concurrency` | 并发数 | `20` | 保持。实测 63 节点全量并发 20 只需 7.2s，通过 56/63 |
| `latency_check_resolve_ip` | 手动检测时同时解析出口IP | `false` | **保持关**：额外 +3~9s，反而让更多节点变红 |
| `speed_test` | 主屏测速 URL | `https://speed.cloudflare.com/` | 不用改 |
| `html_board_port` | 在线面板端口 | `3072` | 默认仅绑 `127.0.0.1`，本机浏览器直接开 |

**手动触发单个节点延迟测试（等价于 UI 点测试）：**

```bash
SEC=$(python -c "import json,os,pathlib;print(json.loads((pathlib.Path(os.environ['APPDATA'])/'karing'/'karing'/'service.json').read_text(encoding='utf-8'))['secret'])")
curl -s -H "Authorization: Bearer $SEC" \
  "http://127.0.0.1:3057/proxies/$(python -c "import urllib.parse;print(urllib.parse.quote('🇩🇪 德国-anytls-aw'))")/delay?timeout=5000&url=$(python -c "import urllib.parse;print(urllib.parse.quote('http://cp.cloudflare.com/generate_204',safe=''))")"
# → {"delay":327,"delay2":667}
```

**查每个节点最近一次实测结果（UI 显示的数据源）：**

```bash
curl -s -H "Authorization: Bearer $SEC" "http://127.0.0.1:3057/proxies/$(python -c "import urllib.parse;print(urllib.parse.quote('🇩🇪 德国-anytls-aw'))")"
# → {"type":"AnyTLS","name":"...","udp":true,"history":[{"time":"...","delay":325}]}
# history 为空 = UI 从未成功测过；有值但 UI 显红 = 越过了 200/300ms 阈值（见 SKILL.md）
```

## 开发者选项（`karing_setting.json` → `dev` 段）

三项都是 **「出问题才开」** 的排障开关，开着只增开销/暴露面：

| UI 项 | `dev` 键 | 默认 | 建议 |
|---|---|---|---|
| 开启调试日志 | `enable_debug_log` | `false` | **关**。开了让 `service_core.log` 无意义膨胀（未开就已 7MB） |
| 启用 pprof | `pprof_port`（0=关） | `0` | **关**。官方 FAQ 定位：内存暴涨 / CPU 持续高 / 连接数>10000 时才开，抓 profile 交开发者 |
| 允许远程访问在线面板 | `allow_remote_access_htmlboard`（另配 `pprof_port` / `allow_remote_access_pprof`） | `false` | **关**。开了会把面板从 `127.0.0.1` 改为监听所有网卡（含 WLAN/VPN），同局域网任何人可访问 |

验证命令（确认实际监听面）：

```bash
powershell -NoProfile -Command "Get-NetTCPConnection -State Listen | Where-Object { \$_.LocalPort -in 3072,3057,3067 } | Select-Object LocalAddress,LocalPort,OwningProcess | Format-Table -AutoSize"
# LocalAddress=127.0.0.1 → 仅本机；0.0.0.0 → 局域网可访问
```

## 系统 Scheme 调用（`karing://` / `clash://` / `sing-box://`）

用途：让外部程序/网页通过链接指挥 Karing。官方支持（`karing.app/cooperation/scheme`）：

```
karing://install-config?url=xxx&name=xxx      # 一键导入订阅（参数需 urlencode）
clash://install-config?url=xxx&name=xxx
karing://restore-backup?url=xxx               # 恢复备份
karing://connect / disconnect / reconnect     # 连接控制
```

| 项 | 建议 | 理由 |
|---|---|---|
| `karing://` | **开**（默认） | 机场一键导入、脚本连断依赖它 |
| `clash://` | 关（默认） | 官方列为可选；未装需要它的客户端时无用 |
| `sing-box://` | 关（默认） | 官方文档**未列此 scheme**，给原版 sing-box 客户端用户 |

**开关 ≠ 注册**：开关只控制「是否处理」，能不能被调用取决于注册表。实测本机
`HKCU\Software\Classes\karing` 已注册（`D:\Karing\karing.exe "%1"`），
`clash` / `sing-box` **均未注册** → 那两个开关就算打开也不生效，要先装对应客户端抢注：

```bash
powershell -NoProfile -Command "foreach (\$k in 'karing','clash','sing-box') { if (Test-Path \"HKCU:\Software\Classes\$k\") { Write-Output \"$k : 已注册\" } else { Write-Output \"$k : 未注册\" } }"
```

风险（设计权衡，不是缺陷）：`karing://` 开着时任意网页都能构造该链接触发导入/断连，
实际会弹确认框。提醒用户别在陌生网页点这类链接。

## 诊断用的旁路手段

- **UI 红三角排查顺序**：① 取 `history` 看是否真有记录（空=从未测成功，有值=越过阈值）；
  ② 取 `delay`+`delay2` 看实际耗时；③ 查 DNS 污染（系统 DNS vs DoH 解析 url_test 的域名）；
  ④ 才考虑节点本身问题。**不要一上来就换节点。**
- `service_core.log` 可能**滞后于当前进程**（实测尾部时间戳落后于 UI 操作时间）——
  拿它当“最近没报错”的证据时会误判；用 `karing_setting.json` 的 mtime 与 clash API 的
  `history.time` 才能对齐到用户的点击时刻。
- `cache.db` **不是** SQLite（直连报 `file is not a database`），不要试图用 sqlite3 读。

## 全量配置审计路径（本次实测总结）

要“全面看一遍配置”，按下面顺序读，能覆盖全部可审计面：

| 步骤 | 读什么 | 能发现什么 |
|---|---|---|
| 1 | `karing_setting.json`（UI 真值，~269 行全读） | 所有开关的**用户意图** |
| 2 | `service_core.json`（运行态真值） | 开关**实际下发**成了什么；与 UI 的 diff 就是被覆盖/被忽略的项 |
| 3 | `karing_subscribe.json` | 订阅源**自己声明的**节点参数（与运行态对比看到全局覆盖） |
| 4 | `karing_subscribe_use.json` | 当前选中节点、favorites、recent、自定义分流组 |
| 5 | 进程 + 监听端口 | 实际暴露面（`Get-NetTCPConnection`，看 `LocalAddress`） |

### 易被忽略但值得查的字段

| 字段 | 含义 | 本次实测值 | 判定 |
|---|---|---|---|
| `tls.enable_insecure` | 全局跳过证书验证 | `true` | ⚠️ 覆盖了订阅的 40 个 `false`；本用户故意开（取舍见 SKILL.md） |
| `auto_update_channel` | 更新通道 | `beta` | 用户偏好尝新，不改 |
| `dns.enable_client_subnet` | 带 ECS 查询 | `true` | 实测零收益零损害 |
| `dns.outbound_addresses` | 出站 DNS 服务器 | `udp://8.8.8.8` | 明文但快 10 倍（实测对比见 SKILL.md） |
| `dns.proxy_resolve_mode` | 代理解析模式 | `fakeip` | 仅 TUN 开启时才有意义，当前 TUN 关 |
| `statistics.enable` | 本地统计 | `false` | 符合隐私偏好 |
| `auto_select.interval` | 自动切换周期 | `28800`（8h） | 但 `urltest.interval=-1s` 使其**实际未生效** |
| `auto_select.filter` | 自动切换时排除失效节点 | `false` | 仅在自动切换启用时才有意义 |
| `proxy.auto_set_system_proxy` | 写系统代理 | `true` | ✓ |
| `proxy.disconnect_when_quit` | 退出时断开 | `true` | ✓ 防止系统代理指向死端口 |
| `proxy.auto_add_to_firewall` | 自动加防火墙规则 | `true` | ✓ |
| `perapp.enable` | 分应用代理 | `true` | Windows 下需管理员身份启动才生效 |
| `tun.enable` | TUN 模式 | `false` | ✓ 按需手动开（符合用户策略） |

### 规则顺序的“假短路”陷阱（本次差点误报）

`service_core.json` 的 `route.rules` 前几条形如：

```json
{"inbound": ["mixed_in_direct"], "outbound": "direct_out", "name": "direct[all]"}
{"inbound": ["mixed_in_proxy"],  "outbound": "<node>",     "name": "proxy[all]"}
```

乍看像“无条件规则排在自定义规则之前 ⇒ 短路了后续所有分流”。**但它是 `inbound` 限定的**：
那两个规则只作用于 3065/3066 两个强制端口，3067（规则端口）不受影响，
会继续跑完全部自定义分流组。

⇒ 判断规则是否全局短路，**必须先看有无 `inbound` / `source_ip_cidr` 等匹配条件**；
   不能只看“有没有 rule_set/domain 字段”。
⇒ 实测端口对应：`mixed_in_direct`=3065、`mixed_in_proxy`=3066、`mixed_in_rule`=3067。

## Paths

- Config dir: `C:\Users\<user>\AppData\Roaming\karing\karing\`
- Key files:
  - `karing_setting.json` — all UI settings (proxy, tun, dns, tls, mux, rule_sets, auto_select)
  - `karing_routing_group.json` — custom diversion groups
  - `karing_subscribe_use.json` — selected node, recent, fav, diversion→outbound mapping
  - `karing_subscribe.json` — subscriptions + every node with its `latency` field
  - `service_core.json` — the generated sing-box config actually running (authoritative)
  - `service_core.log` — core log; grep `ERROR` here for root cause
  - `app.log`, `service_error.log` — launcher level

`service_core.json` is ground truth for what is running; `karing_setting.json` is what the UI shows. Diff them when behavior disagrees with settings.

## 端口速查（含 UI 显示阈值）

| Port | Role |
|---|---|
| 3067 | mixed **rule** inbound — normal system-proxy traffic |
| 3066 | mixed **force proxy** |
| 3065 | mixed **force direct** |
| 3057 | control (local API) |
| 3050 | cluster |
| 3072 | html board（在线面板） |
| 4067 / 4066 | net-share variants |

**节点延迟的颜色阈值（在线面板 zashboard，非 sing-box 内核）：**

| 显示 | 条件 | 位置 |
|---|---|---|
| 🟢 绿 | `< 200 ms` | `D:/Karing/data/flutter_assets/assets/zashboard/assets/index-*.js` 里的 `delay:i=200` |
| 🟡 黄/橙 | `200 ~ 300 ms` | 同上 |
| 🔺 红（警示三角，非「不可用」） | `≥ 300 ms` | `delay(300` —— **只是「慢」的标记** |

⇒ 因此「恰好某几个节点红」多半就是它们越过了 300ms 线，而非故障。
⇒ 面板是 Flutter 应用，`karing.exe` 本身仅 661KB，UI 逻辑在 `D:/Karing/data/`；
   `cache.db` **不是** SQLite（直连报 `file is not a database`），不要用 sqlite3 读。

Windows system proxy is set to `127.0.0.1:3067` via `HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings` (`ProxyServer`, `ProxyOverride`, `ProxyEnable`).

## Diagnostic split test

```
curl -4 -s -o /dev/null -w "code=%{http_code} t=%{time_total}\n" --max-time 15 -x http://127.0.0.1:3065 https://www.baidu.com                  # force direct
curl -4 -s -o /dev/null -w "code=%{http_code} t=%{time_total}\n" --max-time 15 -x http://127.0.0.1:3066 https://www.google.com/generate_204   # force proxy
curl -4 -s -o /dev/null -w "code=%{http_code} t=%{time_total}\n" --max-time 15 -x http://127.0.0.1:3067 https://www.google.com/generate_204   # per rule
```

3065 ok + 3066 fail ⇒ upstream node dead. 3067 differs from 3066 ⇒ routing rule issue.

## Setting fields worth auditing

| Field | Meaning | Watch for |
|---|---|---|
| `proxy.auto_set_system_proxy` | writes Windows proxy | confirm `ProxyEnable=1` matches |
| `proxy.system_proxy_bypass_domain` | bypass list | without the Windows NCSI probe domain (`msftconnecttest.com`) Windows reports "no Internet" whenever the proxy is down |
| `tun.enable` | TUN / global mode | off ⇒ CLI tools, games, and non-proxy-aware apps bypass entirely |
| `dns.proxy_resolve_mode` | `fakeip` etc. | mainly meaningful with TUN on |
| `dns.enable_inbound_domain_resolve` | resolve inbound domain | off ⇒ localhost-style hostnames skip resolution and can fall through to the final outbound |
| `auto_select.interval` / `filter` | auto-switch period / whether dead nodes are excluded | `filter=false` + a long interval = a dead node sticks for hours |
| `url_test_timeout` | health-check timeout | 2 s produces false timeouts to overseas nodes from CN — **recommend 5 s** (see 延迟检测 section) |
| `tls.enable_insecure` | skip cert verify | convenience vs MITM |
| `route.final`, `route.rules[].outbound` | the running policy | read from `service_core.json` |

## Node health

Per-node status lives in `karing_subscribe.json` → `items[].servers[].latency`. Numeric = ms; `连接超时` or a DNS error string = dead. Count numeric entries per subscription for a health ratio; a subscription at 0/N is dead weight.

## Rule ordering

Generated `route.rules` puts custom groups first, then the built-in `geosite:cn`, `geoip:cn`, and `ip_is_private` fallbacks last. Correct as-is (proxy groups proxy, direct groups direct), but any domestic domain added to a proxy group can no longer be caught by the cn fallback. Flag before reordering.

## Log signatures

```
outbound/<proto>[<tag>]: failed to create session: (dial tcp <ip>:<port>: i/o timeout | ...)
```
Multiple dial targets listed = the hostname resolved to several IPs, all unreachable.

```
create outbound failed: <tag> -> unknown obfs type:
```
A node the client cannot parse — typically from a free/public subscription. Harmless but noisy.
