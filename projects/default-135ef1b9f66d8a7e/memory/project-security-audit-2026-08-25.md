---
name: project-security-audit-2026-08-25
description: 2026-08-25 对 tweakbyjie 与 youshouldknow 的安全审计结果及当日完成的七阶段修复
metadata:
  node_type: memory
  type: project
  originSessionId: sess_073ef12c-e861-4f05-92d2-11f62185bf91
---

2026-08-25 对 `C:/Users/VOS-User/Desktop/tweak` 与 `C:/Users/VOS-User/Desktop/youshouldknow` 做只读审计。未发现主运行脚本中的 `Invoke-Expression`、`DownloadString` 或下载远程脚本后直接执行；但 tweakbyjie 仍应按“高权限、需人工审慎运行”的系统修改工具对待，Coverage 通过不等于安全或可完全回滚。

**最高优先级风险：**
- `defender-removal.ps1` 将 SYSTEM 重试命令写入用户可写 `%TEMP%` 的 `.cmd` 后由 SYSTEM 计划任务执行，存在临时文件竞态/劫持风险；另会递归接管并删除 Defender 系统组件，缺少完整恢复机制，并可能在部分失败后强制重启。
- 旁车备份恢复文件位于脚本目录且缺少签名、ACL、机器绑定和充分白名单：`Backup.Nvme.ps1` 恢复时信任 JSON 路径，`Backup.Bcd.ps1` 将 JSON Value 拼入 bcdedit 参数，`Backup.Service.ps1` Restore 缺少服务白名单；管理员恢复前必须视备份为不可信输入。
- VBS“恢复”不是原始状态回滚；测试模式关闭会保留 `nointegritychecks`；EFI 清理缺少实例绑定/事务保护。

**高优先级工程/文档风险：**
- `youshouldknow/docs/系统知识/电源计划创建与优化指南.md` 曾写菜单 6，实际 `tweakbyjie/Modules/Menu.ps1` 是 6=服务优化、7=超性能电源计划，可能把用户导向批量服务修改。
- tweak 的 `-RunModule`/`.cmd` 用法不是真正非交互：`.cmd` 丢弃 `%*`，模块仍调用 `Read-Host`；CI 声明 `workflow_dispatch` 但任务条件未包含该事件，手动运行可能全部 skipped。
- `tweak/tools/knowledge.lock.json` 锁定 `6503dc3...`，落后当前 ysk/main `9da3e7d...`，正式 Coverage/Release 门禁会阻断下一次发布。

**中优先级风险：** 全局 `ErrorActionPreference=Continue` 和多处失败后继续执行可能留下半完成状态；Registry/Defender/Service/Power 等部分操作没有完整原值快照；服务停止失败可能被静默；CI 使用可变 Action/runner，ysk deploy 重新构建而非发布已验证 artifact，lychee 全局接受 403/429 且外链可达性不稳定。

**审计通过项：** 本地 MkDocs 导航/相对链接此前通过；Front Matter 校验 69 篇扫描、5 篇含元数据、单测 10/10；`mkdocs build --strict` 退出 0。当前 Coverage 的 44/44 只证明清单 ID 集合与少量引用可解析，不证明实际行为、风险或恢复正确性。

**后续处理顺序：** 先隔离/修复 Defender SYSTEM 临时任务和强制重启，再修正电源菜单编号与 lock；随后处理备份输入白名单、BCD/VBS 恢复语义、真实非交互接口、旧行号与 CI 发布竞态。不要用 `reset`/`force push` 覆盖 main；高风险改动按 TDD/计划/验证流程执行。

