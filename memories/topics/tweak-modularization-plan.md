---
name: tweak-modularization-plan
description: tweakbyjie 单文件模块化方案与落地进展
metadata:
  node_type: memory
  type: project
  originSessionId: sess_9523491b-83bd-433d-81a2-4d5fdb39af2b
---

tweakbyjie.ps1 已完成第一阶段模块化与工程化补齐：2102 行单文件 → Loader 81 行 + Modules/ 7 文件（Common.ps1 215行 通用注册表/BCD/验证/重启、Backup.Mpo 103、Backup.Bcd 80、Backup.Service 67、Backup.SecurityMitigation 58、Backup.Nvme 159、Menu.ps1 1358行 Show-TweakMenu 11个Part），总计 2121 行。Loader 通过 `. "$PSScriptRoot/Modules/X.ps1"` 点源共享 $script:ok/$fail/$skip/$rebootRequired 与 $PSScriptRoot 锚点，缺模块时提示整仓下载。约束保持：powershell -ExecutionPolicy Bypass -File .\tweakbyjie.ps1 入口、ZIP 可搬运、PSScriptAnalyzer 0 Error、点源不卡死、可回滚。缺失的 Test-NativeNvmeConfigured/Test-NativeNvmeEffective 已补齐于 Modules/Backup.Nvme.ps1:75/83，用 Show-TweakMenu + $MyInvocation 守卫解决点源卡死。

工程化新增：.gitattributes（*.ps1 cRLF / *.yml lf / *.pow binary）、.gitignore（.bak*）、PSScriptAnalyzerSettings.psd1（Error+Warning，排除 PSAvoidUsingWriteHost）、.github/workflows/lint.yml（Invoke-ScriptAnalyzer）与 test.yml（Pester 5 / tests/Backup.Tests.ps1，CI 执行 Install-Module Pester -MinimumVersion 5.0 + New-PesterConfiguration）。文档同步：docs/POWER-PLAN-SOURCE.md、README.md、docs/reference/OPTIMIZATION-DETAILS.md 补充电源计划哈希与来源，行号漂移改为函数定位，docs/design/CODE-REFACTOR-STATUS.md / MODULE-ROADMAP.md / DEVELOPMENT-NOTES.md / docs/README.md 标记第一阶段完成。

2026-08-20 修正 docs/reference/OPTIMIZATION-DETAILS.md:622 过时结论（提交 7f2720c）：将“Test-NativeNvmeConfigured/Test-NativeNvmeEffective 在源码中未找到定义、可能运行时失败”改为由 Modules/Backup.Nvme.ps1:75/83 提供，CI 在 Pester 5 下对定义与返回值已有覆盖（tests/Backup.Tests.ps1:27）；另一 AI 复检指出本机 Pester 3.4.0 与测试文件的 Pester 5 BeforeAll 语法不匹配导致本地 The BeforeAll command may only be used inside a Describe block 报错，属环境版本不匹配非逻辑故障，CI 已 success。复检补充（2026-08-20）：当前 Pester 覆盖仅限函数存在性及返回对象结构（FileExists/State），不等同于覆盖 NVMe 实际配置写入、重启后生效与硬件行为，属于覆盖范围说明非故障。

