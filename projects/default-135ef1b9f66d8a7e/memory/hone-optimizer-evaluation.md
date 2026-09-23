---
name: hone-optimizer-evaluation
description: auraside/Hone (Hone.gg) 游戏优化工具深度评估：闭源商业外壳、负优化工具集与 tweakbyjie/ysk 明确拒绝采纳定案
metadata:
  type: project
---

# auraside/Hone (Hone.gg) 评估与拒绝采纳定案（2026-09-23）

**Why:** 用户问「auraside/Hone 这个项目有没有值得我的 tweak 或 ysk 项目吸收的东西」。经深入审查该仓库、其配套配置仓 `auraside/hone-game-configs` 及社区实测与代码实现，裁定：**完全不吸收、不进上游雷达、不作为正向调优参考，仅作为 ysk 辨析中的典型反面教材。**

## 一、 仓库事实与本质定位

1. **空壳商业分发仓（假开源）**：
   - 官方 README 明确注明：`Built With: [A Private Electron Fork], [CLI], [C++], [C#]`，核心优化逻辑与客户端界面完全闭源，仓库内 **0 真实应用源码**。
   - 仓库仅包含一个 2.7MB 的专有安装包（`Hone - Installer.exe`）。
   - 配套库 `auraside/hone-game-configs` 仅包含少量正则 JSON，用于强行压低 Apex、CS2 等游戏的本地画质（关闭 MSAA、降低分辨率等），将“降画质换来的帧率上升”伪装成“系统黑科技优化”。
2. **捆绑散装工具与无关预设**：
   - `Files/EmptyStandbyList.exe`：古老的待机内存清空工具（在现代 Windows 上会导致微卡顿的负优化）。
   - `Files/restart64.exe`（取自 CRU）与 `Files/dccmd.exe`（Display Changer）：外来闭源命令行工具。
   - `Files/FPS/.../*.cfg` 与 `Files/Settings/Hone.veg`、`ProjectProperties17.reg`：Smooth Video Project (SVP) / RIFE 补帧滤镜配置及 Sony Vegas 剪辑软件注册表，用于视频剪辑渲染动态模糊，与实时游戏系统调优毫无关系。
3. **排他性专有协议**：
   - LICENSE 严格限制：`No Commercial Use`、`No Modification`、`No Derivative Distribution`，法律层面禁止修改与衍生分发。

## 二、 对 tweakbyjie 的裁定：明确不采纳（REJECT）

- **无代码可吸收**：核心逻辑未开源，无合规透明的脚本或模块可供借鉴。
- **机制违背工程原则**：
  1. **内存负优化**：其使用的 `EmptyStandbyList` 周期性清空 Windows Standby List 待机内存，在 Win10/11 会破坏文件缓存，引发频繁的硬缺页中断（Hard Page Faults），直接导致前台游戏规律性卡顿与 1% Low 崩塌；
  2. **过度激进破坏安全**：宣传的优化项包含粗暴禁用 Windows Defender、UAC 及 VBS，缺乏白盒状态机与备份还原（`Backup.*.ps1`）保障；
  3. **不进看门雷达**：不属于透明开源的调优工具，严禁录入 `tools/upstream-sources.json`。

## 三、 对 youshouldknow 的裁定：反面教材沉淀

Hone.gg 完美体现了 ysk `社区降延迟调机清单辨析` 所批判的几大反模式：
1. **Electron 资源开销悖论**：号称降延迟的优化工具，其客户端自身却使用 Electron 常驻后台，占用 300MB+ 内存与 CPU 调度周期，破坏“单一决策者原则”；
2. **画质降级伪装性能提升**：通过正则暴力改写游戏 config 关闭抗锯齿和降分辨率，把图形负载下降冒充为“系统提速”；
3. **商业套路与虚标数据**：免费版限制每月 10 次一键优化、进阶功能付费订阅，并展示缺乏受控测量依据的百分比收益。

**How to apply:** 后续在面对类似商业闭源调优全家桶（如 Hone、WhatTheFast、各类一键游戏提速器）时，坚持「代码白盒透明、无后台守护进程、机制有可验证证据」的准入红线。
