# 🔔 本地能力组件上游更新报告

> 生成时间：2026-09-07 18:41（北京时间） · 清单：`capability-inventory.json`
>
> **跟进方式**：升级对应组件后，把清单里的 `installed.version` 更新为新版本并随共享库推 `main`，本看门会在下次运行时自动收口本 Issue。

## 概览

| 组件 | ID | 上游最新 | 状态 |
|------|----|----------|------|
| Chrome DevTools MCP | `chrome-devtools-mcp` | 1.8.0 | ✅ 最新 |
| Desktop Commander | `desktop-commander` | 0.2.48 | ✅ 最新 |
| Superpowers 开发纪律套件 | `superpowers` | v6.3.0 | ✅ 最新 |
| Serena 语义代码分析 | `serena` | v1.7.0 | ✅ 最新 |
| EasyCLIProxyAPI 网关核心 | `cliproxyapi` | v7.2.152 | ✅ 最新 |
| ZCode 插件：github | `zcode-github` | 0.1.2 | ✅ 最新 |
| ZCode 内置插件组（随客户端构建种子分发） | `zcode-bundled-plugins` | 本地源 | ✅ 最新 |
| 系统 CLI：GitHub CLI | `cli-gh` | v2.100.0 | ✅ 最新 |
| 系统 CLI：Git for Windows | `cli-git` | v2.55.0.windows.5 | ✅ 最新 |
| 系统 CLI：PowerShell 7 | `cli-powershell` | v7.6.5 | ✅ 最新 |
| 系统 CLI：lychee 链接检查 | `cli-lychee` | 0.24.2 | ✅ 最新 |
| Hermes Hub 技能库（skills/ 目录提交） | `hermes-hub-skills` | ee5b5ec2 | ✅ 最新 |
| Anthropic 官方技能库（skills/ 目录提交） | `anthropic-skills` | 41bbe19d | ✅ 最新 |
| Google Gemini 官方技能库（skills/ 目录提交） | `gemini-skills` | 0fa937a5 | ✅ 最新 |
| ECC Agent 优化技能库（skills/ 目录提交） | `ecc-skills` | ca185ef5 | ✅ 最新 |
| Hermes 官网 Skills Hub 全网技能索引 | `hermes-skills-hub` | 90,698 (2026-09-07) | ✅ 最新 |
| SkillHub 社区精选技能库 | `skillhub-market` | 1,405 | ✅ 最新 |
| Cola Skill 精品技能策展市场 | `colaskill-market` | 16 | ✅ 最新 |
| Ponytail 代码极简与反过度工程技能套件 | `ponytail-skills` | 4.9.0 | ✅ 最新 |

## 明细

### Chrome DevTools MCP（chrome-devtools-mcp）

- 上游最新：**1.8.0**
- `ZCode cli/config.json mcp.servers（钉版，含防扩展清空保护参数）`：已装 **1.8.0** → ✅ 一致
- `ZCode 插件 claude-plugins-official（已补保护参数）`：已装 **1.8.0** → ✅ 一致
- `Hermes config.yaml mcp_servers（钉版，含保护参数）`：已装 **1.8.0** → ✅ 一致

### Desktop Commander（desktop-commander）

- 上游最新：**0.2.48**
- `Hermes 插件 upstream.json 记录`：已装 **0.2.48** → ✅ 一致
- `ZCode 插件 claude-plugins-official（插件壳版本 0.2.0，核心随 git-subdir main）`：已装 **0.2.48** → ✅ 一致

### Superpowers 开发纪律套件（superpowers）

- 上游最新：**v6.3.0**
- `ZCode 插件 claude-plugins-official`：已装 **6.3.0** → ✅ 一致
- `Hermes 插件 upstream.json 记录`：已装 **6.3.0** → ✅ 一致

### Serena 语义代码分析（serena）

- 上游最新：**v1.7.0**
- `Hermes 插件 upstream.json 记录`：已装 **1.7.0** → ✅ 一致
- `ZCode 插件 claude-plugins-official（版本号 0.0.0 无意义，随 hermes 评估）`：已装 **1.7.0** → ✅ 一致

### EasyCLIProxyAPI 网关核心（cliproxyapi）

- 上游最新：**v7.2.152**
- `D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64\cpa-core`：已装 **7.2.152** → ✅ 一致

### ZCode 插件：github（zcode-github）

- 上游最新：**0.1.2**
- `ZCode 插件（已启用）`：已装 **0.1.2** → ✅ 一致

### ZCode 内置插件组（随客户端构建种子分发）（zcode-bundled-plugins）

