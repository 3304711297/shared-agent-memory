# 🔔 本地能力组件上游更新报告

> 生成时间：2026-09-05 13:32（北京时间） · 清单：`capability-inventory.json`
>
> **跟进方式**：升级对应组件后，把清单里的 `installed.version` 更新为新版本并随共享库推 `main`，本看门会在下次运行时自动收口本 Issue。

## 概览

| 组件 | ID | 上游最新 | 状态 |
|------|----|----------|------|
| Chrome DevTools MCP | `chrome-devtools-mcp` | 1.8.0 | ✅ 最新 |
| Desktop Commander | `desktop-commander` | 0.2.48 | ✅ 最新 |
| Superpowers 开发纪律套件 | `superpowers` | v6.3.0 | ✅ 最新 |
| Serena 语义代码分析 | `serena` | v1.7.0 | ✅ 最新 |
| EasyCLIProxyAPI 网关核心 | `cliproxyapi` | v7.2.151 | ✅ 最新 |
| ZCode 插件：github | `zcode-github` | 0.1.2 | ✅ 最新 |
| ZCode 内置插件组（随客户端构建种子分发） | `zcode-bundled-plugins` | 本地源 | ✅ 最新 |
| 系统 CLI：GitHub CLI | `cli-gh` | v2.100.0 | ✅ 最新 |
| 系统 CLI：Git for Windows | `cli-git` | v2.55.0.windows.5 | ✅ 最新 |
| 系统 CLI：PowerShell 7 | `cli-powershell` | v7.6.5 | ✅ 最新 |
| 系统 CLI：lychee 链接检查 | `cli-lychee` | 0.24.2 | ✅ 最新 |
| Hermes Hub 技能库（skills/ 目录提交） | `hermes-hub-skills` | 4441a2a2 | ✅ 最新 |

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

- 上游最新：**v7.2.151**
- `D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64\cpa-core`：已装 **7.2.151** → ✅ 一致

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

- 上游最新：**4441a2a2**（2026-09-04）docs(agents): split AGENTS.md into root + per-area files (≤8
- 基线：`4441a2a2` → ✅ 一致

---

**待跟进组件数：0** · 未纳入看门的组件见清单 `notWatched` 字段。