---
name: mechrevo-jiguangx-bios-firmware-reference
description: 机械革命极光X (GM6AQ7C) 32MB BIOS固件解包逆向、硬件规格与DDR5-6400超频参数全量参考
metadata:
  node_type: memory
  type: reference
---

# 机械革命极光X (GM6AQ7C) BIOS/固件架构与硬件全量技术参考

本文档记录基于 `D:\ai coding\backup.fd`（32.00 MB 全量 SPI Flash 物理固件镜像）通过专用固件逆向工具链（`UEFIExtract`、`ifrextractor-rs`、`MEAnalyzer`）深度解包逆向分析所得的全部固件结构、硬件配置、驱动栈、ACPI 设备表、NVRAM 变量数据库与内存超频时序参数。

---

## 一、整机物理硬件与运行态规格

- **整机品牌与型号**：机械革命 极光X（MECHREVO JiguangX Series GM6AQ7C，同方模具 GM6AQ7C）
- **主板代号**：GM6AQ7C（出厂 ODM 批次代号 `weiyang 327670412`）
- **处理器 (CPU)**：第 12 代 Intel Core i7-12800HX（Alder Lake-HX，B0 步进，物理 16 核 24 线程：8P + 8E）
  - **当前运行调优态**：BIOS / 系统中设置为 **8 核 8 线程**（关闭超线程 HT 与能效小核 E-cores，优化微卡顿与 1% low 帧率的低延迟游戏调优配置）
- **独立显卡 (GPU)**：NVIDIA GeForce RTX 4070 Laptop GPU（8GB GDDR6 显存，支持 Advanced Optimus DDS 硬件动态直连切换与 MUX 开关）
- **物理内存条 (RAM)**：24GB 非二进制 DDR5 组合（2x 12GB 单条，单面 1 Rank，8 颗 24Gb / 3GB 高密度颗粒）
  - **DRAM 颗粒原厂**：SK Hynix（海力士，JEDEC ID `0x80AD`）
  - **模组制造/品牌**：雷神/机械革命 OEM（Qingdao Thunderobot，JEDEC ID `0x0E62`，PartNumber: `JJ02HM002`）
  - **板载 PMIC 电源芯片**：Richtek Power（立锜科技独立供电控制）
  - **JEDEC 原生档位**：DDR5-5600（CL46-45-45-90-135 @ 1.10V）
- **网卡与无线**：MediaTek Wi-Fi 6E MT7922 160MHz（驱动钉在 3.6.0.1427，MTKBTSVC 蓝牙服务禁用）

---

## 二、从 backup.fd 提取的真实内存超频参数 (SaSetup 映射)

在固件内解压提取出的主设置表单（`Form 0x27AE: Memory Overclocking Menu`）中，变量命名空间为 **`SaSetup`**（VarStoreId `0x5`，GUID `72C5E28C-7783-43A1-8767-FAD73FCCAFA4`），其实际写入的真实超频时序参数如下：

| IFR 表单项 (Prompt) | 变量偏移 (VarOffset) | 固件实测值 | 含义解析与运行参数 |
| :--- | :--- | :--- | :--- |
| **Memory Profile** | `0x18D` (8-bit) | **`0x01`** | **Custom Profile（用户自定义手动调优档，非默认 SPD 档）** |
| **Memory Ref Clock** | `0x05` (8-bit) | **`1`** | 内存参考基频：**100 MHz**（0=133MHz, 1=100MHz） |
| **Memory Ratio** | `0x06` (8-bit) | **`64`** | 内存倍频：**64x**（$64 \times 100\text{ MHz} =$ **DDR5-6400 MT/s**） |
| **tCL** | `0x08` (8-bit) | **`40`** | CAS 核心读取延迟：**40** |
| **tRCD / tRP** | `0x0E` (8-bit) | **`40`** | RAS 到 CAS 延迟 & 预充电延迟：**40** |
| **tRAS** | `0x0C` (16-bit) | **`77`** | 行激活到预充电时间：**77** |
| **tCWL** | `0x09` (8-bit) | **`38`** | CAS 写入延迟：**38** |
| **tFAW** | `0x0A` (16-bit) | **`32`** | 四激活窗口延迟：**32** |
| **tREFI** | `0x0F` (16-bit) | **`22400`** | 刷新间隔时间：**22400** |
| **tRFC** | `0x11` (16-bit) | **`824`** | 完整行刷新恢复周期：**824** |
| **tRFC2** | `0x436` (16-bit) | **`576`** | 行刷新恢复周期 2：**576** |
| **tRFCpb** | `0x434` (16-bit) | **`432`** | 逐 Bank 刷新恢复周期：**432** |
| **tWR** | `0x15` (8-bit) | **`78`** | 写恢复时间：**78** |
| **tRTP** | `0x14` (8-bit) | **`18`** | 读到预充电延迟：**18** |

