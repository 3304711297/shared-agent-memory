# 🔔 本地能力组件上游更新报告

> 生成时间：2026-09-05 11:26（北京时间） · 清单：`capability-inventory.json`
>
> **跟进方式**：升级对应组件后，把清单里的 `installed.version` 更新为新版本并随共享库推 `main`，本看门会在下次运行时自动收口本 Issue。

## 概览

| 组件 | ID | 上游最新 | 状态 |
|------|----|----------|------|
| Chrome DevTools MCP | `chrome-devtools-mcp` | 1.8.0 | 🔴 有更新 |
| Context7 MCP（文档检索） | `context7-mcp` | 4.0.5 | 🔴 有更新 |
| Desktop Commander | `desktop-commander` | 0.2.48 | ✅ 最新 |
| Superpowers 开发纪律套件 | `superpowers` | v6.3.0 | ✅ 最新 |
| Serena 语义代码分析 | `serena` | v1.7.0 | ✅ 最新 |
| EasyCLIProxyAPI 网关核心 | `cliproxyapi` | v7.2.151 | ✅ 最新 |
| ZCode 插件：github | `zcode-github` | 0.1.2 | 🔴 有更新 |
| ZCode 内置插件组（随客户端构建种子分发） | `zcode-bundled-plugins` | 本地源 | ✅ 最新 |

## 明细

### Chrome DevTools MCP（chrome-devtools-mcp）

- 上游最新：**1.8.0**
- `ZCode cli/config.json mcp.servers（钉版）`：已装 **1.7.0** → 🔴 落后
- `ZCode 插件 claude-plugins-official`：已装 **1.7.0** → 🔴 落后
- `Hermes config.yaml mcp_servers（钉版）`：已装 **1.7.0** → 🔴 落后
- 📦 claude-plugins-official 市场已推进到新版本（pin `45f187b1e320` ≠ 本地 `614b4ebe2319`），可在 ZCode 插件管理里更新该插件。

### Context7 MCP（文档检索）（context7-mcp）

- 上游最新：**4.0.5**
- `Hermes config.yaml（upstream.json 记录）`：已装 **4.0.4** → 🔴 落后
- `ZCode 插件 claude-plugins-official（远端托管版，版本号 0.0.0 无意义）`：已装 **4.0.4** → 🔴 落后

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
- `ZCode 插件（已启用）`：已装 **0.1.1** → 🔴 落后

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

---

**待跟进组件数：3** · 未纳入看门的组件见清单 `notWatched` 字段。