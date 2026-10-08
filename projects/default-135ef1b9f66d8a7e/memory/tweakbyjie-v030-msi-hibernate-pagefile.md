---
name: tweakbyjie-v030-msi-hibernate-pagefile
description: tweakbyjie v0.3.0 发版与 Part 13 PCIe MSI 中断、Part 14 休眠管理、Part 15 虚拟内存诊断模块架构
metadata:
  type: project
---

# tweakbyjie v0.3.0 特性架构与安全规约

在 2026-10-08，`tweakbyjie` 完成重大特性升级并发布 **v0.3.0**，新增三个核心模块（Part 13 PCIe MSI 中断、Part 14 系统休眠管理、Part 15 虚拟内存只读诊断指引），并扩充了核心优化（吸收 XOS TimerCoalescing 防合并、PageCombining 禁用、GPU TdrDelay 防崩溃、DWM 滚轮零延迟）。

## 1. Part 13: PCIe 设备 MSI 消息中断模式管理 (`Modules/Msi.ps1` & `Modules/Backup.Msi.ps1`)

吸收自 XOS Playbook 与 MSI Utility v3 最佳实践，消除传统 Line-based IRQ 跨设备共享与争抢开销。

### 安全白名单与防崩溃隔离铁律
- **纳管白名单**：显卡（`Display`）、网络适配器（`Net`）、存储控制器（`SCSIAdapter`, `hdc`, `IDE`）。
- **严格排除黑名单**：
  * **音频设备（`MEDIA`, `Audio`, `Sound`）**：绝不开启 MSI。实测移动端与笔记本平台（如 Intel SST 智能音频架构）强开 MSI 会直接导致驱动报 Code 10 无法启动、扬声器爆音与音频服务崩溃；
  * **主板芯片组与 PCI 桥（`System`, `Bridge`, `Root Port`, `Host Bridge`, `SRAM`, `LPC`, `eSPI`, `SMBus`）**：绝不修改中断模式，防止触发引导死锁或 PCI 树仲裁冲突。
- **仅修改已声明支持的设备**：仅在设备驱动已存在 `MessageSignaledInterruptProperties` 子键时才予优化，绝不盲目注入。
- **中断消息上限规范**：GPU 与网络设备规范化为 `MessageNumberLimit = 1`；NVMe 存储控制器保持原生多队列上限（如 2048）以维持全核中断散列分发（`DevicePolicy = 5`）。
- **快照与回滚**：操作前自动生成 `msi-backup.json`（含机器加盐签名），支持逐设备精准原子恢复。

## 2. Part 14: 系统休眠与快速启动管理 (`Modules/Hibernate.ps1` & `Modules/Backup.Hibernate.ps1`)

### 休眠物理清除与双层机制
- **双层架构辨析**：
  * **内核物理层**：由 `powercfg -h on/off` 全局控制。执行 `powercfg -h off` 会从内核删除系统根目录下的 `C:\hiberfil.sys`，立即释放与物理内存等大（如 16GB~64GB）的固态硬盘空间，并彻底禁用 Windows 快速启动（Fast Startup）；
  * **用户计划层**：电源方案（`.pow`）中的休眠超时仅控制“空闲多久触发休眠”，无法释放文件本身。
- **工程化闭环**：
  * 提供只读诊断（检测 `HibernateEnabled`、`HiberbootEnabled` 及 `hiberfil.sys` 物理体积）；
  * 关闭时自动备份原始状态至 `hibernate-backup.json`，清理残留文件，同步设置 `HiberbootEnabled = 0`；
  * 杜绝 Win11 快速启动在关机时将脏硬件驱动状态固化至镜像，保障冷重启时硬件彻底重置。

## 3. Part 15: 虚拟内存诊断与个性化设置建议指引 (`Modules/Pagefile.ps1`)

### 用户拍板原则：严格只读，绝不代改
- **原则**：虚拟内存与机型物理 RAM 容量、硬盘分区结构、个人使用习惯紧密耦合，**严禁脚本盲目自动化改动系统页面文件**；
- **只读诊断输出**：
  * 实时采集物理 RAM 总容量、`AutomaticManagedPagefile` 托管状态、所有驱动器 `pagefile.sys` 实际分配与磁盘空闲空间；
  * **阶梯式科学推荐算法**：
    - RAM <= 16GB：建议固定初始 1.5x RAM，最大 2.0x~3.0x RAM；
    - RAM 24GB~32GB：建议固定初始 1.0x~1.5x RAM，最大 1.5x~2.0x RAM（或固定 32GB~48GB 防碎片）；
    - RAM >= 64GB：建议固定 16GB~24GB，最大 32GB~48GB；
    - 分区策略：优先推荐迁移至高速 NVMe 非系统盘（如 `D:`），关闭系统 `C:` 盘托管以防碎片；建议初始大小等于最大大小，消除动态扩展碎片化。
  * 提供直观的 Windows 原生 GUI 图形化设置向导（`sysdm.cpl` ➔ 高级 ➔ 性能设置 ➔ 虚拟内存）及供高级用户参考的手动 PowerShell 脚本。

## 4. 发版门禁与知识库提锁契约
- **Tag 发版与可复现门禁**：日常 push 只做常规测试，而 `v*` tag 触发时强制执行 `tools/knowledge.lock.json` 与 `youshouldknow/main` 最新 commit SHA 的严格比对，确保发布审计结果可复现。
- **编码标准**：所有 PowerShell 模块与测试脚本严格保持 UTF-8 带 BOM（`\xef\xbb\xbf`）与 CRLF 换行，确保 Windows PowerShell 5.1 与 pwsh 双引擎语法与管道洁净。