**2026-08-25 CI 验证结果（推送后实测）：** tweakbyjie 共 7 次运行——第一次推送（`caca8dc`）coverage-audit 失败、release 正确跳过，原因是当时 lock 仍锁旧 `6503dc`（即审计发现的旧问题，被门禁按设计拦下，下一笔提交即修复）；其后 6 次全绿。**副作用：逐笔推送 6 个提交导致自动发布连发 v0.2.9~v0.2.14 六个补丁版本**（设计内行为：main 每次全绿推送自动 patch+1）；最新 v0.2.14 指向 `52b87d0`，ZIP+SHA256SUMS 齐全，含全部安全修复（defender-removal 默认 DryRun）。发布串行化在连发中实测无竞争。**经验：批量改动应攒齐一次推送，或改手动触发发布，避免烧掉补丁版本号。** ysk 3 次 docs 工作流全绿；本地 lychee 报的外链失败在本机 CI 中通过，证实属本机网络波动而非真实死链；线上电源计划页已验证含"选项 7"、无"选项 6"。**明确遗留（留作独立变更）：** Actions 固定完整 commit SHA、Python/PowerShell 依赖哈希锁定、ysk 部署改用已验证构建产物（现以部署互斥并发缓解竞态）、lychee 403/429 全局放行收紧为按域名、高危路径依赖注入适配器化、BCD/EFI/VBS/Defender 真实集成验证只能在隔离 Windows VM 做（禁止开发机执行）。

**遗留项完整清单（2026-08-25 用户追问"只剩这四个了吗"后 grep 核对补全——此前总结只报供应链四项属漏报）：** 代码层还有：①源码 `$script:TweakVersion` 仍为 0.2.1 而 tag 已到 v0.2.14（`tweakbyjie.ps1:26`，发布包被 CI 临时注入但源码/本地运行显示旧版）；②主脚本 `$ErrorActionPreference` 仍为 Continue（`tweakbyjie.ps1:24`，仅 defender-removal 改为 Stop），模块点源失败仍可能继续进菜单；③`Service.ps1:52` 停止失败仍报 "stopped and disabled"；④测试模式 Part 3/4 仍无原值备份、关闭仍无条件保留 `nointegritychecks`（`Bcd.ps1:33/63`）；⑤VBS/EFI 无原始快照，EFI 清理按盘符+固定路径猜、可能误卸用户卷；⑥菜单 1 核心项与 MPO 无备份时"恢复默认"仍直接删受管值；⑦备份文件无机器/环境绑定，跨机复制旧快照仍可通过 schema；⑧适配器注入未做（BCD/注册表/服务/CIM/确认/重启仍硬编码）；⑨隔离 VM 集成验证未做。文档层：ysk 约 20 篇专题文档共 **31 处 `2026-08-21` 旧核查基线**（grep 实测）——不能只改日期，须逐篇复核或如实标注"此后未复核"；执行参考正文 `:NNN` 已标注为历史快照（可接受）；DP-HDMI"设备尚未上市"等时效声明待重核。**建议修复顺序：TweakVersion → 错误策略+误导性成功消息 → 测试模式备份 → 备份机器绑定 → 文档基线逐篇复核 → 供应链四项。**

**2026-08-26 遗留项修复进度（续会话实测）：** 代码层 ①②③④⑤⑥⑦ 已全部完成并推送——①版本常量对齐 tag+VersionConsistency 测试；②ErrorActionPreference=Stop/模块加载失败 exit 3/菜单顶层兜底 catch（`235fe30`）；③Service 停止失败消息区分+rebootRequired 全分支补全（同提交）；④测试模式 Part3 先快照 testmode-backup.json 再改、Part4 按快照恢复原值（`06204f5`）；⑤VBS/Hyper-V 快照 vbs-backup.json（注册表5值+BCD3值+功能3个）+菜单子项3恢复（`f874b0b`）；⑥菜单1核心17值+系统20值快照 registry-backup.json+子项4恢复（`4fa3a34`），MPO 备份此前已存在无需改；⑦新增 Get-BackupMachineId（MachineGuid 的带域 SHA256），8 个备份模块全部写入 Binding 且 schema 校验强制匹配，跨机快照被拒（`b6ad12b`）——**升级后旧无绑定备份不可恢复需重新生成**。测试 56→86 项全绿；Coverage 审计持续全绿；自动发版已到 v0.2.20。**仍遗留：** ⑧适配器注入（大重构，建议单独立项对齐后再做）；⑨隔离 VM 集成验证（禁止开发机执行）；文档层 31 处 `2026-08-21` 基线逐篇复核（ysk 仓库）；供应链四项；发布策略改 tag 触发。注意：当日逐单元推送连发 v0.2.16~v0.2.20 五个版本号。

