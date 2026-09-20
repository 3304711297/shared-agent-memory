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

## 完整枚举配置（避免遗漏）

`karing_setting.json` 实测有 **176 个叶子键**。人工浏览极易遗漏，用递归列举：

```python
import json, pathlib, os
s = json.loads((pathlib.Path(os.environ["APPDATA"])/"karing"/"karing"/"karing_setting.json").read_text(encoding="utf-8"))
rows = []
def walk(o, path=""):
    if isinstance(o, dict):
        if not o: rows.append((path, "{}", "空对象")); return
        for k, v in o.items(): walk(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        rows.append((path, json.dumps(o, ensure_ascii=False)[:60], f"列表({len(o)})"))
    else:
        rows.append((path, repr(o), ""))
walk(s)
print(len(rows))  # → 176
```

汇报时按四类分组，**务必全列**：① 已讨论 ② 真缺口 ③ 隐私/元数据 ④ 界面与配置
（第④类虽无害，但隐去会让用户无法判断审计是否真的完整）。

### 易遗漏但仍值得看的项

| 键 | 本次实测值 | 判读 |
|---|---|---|
| `dns.ttl` | `43200`（12 小时） | **本用户用法下无需改**（见下方专节）：它只影响 DNS 缓存生存时长，而「每次开客户端手动更新订阅」会重启内核并清空缓存 |
| `dns.test_domain` | `'gstatic.com'` | “**DNS 延迟测试**”的探测域名（源码 `testDNSConnectLatency`），**不是**泄露检测，也**不在自动路径上**——只在你手点「自动设置服务器 / 服务器测延迟 / 网络检查」时才用。平时上网根本不读这个值 |
| `webdav.*` + `auto_backup.*` | 全空/全关 | 无任何配置备份（本用户已表态无所谓，不再提醒） |
| `rule_sets.disable_isp_diversion_group` | `true` | 关了运营商线路自适应（节点名里的 CTCU/CMCU/CUCM 就是这类标记） |
| `auto_select.*` | interval=28800 但 urltest.interval=-1s | “配了但不生效”——`route.final` 指向具体节点时会绕过 urltest |
| `ui.net_check_domain` | `daily-cloudcode-pa.googleapis.com` | 用户自定义的连通性检测域名（非默认） |
| `statistics.cache_days` / `cache_size_limit_mb` | 7 / 1024 | 仅 statistics.enable 开启时才有意义 |

### `dns.ttl` 与 `dns.test_domain`：两个曾被误判的项（源码定案）

**先说结论：对本用户都不需要改。** 两条曾被错报，记录正确判读以免重犯。

#### `dns.ttl` = `rewrite_ttl`，但「客户端每次开都更新订阅」会清空缓存

链路上游：`karing_setting.json` 的 `dns.ttl` → 编译为 sing-box 的 **`rewrite_ttl`**
（定义见 `setting_manager.dart:786` → `'ttl': ttl.inSeconds`），
散落下发给每个 outbound 的 `domain_resolver` 与 DNS 规则动作。

**sing-box 语义**：`rewrite_ttl` = **重写 DNS 回应中的 TTL**（不是“缓存存活时长”，但效果等同——
TTL 就是缓存条的过期时间）。实测把上游 30~300s 的 TTL 统一改写为 43200s：

```
www.baidu.com        第1次 191ms TTL=43200 → 第2次 11ms（缓存命中）
gstatic.com          TTL=1（被 fakeip 规则强制，quic 快速刷新）
<出站节点域名>   第1次 5.5ms TTL=41535（= 43200 减去已存活时间，倒计时中）
上游真实值（Google DoH，绕开 rewrite）：节点域名 TTL=30、google 系 300s
```

**为何不用改（决定性证据）**：用户习惯「每次打开客户端手动更新订阅」，
而 `home_screen.dart:1227` 显示：只要任一订阅 `enable && reloadAfterProfileUpdate` 为真，
就调 `setServerAndReload()` → `VPNService.reload()` ⇒ **内核重启、DNS 缓存清空**。
本机三个订阅中「自定义」为 `true`，故每次更新订阅都会清缓存，12h TTL 活不到一半。

⇒ **判据**：评估 TTL 类“缓存生存时长”参数前，**先查用户是否频繁重启内核/更新订阅**。
   频繁重启 ⇒ 长 TTL 无害（只省查询）；长期不重启 ⇒ 才考虑改短（如 600s）。
⇒ 唯一的真实代价：上游节点域名 TTL 仅 30s（机场可能快速切 IP），被放大到 12h 后
   切 IP 时本地不能及时跟上——但用户遇到连不上本来就会去更新订阅，自动清除。

#### `dns.test_domain` 不是泄露检测，也不在自动路径上

源码 `server_manager.dart` → `testDNSConnectLatency(dnsUrl, detour, testDomain)`：
`req.domain = testDomain ?? settingConfig.dns.testDomain`。

