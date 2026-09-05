---
name: tweak-upstream-watch
description: tweakbyjie 上游看门机制、四源清单与用户拍板的完整提交原则
metadata:
  type: project

tweakbyjie 的上游看门（`upstream-watch` CI，每周一/三/五北京时间 10:00）：`tools/check-upstream.py` 以 `tools/upstream-sources.json` 为真源，逐源拉配置分支头部最新 1 个 commit 与基线 SHA 对比、并对比 releases/latest tag，有动静就开 `upstream-watch` 标签 Issue（含完整 Compare diff 链接），"是否值得吸收"由人工点 diff 判断。

**当前四源**（2026-09-05 扩至四源，commit/版本为基线快照）：Kiwi-Tweaks（菜单 12 QoS 来源）、Atom-Tool-Box（菜单 1 WPBT/TaskbarEndTask/PS Core 遥测来源）为正式采纳；MPO-GPU-FIX（菜单 11 排障参考）、ViVeTool（菜单 8 工具依赖，thebookisclosed/ViVe）为参考/依赖级，同样纳入看门。吸收关系与落地位置见 tweakbyjie README「上游采纳与外部依赖」章节。

**用户拍板（2026-09-05）：看门永远看完整提交，不做路径/功能过滤**——吸收是思路级而非单文件级，宁滥勿缺。**Why:** 上游任何文件的新思路都可能值得吸收，按路径过滤会漏。**How to apply:** 以后新增采纳来源时：① `upstream-sources.json` 加源，`last_synced_commit/release` 取加入当时的最新值（避免上线即误报）；② 同步更新 README 上游章节（表格 + 看门覆盖说明）；③ 不加 watch_paths 之类的过滤字段；④ 分支名用仓库默认分支（Kiwi/Atom=main，MPO/ViVe=master）。新增源与 coverage manifest/审计器正则无关（见 [[cross-repo-coverage-audit]]），但若吸收内容产生新 tweak 调优项则触发其四资料联动。

[[cross-repo-coverage-audit]] [[desktop-projects-tweak-youshouldknow]]
