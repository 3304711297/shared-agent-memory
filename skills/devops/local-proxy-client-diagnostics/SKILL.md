---
name: local-proxy-client-diagnostics
description: Diagnose local proxy clients from config and live probes.
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

## Pitfalls

- **Always pass `-4` and `--max-time N` to curl on Windows.** Resolution returns AAAA first; a dead upstream then makes curl sit for the full 60 s default, which reads as "the proxy is broken" when the node is simply unreachable.
- **`CONNECT ... 200` followed by a hang is an upstream failure, not a routing one.** Don't start editing rule sets until you've seen this.
- **Never write a running client's config file.** It auto-saves and overwrites your edit, or drops it silently. Recommend the GUI path and name the menu location instead.
- **Use the client's split ports to isolate layers** rather than reasoning from the rule file: rule port, force-proxy port, force-direct port. If force-direct works and force-proxy fails, the node is dead regardless of what the rules say.
- **Don't run a latency sweep to find dead nodes** — the subscription JSON already has per-node latency/error. Sweeping hundreds of nodes is slow and re-tests known failures.
- **A free/public subscription with zero healthy nodes is noise, not a backup:** it slows list load and auto-switch. Recommend disabling rather than keeping "just in case".
- **Custom rule groups are usually evaluated before the built-in region fallback** (geosite:cn / geoip:cn / private-IP). Fine until someone adds a domestic domain to a proxy group — then the cn fallback can't catch it. Flag the ordering; don't silently reorder.
- **A health-check timeout of 2 s misjudges healthy overseas nodes from inside CN** and floods the list with false timeouts. Raise to 5–8 s.

## Verification

- Every 🔴/🟡 row is backed by a quoted log line, a curl result, or a config value — no row rests on inference.
- At least one domestic URL and one external URL were actually fetched through the proxy.
- The report ends with a sign-off question; no config file was modified.

## References

- `references/karing-windows.md` — Karing on Windows: config paths, port map, key setting fields, rule-order note.
