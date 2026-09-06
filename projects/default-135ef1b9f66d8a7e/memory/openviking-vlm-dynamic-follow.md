---
name: openviking-vlm-dynamic-follow
description: OpenViking 记忆提炼模型动态跟随当前聊天模型的机制、实现位置与避坑（token-stats 插件 /ovlm）
metadata:
  type: project
---

# OpenViking 提炼模型动态跟随（2026-09-06 落地）

## 背景
`ov.conf` 的 `vlm` 段原钉死 `gemini-3.8-flash@18080`（EasyCLIProxyAPI）。用户把聊天切到 WorkBuddy/glm 后，记忆提炼链路仍烧 Gemini 额度（附：2026-09-06 当天 09:58-13:14 的 gemini-3.8-flash 会话产生 879 次调用/144M 输入 token，为额度大头）。

## 生效机制（为什么改配置文件即可"动态"）
- OpenViking 的 VLM 实例在服务进程启动时创建并**进程内单例缓存**（`openviking_cli/utils/config/vlm_config.py::get_vlm_instance`），改配置对运行中进程无效；
- 但 1933 懒唤醒网关会让 1934 真实服务**空闲 2 分钟自杀**，下次请求重新拉起并重读 `ov.conf`；
- 因此「写 `ov.conf` +（可选）杀 1934」即可让新提炼模型生效，零侵入（不改 openviking 包源码，升级不被覆盖）。

## 实现位置（token-stats 用户插件）
- 后端 `plugins/token-stats/dashboard/plugin_api.py`：`/api/plugins/token-stats/ovlm`（GET 状态；`sync=1` 写 ov.conf；`apply=1` 踢 1934；`toggle=1` 跟随开关，状态存 `desktop-plugins/token-stats/ovlm-state.json`）；`/quota` 轮询顺路自动跟随 `_auto_ovlm_follow`（非阻塞锁 + 30s 冷却 + 会话静默 >90s 不自动切，`follow_enabled=false` 全停；锁必须 finally release）。
- 前端 `desktop-plugins/token-stats/plugin.js`：面板卡片 `OvlmCard`（状态徽标/跟随开关/手动同步按钮）。
- **当前聊天模型真源**：`state.db.sessions` 按 `last_activity_at` 最新行的 `model` + `billing_provider` 列（slug = `custom:` + provider 名小写空格转横线；改名前旧 slug 用括号内 host:port 对 base_url 兜底匹配）。`config.yaml` 的 `model.default` 不是真源。
- 安全阀：provider 非 `custom:*`、custom_providers 无匹配、缺 api_key → 拒绝改写。

**Why:** 提炼走哪个模型与聊天模型无关（ov.conf 独立钉死），不跟随就会在用户无感知时烧掉 Gemini 订阅额度。
**How to apply:** 排查提炼走线先看 `ov.conf` vlm 段与 state.db 最新会话；改提炼模型一律走插件端点或直接改 ov.conf 后踢 1934，勿改 openviking 包源码。

## E2E 验证记录（16:36-16:37）
- 临时测试文档经 `POST /api/v1/content/write`（`wait=false`）触发真实提炼 → 提炼调用全部落 `glm-5.3-flash@8787`，18080 Gemini 侧零调用；测试文档已删。
- 避坑①：`wait=true` 会撞 1933 网关 60s 超时返回假 502（请求实际仍在跑），长任务一律 `wait=false`；
- 避坑②：WebDAV PUT（204）只存文件**不触发**语义提炼，要触发提炼用 `/api/v1/content/write`；
- 避坑③：codebuddy2openai 的 `usage.jsonl` 时间字段 `ts` 是 **epoch 毫秒**，用字符串 `HH:mm` 匹配会假阴性；
- 避坑④：OpenViking 路由挂 `/api/v1` 前缀下（`/api/v1/content/write`），裸 `/write` 404。

## 附带事故记录
16:09 桌面端整体退出（backend exit(1)，孤儿运行时进程由新实例接管）：无 OS 级崩溃、无 traceback、无插件热重载证据，与插件文件写入时间相邻但因果未证实；重启后健康。若复现优先查 desktop.log 与 state.db 会话锁。
