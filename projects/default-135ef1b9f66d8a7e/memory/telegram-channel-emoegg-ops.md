---
name: telegram-channel-emoegg-ops
description: 用户个人 Telegram 频道 @emoegg（蛋总的圈）专属 Bot 管理体系、主号风控背景与 14 款纯暗黑精选主题落地
metadata:
  type: project
---

# Telegram 频道 @emoegg 自动化管理与主题资产沉淀

## 一、频道基本概况与风控背景
- **频道名称**：**「蛋总的圈」**（曾用名「某不知名杂货铺」）
- **公开地址**：`@emoegg`（`https://t.me/emoegg`，Web 预览端点 `https://t.me/s/emoegg`）
- **频道定位**：专注网络代理协议深度解析（SS / Trojan / VLESS 等）、实际延迟与 RTT 测评辨析、TUN 协议栈机制、GFW 与地方防火墙（河南/江苏/新疆反向墙）审查实测，以及定制软件/音乐工具资源存档。
- **主号风控限制与排错结论（2026-09-05）**：
  - 用户主号因多次累积风控，处于深度禁言/限制状态，`@Spambot` 与官方邮件申诉均已被系统忽略；
  - **严禁尝试 Userbot / Telethon 客户端脚本登录**：风控生效于 Telegram 服务端（MTProto 协议），脚本发请求同样会被 `UserRestrictedError` 拦截；且高危受限账号尝试调用底层 API 极易直接触发反作弊系统导致永久销号（`PHONE_NUMBER_BANNED`）；
  - **正规破局路径**：利用互存手机号的「双向联系人（Mutual Contacts）」突破私聊限制，借小号向 `@BotFather` 申请 Bot 并拉入频道设为管理员，或直接转移频道所有权（Transfer Ownership）。

## 二、专属管理员机器人体系
已成功为 `@emoegg` 频道配置专属管理员机器人并完成实机权限核验：
- **机器人标识**：`@HermesAgentByjieBot`（ID: `8361539844`）
- **频道 Chat ID**：`-1002070574431`
- **核验通过权限**：
  - `can_post_messages: true`（发布消息）
  - `can_edit_messages: true`（编辑消息）
  - `can_delete_messages: true`（删除消息）
  - `can_change_info: true`（修改频道资料与简介）
  - `can_invite_users: true`（生成邀请链接）
- **本地凭据与通信配置**：
  - 配置文件：`%LOCALAPPDATA%\hermes\auth\telegram_channel.json`（不入公开版本库）；
  - 网络走本地代理：`http://127.0.0.1:3067`。
- **运维与管理脚本**：
  - 脚本路径：`%LOCALAPPDATA%\hermes\scripts\tg_channel.py`；
  - 支持指令：`info`（获取权限与状态）、`post <text>`（发帖）、`edit <id> <text>`（改帖）、`delete <id>`（删帖）、`pin <id>`（置顶）；
  - 规范技能：`skills/productivity/telegram-channel-ops/SKILL.md`。

## 三、频道第 12 号消息精选 14 款纯暗黑主题落地
从频道第 12 号消息（精选主题）提取色值与视觉规范，按用户要求彻底剔除所有日间浅色（微信日间、卡通日间、蓝色日间、酒红日间、米色日间），全量收敛为纯粹面向极客与夜间工作的 **14 款纯暗黑/夜间沉浸主题**：
1. `qq-classic`：QQ 经典 (Such QQ 暗夜天蓝)
2. `wechat-dark`：微信夜间 1 (小而美 8.0 暗黑模式)
3. `wechatify-dark`：微信夜间 2 (WeChatify Dark OLED 纯黑)
4. `wechat-dark3`：微信夜间 3 (夜间微信高对比)
5. `anime-designer`：动漫夜间 (Designer 霓虹紫)
6. `brownie-dark`：酒红简洁 (Brownie 巧克力酒红)
7. `palenight`：紫色简洁 (Palenight Material)
8. `spacegrey`：黄色文字 (Spacegrey 琥珀金)
9. `puaro-grey`：淡灰简洁 (Puaro 莫兰迪极简冷灰)
10. `forest-green`：暗绿文字 (Forest Green 苍松深绿)
11. `dracula-mint`：蓝绿夜间 (Dracula Mint 德古拉薄荷绿)
12. `amber-orange`：橙黄夜间 (Is So Elegant 琥珀暗金)
13. `neon-purple`：暗紫夜间 (Buifys 赛博暗紫)
14. `jotunheim-blue`：湛蓝夜间 (Jotunheim 北欧极地冰蓝)

- **落地形态**：`%LOCALAPPDATA%\hermes\desktop-plugins\im-themes\plugin.js`，全部注册至 `THEMES_AREA` 和 `PALETTE_AREA`，桌面端按 `Ctrl+K` 即可秒级换肤。零外部 `.attheme` 垃圾残留。
