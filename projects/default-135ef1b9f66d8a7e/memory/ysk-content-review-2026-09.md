---
name: ysk-content-review-2026-09
description: ysk 131 篇全库内容审查（2026-09-12）：P0×6/P1×26/P2 修复、审查方法论与遗留项
metadata:
  node_type: memory
  type: project
---

# ysk 全库内容审查与修复（2026-09-12）

六路并行子代理审查 131 篇（P0×6、P1×37、P2×78），已修复并推送 3 个提交：`a68459d`（P0×6+P1×26）、`9cbe667`、`6abc8b8`（P2 收尾）。CI 全绿，审查报告存 `%TEMP%/ysk-review/findings-0~5`。

## 修复的关键问题（按类型）

**安全类**：EasyCLIProxyAPI 篇 4 处明文网关 API Key → `<YOUR_GATEWAY_KEY>` 占位符（公开站点泄露）。

**环境失效类**（ZCode 2026-09-09 弃用）：两篇 ZCode 专题加历史存档横幅+过去时化；高阶指令篇 5 个幽灵命令（/temp /thinking /doctor /health /env 经源码 103 个 CommandDef 核实不存在，/thinking→/reasoning，其余→CLI 子命令）；use_real_profile 故障链勘误（v0.21.1 快照副本隔离，两文同步）。

**tweakbyjie 漂移类**（基线 b905950→5fce57f 落后 49 提交）：菜单 0-11→0-12、-RunModules→-RunModule、补 GameQos/Adapters/Backup.GameQos、BOOT-003 快照勘误（testmode-backup.json 实存）。

**Windows 事实类**：BypassNRO 25H2 被封堵、DisableAntiSpyware 已废弃、powercfg /duplicatescheme 无名称参数（26200 实测 EXIT=1）、fsutil DisableDeleteNotify 不支持逐卷、IRQL 0xFF 非法（x64 上限 15）、PS7 IWR 支持环境变量代理、GITHUB_TOKEN 1000/h/repo。

**BIOS/硬件类**：Clear CMOS 清密码仅老式主板、5800X3D 无 PBO/CO、X3D 温度墙分代 89/90/95°C、VCCIN 差一个量级、MCR+PD 因果反转（华硕口径）、SecureBoot 2011 证书 2026-06 才到期、华擎 700 系已有 ADI、DP RBR 6.48 不是 8.64、UHBR13.5 属 DP 2.0。

## 方法论沉淀（复用价值高）

1. **子代理必须增量落盘**：第一轮 6 个子代理全部在汇总阶段死于限流（模型额度 18:55 重置），成果全丢；第二轮改为每审 2-3 篇即写 findings 文件，且先读上轮 transcript 抢收中间结论。教训：长任务子代理的输出策略必须防中断。
2. **发现→双证→修复**：每个 P0/P1 都经第二证据（源码 grep、本机实测、官方文档）核实后才改，实测推翻核查记录时连记录一起改。
3. **勘误格式**：⚠️ 勘误（2026-09-12 对照<证据>）：<修正内容>，保留原判断的错误痕迹供追溯。
4. **限流应对**：deepseek-v4.1-flash 额度池枯竭时切 glm-5.3-flash（workbuddy2api 多模型路由），主会话与子代理分开评估额度。

## 遗留项（有意未做）

- 62 篇缺事实核查记录：用户拍板"全库补齐分批次"，子代理已在 findings 报告尾部列出每篇可核查声明清单，下次按清单补。
- P2×70+ 纯措辞/快照类未动（各 findings 有明细）。
- tweakbyjie 的 knowledge.lock 停在 8d0f172，日常 push 不校验（2026-09-05 策略），仅 tag 发版需提升。

[[ysk-layout-audit-typography-tools]] [[desktop-projects-tweak-youshouldknow]] [[youshouldknow-doc-details]] [[cross-repo-coverage-audit]]
