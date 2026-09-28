# 换客户端可行性判定 & 活跃度核实

## 订阅格式由 UA 决定（一手实测法）

**判据既不是机场宣传，也不是客户端里的 UA 白名单——而是拿目标客户端的 UA 直接 GET 订阅地址，看回什么格式。**

实测（同一批订阅 URL、同一出口、同一天）：

| 请求 UA | 返回 |
|---|---|
| `clash-verge` / `ClashMeta` / `FLClash` | Clash YAML（含 `proxies:` / `proxy-groups:` / `rules:`） |
| `sing-box 1.13.0` | sing-box JSON（`outbounds`） |
| `mihomo/1.19.28` | base64 分享链接列表 |
| 无 UA / curl 默认 | base64 分享链接列表 |

⇒ **判断「客户端 X 能不能吃这个订阅」，先用 X 的 UA 试一次 GET。**
⇒ Karing 的 `userAgentCompatibles` 字段只是它在 UI 里可选的 UA 预设，**不等于机场会按它分发对应格式**；
   把它当“机场支持这些客户端”的证据会误判（实测 mihomo UA 拿回的不是 YAML）。
⇒ 反向同样成立：不要因为拿到 base64 就断言“机场不支持 Clash”——换个 UA 结果就变。
⇒ 客户端默认 UA 要读源码定案，不要按名字猜。实测 Clash Verge Rev：
   `src-tauri/src/utils/network.rs` 拼 `clash-verge/v{CARGO_PKG_VERSION}`，
   且 `src-tauri/src/config/prfitem.rs` 的 profile 项有 `user_agent: Option<String>` 可逐条覆盖。

## 内核侧协议兼容性要单独验，别被“客户端支持”带过

- AnyTLS：mihomo 已支持（`adapter/outbound/anytls.go` + 官方 wiki `type: anytls`），
  **但明确不支持 AnyTLS+Reality，且声明未来也不会支持**。
  ⇒ 订阅里出现 `reality-opts` 时必须确认它挂在哪个协议上：挂 vless/vmess/trojan 上无妨，
    挂 anytls 上则 mihomo 系客户端整体不可用（只能选 sing-box 系）。
  ⇒ 一手验法：按目标客户端 UA 取回订阅后，统计 `reality-opts` 落在哪些 `type:` 条目下。
- 这套判定器不需要安装任何客户端，也不需要跑节点，纯读取即可给出
  “哪些客户端能直连导入该订阅”的结论。

### 先确认“更新清单”的来源是本仓库还是服务端

只看 `releases.atom` 不够。有的客户端（实测 Karing）程序内的版本清单**不来自 GitHub**，而是服务端接口：
`auto_update_manager.dart` 里只有 `updateChannels() = ["beta","stable"]` 与过滤式
`item.updateChannel.contains(autoUpdateChannel)`，真正的候选列表由 `AutoupdateUtils.getAutoupdate()` 拉取，
**公开仓库里没有这份清单**。
⇒ 此时“为什么切了 beta 也拿不到预发布”**不可从公开材料验证**——这是服务端行为，不要猜，也不要当成客户端 bug。
⇒ 反过来这是“透明度”维度的硬证据：更新分发与核心源码都不公开时，用户无法自证“它到底停没停”。

### 镜像站 / 搜索快照里的 README 会过时

判定“某行为是不是设计如此”时，必须拉 `raw.githubusercontent.com/<repo>/main/README.md` 原文，
**不要用目录站、搜索引擎摘要或镜像仓的快照**。实测同一项目：旧快照仍写着
“无法同时开启系统代理和虚拟网卡：预期行为”，而 main 原文已删掉这句，且变更记录里写着
“移除 Windows 平台下 TUN 和系统代理的互斥逻辑”——两边结论相反。
⇒ 两者矛盾时**以 main 原文 + 变更记录的时间顺序为准**；拿快照当现状会报错结论。

## 客户端“是否停更”的零成本核实法（不要凭目录站/印象）

1. `https://github.com/<o>/<r>/releases.atom` —— 真实发布节奏（tag + 时间）。
2. `https://github.com/<o>/<r>/commits.atom` —— 真实提交节奏。
3. `curl -sI .../releases/latest` 看 302 的 `Location` —— **区分“最新正式版”与预发布**；
   只出预发布的项目，该重定向会停在上一个正式版。
   ⇒ “app 提示没有新版本”往往是**通道语义**（正式版 vs 预发布），不是项目停更。
   ⇒ 别把“目录站/应用商店显示的最后更新时间”（通常只跟正式版）当成项目活跃度。
4. `api.github.com` 匿名额度常为 0；`releases.atom` / `commits.atom` 不受此限，优先用它们。

⇒ 顺带：某项目官方仓库**所有提交信息都是同一句 `update`**（真实开发在非公开仓库）
   是“看着像停更”的常见成因——看上面第 1、2 条的时间，而不是看提交信息。

## 换客户端不会让节点变快

同一内核（mihomo / sing-box）下的不同 GUI 共享内核实现，换 GUI 不改变同节点同配置的速度。
⇒ 报「换工具能提升网速」必须有同节点 A/B 实测；否则只能声称 UI、可维护性、透明度的改善。
⇒ 只有当内核不同（sing-box ↔ mihomo）时才存在实测意义；此时任何速度结论都必须带同输入对照组。