- **时钟与分频机制**：
  - **内存时钟频率 (MCLK)**：3200.0 MHz（1:32 比率）
  - **内存控制器频率 (UCLK)**：1600.0 MHz（**Gear 2 模式**，控制器与内存频率 1:2）
  - **Ring / Uncore 频率**：4400.0 MHz
  - **通道模式**：4 x 32-bit（DDR5 双条 4 子通道，即双通道）
  - **工作电压**：1.20 V (1200 mV)

---

## 三、SPI Flash 32MB 固件物理分区架构

基于 Intel Flash Descriptor 架构的物理地址划分：

1. **`0x000000 - 0x000FFF`（4 KB）**：**Flash Descriptor**（闪存主控描述符、Soft Straps、Master 读写权限表与 VSCC 芯片参数表）
2. **`0x001000 - 0x002FFF`（8 KB）**：**GbE Region**（千兆网卡硬件 MAC 与物理控制器配置）
3. **`0x003000 - 0x3DCFFF`（~3.85 MB）**：**Intel CSME 16**（独立安全管理引擎微内核系统）
   - **CSE ME 版本**：`16.1.30.2361`（Production Release，Consumer H SKU，Flash Image Tool: `16.1.30.2319`，芯片组平台 `ADP/RPP`）
   - **PMC 固件**：Version `160.2.00.1043`（电源管理控制器）
   - **PCHC 固件**：Version `16.1.0.1014`（PCH 配置固件）
   - **USB Type-C PHY 固件**：Version `13.62.211.7255`（SKU N）与 `13.0.1.7085`（SKU S）
4. **`0x3DD000 - 0x0FFFFFF`（~12.14 MB）**：**Device Expansion**（平台扩展空间）
5. **`0x1000000 - 0x1FFFFFF`（16.00 MB）**：**BIOS / UEFI 主区**（AMI Aptio V 核心主固件体）
   - 内部包含 15 个顶级 Firmware Volume（FV）

---

## 四、底层启动契约与微码 (FIT Table @ 0x1E90100)

1. **Startup ACM 模块**：基址 `0xFFF40000`（物理偏移 `0x1F40000`），大小 `0x26000`，由 Intel 官方 RSA 密钥签名，负责硬件级度量启动与 Boot Guard 认证。
2. **三组全量 CPU 微码**：
   - **`CPUID 0x90672`**（rev `0x2C`，日期 2023-01-04，大小 219,136 字节）：**Alder Lake-HX B0**（原生匹配当前 i7-12800HX）
   - **`CPUID 0xB0671`**（rev `0x115`，日期 2023-03-15，大小 209,920 字节）：**Raptor Lake-HX B0**（支持 13 代 HX 升级）
   - **`CPUID 0xB06F2`**（rev `0x20`，日期 2022-03-31，大小 214,016 字节）：**Raptor Lake Refresh C0**（支持 14 代 HX 兼容）

---

## 五、UEFI 固件驱动生态（解包提取 285 个 DXE/SMM 模块 + 60+ PEI 模块）

通过解压主 DXE 卷（LZMA 压缩体，解压后 16.64 MB），完整提取出全部核心驱动：
1. **显示与动态直连切换**：
   - `OemDDSSupportDxe`：**NVIDIA Advanced Optimus 动态直连切换 (DDS)** 核心驱动（免重启动态切换）
   - `OemDisplayModeDxe`：主板 MUX 硬件切换器
   - `OemDgpuBoardIDDxe`：独立显卡板卡 ID 识别驱动
   - `OemColorCalibrationDxe`：出厂**屏幕原色校准 ICC / 色彩查找表**加载驱动
   - `OemPanelEdidSwitchDxe`：屏幕面板 EDID 热切换驱动
2. **底层外设与供电总线**：
   - `CastroCovePmicNvm`：Intel 移动端专用 **Castro Cove PMIC 供电芯片**固件驱动
   - `Usb4CmDxe` / `UsbTypeCDxe`：USB4 连接管理器与全功能 Type-C 控制驱动
   - `RstUefiDriverSupport`：Intel RST 快速存储驱动
   - `Ofbd`：AMI 官方在线 Flash BIOS 驱动接口
3. **电竞与性能控制**：
   - `OemPowerModeDxe` / `OemTurboModeDxe`：办公 / 平衡 / 狂暴性能模式切换驱动
   - `OemOcDxe` / `OemOcPei`：CPU / 内存超频与电压墙底层调节驱动
   - `OemKbLightDxe` / `OemKbLightSupportDxe` / `OemRgbLbDxe` / `OemUsbLightBarDxe`：键盘背光、机身 RGB 灯带与 USB 外接灯效驱动
   - `OemQkeyDxe`：机身电竞快捷键 / Fn 组合键响应驱动
4. **存储与容灾**：
   - `NvmeUnlockPei`、`NvmeRecoveryPei`、`NvmeDynamicSetup`、`FirmwareBootMediaInfoPei`
