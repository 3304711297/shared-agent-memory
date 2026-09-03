# Hermes Agent 核心记忆与能力资产库 🧠

<p align="center">
  <strong>跨会话持久化长期记忆 · 定制化扩展技能 (Skills) · 桌面原生插件 (Desktop Plugins)</strong>
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

本仓库（`3304711297/shared-agent-memory`）是 **Hermes Agent** 作为用户主力 AI 编程与操作系统助手时的**跨端唯一真源（Single Source of Truth）**。

用于集中持久化备份：
1. **跨会话长期记忆**：用户画像、操作偏好、系统环境配置、工程架构契约与避坑指南；
2. **定制化技能库（Skills）**：领域专业工作流（如 `shared-agent-memory`、`superpowers`、`frontend-design` 等）；
3. **桌面端原生插件（Desktop Plugins）**：实时 Token 监控、额度看板等定制桌面组件；
4. **Agent 人设与灵魂设定（SOUL.md）**。

> 🔒 **私有仓库安全说明**：本仓库设为 Private，严禁跟踪与上传任何 `.env`、`auth.json`、API Token、Session 数据库及带锁的运行时敏感凭据。

---

## 📂 资产目录全景

```text
C:\Users\VOS-User\AppData\Local\hermes/  (Repo Root: branch hermes)
├── README.md               # 本自述文件与新机灾备恢复指南
├── .gitignore              # 严格白名单过滤，仅跟踪记忆、技能与插件
├── SOUL.md                 # Hermes 核心人设与交互底座规范
│
├── memories/               # 长期记忆核心存储
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
├── skills/                 # 定制化扩展技能库 (Skills)
│   ├── zcode-custom/       # 专属定制技能 (shared-agent-memory、frontend-design 等)
│   ├── superpowers/        # 工程开发与 TDD 纪律套件 (计划、调试、代码审查)
│   └── ...
│
└── desktop-plugins/        # Hermes 桌面原生前端插件
    └── token-stats/        # 实时输入/输出 Token 速率与 Google 额度看板
```

---

## 🔄 双 Agent 演进与自动备份契约

### 1. 记忆体系整合
- 原 ZCode 历史长期记忆（30+ 篇详尽专题）已完整合并迁移至 Hermes 专属记忆目录 `memories/topics/`；
- 默认主分支（Default Branch）正式设定为 **`hermes`**。

### 2. 自动静默备份铁律 (Silent Auto-Push)
- **触发时机**：每当会话中发生记忆新增、修改、技能更新或插件变更时；
- **执行规则**：Hermes 会在**当轮结束前自动静默提交并推送到 GitHub `hermes` 主分支**，无需等待用户提醒，无需中断确认：
  ```bash
  git -C "%LOCALAPPDATA%\hermes" -c http.proxy=http://127.0.0.1:3067 add memories/ .gitignore skills/ README.md && \
  git -C "%LOCALAPPDATA%\hermes" commit -m "docs(memory): <更新摘要>" && \
  git -C "%LOCALAPPDATA%\hermes" -c http.proxy=http://127.0.0.1:3067 push origin hermes
  ```

---

## 💻 更换电脑 / 重装系统一键恢复指南

在全新机器或重装系统后，通过以下步骤即可瞬间恢复全部记忆与扩展能力：

```powershell
# 1. 确保安装 Git 与 GitHub CLI 并完成登录
gh auth status

# 2. 将本私有仓库直接克隆/对齐到 Hermes 本地根目录：
git clone -b hermes https://github.com/3304711297/shared-agent-memory.git "$env:LOCALAPPDATA\hermes"

# 3. 启动 Hermes Agent
hermes
```

启动后，Hermes 将自动读取所有常驻记忆、扩展技能与桌面插件，无缝延续所有开发习惯与项目上下文！