它**只被三处手动调用**（无定时/自动任务）：

| 调用点 | 触发时机 |
|---|---|
| `dns_auto_setup_screen.dart` | 手点「自动设置服务器」 |
| `dns_settings_screen.dart` | 手点某 DNS 服务器测延迟 |
| `net_check_screen.dart` | 手点「网络检查」 |

⇒ 平时上网时这个值**根本不会被读取**，与 DNS 泄露检测无关（那个看的是系统私有 DNS 配置）。
⇒ `gstatic.com` 作为探测目标合适（全球可解析、不敏感、结果无关紧要），无需替换。
⇒ 仅当 DNS 延迟测试结果异常时才考虑换（如 `example.com`）。

### “配置了但不生效”的识别法

一个开关写着非默认值，不代表它生效。必验三处：
1. 设置文件里的值（用户意图）
2. 运行态配置里是否真的下发了（`service_core.json`）
3. **上游依赖开关是否开启**——例：`auto_select.interval` 只在出口指向 `urltest_out` 时才起作用；
   `dns.proxy_resolve_mode=fakeip` 只在 `tun.enable=true` 时有意义；
   `statistics.cache_*` 只在 `statistics.enable=true` 时生效。

## 内置 DNS 清单与槽位选型（2026-09-20 全量实测）

### 内置清单在哪里（要改 DNS 时先看这里）

`lib/app/modules/setting_manager.dart` 的 `SettingConfigItemDNS` 常量表（约 700-760 行），
**30+ 条**预设，按提供商分组，每家含 UDP / DoT(`tls://`) / DoH(`https://`) / QUIC 变体：
Local、DHCP、AliDNS、DNSPod、Cloudflare、Google、TrafficRoute、OpenDNS、Yandex、Comodo、AdGuard。

反查命令（不需要 clone 仓库）：

```bash
gh search code 'dns.alidns.com' --repo KaringX/karing --limit 20   # 反查定义点
gh api "repos/KaringX/karing/contents/lib/app/modules/setting_manager.dart" \
  --jq .content | base64 -d > sm.dart && grep -n "kDNSIsp" sm.dart  # 拿全表
```

### 槽③『直连流量』实测排名（23 选项 × 10 个国内域名）

指标 = 解析出的首个 IP 的 **TCP:443 握手耗时**（直接对应浏览体验，比解析耗时重要）。

| 服务器 | 成功率 | 解析中位 | TCP 中位 |
|---|---|---|---|
| DNSPod doh `1.12.12.12` | 10/10 | 278ms | **32ms** |
| AliDNS udp `223.6.6.6` | 10/10 | **43ms** | **32ms** |
| AliDNS udp `223.5.5.5` | 10/10 | **40ms** | 33ms |
| AliDNS doh 域名 / DNSPod doh 域名 / AliDNS dot | 10/10 | 146~298ms | 33~34ms |
| TrafficRoute `180.184.1.1` / `2.2` | 10/10 | 72~81ms | 36~39ms |
| OpenDNS / **Local（路由器/系统）** | 10/10 | 110ms / 0ms* | 47ms / **49ms** |
| Cloudflare dot `1.1.1.1` | 10/10 | 1391ms | 164ms |
| Cloudflare udp `1.1.1.1` | **9/10** | 71ms | 183ms |
| Comodo / Yandex | 10/10 · 9/10 | 232~300ms | 198~254ms |

\* Local 的“0ms”是 Windows 本地缓存假象。真实差距在 TCP 那列：
**`local`(49ms) 比 AliDNS(33ms) 慢 ~16ms**，12 个域名里 11 个变快。

⇒ **槽③ 建议 `udp://223.5.5.5`**：解析快（40ms）+ TCP 快（33ms）+ 10/10 稳定。
   不选 DNSPod DoH——TCP 虽同为 32ms，但**解析阶段多花 240ms**（278 vs 40）。
⇒ 不能选的：Google/Cloudflare 的 DoT/DoH **直连不通**（槽③ 就是直连，填了直接失效）；
   `dot.pub`(7/10) / `1.1.1.1 udp`(9/10) / `Yandex`(9/10) 不稳定。

### 槽②『代理服务器』实测——所有可用选项无差别

指标 = 解析出的 IP 连**节点端口**的耗时（决定能否连上）。

| 服务器 | 成功率 | TCP 中位 |
|---|---|---|
| AliDNS udp / DNSPod doh / Google udp / Local | 8/8 | **90~93ms** |
| Cloudflare dot / Yandex / Comodo / OpenDNS | 7~8/8 | 92~101ms |
| Google dot `8.8.8.8` / Google doh / Cloudflare doh | **0/8** | 失败 |

