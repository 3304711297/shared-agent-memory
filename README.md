# Hermes Agent 核心资产与记忆库 🧠

<p align="center">
  <strong>跨会话持久化长期记忆 · 领域专业技能库 (Skills) · 核心扩展插件库 (Plugins) · 桌面原生组件 (Desktop Plugins)</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Agent-Hermes%20Desktop-526CFE?style=flat-square&logo=visualstudiocode" alt="Agent">
  <img src="https://img.shields.io/badge/Platform-Windows%2011-0078D6?style=flat-square&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/Main%20Branch-hermes-success?style=flat-square&logo=git" alt="Branch">
  <img src="https://img.shields.io/badge/Storage-Private%20Repository-blueviolet?style=flat-square&logo=github" alt="Storage">
  <img src="https://img.shields.io/badge/Auto%20Sync-Silent%20Push-green?style=flat-square" alt="Auto Sync">
</p>

---

## 📖 仓库简介

本仓库（`3304711297/shared-agent-memory`）是 **Hermes Agent** 作为日常主力 AI 编程与操作系统助手时的**跨端唯一真源（Single Source of Truth）**。

用于集中持久化备份与跨设备同步四大核心资产：
1. **长期记忆（Memories）**：用户画像、操作铁律、本地模型桥接、系统环境与 30+ 篇深度项目工程档案；
2. **扩展技能（Skills）**：113+ 个领域专业工作流规范（Superpowers 流程体系、前端设计、代码审查、知识检索等）；
3. **核心插件（Plugins）**：4 大核心扩展插件（Context7、Desktop Commander、Serena、Superpowers），提供底层 MCP 工具、系统交互与协议扩展；
4. **桌面插件（Desktop Plugins）**：Hermes 桌面端原生前端组件（如 Token 速率与 Google 额度实时看板）。

> 🔒 **私有仓库安全规范**：本仓库设为 Private，严禁跟踪或上传任何 `.env`、`auth.json`、API Token、Session 数据库及带锁的运行时敏感凭据。

---

## 🏛️ 资产分层与架构解耦说明

在 Hermes Agent 体系中，**Plugins（插件）** 与 **Skills（技能）** 承担不同层级的职责，彼此解耦并独立维护：

```text
┌─────────────────────────────────────────────────────────────┐
│                    User / Session Context                   │
├──────────────────────────────┬──────────────────────────────┤
│     Memories (长期记忆)       │     Skills (上层技能规范)     │
│  - USER.md / MEMORY.md       │  - SKILL.md 流程指导与标准   │
│  - 30+ 篇项目/系统专题档案   │  - 思考框架、TDD与验收门禁   │
├──────────────────────────────┴──────────────────────────────┤
│                    Plugins (底层核心插件)                    │
│  - 提供原生 Python 模块、MCP 服务挂载与扩展工具链           │
├─────────────────────────────────────────────────────────────┤
│                 Desktop Plugins (桌面前端组件)               │
│  - 客户端侧边栏/浮层 UI 组件（如 Token 监控看板）           │
└─────────────────────────────────────────────────────────────┘
```

- **Skills（技能）**：纯 Procedural Memory（程序性记忆与规范），通过 `SKILL.md` 告诉 Agent “如何做一件事情”（例如开发规范、设计哲学、排错流程）。
- **Plugins（插件）**：底层运行环境扩展，通过 `plugin.json` / `plugin.yaml` 与 Python/MCP 代码向 Agent 注入可执行工具、注册系统钩子与扩展协议。

---

## 🧩 4 大核心插件详解 (`plugins/`)

本仓库独立管理并跟踪 4 大核心插件资产：

| 插件名称 | 目录路径 | 核心能力与定位 | 提供的关键工具 / MCP |
| :--- | :--- | :--- | :--- |
| **`context7`** | `plugins/context7/` | **实时最新文档与代码检索**<br>解决模型训练数据截止期问题，实时查询主流库/框架的最新官方 API 与代码示例。 | `mcp__context7__query_docs`<br>`mcp__context7__resolve_library_id` |
| **`desktop-commander`** | `plugins/desktop-commander/` | **桌面级系统控制与交互终端**<br>提供长运行进程管理、流式搜索、交互式 PTY 驱动与文件编辑等高级能力。 | `mcp__desktop_commander__start_process`<br>`mcp__desktop_commander__start_search` |
| **`serena`** | `plugins/serena/` | **语义代码分析与安全重构**<br>基于 AST 与符号引用的语义级代码检索、跨文件重命名、声明跳转与语法诊断。 | `mcp__serena__find_symbol`<br>`mcp__serena__rename_symbol`<br>`mcp__serena__get_diagnostics_for_file` |
| **`superpowers`** | `plugins/superpowers/` | **Superpowers 代理工程框架**<br>提供 Superpowers 规范套件、全局流程门禁（TDD、Plan、Review）、跨平台适配与上下文注入机制。 | Superpowers 核心工作流引擎与拦截门禁 |

