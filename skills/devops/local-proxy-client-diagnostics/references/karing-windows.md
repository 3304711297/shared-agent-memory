# Karing on Windows — config map

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

## Port map (defaults)

| Port | Role |
|---|---|
| 3067 | mixed **rule** inbound — normal system-proxy traffic |
| 3066 | mixed **force proxy** |
| 3065 | mixed **force direct** |
| 3057 | control (local API) |
| 3050 | cluster |
| 3072 | html board |
| 4067 / 4066 | net-share variants |

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
| `url_test_timeout` | health-check timeout | 2 s produces false timeouts to overseas nodes from CN |
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
