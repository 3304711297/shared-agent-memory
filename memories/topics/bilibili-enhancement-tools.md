---
name: bilibili-enhancement-tools
description: B站增强工具调研结论：make-bilibili-great-than-ever-before 油猴脚本 + BewlyCat 与
  AveMujica 两个扩展分支的对比与共存建议
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_5aaf10dd-f320-4323-9c4e-f0fba4ee03cf
---

2026-08-30 应用户要求调研了三个 B 站增强工具（原版 BewlyBewly 8.8k 星已于 2025-02 存档，以下为其生态延续）：

**make-bilibili-great-than-ever-before**（SukkaW 油猴脚本，v1.8.4，MIT，实验分支，kookxiang《Make Bilibili Great Again》的 TS 重写）
- 安装：unpkg dist 的 .user.js，自带 @updateURL 跟 @latest 自动更新
- 15 个模块：defuse-spyware（吞掉 data.bilibili.com/cm.bilibili.com/ExClimbWuzhi buvid 指纹激活，伪造 Sentry/MReporter/sendBeacon）、defuse-storage、disable-av1、force-enable-4k、no-p2p/no-webtrc（反 PCDN 偷带宽）、no-ad、enhance-live、fix-copy-in-cv、optimize-homepage/story、player-video-fit、remove-black-backdrop-filter、remove-useless-url-params、use-system-fonts
- 实现核心：document-start 子类化 XHR + hook fetch，动态改写 playinfo 的 PCDN/mCDN URL 为正常镜像 CDN；open/send toString 伪装回原生防检测
- 安全结论：无 GM_xmlhttpRequest、无 @connect 外联，dist 里 nxdomain.skk.moe 是故意不可解析的假域名非外联，可放心用

**BewlyCat**（keleus，4106 星，MIT，已获原作者授权上架商店）：功能增强向。最新 v1.7.8（2026-08-24），更新很勤。要点：B 站 2026 年 1 月调整首页推荐 API，需 ≥1.5.6；删内置字体后包体 14.4M→600K；禁止封装客户端。

**BewlyBewly-AveMujica**（VentusUta，636 星，AGPL-3.0）：外观向（YouTube/VisionOS/iOS 风格重设计），自称不做功能/效率提升，暗色模式只适配常用页面。最新 v1.8.31（2026-07-29）。低人力维护、节奏慢。

选型结论：两个扩展二选一（要功能选 BewlyCat，要好看选 AveMujica）；userscript 与扩展可共存，职责不重叠（反跟踪/反 PCDN 归脚本，UI 归扩展），首页去广告重复时可在脚本菜单单关 optimize-homepage。用户环境见 [[edge-dev-cdp-mcp-setup]]：扩展从 GitHub Releases 下 extension.zip 拖进 edge://extensions 安装即可，不依赖商店。

2026-08-30 源码级重叠核实（已浅克隆两扩展仓库 grep 确认，非只看 README）：
- 真重复四块：①清理 URL 跟踪参数（脚本 remove-useless-url-params ↔ 两扩展 cleanUrlArgument 均默认开）；②首页广告/优化（扩展整体接管首页，脚本的 no-ad/optimize-homepage 基本无处发挥，伪重复无害）；③字体（脚本 use-system-fonts 强制系统字体 ↔ 两扩展 customizeFont；**AveMujica 默认用它自己的推荐字体，与脚本真打架**，BewlyCat 默认 default 不冲突）；④播放器宽屏（脚本 player-video-fit ↔ BewlyCat 的 bewlyWidescreen 宽屏布局系统；AveMujica 无此功能）
- 脚本独有（两扩展源码均无对应）：反跟踪/伪造上报 SDK、禁 PCDN、禁 WebRTC P2P、禁 AV1、强制 4K、直播原画、专栏解复制、去除全站黑白哀悼滤镜
- 共存建议：脚本菜单里关掉 remove-useless-url-params、no-ad、optimize-homepage、player-video-fit；用 AveMujica 时再关 use-system-fonts；其余模块保持开启
- 关联新项目：[[bilibili-great-together-project]]
