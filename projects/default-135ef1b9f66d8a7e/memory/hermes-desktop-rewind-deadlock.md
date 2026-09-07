---
name: hermes-desktop-rewind-deadlock
description: Hermes Desktop 会话假死排查闭环——切模型注入 user 角色系统消息+客户端带截断参数重试被拒（上游 #94486），重启不自愈的根因与手工修复 SOP
metadata:
  type: feedback
---

**Hermes Desktop「会话运行不了」假死的根因链与修复 SOP**（2026-09-07 实战闭环，上游 issue NousResearch/hermes-agent#94486，已评论补充 Windows v0.21.0 复现证据）。

根因链：会话中切模型 → `[System: The active model ... changed]` 以 role=user 落库，紧跟真实用户消息形成 user/user 违例 → 该轮 API 调用被中断（常叠加自定义网关 429 限额）→ Desktop 客户端自动携带 `truncate_before_row_id` 重试「编辑/重发」→ 网关防误删保护 `refusing truncation without fallback`（4018）拒绝 → 会话假死。

**Why:** 重启网关/应用不自愈：重启后内存 `_row_id` 戳全丢，durable 兜底 `_load_durable_truncation_history()`（tui_gateway/methods_prompt.py ~L71）在 desktop 会话 `session_key` 为空（全 6 个 desktop 行皆 NULL）时直接返回 `[]`，跳过 heal 并对每次重试 fail-closed；客户端 resume 时又把挂起的截断参数带回来，死循环。`hermes sessions repair-routing` 对 desktop 孤儿行无效（无 keyed predecessor）。日志特征：`errors.log` 出现 `prompt.submit: target row_id N not found (in-memory + durable); refusing truncation without fallback`。

**How to apply:** ① 先查 `logs/errors.log` 确认 refusing truncation 特征 + `state.db` 查 `messages` 尾部是否 user/user 违例；② 备份 `state.db`（sqlite3 在线 backup API）后直接 DELETE 毒尾行（切模型 user 行 + 挂起用户行；FTS/trigram 触发器自动同步索引），UPDATE `sessions.message_count` 校准；③ 重启 Desktop 后先按 Esc 清客户端挂起编辑态再发全新消息，严禁原样重试卡住那条；④ 顺带核对自定义网关（WorkBuddy 8787 / EasyCLIProxyAPI 18080）是否 429 限额（错误码 6004 带重置时间），切回未限额模型可避开中断触发条件。
