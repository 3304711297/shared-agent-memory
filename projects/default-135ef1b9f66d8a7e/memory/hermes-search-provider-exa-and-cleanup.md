---
name: hermes-search-provider-exa-and-cleanup
description: Hermes 检索提供商锁定为 Exa 独享、解构 gemini-web-search 伪联网本质与冗余技能清理
metadata:
  type: reference
---

## 1. Exa 独享搜索引擎配置
- **配置与生效**：用户提供专属 Exa API Key（`b01b0c97-...`），已校验 `https://api.exa.ai/search` 200 连通性，凭证安全持久化于 `~/.hermes/.env` (`EXA_API_KEY`)。
- **底层路由锁定**：在 `config.yaml` 中将 `web.backend`、`web.search_backend`、`web.extract_backend` 全量设定为 `exa`。
- **收益**：脱离了此前 Hermes 默认使用的公共免密环（Keyless Ring: Exa/Parallel/Firecrawl/Keenable），避免高峰期 429 速率限制；`web_search` 与 `web_extract` 端到端实测稳定走独享通道。

## 2. EasyCLIProxyAPI 网关中 `gemini-web-search` 本质排查
- **实测验证**：向 `127.0.0.1:18080/v1` 的 `gemini-web-search` 发起时效性提问，模型返回时间停留在 2024-05-22，未触发任何网络检索。
- **底层映射**：在 `D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64\cpa-core\config.yaml` (第 1486 行) 中，`gemini-web-search` 仅为 `gemini-3.1-flash-lite` 的强制别名（`force-mapping: true`），并未在 payload 中注入 Google Grounding 工具链。
- **架构定性**：对话模型即使具备 Grounding 也是输出自然语言文本，不能替代需要结构化元数据（`title`, `url`, `snippet`）的 Agent 工具搜索源；双端 Agent 严禁将其视作可用搜索工具。

## 3. 冗余社区搜索技能双端清理
- **溯源确认**：经对比官方内置清单 `.bundled_manifest` 与 `skills/.usage.json`，`duckduckgo-search`（作者 gamedevCloudy）与 `searxng-search` 均为 2026-09-03 后续安装的社区技能，并在 09-05 双端同步时进入 ZCode。
- **清理下线**：
  - `duckduckgo-search`：环境未装 `ddgs` 依赖，且内核原生支持 Exa 独享与公共环。
  - `searxng-search`：平台被限定为 `[linux, macos]` 且无本地/远程 `SEARXNG_URL`。
- **双端对齐闭环**：
  - Hermes 侧：通过 `hermes skills uninstall -y` 彻底卸载。
  - ZCode 侧：同步清理 `~/.zcode/skills/` 下对应两项目录。
  - 比对结果：ZCode 技能库收敛为 91 项，与 Hermes 完全对齐（无任何孤立遗留技能）。

## 4. 海外商业搜索引擎绑卡壁垒（避坑定论）
- **实测踩坑**：Brave Search 与 Tavily 均已全面收紧防薅羊毛风控，免费计划亦强制绑定外币信用卡通过 Stripe $0/小额预授权验证；国内发行的大多数双币/全币信用卡会遭遇发卡行或 Stripe 严格拦截（持续报错“未能验证您的支付方式”）。
- **协同铁律**：严禁在后续任何会话中再次向用户建议去 Brave 或 Tavily 注册“免卡免费 Key”。当前 Exa 独享额度已完全满足全场景高精度检索，免密备用严格走内核内置公共免密环或本地无密驱动（`ddgs`），杜绝无效折腾。
