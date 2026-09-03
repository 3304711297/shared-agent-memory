---
name: pow-file-traceability
description: ultimate-performance.pow 电源计划文件的哈希与来源可追溯性补齐
metadata:
  node_type: memory
  type: project
  originSessionId: sess_510f94fa-355d-4031-bc67-00621ccf8b1c
---

tweak 项目的二进制文件 ultimate-performance.pow 曾无法复现与校验，已补齐：
- 大小 16384 bytes，方案名 kirby，SHA256 2EADB1A9A297C985A79100B1F1DBE994A2639D53C2D6A701CA019E5012868C7B，SHA1 59015BD7662A085F0401531F768D3150838CA5AE
- 新增 docs/POWER-PLAN-SOURCE.md 记录来源、校验命令（Get-FileHash）、复现方法（powercfg /export /import /query）
- README 和 docs/reference/OPTIMIZATION-DETAILS.md 已补充哈希与来源索引
- 2026-08-27 起命名统一：`.pow` 内嵌名是 kirby，Power.ps1 导入后追加 `powercfg /changename <GUID> "ultimate-performance"` 强制规范命名（commit `95e6f64`）；本机活动计划 GUID 77cb9369-b0dd-495a-a757-f868dbf98545 也已由 kirby 改名 ultimate-performance（参数不变）。再发现名为 kirby 的计划属导入残留旧版行为，不是回归。

**Why:** 二进制文件需可追溯，否则用户无法验证完整性与复现来源。
**How to apply:** 更新 .pow 文件后需同步更新哈希于 POWER-PLAN-SOURCE.md 与 README；校验前执行 Get-FileHash。

[[desktop-projects-tweak-youshouldknow]]
