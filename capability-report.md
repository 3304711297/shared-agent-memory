# 🔔 本地能力组件上游更新报告

> 生成时间：2026-09-08 11:36（北京时间） · 清单：`capability-inventory.json`
>
> **跟进方式**：升级对应组件后，把清单里的 `installed.version` 更新为新版本并随共享库推 `main`，本看门会在下次运行时自动收口本 Issue。

## 概览

| 组件 | ID | 上游最新 | 状态 |
|------|----|----------|------|
| Chrome DevTools MCP | `chrome-devtools-mcp` | 1.8.0 | ✅ 最新 |
| Desktop Commander | `desktop-commander` | 0.2.48 | ✅ 最新 |
| Superpowers 开发纪律套件 | `superpowers` | N/A | ⚠️ 查询失败 |
| ZCode 插件：github | `zcode-github` | 0.1.2 | ✅ 最新 |
| ZCode 内置插件组（随客户端构建种子分发） | `zcode-bundled-plugins` | 本地源 | ✅ 最新 |
| 系统 CLI：GitHub CLI | `cli-gh` | N/A | ⚠️ 查询失败 |
| 系统 CLI：Git for Windows | `cli-git` | N/A | ⚠️ 查询失败 |
| 系统 CLI：PowerShell 7 | `cli-powershell` | N/A | ⚠️ 查询失败 |
| 系统 CLI：lychee 链接检查 | `cli-lychee` | N/A | ⚠️ 查询失败 |
| Hermes Hub 技能库（skills/ 目录提交） | `hermes-hub-skills` | N/A | ⚠️ 查询失败 |
| Anthropic 官方技能库（skills/ 目录提交） | `anthropic-skills` | N/A | ⚠️ 查询失败 |
| Google Gemini 官方技能库（skills/ 目录提交） | `gemini-skills` | N/A | ⚠️ 查询失败 |
| ECC Agent 优化技能库（skills/ 目录提交） | `ecc-skills` | N/A | ⚠️ 查询失败 |
| Hermes 官网 Skills Hub 全网技能索引 | `hermes-skills-hub` | 90,698 (2026-09-07) | ✅ 最新 |
| SkillHub 社区精选技能库 | `skillhub-market` | 1,433 | ✅ 最新 |
| Cola Skill 精品技能策展市场 | `colaskill-market` | 16 | ✅ 最新 |
| Ponytail 代码极简与反过度工程技能套件 | `ponytail-skills` | N/A | ⚠️ 查询失败 |
| Hermes 本地配置守卫（更新后漂移检查） | `hermes-config-guard` | 本地源 | ✅ 最新 |
| Cangjie 仓颉内容方法论蒸馏技能 | `cangjie-distill` | N/A | ⚠️ 查询失败 |

## 明细

### Chrome DevTools MCP（chrome-devtools-mcp）

- 上游最新：**1.8.0**
- `ZCode cli/config.json mcp.servers（钉版，含防扩展清空保护参数）`：已装 **1.8.0** → ✅ 一致
- `ZCode 插件 claude-plugins-official（已补保护参数）`：已装 **1.8.0** → ✅ 一致
- `Hermes config.yaml mcp_servers（钉版，含保护参数）`：已装 **1.8.0** → ✅ 一致
- ⚠️ claude 市场查询失败：HTTPError: HTTP Error 403: rate limit exceeded

### Desktop Commander（desktop-commander）

- 上游最新：**0.2.48**
- `Hermes 插件 upstream.json 记录`：已装 **0.2.48** → ✅ 一致
- `ZCode 插件 claude-plugins-official（插件壳版本 0.2.0，核心随 git-subdir main）`：已装 **0.2.48** → ✅ 一致

### Superpowers 开发纪律套件（superpowers）

- ⚠️ 上游查询失败：HTTPError: HTTP Error 403: rate limit exceeded
- `ZCode 插件 claude-plugins-official`：已装 **6.3.0** → ⚠️ 上游查询失败
- `Hermes 插件 upstream.json 记录`：已装 **6.3.0** → ⚠️ 上游查询失败
- ⚠️ claude 市场查询失败：HTTPError: HTTP Error 403: rate limit exceeded

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

- ⚠️ 上游查询失败：HTTPError: HTTP Error 403: rate limit exceeded
- `MSI 机器级安装（gh auth 走 keyring）`：已装 **2.100.0** → ⚠️ 上游查询失败

### 系统 CLI：Git for Windows（cli-git）

