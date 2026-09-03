---
name: pester6-mock-pitfalls
description: Pester 6（本机 6.1.0）mock 原生命令的三个实测坑：param 条件分支不可靠、$script: 捕获列表不稳、It 必须包 Describe
metadata:
  type: reference
---

在 tweak 项目用 Pester 6.1.0 给 PowerShell 脚本写测试时实测踩过的坑：

1. **Mock cmdlet（如 Read-Host）不要写 `param($Prompt)` 再按提示词分支返回不同值**——参数绑定不可靠，实测菜单 prompt 拿到空值走进无效输入分支。若各调用点需要不同返回值，优先改被测代码走适配器（如 Test-ConfirmChoice 走 Set-TweakAdapters -Confirm 注入），mock 则无条件返回单一值。
2. **跨 BeforeAll/mock 回调捕获调用序列要用闭包普通变量**（`$calls = [List[string]]::new()` 定义于 BeforeAll，mock 体直接 `$calls.Add(...)`，It 里同样读 `$calls`）；用 `$script:$name` 绑定实测抓到空列表。
3. **mock 原生 exe（powercfg.exe/bcdedit.exe）时 `$args -join ' '` 是完整命令行含绝对路径**，switch 正则要写成 `'import .*xxx\.pow'` 这类含路径匹配，不能假设只有子命令相邻；循环使用前记得在 mock 里 `$global:LASTEXITCODE = 0`。
4. **It 不能放在文件根级**，必须包 Describe/Pester 6 会报 "Test cannot be directly in the root"；临时诊断测试文件放 tests/_diag.Tests.ps1 用 `-Path` 单跑，跑完删除。

**Why:** 这些坑每个都浪费了 2-4 轮调试轮次，且症状（断言拿到 0 次/空值）会误导排查方向先怀疑生产代码。
**How to apply:** 在 [[project-security-audit-2026-08-25]] 相关两仓写 Pester 测试前按此避坑；优先复用已有 Adapters.Tests.ps1 与 PowerPlan.Tests.ps1 的成熟写法。
