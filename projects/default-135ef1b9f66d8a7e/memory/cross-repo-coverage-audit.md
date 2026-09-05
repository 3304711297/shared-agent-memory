---
name: cross-repo-coverage-audit
description: tweakbyjie 与 youshouldknow 跨仓库 Coverage 审计契约、修复与同步约定
metadata:
  type: project

2026-08-21，两个项目从 GitHub main 快进同步后发现跨仓库 Coverage CI 失败：tweak 审计器错误地从 youshouldknow 请求实际属于 tweak 的 `docs/coverage/YOUSEHOULDKNOW-COVERAGE-CHECK.md`，且 manifest 为 44 项而 mapping/reference/coverage check 分别只列 26/35/21 项。修复已推送：youshouldknow `442bcda` 增加 `coverageRepository=3304711297/tweakbyjie`、`coverageBranch=main`，并将 `coverageCheck` 改为源仓库内相对路径；tweak `9e9cd53` 改审计器为本地读取 coverage check、每份资料拒绝清单外 ID、三份资料并集必须覆盖 manifest 全部 44 项，另修复 Windows PowerShell UTF-8 BOM、中文后 ID 正则、仓库根路径与 Loader warning。Coverage/test/lint/docs Actions 均成功。

**2026-08-21 路径契约变更（ysk `b42fefd` / tweak `1dbfa87`）**：youshouldknow 内容迁入 `docs/`（标准 MkDocs 布局），manifest/mapping/reference 的真实路径变为 `docs/项目导航/...`；tweak 的 `tools/Test-CrossRepoCoverage.ps1` 三处硬编码路径与 manifest 内 `mappingDocument`/`executionReference` 字段均已同步加 `docs/` 前缀。coverageCheck 字段仍指向 tweak 仓库的 `docs/coverage/YOUSEHOULDKNOW-COVERAGE-CHECK.md`（tweak 自身布局未变）。

**2026-08-21 审计收紧为逐份完全一致（ysk `c809bf9` / tweak `0392638`）**：原 `Compare-IdSet` 算出的 missing 差集被调用方 `| Out-Null` 丢弃，只有 extra 判失败，missing 仅靠三资料并集兜底——单份文档缺项但另一份补上时 CI 仍绿。收紧后每份资料（mapping/reference/coverage check）都必须与 manifest 44 项完全一致，missing 与 extra 均判失败；并集兜底已删（被子逻辑包含）。严格审计首跑即抓出 27 个真实漏项，全部是"合并编号写法"所致：执行参考的合并标题（如 `MEMORY-001/002`）展开为完整 ID，tweak 的 YOUUSEHOULDKNOW-COVERAGE-CHECK.md 检查分类重写为 44 个 ID 全显式列出。文档契约表述（两处"ID 并集"）同步更新。

**2026-08-21 跨仓库可复现锁定（tweak `0ffb512`）**：CI 此前硬编码 `-KnowledgeRef main`，同一 tweakbyjie commit 的审计结果随 youshouldknow/main 推进而漂移。现在默认从 `tools/knowledge.lock.json` 的固定 SHA 读取资料（显式 `-KnowledgeRef main` 可覆盖，供本地试跑最新 main）；CI 不再传参。提升锁定流程：先 `-KnowledgeRef main` 试跑全绿，再把 lock 的 ref 更新为新 SHA 提交。注意 lock 文件读取必须显式 `-Encoding UTF8`（PS 5.1 默认按系统码页读无 BOM 文件会乱码毁掉 JSON 解析）。

**Why:** 两仓库独立发布时，manifest 与审计资料容易先后不同步，导致 404 或错误的“每份文档必须完整一致”规则；该契约记录了文件归属和可持续校验方式。
**How to apply:** 后续修改 tweak 执行项目时同步更新 youshouldknow manifest、mapping、execution reference 与 tweak 的 coverage check；检查以 manifest 为基准，每份资料都必须与 manifest 完全一致——缺少清单内 ID 与出现清单外 ID 均判失败，不允许“另一份资料补上”的宽松口径（2026-08-21 收紧）。新增清单项时四份文件（manifest/mapping/reference/coverage check）都要同步补显式完整 ID，禁止 `X-001/002` 合并写法（审计正则提不出）。不要用忽略 404 或删掉审计来“修复” CI；先修正路径归属与资料同步。提交使用中文，main 同步优先快进，不用 reset/force push。