Actions 修复：PSUseCompatibleCommands/Syntax 报 TargetProfiles cannot be empty → 删除该两条规则；test 点源进入 while → 封装 Show-TweakMenu 加守卫。2026-08-21 又新增跨仓库 Coverage 审计并修复：`tools/Test-CrossRepoCoverage.ps1` 从 youshouldknow 拉取 manifest/mapping/reference，从当前 tweak checkout 读取 coverage check，采用资料 ID 并集覆盖规则。同日提交 `b639664` 修复两个模块化回归：① 函数体内 $PSScriptRoot 解析到 Modules/ 目录 → Loader 顶层定义 `$script:RepoRoot = $PSScriptRoot`，模块内定位仓库根文件（.pow/ViVeTool.exe）一律用它，禁止在 Modules/*.ps1 函数体用 $PSScriptRoot；② 删除 Part 8 回滚分支对 $script:rebootRequired 的无条件清零；另清理死变量 moduleFailBaseline、新增 release.yml（推 v* tag 打整仓 ZIP+SHA256SUMS 发 Release）、lint 钉 PSScriptAnalyzer 1.25.0、三工作流补 permissions/timeout/concurrency/checkout v5、删除 lint.yml 恒绿空转 job。下一阶段待办：Menu.ps1 按 Power→Bcd→Mpo→Service 增量拆 Parts（1358 行仍整块），最大块是 Part 5 Defender（328 行，且是唯一无快照闭环的高风险模块，拆分时应同批做 Defender 策略快照）。

2026-08-21 第二批（提交 `53b54ac`）：Part 5 已拆出——`Modules/Defender.ps1`（Invoke-DefenderModule 子菜单：1 应用 / 2 按快照恢复 / 0 返回）+ `Modules/Backup.Defender.ps1`（约 95 个策略值 + 4 个自启动项统一定义于 `$script:defenderPolicyValues`/`$script:defenderStartupValues`，快照/写入/恢复共用一份清单；`defender-policy-backup.json` Version 1 结构校验、已有快照不覆盖、备份失败阻止修改）。Menu.ps1 1355→1025 行。修复潜伏 bug：`0xFFFFFFFF` 十六进制字面量在 PS 5.1 与 7.x 中同样被解析为 Int32 的 -1（最高位为 1 的 8 位十六进制按二补码处理，规则两版一致），schema 的 DWord 上限比较必须用 `[uint32]::MaxValue`——5.1 不支持 7.x 才有的 `u` 无符号后缀，此写法两版通用（SecurityMitigation 同款已修）。Loader 新增 `TWEAK_SKIP_ADMIN_CHECK=1` 跳过管理员检查供本地测试。新增 Pester 用例：Defender schema 负向×4、清单无重复、数量=95。剩余待拆：Registry(Core Part 1)、Virtualization(Part 9/10)、Nvme 执行(Part 8)；后续方向：Ensure/Restore 往返测试与 CodeCoverage、Write-Log 日志、Loader param() 参数化入口。

2026-08-21 第三批（提交 `e9f7c31`）：Ensure/Restore 真实往返测试落地——Backup.SecurityMitigation/Backup.Defender 的 Ensure/Test/Restore 增加可选清单参数（默认内置清单，菜单调用零改动），`tests/RoundTrip.Tests.ps1` 在 HKCU 临时键沙箱做备份→篡改→恢复→断言闭环（DWord/String/Binary/启动项，不碰真实系统）；顺带修复两处：Ensure 写后回读校验未传注入清单、Restore-DefenderStartupValue 对"原始不存在但当前存在"的启动项现在删除还原（与策略值语义对齐）。CI pester 任务启用 CodeCoverage（29.6%）。本地 pwsh 与 5.1 均 18/18；pwsh 本地测试需先 `Install-Module Pester -RequiredVersion 6.1.0 -Scope CurrentUser`（pwsh 与 5.1 的用户模块目录不共享）。下一批候选：Write-Log 日志/Loader param() 参数化入口，或继续拆 Registry(Part 1)/Virtualization(9/10)/Nvme(Part 8)。

2026-08-21 第四批（提交 `94aff84`）：**模块化全部完成**——Part 1 → `Modules/Registry.ps1`（Invoke-RegistryModule）、Part 8 → `Modules/Nvme.ps1`（Invoke-NvmeModule，编排层；备份逻辑仍在 Backup.Nvme.ps1）、Part 9/10 → `Modules/Virtualization.ps1`（Invoke-DeviceGuardModule + Invoke-VbsModule）。Menu.ps1 1041 → 509 行（仍含 Part 2/3/4/6/7/11 六个内联块与横幅/队列调度/分发链）。⚠️ 勘误：此前总结「11 个功能模块全部为独立函数」不准确——实际迁出为独立函数的仅 Part 1/5/8/9/10 共 5 个，其余六个仍内联。用户已确认下一步（2026-08-21）：继续拆分这六个内联 Part。计数器统一为 `$script:` 作用域。Loader 模块清单现为：Common、Backup.Mpo、Backup.Bcd、Backup.Service、Backup.SecurityMitigation、Backup.Nvme、Backup.Defender、Defender、Registry、Nvme、Virtualization、Menu（12 个）。本地 pwsh/5.1 均 25/25。

**Why:** 单文件维护与测试困难，模块化提升可维护性；工程化与文档可追溯性是联动基础；需区分本地 Pester 版本与 CI 环境，避免误判。
**How to apply:** 新增功能以独立 Modules/X.ps1 加入并在 Loader 点源，避免动 Menu 嵌套；模块内定位仓库根文件一律用 `$script:RepoRoot`（函数体内 $PSScriptRoot 指向 Modules/）；新建含中文 .ps1 必须带 UTF-8 BOM（无 BOM 被 PS 5.1 按 GBK 解析）；每阶段验证 Parse OK、dot-source OK、lint/test 通过；更新 .pow 后同步哈希；本地测试用 TWEAK_SKIP_ADMIN_CHECK=1 + Pester 5+，CI 以 test.yml 为准。

[[desktop-projects-tweak-youshouldknow]] [[pow-file-traceability]] [[youshouldknow-modular-linkage]] [[youshouldknow-doc-details]]
