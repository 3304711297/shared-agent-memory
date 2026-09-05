---
name: github-stars-organization
description: GitHub 星标 495 个与 13 个 Lists 的分类整理任务
metadata:
  node_type: memory
  type: project
  originSessionId: sess_f98123b6-de30-44f4-9ffd-68815cc24d78
---

用户要求将 GitHub 星标通过 GitHub 上的 Stars Lists（UserList）创建分类并归档，而非本地表格。
- 账号：3304711297（智商已更新），gh 已登录（scopes: gist, read:org, repo, workflow），starred 总数 495（2026-08-20 验证，缓存在 D:\ai coding\.zcode\workspace\default\starred_raw.json）
- 已有 13 个 Lists（viewer.lists）：系统优化工具(32)、代理工具(20)、我的世界(40)、steam内核(13)、Steam(64)、视频播放器(4)、浏览器(13)、音乐(29)、bilibili(22)、脚本/模块(5)、文件管理器(2)、UEFI-修改BIOS(7)、tracker-bt种子(5)，约 256 个槽位（含跨列表去重后未归档约 200+）
- 画像：语言 Top C# 83、TypeScript 68、Unknown 52、C++ 48、JavaScript 40、Python 37、Rust 29；话题 Top windows 80、android 33、linux 32、steam 31、windows-11 23 等
- 接口：GraphQL `createUserList(name, description, isPrivate)` 建分类，`updateUserListsForItem(itemId, listIds)` 批量归档，`deleteUserList`，`updateUserList`；`starred_raw.json` 为全量来源
- 关联环境坑：Git Bash 下 `python3` 会触发 Microsoft Store 的 Python Install Manager 弹窗，需用 `py`，gh api 带前导斜杠需 `MSYS_NO_PATHCONV=1`

**Why:** 用户已明确拒绝本地分类方案，坚持 GitHub 原生 Lists；需记录总数、已有分类占用与接口以避免重复创建和重复归档。
**How to apply:** 后续分类前先校验 13 个现有 Lists 名称去重；聚类依据 description+topics+language 而非单纯 language；预览新分类表经用户确认后再调用 createUserList/updateUserListsForItem 批量执行；Python 脚本统一用 `py` 启动。

**2026-09-05 任务重启状态：** 用户要求继续整理并把 **AI 大类细分为三个新分类：「Agent 端」（agent 框架/harness/CLI 智能体）、「Plugin 和 Skill 库」（skills/plugins 市场与仓库）、「AI 其他」**（模型工具/提示词/教程资源）。实查 Lists 已是 **27 个**（非基线 13），其中已有「AI·大模型与工具」53 项——用户确认方案时需二选一：(a) 新建三 List 并重分配该 53 项；(b) 保留现有、三新分类只收未归档。数据/方案文件：D:i coding\workspace 缓存 stars_org_20260905.json + stars_plan_20260905.md（子代理产出）。方案经用户确认后执行 createUserList/updateUserListsForItem。

**2026-09-05 任务完成：AI 三细分已落地（用户拍板"拆完删除"+ohmyzsh/qinglong 移表，不做跨表去重）。** 执行结果 ALL PASS：新建「Agent 端」21 项、「Plugin 和 Skill 库」14 项、「AI 其他」19 项（成员逐项精确匹配方案）；原「AI · 大模型与工具」53 项迁移 54 项（含 2 个未归档新星标）后清空删除；ohmyzsh 移入桌面增强、qinglong 真实移表（+自托管 −桌面增强）；Lists 27→29，未归档仅 HelloGitHub（1 个，按约定保留）。**基线勘误：08-20 晚间会话其实已完成 14 个中文 List 归档，"约 200+ 未归档"是执行前旧基线**。数据/快照/执行器：D:i coding\.zcode\workspace\default\stars_*.json/py。GraphQL 坑：deleteUserList 的输入字段是 listId 不是 id；根级 repository(owner:,name:) 而非 viewer.repository。

[[user-windows-environment]] [[desktop-projects-tweak-youshouldknow]]