5. **安全与芯片组**：
   - `PlatformVTdInfoSamplePei`、`IntelVTdPmrPei`、`TcgPlatformSetupPeiPolicy`、`AmiTxtPei`、`CryptoPei`、`TCMPEI`（国密 TCM 支持）

---

## 六、全量 ACPI 设备表架构（85 组 ACPI 表格全部校验通过）

1. **`DSDT` 主表（661,436 字节，~661 KB）**：OEM ID `ALASKA`，TableID `A M I`，整机全部硬件总线（PCIe、I2C、GPIO、EC、电源按钮）的完整 ASL/AML 设备树定义。
2. **NVIDIA DDS & Optimus 专有表**：`NvDDSTl`、`NvDDSN20`、`OptTabl`、`Opt1Tabl`、`Opt2Tabl`、`OemNvT`、`OemNv1T`、`OemNv2T`。
3. **CPU 功耗与电源调优 SSDT**：`ApCst`、`ApHwp`、`ApIst`、`ApPsd`、`ApTst`、`Cpu0Cst`、`Cpu0Hwp`、`Cpu0Ist`、`CpuSsdt`（23.8 KB，Intel 自动调频 HWP 与全套 C-States 电源状态表）。
4. **雷电与高速接口 SSDT**：`TbtTypeC`（29.9 KB）与 `UsbCTabl`；16 组针对各步进的 XHCI 物理 USB 端口映射表。
5. **Runtime D3 深度休眠表 (Rtd3)**：包含 `AdlM_Rvp`、`AdlP_Rvp`、`RplHxAep`、`RplS_BR_` 等 29 组移动平台低功耗休眠策略表。

---

## 七、当前运行时 NVRAM 变量数据库（425 条活跃 NVAR 记录）

位于 `0x1000000` 与 `0x1030000` 的**双 192KB 容错 NVRAM 变量区**：
1. **`Setup`（3,267 字节）**：全局 BIOS 核心配置。
2. **`CpuSetup`（961 字节）**：CPU 电源与核心参数（功耗墙 PL1/PL2/Tau 爆发调优设定在 **170W ~ 190W** 档位，记录核心使能与 C-States）。
3. **`SaSetup`（1,400 字节）**：显卡输出拓扑（MUX 开关）与**上述第二节记录的内存超频时序核心参数**。
4. **`PchSetup`（2,063 字节）**：双 M.2 NVMe 通道分配、USB 3.2 控制器、HD Audio 高清音频、PCIe ASPM 节能。
5. **`UniWillVariable`（180 字节，历经 347 次写入迭代）**：机械革命 Control Center 电竞控制台核心持久化变量（办公/平衡/狂暴模式、自定义风扇转速曲线、80% 电池保养健康充放电限制阈值）。
6. **`Boot0000`（Windows Boot Manager）**：唯一默认引导项，指向 `\EFI\Microsoft\Boot\bootmgfw.efi`，绑定当前系统 NVMe GUID 分区 `{9dea862c-5cdd-4e70-acc1-f32b344d4795}`。
7. **外设 ACPI 设备树节点**：键盘 RGB 控制器 `\_SB.PC00.XHCI.RHUB.HS00.CRGB`、IR 红外人脸摄像头 `\_SB.PC00.XHCI.RHUB.HS01.CIR`。

---

## 八、BIOS Setup IFR 菜单表单体系（47 组 HII Formsets / 251 组 Form）

由 `ifrextractor` 从主 Setup 模块反解出完整的 BIOS 菜单树（已导出至 `D:\ai coding\backup.fd.setup.ifr.txt`，2.1 MB）：
- `OverClocking Performance Menu` (`Form 0x2887`)：底层核心超频入口
- `Memory Configuration` (`Form 0x27AC`) & `Memory Overclocking Menu` (`Form 0x27AE`)：内存频率、倍频、主副时序手动调节菜单
- `Memory Training Algorithms` (`Form 0x27B9`)：内存开机训练算法开关
- `Memory Thermal Configuration` (`Form 0x27BB`) & `Memory Power and Thermal Throttling` (`Form 0x27BC`)：内存温控与功耗限制表单
- `Advanced`（52 处）、`Chipset`（13 处）、`Security`（48 处）、`Boot`（303 处）

---

## 九、开机画面图形资源 (Boot Splash / Logo)

- **BMP 徽标**：位于 `0xbfde6c`，378x100 分辨率，113 KB
- **3 组开机背景 JPEG 画面**：分别位于 `0x11bdd`（1.43 MB）、`0x9e7814`（1.00 MB）、`0x9e7b17`（1.00 MB）

---

## 十、专用 BIOS 工具链与本地持久化产物清单

