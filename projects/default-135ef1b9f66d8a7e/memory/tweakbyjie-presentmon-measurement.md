---
name: tweakbyjie-presentmon-measurement
description: tweakbyjie 模块 18（PresentMon 帧率测量）的实现、权限边界与发布/升级契约
metadata:
  type: project
---

# tweakbyjie 模块 18：PresentMon 帧率测量（2026-11-09）

## 落地

- 模块编号固定：15 只读体检、16 着色器缓存、17 游戏 exe 配置、18 帧率测量。
- `Modules/PresentMon.ps1`：菜单 1=基线、2=变更后、3=对比、4=状态；调用 `tools/PresentMon/PresentMon.exe` 采集 CSV，计算平均 FPS、1% Low、P99 帧时间、中位帧时间、卡顿次数与每分钟卡顿；判定 `improved` / `regressed` / `inconclusive`。
- 二进制：PresentMon v2.6.0 x64，随仓库分发，不自动下载；SHA256 `b2a706bc6ad475749e3b7e3409263aa1e6906d45bdcf993f6dbc0f660188f1af`，Intel Authenticode 签名，MIT。
- 发布 ZIP 必须包含 `SKILL.md` 与 `tools/PresentMon`；`measure-*.json` / `measure-*.csv` 已 gitignore。
- ysk 覆盖矩阵模块范围已扩到 1-18，`游戏性能验证流程` 映射 `tweak_module: [18]`。

## 已验证的边界

- PresentMon 需要当前用户在 **Performance Log Users** 组，否则报 `failed to start trace session (access denied)`；模块不会自动改组。
- `-Detect -Json` 输出必须为纯 ASCII（非 ASCII 转 `\uXXXX`）；Windows PowerShell 5.1 的重定向/管道按 ANSI 处理，直接输出中文会损坏。Pester 用 `Start-Process` 重定向验证。
- 单轮测量只作参考：同场景、同画质、同路线重复 3 次再下结论；1% Low 提升 ≥5% 且平均 FPS 不低于 -2%、卡顿不增加 >20% 才判 `improved`。

## 升级契约

替换 `tools/PresentMon/PresentMon.exe` → 更新 `tools/PresentMon/presentmon.json`（版本/SHA256）→ 同步 README 哈希与 `tools/upstream-sources.json` 基线 → 跑 Pester 与 PSScriptAnalyzer → CI 发布 ZIP 验证。

**Why:** 避免下次重新推断模块编号、二进制来源、权限前提与判定阈值。

**How to apply:** 改模块 18 或升级 PresentMon 时先读本卡；新增 tweak 模块时同步扩 ysk 的 `check_front_matter.py`、`gen-matrix.py` 与覆盖矩阵范围。
