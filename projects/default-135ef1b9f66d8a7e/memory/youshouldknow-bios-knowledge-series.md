---
name: youshouldknow-bios-knowledge-series
description: ysk 新增 BIOS 选项科普系列 21 篇（2026-09-02 批次）与 gen-matrix 平台排序缺陷修复
metadata:
  node_type: memory
  type: project
  originSessionId: sess_d3d1e7a7-cc14-4c9d-b4d1-95ca720952e9
---

2026-09-02 把 B 站 UP 主「所盼皆欣然」（mid 589200735）两个 BIOS 合集（旧版《主板BIOS选项科普》27 集 sid=8222417 + 重制版《电脑BIOS/UEFI选项内容全科普》14 集 sid=8897657）全部转录总结后整合进 youshouldknow：

- **最新同步点**：ysk `d0fc852`，tweak `653c23d`（lock=3936e704…）已闭环同步，双仓 CI 全绿、线上 Pages 已含新页面。
- **B站看门与自动 Issue 机制**：已部署 `.github/workflows/bilibili-watch.yml` 与 `tools/watch_bilibili.py`（每 6 小时自动轮询 UP 主合集），新视频自动在 GitHub 开 Issue 并通知用户。
- **重制版收录追踪**：
  - 2026-09-03 收录重制版 EP15 《NVMe识别全链路与故障排查.md》（BV1BdtX6XEdu，close #9）；
  - 2026-09-26 收录第二季 EP04 《CPPC首选核-CState与SMT调度机制.md》（BV1jVhU62Ef9，close #34）；
  - 2026-09-27 收录第二季 EP05 《CurveOptimizer原理机制与验证工具箱.md》（BV13qhR6sEXi，close #35），建立 PSIC 控制变量、V/F 曲线动态选点、首选核余量认知与五工具七步证据链体系；
  - 2026-09-28 收录第二季 EP06 《CurveOptimizer实操分核精调与翻车排查.md》（BV1Pzaa6UEaF，close #36），建立全核找底线、分核精调（APIC ID 换算与金核反常识防坑）、低负载瞬态黑屏排查树与时钟拉伸跑分铁证。
- **新增内容**：docs/BIOS与固件/ 下 20 篇系列文章（总览+入门3篇+安全2篇+硬件选项各篇含 EP15 NVMe+CPU 系列5篇）+ docs/内存超频/XMP-EXPO内存认证档科普.md；mkdocs.yml nav、两分类 README、根 README 全景表同步。每篇底部附视频出处链接；口播数字无法从转录确认处标"待核"。
- **重大缺陷修复（ysk `3936e70`）**：`scripts/gen-matrix.py` 原用 `sorted(DOCS.rglob("*.md"))` 排序 Path 对象——**Windows Path 比较大小写不敏感、CI Linux 敏感**，新增 Above4G…/AMD-PBO… 两个文件后本地校验通过而 CI 覆盖矩阵校验失败。已改为按 posix 相对路径字符串排序。教训：**ysk 新增页面后必须先跑 `python scripts/gen-matrix.py` 重新生成矩阵再提交**（workflow 的 front-matter-check/build 两个 job 都会 `--check`）；本地校验通过不代表 CI 会过，排序这类平台差异要警惕。
- 站内链接：docs/系统知识/安装系统时跳过硬件和TPM检测.md 的 firpe.cn 外链在 runner 上曾瞬时连接失败（本地 200），属偶发，重跑即绿。

**Why:** 用户指定把该系列整理进 ysk（可单开分类或完善已有内容、必须提及出处）；BIOS与固件分类被选为落点，XMP 篇放内存超频分类并互链。
**How to apply:** 后续该 UP 主出新集或用户要求补内容时，未明确强调云端时优先在当前会话直接使用当前模型调用 `video_analyze` 分析视频，且必须提取音频结合本地 Whisper 双轨交叉比对消除误差（详见 `agentic-video-distill` 与 `bilibili-content` 技能）（ZCode 已于 2026-09-09 拆除退役，旧 .zcode 工作区已作废清空；youshouldknow 仓库物理路径位于 `D:/ai coding/GitRepos/youshouldknow`）。

[[desktop-projects-tweak-youshouldknow]] [[cross-repo-coverage-audit]]