工具链常驻存盘于：`D:\ai coding\tools\bios_tools\`
1. **`UEFIExtract.exe` (NE A75)**：工业级 UEFI 固件树解析与解包工具
2. **`ifrextractor.exe` (v1.6.1)**：UEFI HII IFR 表单反编译工具
3. **`UEFIFind.exe` (NE A75)**：固件区段 GUID/文本检索工具（与 UEFIExtract 同套件）
   - 注：早期记录的 `MEAnalyzer` 工具在本机已不存在（全盘检索 0 命中），ME/CSME 区段分析改以 `UEFIExtract` 解包 + 十六进制核对方式完成
4. **`D:\ai coding\backup.fd.setup.ifr.txt`（2.0 MB）**：全量 251 个表单、4,192 个 Question 的完整 BIOS 选项与 VarOffset 映射文本
5. **`D:\ai coding\backup.fd.dump\info.txt`**：UEFIExtract 生成的区段清单与固件结构信息
6. **`D:\ai coding\backup.fd.dump\`**：全量解包固件区段目录树（10,159 个文件 / 53 MB，含 Descriptor、GbE、ME、BIOS 五大区）
7. **固件基线镜像**：现行 = `C:\1、备份原版本bios\backup.fd`（用户自 BIOS 内导出，含 `xDCI=Disabled`）；历史 = `D:\ai coding\backup.fd`（本目录产物均由该代解包）。两代校验值与核查方法见 **§11.6**。

---

## 十一、BIOS 设置项「按菜单路径」索引台账

> **查找方式**：以 BIOS **真实菜单路径**为一级索引，照路径逐级点进即可定位；每行的 `变量:偏移` 是该项在 NVRAM 中的落点（IFR `VarOffset`），可直接读写核对。
> **数据来源**：`backup.fd` Setup 模块 IFR 反编译（4,192 个 Question）与 SPI Flash `0x1000000` 处活跃 NVRAM 实值交叉映射（**现行基准镜像见 §11.6**）。
> **图例**：★ = 用户手动调校项；○ = 出厂预置或未改动（列出实盘值仅供参考）。
> **顶层六页**（表单 `0x2710`）：`Main` / `Advanced` / `Chipset` / `Security` / `Boot` / `Save & Exit`。

### 11.1 `Advanced` 页

#### `Advanced → CPU Configuration`

| 选项 | 落点 | 当前值 | 出厂默认 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| `Intel (VMX) Virtualization Technology` | `CpuSetup:0x0b9` | **`Enabled`** | `Enabled` | ○ **业务强需求**：运行 D加密游戏虚拟机破解版，依赖 VT-x，禁止关闭 |
| `Hyper-Threading` | `CpuSetup:0x005` | **`Disabled`** | `Enabled` | ★ 纯 8 物理核，消除线程抢占延迟 |
| `MonitorMWait` | `CpuSetup:0x0bc` | **`Disabled`** | `Enabled` | ★ 禁用 MWAIT 休眠指令 |
| `AP threads Idle Manner` | `CpuSetup:0x120` | **`RUN Loop`** | `MWAIT Loop` | ★ 空闲核心保持轮询态 |
| `C6DRAM` | `CpuSetup:0x114` | `Disabled` | `Enabled` | ○ 随 C-State 一并关闭 |
| `CPU Flex Ratio Settings` | `CpuSetup:0x001` | `23` | `Disabled` | ○ |

#### `Advanced → OverClocking Performance Menu`

| 选项 | 落点 | 当前值 | 出厂默认 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| `UnderVolt Protection` | `CpuSetup:0x381` | **`Disabled`** | `Enabled` | ★ **解开降压保护**，放行 MSR 0x150，使 TS 的 -185.5 mV 生效 |
| `CPU BCLK OC Frequency` | `CpuSetup:0x2f7` | `10024` | `Disabled` | ○ BCLK 微调（0.01 MHz 单位，约 100.24 MHz） |
| `WDT Enable` | `PchSetup:0x024` | `Enabled` | `Disabled` | ○ |
| `  → CEP Disable` → `IA CEP Enable` | `CpuSetup:0x334` | **`Disabled`** | `Enabled` | ★ 消除负压下的 Clock Modulation 软限频 |
| `  → CEP Disable` → `GT CEP Enable` | `CpuSetup:0x335` | **`Disabled`** | `Enabled` | ★ 关闭核显欠压保护 |
| `  → Processor` → `Per Core Disable Configuration` | `CpuSetup:0x34c` | **`Enabled`** | `Disabled` | ★ 关闭全部 E-core，构成 8P+0E |
| `  → Processor` → `Core 0~7 Max Ratio` | `CpuSetup:0x2bc~0x2c3` | `47`（8 项） | `Disabled` | ○ |
| `  → Processor` → `P-core Voltage Override` | `CpuSetup:0x1de` | `1200` | `Disabled` | ○ 1.20 V |
| `  → Processor` → `Thermal Velocity Boost` | `CpuSetup:0x2e3` | **`Disabled`** | `Enabled` | ★ |
| `  → Processor` → `TVB Voltage Optimizations` | `CpuSetup:0x2e4` | **`Disabled`** | `Enabled` | ★ |
| `  → Processor` → `Enhanced Thermal Velocity Boost` | `CpuSetup:0x378` | **`Disabled`** | `Enabled` | ★ 彻底关停 TVB，定频定压 |
| `  → Ring` → `Ring Down Bin` | `CpuSetup:0x1e8` | **`Disabled`** | `Enabled` | ★ 锁定 Ring 4.4 GHz 满血常驻 |
| `  → Ring` → `Ring Voltage Override` | `CpuSetup:0x1ea` | `1200` | `Disabled` | ○ 1.20 V |
| `  → VR ICCMAX Current Override` → `IA ICC Unlimited Mode` | `CpuSetup:0x346` | **`Enabled`** | `Disabled` | ★ 解除 IA 核心电流限制 |
| `  → VR ICCMAX Current Override` → `IA ICC Max Current Limit Override` | `CpuSetup:0x347` | `800` | `Disabled` | ○ 已被 Unlimited 模式覆盖 |
| `  → VR ICCMAX Current Override` → `GT ICC Max Current Limit Override` | `CpuSetup:0x34a` | `180` | `Disabled` | ○ |

#### `Advanced → Power & Performance`

| 选项 | 落点 | 当前值 | 出厂默认 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| `→ CPU - Power Management Control` → `Intel(R) SpeedStep(tm)` | `CpuSetup:0x009` | **`Disabled`** | `Enabled` | ★ 关 EIST |
| `→ CPU - Power Management Control` → `Race To Halt (RTH)` | `CpuSetup:0x00a` | **`Disabled`** | `Enabled` | ★ |
| `→ CPU - Power Management Control` → `Intel(R) Speed Shift Technology` | `CpuSetup:0x00b` | **`Disabled`** | `Enabled` | ★ 调频权交给系统与 ThrottleStop |
| `→ CPU - Power Management Control` → `HDC Control` | `CpuSetup:0x04a` | **`Disabled`** | `Enabled` | ★ |
| `→ CPU - Power Management Control` → `C states` | `CpuSetup:0x014` | **`Disabled`** | `Enabled` | ★ **消灭 0x0A 蓝屏**：杜绝 C0 唤醒瞬态 Vdroop |
| `→ CPU Lock Configuration` → `CFG Lock` | `CpuSetup:0x043` | **`Disabled`** | `Enabled` | ★ 解开 MSR 0xE2 写保护 |
| `→ CPU Lock Configuration` → `Overclocking Lock` | `CpuSetup:0x10e` | **`Disabled`** | `Enabled` | ★ |
| `→ CPU VR Settings → Core/IA VR Settings` → `AC Loadline` | `CpuSetup:0x132` | `110` | `110` | ○ **保持出厂 1.10 mΩ，严禁跟风改 20~30**（叠 TS 负压必崩 0x0A） |
| `→ Core/IA VR Settings` → `DC Loadline` | `CpuSetup:0x13c` | `110` | `110` | ○ |
| `→ Core/IA VR Settings` → `Core VR Fast Vmode` | `CpuSetup:0x379` | **`Disabled`** | `Enabled` | ★ |
| `→ CPU VR Settings → GT VR Settings` → `AC Loadline` / `DC Loadline` | `CpuSetup:0x134` / `0x13e` | `80` / `80` | `80` | ○ 核显 VR 保持出厂 |
| `→ Config TDP Configurations` → `Power Limit 1` | `CpuSetup:0x05b` | **`180000`（180 W）** | 差异项 | ★ 用户手调 |
| `→ Config TDP Configurations` → `Power Limit 2` | `CpuSetup:0x05f` | **`190000`（190 W）** | 差异项 | ★ 与 OpenRevo 设定值对齐 |
| `→ Config TDP Configurations` → `Power Limit 1 Time Window` | `CpuSetup:0x063` | `128` | `0` | ○ |
| `→ View/Configure Turbo Options` → `Power Limit 1` / `Power Limit 2` | `CpuSetup:0x017` / `0x01e` | `160000` / `170000` | 同左 | ○ 该分支为出厂值，未改 |
| `→ Turbo Ratio Limit Options` → `P-core Turbo Ratio Limit Ratio0~7` | `CpuSetup:0x0d6~0x0dd` | `48/48/46/46/44/44/42/42` | — | ○ |
| `→ Turbo Ratio Limit Options` → `E-core Turbo Ratio Limit Ratio0~7` | `CpuSetup:0x0f6~0x0fd` | `34/34/34/34/31/31/31/31` | — | ○ E-core 已物理关闭 |
| `→ GT - Power Management Control` → `Disable Turbo GT frequency` | `SaSetup:0x040` | **`Enabled`** | `Disabled` | ★ 禁核显睿频，杜绝供电分流 |

#### `Advanced → Thermal Configuration`

| 选项 | 落点 | 当前值 | 出厂默认 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| `→ CPU Thermal Configuration` → `Tcc Offset Lock Enable` | `CpuSetup:0x1cd` | **`Disabled`** | `Enabled` | ★ 解除温度墙锁定 |
| `→ CPU Thermal Configuration` → `Bi-directional PROCHOT#` | `CpuSetup:0x07a` | **`Disabled`** | `Enabled` | ★ 防外设高温误触发 CPU 降频 |
| `→ Intel(R) Dynamic Tuning Technology Configuration` → `Intel(R) Dynamic Tuning Technology` | `Setup:0x6d1` | **`Disabled`** | `Enabled` | ★ **DTT 已彻底关闭**，不再插手功耗调度 |