- 本地清单：`C:/Users/VOS-User/.zcode/cli/plugins/marketplaces/zcode-plugins-official/marketplace.json`
- `ZCode 内置插件（已启用）`：已装 **0.4.2** / 本地清单 **0.4.2** → ✅ 一致
- `ZCode 内置插件（已启用）`：已装 **0.5.14** / 本地清单 **0.5.14** → ✅ 一致
- `ZCode 内置插件（已启用）`：已装 **0.1.4** / 本地清单 **0.1.4** → ✅ 一致
- `ZCode 内置插件（已启用）`：已装 **0.1.0** / 本地清单 **0.1.0** → ✅ 一致
- `ZCode 内置插件（已启用）`：已装 **0.1.0** / 本地清单 **0.1.0** → ✅ 一致
- `ZCode 内置插件（已启用）`：已装 **0.1.0** / 本地清单 **0.1.0** → ✅ 一致
- `ZCode 内置组件（缓存随计算机控制联动）`：已装 **0.5.12** / 本地清单 **缺失** → 🟡 本地清单无此项
- `ZCode 内置插件（已停用）`：已装 **0.1.0** / 本地清单 **0.1.0** → ✅ 一致
- `ZCode 内置插件（已停用）`：已装 **0.1.0** / 本地清单 **0.1.0** → ✅ 一致

### 系统 CLI：GitHub CLI（cli-gh）

- 上游最新：**v2.100.0**
- `MSI 机器级安装（gh auth 走 keyring）`：已装 **2.100.0** → ✅ 一致

### 系统 CLI：Git for Windows（cli-git）

- 上游最新：**v2.55.0.windows.5**
- `D:\Git（自定义路径，升级须走官方安装器锁路径流程，禁用 winget）`：已装 **2.55.0.windows.5** → ✅ 一致

### 系统 CLI：PowerShell 7（cli-powershell）

- 上游最新：**v7.6.5**
- `winget 用户级（5.1 系统内置不列入）`：已装 **7.6.5** → ✅ 一致

### 系统 CLI：lychee 链接检查（cli-lychee）

- 上游最新：**0.24.2**
- `%LOCALAPPDATA%\Programs\lychee`：已装 **0.24.2** → ✅ 一致

### Hermes Hub 技能库（skills/ 目录提交）（hermes-hub-skills）

- 上游最新：**ee5b5ec2**（2026-09-05）docs(skills): reddit-reading spells out that no login is nee
- 基线：`ee5b5ec2` → ✅ 一致

### Anthropic 官方技能库（skills/ 目录提交）（anthropic-skills）

- 上游最新：**41bbe19d**（2026-09-03）Update frontend-design skill to avoid generic design default
- 基线：`41bbe19d` → ✅ 一致

### Google Gemini 官方技能库（skills/ 目录提交）（gemini-skills）

- 上游最新：**0fa937a5**（2026-09-02）feat: update skills for gemini-3.8-flash and canonical doc l
- 基线：`0fa937a5` → ✅ 一致

### ECC Agent 优化技能库（skills/ 目录提交）（ecc-skills）

- 上游最新：**ca185ef5**（2026-08-31）chore(release): prepare signed 2.2.1 patch (#2920)
- 基线：`ca185ef5` → ✅ 一致

### Hermes 官网 Skills Hub 全网技能索引（hermes-skills-hub）

- 上游最新：**90,698** 技能（索引时间：`2026-09-07`，自营: 197, 外部: 90501）
- 基线记录：**90,698** 技能（记录时间：`2026-09-06`）→ ✅ 一致
- 主要源分布：ClawHub: 69,150, skills.sh: 19,967, LobeHub: 505, browse.sh: 440, NVIDIA: 299 等

### SkillHub 社区精选技能库（skillhub-market）

- 上游最新：**1,405** 社区技能
- 基线记录：**1,405** 技能 → ✅ 一致

### Cola Skill 精品技能策展市场（colaskill-market）

- 上游最新：**16** 个精选技能（包含：写作蒸馏器 | 任意写作风格蒸馏复刻技能集合, 白毛股神Serenity投资思维框架, 面试准备助手 等）
- 基线记录：**16** 个技能 → ✅ 一致

### Ponytail 代码极简与反过度工程技能套件（ponytail-skills）

- 上游最新：**4.9.0**
- `Hermes skills/（6 项）+ ZCode ~/.zcode/skills（6 项副本）`：已装 **4.9.0** → ✅ 一致

---

**待跟进组件数：0** · 未纳入看门的组件见清单 `notWatched` 字段。