**2026-08-25 锁定恢复与审计器升级（tweak `cd95802`）：** lock 已提升至当前 ysk/main（`fa6f8ad8...`），CI 的 GitHub API 查询显式加 `?sha=main` 防默认分支漂移。**用户已拍板保持严格同步策略**：ysk 任何 main 提交（含 CI-only 改动）都会使 lock 过期并阻断 tweak Coverage/Release；正确顺序是先推 ysk→取新完整 SHA→提升 tweak lock→跑 Coverage→再推 tweak。审计器同日升级：`Get-ModuleSourceRefs` 解析 `Modules/X.ps1` 的 `/函数名`、`#函数名`、`:NNN` 三种后缀（通配符 glob 不匹配），`Test-ModuleSourceRef` 用 PowerShell AST 校验函数真实定义（旧正则只查文件存在、斜杠后函数名从未被校验），源码引用校验扩展到执行参考文档；新增菜单契约（11 个 `Invoke-*Module` 必须在 Menu.ps1）与 Loader 契约（Modules/*.ps1 必须全部被主入口点源）；脚本加 dot-source 守卫供 Pester 复用（`tests/CoverageTool.Tests.ps1`，10 用例）。注意：审计正则会把文档中任何 `Modules/X.ps1` 字样当真实文件校验——映射/参考文档禁止出现占位路径（曾因规范说明里写 `Modules/File.ps1#FunctionName` 而审计失败）。Coverage 44/44 仍只证明清单完整性，不证明菜单编号、目标值、备份/恢复或运行时行为正确。

**2026-08-27 策略拦截实测 + 推送合并规则（tweak 红→绿闭环）：** 同日同时改两仓时曾把 tweak 改动（`6898ca1`）先于提锁单独推送，ysk `9b1e212` 一落地即令 lock 过期，coverage-audit 实测转红（run 33072955544，12 秒即拦），证实策略自动执行而非摆设；随后单独提交锁 bump（`893b3a2`，→ ysk `9b1e212b3e...`）恢复全绿。沉淀操作规则：**凡涉及两仓，一律"先推 ysk→取完整 SHA→把提锁与 tweak 其余改动合并为同一次 tweak 提交再推"，不为锁单独烧一个提交**。lychee 已收紧为仅 200..=299 可达并按域名显式排除约 20 个反爬站（CI 不再检查这些域名，属人工复核责任）；CI Actions 全部固定完整 commit SHA。

**2026-09-05 清单 44→48 项 + 新类别需扩审计正则（tweak `fc6a39b`）：** 为闭合上游吸收联动（Kiwi-Tweaks→菜单 12、Atom-Tool-Box→菜单 1），manifest 新增 `GAMEQOS-001`（category `GameQos`，新类别）与 `CORE-017/018/019`（WPBT/TaskbarEndTask/PS Core 遥测），四资料同步。**坑：审计器 ID 提取正则（`Test-CrossRepoCoverage.ps1` 的 `Get-CoverageIds`，约 :34）硬编码前缀清单，manifest 侧直接读 JSON id 不受影响 → 本地用通用正则预检会显示一致，CI 却对每份文档报"缺少 GAMEQOS-001"**。新增清单类别时必须同步把前缀加进该正则；已有前缀下加编号则不用。ysk 侧新页联动清单：front matter `tweak_module`（gen-matrix.py 会校验矩阵页）+ mkdocs.yml nav + 分类索引 README，三者缺一会挂 docs CI；WPBT 页含微软 learn 外链已过 lychee。

[[desktop-projects-tweak-youshouldknow]] [[tweak-modularization-plan]] [[youshouldknow-modular-linkage]]