- ⚠️ 上游查询失败：HTTPError: HTTP Error 403: rate limit exceeded
- `D:\Git（自定义路径，升级须走官方安装器锁路径流程，禁用 winget）`：已装 **2.55.0.windows.5** → ⚠️ 上游查询失败

### 系统 CLI：PowerShell 7（cli-powershell）

- ⚠️ 上游查询失败：HTTPError: HTTP Error 403: rate limit exceeded
- `winget 用户级（5.1 系统内置不列入）`：已装 **7.6.5** → ⚠️ 上游查询失败

### 系统 CLI：lychee 链接检查（cli-lychee）

- ⚠️ 上游查询失败：HTTPError: HTTP Error 403: rate limit exceeded
- `%LOCALAPPDATA%\Programs\lychee`：已装 **0.24.2** → ⚠️ 上游查询失败

### Hermes Hub 技能库（skills/ 目录提交）（hermes-hub-skills）

- ⚠️ 上游查询失败：HTTPError: HTTP Error 403: rate limit exceeded

### Anthropic 官方技能库（skills/ 目录提交）（anthropic-skills）

- ⚠️ 上游查询失败：HTTPError: HTTP Error 403: rate limit exceeded

### Google Gemini 官方技能库（skills/ 目录提交）（gemini-skills）

- ⚠️ 上游查询失败：HTTPError: HTTP Error 403: rate limit exceeded

### ECC Agent 优化技能库（skills/ 目录提交）（ecc-skills）

- ⚠️ 上游查询失败：HTTPError: HTTP Error 403: rate limit exceeded

### Hermes 官网 Skills Hub 全网技能索引（hermes-skills-hub）

- 上游最新：**90,698** 技能（索引时间：`2026-09-07`，自营: 197, 外部: 90501）
- 基线记录：**90,698** 技能（记录时间：`2026-09-06`）→ ✅ 一致
- 主要源分布：ClawHub: 69,150, skills.sh: 19,967, LobeHub: 505, browse.sh: 440, NVIDIA: 299 等

### SkillHub 社区精选技能库（skillhub-market）

- 上游最新：**1,433** 社区技能
- 基线记录：**1,433** 技能 → ✅ 一致

### Cola Skill 精品技能策展市场（colaskill-market）

- 上游最新：**16** 个精选技能（包含：写作蒸馏器 | 任意写作风格蒸馏复刻技能集合, 白毛股神Serenity投资思维框架, 面试准备助手 等）
- 基线记录：**16** 个技能 → ✅ 一致

### Ponytail 代码极简与反过度工程技能套件（ponytail-skills）

- ⚠️ 上游查询失败：HTTPError: HTTP Error 403: rate limit exceeded
- `Hermes skills/（6 项）+ ZCode ~/.zcode/skills（6 项副本）`：已装 **4.9.0** → ⚠️ 上游查询失败

### Hermes 本地配置守卫（更新后漂移检查）（hermes-config-guard）

- ✅ 拍板配置齐全、无 stash 残留、核心技能未被 curator 标记。

- 配置文件：`C:/Users/VOS-User/AppData/Local/hermes/config.yaml`

**① 拍板配置键（上游深合并新增默认值不会冲掉叶子，但需确认仍在）**

- ✅ `curator.enabled` = `False`（拍板值 `False`）
- ✅ `memory.nudge_interval` = `0`（拍板值 `0`）
- ✅ `skills.creation_nudge_interval` = `0`（拍板值 `0`）
- ✅ `auxiliary.background_review.enabled` = `False`（拍板值 `False`）
- ✅ `updates.non_interactive_local_changes` = `stash`（拍板值 `stash`）

**② 本地源码 stash 残留（桌面端更新不自动还原）**

- ✅ `C:/Users/VOS-User/AppData/Local/hermes/hermes-agent` 无 stash 残留
- ✅ `C:/Users/VOS-User/AppData/Local/hermes` 无 stash 残留

**③ 核心自研技能 `created_by` 标记巡查**

- ✅ 7 项核心自研技能均为非 agent 标记，curator 不会触碰

### Cangjie 仓颉内容方法论蒸馏技能（cangjie-distill）

- ⚠️ 上游查询失败：HTTPError: HTTP Error 403: rate limit exceeded
- `Hermes skills/productivity/cangjie-distill + ZCode ~/.zcode/skills/cangjie-distill`：已装 **2.5.0** → ⚠️ 上游查询失败

---

**待跟进组件数：0** · 未纳入看门的组件见清单 `notWatched` 字段。