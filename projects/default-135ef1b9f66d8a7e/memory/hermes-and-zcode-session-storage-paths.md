---
name: hermes-and-zcode-session-storage-paths
description: Hermes 与 ZCode 会话存储物理路径、桌面工作区锚定与快捷方式启动规范（state.db、projects.db 与 D:/ai coding 对齐全貌）
metadata:
  type: reference
---

# Hermes 与 ZCode 会话存储物理路径与工作区对齐规范

## 一、 会话底层物理存储路径（真源索引）

双端均采用 **SQLite 数据库（WAL 模式）+ 本地结构化 JSON 缓存** 的持久化架构：

| 客户端 | 存储层级 | 物理路径 | 作用与表结构 |
| :--- | :--- | :--- | :--- |
| **Hermes Agent** | **核心会话数据库** | `%LOCALAPPDATA%\hermes\state.db` | 包含 `sessions`、`messages`、`conversation_history` 等表；左侧会话历史、上下文读取、多轮恢复均直读此库。 |
| **Hermes Agent** | **桌面项目索引** | `%LOCALAPPDATA%\hermes\projects.db` | 记录本地项目元数据及会话与工作区（Project）的绑定关系。 |
| **Hermes Agent** | **会话转储明细** | `%LOCALAPPDATA%\hermes\sessions\` | 存放各次会话请求与调试转储（`request_dump_*.json`）。 |
| **ZCode** | **GUI 会话主数据库** | `%USERPROFILE%\.zcode\cli\db.sqlite` | ZCode 桌面端主工作区（`-.zcode-workspace-default`）所有会话与对话记录。 |
| **ZCode** | **CLI 独立会话缓存** | `%USERPROFILE%\.zcode\cli\agents\` | 按会话 UUID 目录存放 `metadata.json` 与历史（CLI 专用）。 |

## 二、 工作区（Workspace）与项目路径对齐（2026-09-07 固化）

1. **统一主工作区路径**：双端主工作区均严格锚定于 **`D:\ai coding`**。
2. **Hermes Desktop 项目绑定**：
   - 通过 `desktop_project` 工具已创建并激活桌面项目 **`ai coding`**（ID: `p_02f2312b`，绑定路径 `D:\ai coding`）；
   - 界面侧边栏已正式挂载该目录，与 ZCode 保持一致。
3. **桌面快捷方式固化**：
   - 桌面快捷方式 `%USERPROFILE%\Desktop\Hermes Agent.lnk` 的「起始位置」（`WorkingDirectory`）已修改并锁定为 **`D:\ai coding`**；
   - 无论从桌面直接双击启动还是命令行唤起，初始工作目录均默认落在 `D:\ai coding`。

相关记忆：[[desktop-projects-tweak-youshouldknow]] [[zcode-desktop-config-architecture]] [[user-windows-environment]]
