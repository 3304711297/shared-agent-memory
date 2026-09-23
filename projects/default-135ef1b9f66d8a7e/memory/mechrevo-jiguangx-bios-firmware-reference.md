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
3. **`MEAnalyzer\` (v1.312.0)**：Intel ME/CSME 引擎固件分析工具库
4. **`D:\ai coding\backup.fd.setup.ifr.txt`（2.1 MB）**：全量 251 个表单的完整 BIOS 选项与 VarOffset 映射文本
5. **`D:\ai coding\backup.fd.report.txt`（452 KB）**：固件全区段树状层级与校验报告
6. **`D:\ai coding\backup.fd.dump\`**：全量解包出的 11,644 个固件区段与驱动文件目录树