#### `Advanced → RC ACPI Settings`

| 选项 | 落点 | 当前值 | 出厂默认 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| `EC Low Power Mode` | `Setup:0x053` | **`Disabled`** | `Enabled` | ★ EC（1.19）不休眠，风扇与性能档位响应更快 |
| `Native ASPM` | `Setup:0x032` | `Auto` | `Auto` | ○ |
| `→ PEP Constraints Configuration` → `PEP VMD` | `Setup:0x99d` | `Enabled` | `Enabled` | ○ |

#### 其他 `Advanced` 子菜单

| 路径与选项 | 落点 | 当前值 | 出厂默认 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| `→ CSM Configuration` → `Network` | `Setup:0xc7f` | `Do not launch` | `UEFI` | ○ |
| `→ Switchable Graphics` → `Display Mode` | `Setup:0xc6d` | **`dGPU Only`** | `MsHybrid` | ★ 纯独显直连（IFR 中该表单由 Advanced 页引用，BIOS 实际入口以界面显示为准） |
| `→ Platform Settings → VTIO` → `Firmware Hash [63:0]~[255:192]` | `Setup:0x890~0x8c8` | 全 `0` | — | ○ OEM 预置，非调优项 |

### 11.2 `Chipset` 页

#### `Chipset → PCH-IO Configuration`

