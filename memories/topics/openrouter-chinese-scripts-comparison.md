---
name: openrouter-chinese-scripts-comparison
description: 三个 OpenRouter 汉化油猴脚本对比结论与 datou1996+LynnGuo666 共存配置方案
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_619b1ebc-599b-48a5-ac7f-6eb15deb6d77
---

用户评估了三个 openrouter.ai 汉化油猴脚本（2026-08-21 分析），结论：

- **datou1996/openrouter-chinese**（推荐主力）：迭代最快（v1.5.22，两天 59 commits）、覆盖 20+ 页面类型、架构参考 maboloshi/github-chinese、MIT 但仓库缺 LICENSE 文件；词库经 `@require` 外链，Tampermonkey 缓存会导致更新不生效（其 FAQ 头号问题）。
- **isdoge/openrouter-chinese**：仓库最规范（CHANGELOG/截图/npm test）但 2026-07-29 后停滞（仅 6 commits），不推荐主力。
- **LynnGuo666/OpenRouter_Chinese**：工程质量最高（模块化 src + 零依赖构建 + 离线单元测试），独有人民币价格增强（Yahoo 汇率 + Frankfurter 兜底 + 30 分钟缓存）；PolyForm Noncommercial 许可**禁止商用**；`translateContent` 默认开启会把公开页正文发 Google 翻译端点（国内不通且有隐私面）。

用户选定 datou1996 + LynnGuo666 共存。推荐配置：datou1996 保持默认做全站汉化；LynnGuo 在设置面板关闭「界面翻译」(translateUi) 和「页面内容中文」(translateContent)、保留「人民币价格」(showCny)，变成纯价格增强。共存已知冲突点：两词库术语不一致、双 MutationObserver 性能开销、datou 的价格正则可能二次处理 LynnGuo 追加的 ¥ 文本。

三者安装/更新源都是 raw.githubusercontent.com，国内直连不通，均未发布 GreasyFork。与 [[github-stars-organization]] 相关（可能纳入星标整理）。
