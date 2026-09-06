---
name: hermes-android-clients-and-gateway-topology
description: Hermes Agent 两款 Android 客户端（hermes-android 与 hermes-mobile）协议差异、多进程运行时拓扑与安全暴露实践
metadata:
  type: project
---

# Hermes Agent Android 客户端选型与双端通信机制

2026-09-07 实测沉淀：对社区两款开源 Android 客户端（`rusty4444/hermes-android` 与 `Hy4ri/hermes-mobile`）完成端到端调优与通信拓扑梳理，确立多进程并发隔离与局域网安全暴露工程规范。

## 客户端横向特性与选型矩阵

1. **`rusty4444/hermes-android` (Flutter / v2.0.1)**：
   - **通信契约**：基于 **Desktop Gateway JSON-RPC**（端口 8642，Bearer 鉴权 `API_SERVER_KEY`）；
   - **交互能力**：**100% 桌面级交互复刻**。实时渲染工具调用事件流（Tool Activity）、思考链折叠展开（Reasoning）、高危指令审批（Approval/Sudo）、反问澄清（Clarification）及子代理状态（Subagents）；
   - **移动端增强**：支持后台任务系统通知（Turn Notification）与断线精确恢复（Turn Recovery），支持单会话（Per-chat）独立切换模型与调节 Thinking Effort；
   - **局限性**：**界面硬编码英文**（截至 v2.0.1 暂未接入 i18n 多语言，但对话内容本身完全支持 UTF-8 中文）。
2. **`Hy4ri/hermes-mobile` (Kotlin Jetpack Compose / v1.22.1+)**：
   - **通信契约**：基于 **Dashboard REST API + TUI WebSocket**（端口 9119，Basic Auth 凭据 `HERMES_DASHBOARD_BASIC_AUTH_*`）；
   - **语言支持**：**原生内置完整简体中文**（1000+ 词条资源，自动跟随系统语言或在设置内手动切换）；
   - **核心定位**：全能型运维管理控制台。强在实时日志过滤、环境变量修改、Cron 调度管理、Kanban 任务看板与 6 套主题切换。

## 局域网暴露与安全门禁最佳实践

1. **非本地回环绑定门禁**：
   - 当 Hermes 网关或 Dashboard 绑定到非回环地址（`0.0.0.0`）时，Hermes 强制开启安全防护门禁，拒绝任何未经认证的裸奔连接。
2. **免污染主配置的 `.env` 凭据注入法**：
   - 为避免直接修改 `~/.hermes/config.yaml` 导致 YAML 格式重排、引入版本漂移及破坏双端配置同步基线，最佳实践是将凭据写入 `~/.hermes/.env`：
     ```ini
     API_SERVER_KEY=<32位以上强随机Token>
     API_SERVER_HOST=0.0.0.0
     API_SERVER_PORT=8642
     HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
     HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=<高强密码>
     ```
   - 防火墙放行：需放行 Windows Defender 防火墙 TCP 8642 与 9119 入站规则。

## 双端多进程运行时与会话隔离机制

用户在手机端发送消息时，常出现 **“电脑屏幕没有实时跳动打字”** 的疑问，其底层运行机制如下：

1. **进程与事件通道物理隔离**：
   - PC 桌面端（Hermes Desktop）启动时，由 Electron 拉起独立的私有 Python 后端进程（`serve --port 0`，动态本地端口如 4837），屏幕界面的实时消息流仅绑定在该私有 WebSocket 通道上；
   - 手机端连接的是系统常驻的 Gateway（8642）或 Dashboard（9119）服务进程，两者在运行时内存与实时事件推送上完全解耦。
2. **底层数据真实一致与会话隔离**：
   - 手机端发起的所有交互均真实写入本地单一 SQLite 数据库（`~/.hermes/state.db`）；
   - 手机端新建独立会话时，PC 桌面端为了避免打断用户当前屏幕工作，不会强制切页；用户只需在 PC 客户端历史列表中点开对应会话，即可完整读取手机端历史。