| 选项 | 落点 | 当前值 | 出厂默认 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| `Compatible Revision ID` | `PchSetup:0x012` | `Disabled` | `Enabled` | ○ |
| `→ PCI Express Configuration` → `DMI Link ASPM Control` | `PchSetup:0x517` | `L1` | `L1` | ○ |
| `→ PCI Express Configuration` → `PCI Express Root Port 1~28` → `ASPM` | `PchSetup:0x11b~0x136` | 27 项 `L1`，1 项 `Disabled`（Root Port 21 @ `0x12f`） | `L1` | ○ **南桥控温基础**（空闲网卡/SSD 自动节能） |
| `→ PCI Express Configuration` → `PCI Express Root Port 1~28` → `L1 Substates` | `PchSetup:0x2bf~0x2da` | 全部 `L1.1 & L1.2` | `L1.1 & L1.2` | ○ |
| `→ SATA Configuration` → `SATA Controller(s)` | `PchSetup:0x048` | `Disabled` | `Disabled` | ○ 整机无 SATA 盘，控制器整体关闭 |
| `→ SATA Configuration` → `Mechanical Presence Switch`（Port 0~7） | `PchSetup:0x05a~0x061` | `Disabled`（8 项） | `Enabled` | ○ |
| `→ USB Configuration` → **`xDCI Support`** | `PchSetup:0x047` | **`Disabled`** | `Disabled` | ★ **已改 `Disabled`（2026-09-23 实机验证）**：USB OTG 从机控制器，日常无用；新固件 NVRAM 该落点由 `0x01` 归零，重启后 `PCI\VEN_8086&DEV_7AE1`（`ufxsynopsys`）已从设备树消失 |
| `→ USB Configuration` → `USB SS Physical Connector #0` / `#3` | `PchSetup:0x038` / `0x03b` | `Enabled` | `Disabled` | ○ |
| `→ HD Audio Configuration → HD Audio DSP Features Configuration` → `Discrete BT HCI Audio Offload Link` | `PchSetup:0x80e` | `SSP #0` | `SSP #1` | ○ |

#### `Chipset → System Agent (SA) Configuration`