[[desktop-projects-tweak-youshouldknow]] [[cross-repo-coverage-audit]] [[tweak-modularization-plan]] [[youshouldknow-modular-linkage]]

**2026-08-26 收尾结果（最终核验）：** 供应链/发布/文档/适配器均已落地：tweak `c075cf3`，ysk `a6ba1ec`；两仓工作区干净；tweak main push CI `32980222681` success，ysk docs CI `32980116729` success，Pages `32980203093` success；tag-only 发布策略生效，main push 未创建新 release，Latest 仍 v0.2.20。tweak 本地 Pester 90/90、Coverage 44/44；ysk strict build、Front Matter 69/69、unittest 10/10、lychee 413 inputs/0 errors 均有实测证据。已新增 `tweak/docs/isolated-vm-verification.md`；#9 仅写验证方案，未在开发机执行。

**用户已明确表示不使用虚拟化相关功能：** 不需要准备 VM，也不需要执行 #9 真实高权限集成验证；可忽略主菜单 9（Device Guard EFI 清理）和 10（VBS/Hyper-V 管理）及验证文档中对应部分。除非未来主动启用这些功能，否则无需在当前开发机执行 BCD、EFI、Defender、VBS/HVCI、批量服务修改或恢复测试；代码、文档、供应链和 CI 已完成。

**2026-08-27 本机优化状态审计结论（用户逐条确认的故意偏离，后续审计勿再标记为回归）：** 除以下三点外全部一致（Defender 95/95、核心17、系统20、MPO方案A、BCD高级7项、内存压缩/Trim 等）：①活动电源计划 GUID `77cb9369` 原名 kirby，2026-08-27 已应用户要求改名为 **ultimate-performance**（GUID 与参数不变，等同 ultimate-performance.pow）；②hypervisorlaunchtype/vsmlaunchtype 已由用户改为脚本目标 off（不用虚拟化）；③XboxGipSvc/XblAuthManager/XboxNetApiSvc/XblGameSave/bthserv/embeddedmode 为 Disabled 属用户故意（本机不玩 Xbox；脚本设 Manual 是为兼容他人机器），BITS=Manual 正确。仓库根无任何 *-backup.json 快照属正常。

**2026-08-27 治理收尾增量：** `6898ca1` 两仓 .gitignore 补 `__pycache__/`、`*.pyc` 及 tweak 四个漏掉的备份产物（testmode/defender-policy/vbs/registry-backup.json），主脚本头注释同步最新菜单行为；ysk 同日 `9b1e212` 仅 gitignore。Pester 基线升至 92 项。

**2026-08-27 发布与文档治理变更：** 提交 `84bf502` 移除 CHANGELOG.md：Release 说明改用 `gh release create --generate-notes` 自动生成，打包清单与 README 去掉 CHANGELOG 引用；release 任务死分支清理后版本号即 tag 本身，因此发版流程变为：先改源码 `$script:TweakVersion` → 提交 → 推 `v*` tag（VersionConsistency 测试校验常量与最高 tag 一致）。提交 `95e6f64` 为上述电源计划命名修复。CI run 33069606973、33072076949 均绿。

**BCD 变化质疑的调查结论（2026-08-27）：** 用户发现本机 BCD 有非默认项并询问是否 AI 所改。只读核查：会话中仅执行过 `bcdedit /enum*` 只读命令；测试中 BCD 写入路径均有 mock；但用户的 PowerShell 历史（`%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`，Documents 下旧路径不存在）记录了用户自己执行过 `bcdedit /set hypervisorlaunchtype off`、`/set vsmlaunchtype off`。教训见 [[evidence-before-absence-claims]]。

**Why:** 用户要求检查两个项目的问题/隐患；这些是跨会话仍会影响后续修复排序和安全边界的非代码历史事实。
**How to apply:** 后续涉及 tweak 高权限路径、Coverage lock、联动文档或 CI 发布时，先读本审计；将 Coverage 44/44 表述为清单完整性，不作为安全认证；任何修复前先重新核对当前源码与远端状态。