⇒ 全部可用项落在 **90~101ms**，差异属噪声 ⇒ **保持 `udp://8.8.8.8` 即可，不必改**。

### 四槽选型结论（本机基线）

| 槽 | 最优值 | 状态 |
|---|---|---|
| DNS服务器 | `local` | ✅ 不参与（四项全为 IP 字面量时） |
| 代理服务器 | `udp://8.8.8.8` | ✅ 最优区（无差别，不改） |
| 直连流量 | `udp://223.5.5.5` | ❌ 原为 `local`，**唯一值得改的一项** |
| 代理流量 | `udp://8.8.8.8`（经节点） | ✅ 最优（明文 UDP 5~6ms vs DoH 267~279ms） |

### 复用脚本

`scripts/dns_slot_bench.py` — 一键对比内置清单在各槽的表现。
改 `SLOT` 变量选槽位；含正确的 DNS 报文解析（CNAME + 压缩指针）与 DoT/DoH 客户端。

## DNS-服务器 页逐项语义（源码 + 官方文案定案）

UI 四行 + 一开关 = `karing_setting.json` → `dns` 的四个数组 + `enable_static_ip_for_resolver`：

| UI 行 | 配置键 | 运行态批次 | 用途（官方文案/源码） |
|---|---|---|---|
| DNS服务器 | `resolver_addresses` | `dns_resolver_out` | 为“其它 DNS 服务器”解析域名（引导用）；填 IP 字面量时实际不参与 |
| 代理服务器 | `outbound_addresses` | `dns_outbound_out` | 解析**节点（机场）域名** —— **必须不走代理**（鸡生蛋：连上节点前就得解析它） |
| 直连流量 | `direct_addresses` | `dns_direct_out` | 直连流量的域名解析；国内域名→`local` 才对（才能拿就近 CDN） |
| 代理流量 | `proxy_addresses` | `dns_proxy_out`（=`dns.final`） | 代理流量的域名解析；实测运行态为 `detour:udp://8.8.8.8`（经节点转发） |
| 优先静态解析 | `enable_static_ip_for_resolver` | — | 官方提示「有效防止 DNS 服务器本身解析时被污染」；默认 true |

- **为何“代理流量经节点转发”是对的**：实测直连明文 `8.8.8.8` 会被**选择性污染**
  （`www.gstatic.com` → `120.253.x`，而 `gstatic.com` 却拿到真 IP），经节点转发才拿真结果。
- **两个按钮不是设置，会改配置**：`自动设置服务器` → 进向导按延迟检测结果改写上述 4 项；
  `重置服务器` → 源码 `setOutboundDns([])/setDirectDns([])/setProxyDns([])/setResolverDns([])`
  一次清空 4 项（回默认）。
- 页内 `直连流量`/`代理流量` 行的**可点性**受源码条件 `!tun.hijackDns && !novice` 控制
  （两者都假时 `onPush=null`）；但**已写入的值照常生效**，与是否可点无关。
- **易混淆**：`优先静态解析`（`enable_static_ip_for_resolver`）与主 DNS 页的
  `静态IP`（`enable_static_ip`：自定义域名→IP 映射，类 hosts）是**两个不同开关**。
- **页面归属**：`dns.ttl` 与 `dns.test_domain` 在**上一级“DNS 设置”页**，不在本页。
- **直连解析节点域名时，“两方结果不一致”不等于污染**（2026-09-20 实测，易误报）。
  把 37 个节点域名逐个对比“直连 8.8.8.8” vs “经代理 DoH 真值”：
  **35/37 结果完全一致**；2 个 Cloudflare 域名（同一机场的 node domain）返回不同 IP，
  但**两个 IP 的 TCP:443 都能连通**（实测 71ms / 256ms）⇒ 这是 **Cloudflare anycast/GeoDNS 按解析器位置返回不同就近节点**，**不是污染**。
  ⇒ 判据：结果不同时，**先实测两边 IP 的连通性**。都通 = anycast 选路；不通/超时 = 才可能是污染。
  ⇒ 同一域名在不同节点上延迟各异（实测 404ms vs 1201ms），说明**瓶颈在节点而非解析**。
  ⇒ 走代理查到的 `104.21.*` 与直连查到的 `141.193.*` 均属 Cloudflare 段；无 PTR 可查（正常）。
- **节点域名解析必须直连，这是设计而非疏漏**：鸡生蛋问题——连上节点前就得先解析它的域名。
  故 `outbound_addresses` 不带 `detour` 是**唯一正确选择**，不要“为避污染”给它加代理。
- 该页 4 项解析器的配置=生效映射（实测 `service_core.json`）：
  `resolver_addresses`→`dns_resolver_out`、`outbound_addresses`→`dns_outbound_out`、
  `direct_addresses`→`dns_direct_out`、`proxy_addresses`→`dns_proxy_out`（=`dns.final`）。

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