| 选项 | 落点 | 当前值 | 出厂默认 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| `VT-d` | `SaSetup:0x07d` | **`Disabled`** | `Enabled` | ★ 消除 DMA 重映射中断开销 |
| `DMA Control Guarantee` | `SaSetup:0x087` | `Disabled` | `Enabled` | ○ |
| `Above 4GB MMIO BIOS assignment` | `SaSetup:0x07e` | `Enabled` | `Enabled` | ○ ReBAR 前置条件 |
| `→ PCI Express Configuration` → `PCIE Resizable BAR Support` | `SaSetup:0x42b` | **`Enabled`** | `Enabled` | ★ BAR1 8192 MiB 全域映射 |
| `→ DMI/OPI Configuration` → `DMI Gen3 ASPM` | `SaSetup:0x0ac` | `ASPM L1` | `ASPM L1` | ○ |
| `→ DMI/OPI Configuration` → `DMI ASPM` | `SaSetup:0x0ad` | **`Disabled`** | `ASPM L1` | ★ 差异项（CPU↔PCH 主链路不做 ASPM 降级） |
| `→ DMI/OPI Configuration → DMI Advanced Menu` → `DMI Gen4 EQ Mode` | `Setup:0xbae` | `Fixed EQ` | `HW EQ` | ○ |
| `→ DMI Advanced Menu` → `DMI Gen3/Gen4 RTCO Cpre/Cpost Lane0~7` | `Setup:0xb8e~0xbad` | 数值 3~10 | — | ○ OEM 信号完整性预置 |
| `→ VMD setup menu` → `Enable VMD controller` | `SaSetup:0x0f8` | `Disabled` | `Disabled` | ○ 原生 NVMe 直通（`stornvme`） |
| `→ VMD setup menu` → `Enable VMD Global Mapping` | `SaSetup:0x3e6` | `Enabled` | `Enabled` | ○ |
| `→ Graphics Configuration` → `Primary Display` | `SaSetup:0x0b1` | **`PEG Slot`** | `HG` | ★ 独显直出 |
| `→ Graphics Configuration` → `Intel Graphics Pei Display Peim` | `SaSetup:0x039` | **`Disabled`** | `Enabled` | ★ PEI 阶段屏蔽核显初始化 |
| `→ Graphics Configuration` → `Share Memory Size (DVMT)` | `SaSetup:0x07a` | `254`（Auto） | `64M` | ○ |
| `→ Memory Configuration` → `Memory Test on Warm Boot` | `SaSetup:0x1a1` | **`Disabled`** | `Enabled` | ★ 热重启跳过重复内存训练 |
| `→ Memory Configuration` → `Power Down Mode` | `SaSetup:0x1a2` | **`No Power Down`** | `Auto` | ★ 关 DRAM PHY 休眠，消除唤醒气泡 |
| `→ Memory Configuration` → `Fast Boot` | `SaSetup:0x18f` | `Enabled` | `Enabled` | ○ 内存快起 |
| `→ Memory Configuration` → `Maximum Memory Frequency` | `SaSetup:0x18b` | `7000` | `Auto` | ○ 频率上限封顶 |
| `→ SA TCSS USB Configuration` → `TCSS xDCI Support` | `SaSetup:0x0bf` | `Disabled` | `Disabled` | ○ Type-C 从机端点已关 |
| `→ SA TCSS USB Configuration` → `USB CONNECT OVERRIDE` | `SaSetup:0x0c3` | `Disabled` | `Enabled` | ○ |
| `→ MIPI Camera Configuration` → `Camera1` | `Setup:0x075` | `Enabled` | `Disabled` | ○ |

#### `Chipset → System Agent (SA) → Memory Configuration → Memory`（内存超频子菜单，★ 全项用户手调）

| 选项 | 落点 | 当前值 | 说明 |
| :--- | :--- | :--- | :--- |
| `Memory profile` | `SaSetup:0x18d` | `Custom Profile` | 激活自定义时序档 |
| `Memory Reference Clock` | `SaSetup:0x005` | `100`（MHz） | 锁定 100 MHz 基准，稳定 Gear 2 |
| `Memory Ratio` | `SaSetup:0x006` | `64` | 100 × 64 = **DDR5-6400 MT/s** |
| `tCL` / `tRCD/tRP` / `tRAS` | `SaSetup:0x008` / `0x00e` / `0x00c` | `40` / `40` / `77` | 主时序 40-40-40-77 2T |
| `tCWL` / `tFAW` | `SaSetup:0x009` / `0x00a` | `38` / `32` | |
| `tREFI` | `SaSetup:0x00f` | `22400` | 严守 $6400 \times 3.5 = 22400$ 耐温基准 |
| `tRFC` / `tRFC2` / `tRFCpb` | `SaSetup:0x011` / `0x436` / `0x434` | `824` / `576` / `432` | |
| `tWR` / `tRTP` | `SaSetup:0x015` / `0x014` | `78` / `18` | 保持 $tWR = tRTP \times 4$ 容错窗口 |
| `tRRD_L` / `tRRD_S` | `SaSetup:0x43a` / `0x43b` | `12` / `8` | |
| `tWTR_L` / `tWTR_S` | `SaSetup:0x43c` / `0x43e` | `32` / `8` | |
| `NMode` | `SaSetup:0x017` | `2` | 2T 命令速率 |
| `Memory Voltage` / `VDDQ` / `VPP` | `SaSetup:0x003` / `0x3f5` / `0x3f7` | `1200` / `1200` / `1800` | 1.20 V VDD/VDDQ、1.80 V VPP |

