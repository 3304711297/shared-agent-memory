---
name: file-workflow-official-benchmark
description: 官方读文件流四件套与 2026-09-13 实测对比结论
metadata:
  type: reference
---

Hermes 官方文件流（tools-reference / context-references）：`read_file` 分页（offset/limit，~100K 截断 + next_offset，Office/ipynb/PDF 自动抽文本）→ 先 `search_files` 定位再读 → 终端禁 cat/head/tail/grep/rg/find/ls → 3 步以上带过滤的批量走 `execute_code` → CLI 限定 `@file:L1-L2` / `@folder:` / `@diff`（桌面端不可用）→ 移动/复制无原生工具，走 terminal mv/cp。

2026-09-13 实测（代码按 4 chars/token 估算）：小文件（39KB / 764 行）行号开销 +7.5%（约 +750 token），单次小读旧方式反而更省；大文件（4.6MB）全量注入约 1.16M token vs 截断约 25K token，相差约 46 倍。搜索同引擎 ripgrep：`rg -c` 纯计数最瘦，定位 + 精读 `search_files` 一次到位。批量任务 `execute_code` 单次 0.03s vs terminal + python 89ms，N 步链差距按步数放大。

Why: 大文件截断是生死线；小读行号税是自愿交的保险费，防一次百万 token 级手滑。
How to apply: 常驻规则已进 SOUL / USER（2026-09-13）；`@引用` 相关写法只在 CLI 会话生效，桌面会话不写。
