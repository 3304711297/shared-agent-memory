---
name: tweak-upstream-watch
description: tweakbyjie 上游看门机制（v2 多分支）、四源清单与用户拍板的完整提交原则
metadata:
  type: project

tweakbyjie 的上游看门（`upstream-watch` CI，每周一/三/五北京时间 10:00）：`tools/check-upstream.py`（**v2，2026-09-05 重写**，tweak `4efcf77`）以 `tools/upstream-sources.json`（**v2 schema**：`branches` 数组 + `last_synced_commits` 按分支基线）为真源，每次巡检拉上游全部分支列表：已知分支经 compare API 把基线→头部**全部 commit 明细**（SHA 锚定链接 + message）列入 Issue 报告；远端新出现的分支自动上报（附头部提交，人工评估后写基线）；分支消失提示清理基线；release tag 变化单独上报。"是否值得吸收"由人工点 diff 判断。（2026-09-05 用户确认两点：Issue 摘要须列全多条 commit；其他分支也要纳入——均已实现。）

**当前四源**（2026-09-05 扩至四源，commit/版本为基线快照，四仓当前均只有默认分支：Kiwi/Atom=main，MPO/ViVe=master）：Kiwi-Tweaks（菜单 12 QoS 来源）、Atom-Tool-Box（菜单 1 WPBT/TaskbarEndTask/PS Core 遥测来源）为正式采纳；MPO-GPU-FIX（菜单 11 排障参考）、ViVeTool（菜单 8 工具依赖，thebookisclosed/ViVe）为参考/依赖级，同样纳入看门。吸收关系与落地位置见 tweakbyjie README「上游采纳与外部依赖」章节。`upstream-report.md` 已入 .gitignore（本地试跑产物）。

**用户拍板（2026-09-05）：看门永远看完整提交，不做路径/功能过滤**——吸收是思路级而非单文件级，宁滥勿缺。**Why:** 上游任何文件的新思路都可能值得吸收，按路径过滤会漏。**How to apply:** 以后新增采纳来源时：① `upstream-sources.json` 加源（v2 字段：`branches` + `last_synced_commits`），基线取加入当时的最新值（避免上线即误报）；② 同步更新 README 上游章节（表格 + 看门覆盖说明）；③ 不加 watch_paths 之类的过滤字段；④ 无需手工指定分支——巡检会自动发现远端新分支并上报。新增源与 coverage manifest/审计器正则无关（见 [[cross-repo-coverage-audit]]），但若吸收内容产生新 tweak 调优项则触发其四资料联动。

[[cross-repo-coverage-audit]] [[desktop-projects-tweak-youshouldknow]]