---

## 📂 资产目录全景

```text
C:\Users\VOS-User\AppData\Local\hermes/  (Repo Root: branch hermes)
├── README.md               # 本自述文件、资产分层说明与灾备恢复指南
├── .gitignore              # 严格白名单过滤，仅跟踪记忆、技能与插件
├── SOUL.md                 # Hermes 核心人设与交互底座规范
│
├── memories/               # 长期记忆核心存储 (Memories)
│   ├── USER.md             # 用户画像、工作流偏好与不可逾越的铁律 (动态注入)
│   ├── MEMORY.md           # 本地模型桥接、端口配置与环境常驻事实 (动态注入)
│   └── topics/             # 细分专题与项目级深度记忆档案 (30+ 篇 Markdown)
│       ├── MEMORY.md       # 专题记忆总索引清单
│       ├── user-windows-environment.md              # Windows 环境与本地网络代理规范
│       ├── edge-dev-cdp-mcp-setup.md                # Edge Dev 浏览器接管与 CDP 方案
│       ├── desktop-projects-tweak-youshouldknow.md  # 核心项目双向工程联动与锁契约
│       ├── youshouldknow-bios-knowledge-series.md   # 知识库收录、EP15及B站看门机制
│       ├── bilibili-great-together-project.md       # MBGT 项目架构与指纹分层
│       ├── workbuddy-to-api-setup.md                # 本地多模型协议转换网关
│       └── ...
│
├── skills/                 # 定制化扩展技能库 (Skills - 113 个)
│   ├── zcode-custom/       # 专属定制技能 (shared-agent-memory、frontend-design 等)
│   ├── superpowers/        # 工程开发与 TDD 纪律套件 (计划、调试、代码审查)
│   ├── software-development/ # 软件开发与调试 (python-debugpy、github、ast-grep 等)
│   ├── dogfood/            # 可用性测试 (dogfood、adversarial-ux-test)
│   └── ...
│
├── plugins/                # Hermes 核心扩展插件 (Plugins - 4 大核心插件)
│   ├── context7/           # Context7 最新文档检索 MCP
│   ├── desktop-commander/  # 桌面进程与交互终端工具集
│   ├── serena/             # 语义符号分析与代码诊断重构引擎
│   └── superpowers/        # Superpowers 规范套件与流程挂钩
│
└── desktop-plugins/        # Hermes 桌面原生前端插件 (Desktop Plugins)
    └── token-stats/        # 实时输入/输出 Token 速率与 Google 额度看板
```

---

## 🔄 自动静默备份铁律 (Silent Auto-Push)

- **触发时机**：每当会话中发生记忆新增、修改、技能调整或插件更新时；
- **执行规则**：Hermes 会在**当轮结束前自动静默提交并推送到 GitHub `hermes` 主分支**，严禁遗漏或等待用户提醒：
  ```bash
  git -C "%LOCALAPPDATA%\hermes" -c http.proxy=http://127.0.0.1:3067 add memories/ skills/ plugins/ desktop-plugins/ .gitignore README.md && \
  git -C "%LOCALAPPDATA%\hermes" commit -m "docs(memory): <更新摘要>" && \
  git -C "%LOCALAPPDATA%\hermes" -c http.proxy=http://127.0.0.1:3067 push origin hermes
  ```

---

## 💻 更换电脑 / 重装系统一键恢复指南

在全新机器或重装系统后，通过以下步骤即可瞬间恢复全部记忆、技能与插件资产：

```powershell
# 1. 确保安装 Git 与 GitHub CLI 并完成登录
gh auth status

# 2. 将本私有仓库直接克隆/对齐到 Hermes 本地根目录：
git clone -b hermes https://github.com/3304711297/shared-agent-memory.git "$env:LOCALAPPDATA\hermes"

# 3. 启动 Hermes Agent
hermes
```

启动后，Hermes 将自动加载所有常驻记忆、扩展技能、底层插件与桌面看板，无缝延续所有开发习惯与工作上下文！