### 11.3 `Boot` 页

| 选项 | 落点 | 当前值 | 出厂默认 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| `SATA Support` | `Setup:0x003` | **`Last Boot SATA Devices Only`** | `All SATA Devices` | ★ 只枚举上次引导设备，加速 POST |
| `USB Support` | `Setup:0x005` | **`Partial Initial`** | `Full Initial` | ★ 减少开机 USB 自检耗时 |
| `Network Stack Driver Support` | `Setup:0x009` | **`Disabled`** | `Enabled` | ★ 关 UEFI PXE 网络栈 |
| `Fast Boot` | `Setup:0x002` | `Disabled` | `Disabled` | ○ |

### 11.4 `Security` 页

| 选项 | 落点 | 当前值 | 出厂默认 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| `→ Secure Boot` → `Secure Boot` | `SecureBootSetup:0x000` | **`Disabled`** | `Enabled` | ★ |
| `→ Secure Boot` → `Secure Boot Mode` | `SecureBootSetup:0x001` | **`Custom`** | `Standard` | ★ |

### 11.5 复现与自助查询（后续按需复查）

- **工具链**：`D:\ai coding\tools\bios_tools\` → `UEFIExtract.exe`、`UEFITool.exe`、`ifrextractor.exe`
- **产物**：`D:\ai coding\backup.fd.dump\`（全量解包 53 MB）、`D:\ai coding\backup.fd.setup.ifr.txt`（2.0 MB 全量 4,192 Question 索引，可直接按 Prompt 搜路径）
- **活跃 NVRAM 位置**：`backup.fd` 偏移 `0x1000000` 起 `0x30000` 字节，按 `NVAR` 头 + 变量名解析（`Setup` 3267B / `CpuSetup` 961B / `SaSetup` 1400B / `PchSetup` 2063B / `SecureBootSetup` 7B）
- **查询套路**：① 在 `ifr.txt` 搜 `Prompt: "<选项名>"` 取 `VarStoreId` / `VarOffset` / `Size` → ② 在对应变量体按偏移取字节 → ③ 用该 Question 块内的 `OneOfOption Value:` 反查显示名

### 11.6 固件基线镜像与「BIOS 改动是否落地」核查法

**基线镜像台账**（用户自 BIOS 内备份导出的 32 MB 全片镜像）：

| 代次 | 路径 | 提取时间 | SHA-256（前 8 / 后 8 位） | 关键状态 |
| :--- | :--- | :--- | :--- | :--- |
| **现行** | `C:\1、备份原版本bios\backup.fd` | 2026-09-23 14:43（重启后） | `886e22cf` … `18cbd4cc` | 含 `xDCI=Disabled`，其余 NVRAM 与上一代逐字节一致 |
| 历史 | `D:\ai coding\backup.fd` | 2026-09-23 12:15 | `cd394339` … `14a76370` | 含 `xDCI=Enabled`（改前态） |

**核查法（已在 xDCI 一役验证成立）**：
1. **全片字节 diff 定位写入区**：两代镜像全片仅差 7 段（5 处 NVAR 头部写入标记刷新 + 2 段尾部新增记录区），差异全部落在 NVRAM 变量区（`0x1000000` 起），BIOS 区段/DXE 模块零差异——即「只改了设置，没动固件本体」。
2. **NVAR 记录解析**：`'NVAR' + 2B 总长(LE) + 3B 写入标记 + 1B 属性 + [1B 名字段 + NUL 结尾名字] + 载荷`；名字为空（`0x00`）的记录是**数据-only 追加记录**（名字复用同名变量的首条记录），其载荷长度恰等于该变量的 VarStore 长度。
3. **追加记录 = 最新值**：AMI 采用日志式追加，改动写在**存储区尾部新记录**里；同一变量的旧副本仍在原处保留旧值（垃圾回收前并存）。**只比载荷，忽略 3 字节写入标记**——该标记会随任何写入/访问刷新，据此判断"哪个副本是新值"必错。
4. **判定单选项改动**：把新旧载荷对齐比较，全载荷只差 1 字节 → 只动了一个选项；该字节偏移即 IFR 的 `VarOffset`（对齐自检：错位对齐会产生数百处差异，一眼可辨）。
5. **OS 侧交叉验证**：设置项若对应 PCI/USB 功能，重启后可直接看设备树——消失/出现即生效（本例 `PCI\VEN_8086&DEV_7AE1`，服务 `ufxsynopsys`，PnP 类 `USBFunctionController`）。注意 Windows 只枚举**当前存在**的设备；历史记录留在 `HKLM\SYSTEM\CurrentControlSet\Enum\PCI`，可作"改前曾存在"的佐证。
