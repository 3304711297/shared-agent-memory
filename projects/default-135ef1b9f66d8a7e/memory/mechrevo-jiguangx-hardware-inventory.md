---
name: mechrevo-jiguangx-hardware-inventory
description: 机械革命极光X (GM6AQ7C) 整机全物理硬件设备规格全景台账、CPU降压调优(ThrottleStop)与排障记录 (AIDA64/实测)
metadata:
  node_type: memory
  type: reference
---

# 机械革命极光X (GM6AQ7C) 全物理硬件设备规格全景台账

本文档整合了通过图吧工具箱工业级套件（`D:\TubaWinUi3\Tools`：AIDA64 v8.30 商业内核驱动级扫描、CPU-Z 物理寄存器抓取）与底层系统 WMI/PCIe/EDID 探活所提取的**除操作系统软件层以外的所有物理硬件信息**。已严格执行硬件序列号与唯一指纹脱敏。

---

## 1. 核心计算与芯片组架构 (Processor & Chipset)

- **主机型号**：MECHREVO JiguangX Series GM6AQ7C（机械革命 极光X）
- **模具与制造商**：同方模具 GM6AQ7C（TongFang，产品代号 Standard，ODM 批次代号 `weiyang 327670412`）
- **处理器 (CPU)**：第 12 代 Intel Core i7-12800HX
  - **微架构**：Alder Lake-HX（Intel 7 工艺 10nm，B0 步进，修订 02，CPUID `90672`，插槽 `U3E1`，封装支持 LGA1700 BGA）
  - **物理核心规格**：物理 16 核 24 线程（8P 性能核 + 8E 能效核）
  - **高速缓存体系**：
    - L1 数据缓存：384 KB（12-way Set-Associative）
    - L1 指令缓存：256 KB（8-way Set-Associative）
    - L2 二级缓存：10 MB（$8 \times 1.25\text{MB}$）
    - L3 三级智能缓存：25.6 MB（Intel Smart Cache）
  - **频率与电压**：基准 2.30 GHz，当前实跑 4.60 GHz（46x 100MHz），核心电压约 1.209 V
  - **神经网络与语音加速单元**：**Intel GNA Scoring Accelerator**（Gaussian & Neural Accelerator 3.0，硬件 ID `PCI\VEN_8086&DEV_464F`）
  - **当前运行调优态**：**8 核 8 线程**（BIOS 内关闭超线程 HT 与能效小核 E-cores，纯 8P 大核低微卡顿模式；Core/P-Cache 双轨锁定 -185.5 mV 负压，BIOS 彻底关闭 C-State，详见第 10 节）
- **北桥与内存控制器 (IMC)**：
  - **型号**：Intel Alder Lake-HX IMC（支持 VT-d、x2APIC 扩展中断控制器）
  - **PCIe 总线分配**：PCIe 5.0 x8 Port #2 正使用 @ x8（直连 AD106 独显）
- **南桥芯片组 (PCH)**：
  - **型号**：**Intel Alder Point-S HM670**（14nm 工艺，修订 11，1045 Ball FC-BGA 封装，DeviceID `7A8C`）
  - **PCIe 通道划分**：
    - PCIe 3.0 x1 Port #3：分配给 Realtek RTL8168/8111 千兆有线网卡
    - PCIe 4.0 x4 Port #13：分配给 Kingston NVMe SSD 固态硬盘
    - PCIe 4.0 x1 Port #25：分配给 MediaTek MT7922 Wi-Fi 6E 无线网卡
- **主板传感器与热区**：ACPI ThermalZone `ECTZ_0` / `TZ00_0`，待机 PCH 约 63℃，CPU 核心约 39~42℃
- **安全芯片状态**：TPM 物理未激活 / 关闭状态（`TpmPresent: False`，BIOS 中未启用 PTT/dTPM）

---

## 2. 独立显示核心与显卡 (Discrete GPU)

- **显卡型号**：NVIDIA GeForce RTX 4070 Laptop GPU（同方 OEM 独显板卡）
- **GPU 架构**：Ada Lovelace（AD106 核心，GPU Part Number: `2820-775-A1`，Board ID: `0x100`）
- **显存规格**：8GB GDDR6（物理容量 8,188 MiB，等效显存频率 8,001 MHz，总带宽 256.0 GB/s）
- **功耗墙设定 (TGP)**：
  - **默认基础功耗 (Default Limit)**：115.00 W
  - **动态加速最大功耗 (Max Limit / Dynamic Boost)**：**140.00 W 满血功耗版**
- **核心频率规格**：最大 Boost 频率 3,105 MHz，CUDA 核心数 4,608
- **总线接口**：PCIe 4.0 x8（当前实跑 PCIe Gen4 x8 @ Gen4 速率）
- **VBIOS 版本**：`95.06.15.40.63`
- **显示直连拓扑**：硬件 MUX 开关 + NVIDIA Advanced Optimus（DDS 动态直连切换驱动支持，当前 BIOS 设置为 **`dGPU Only` 纯独显直连**）
- **音频控制器**：NVIDIA AD106 High Definition Audio Controller（硬件 ID `PCI\VEN_10DE&DEV_22BD`）

---

## 3. 物理内存子系统 (RAM & SPD)

- **物理总容量**：**24 GB**（新一代非二进制 Non-Binary DDR5 组合：2 条 12GB）
- **内存插槽**：2 组 SO-DIMM 插槽（最大寻址支持 64GB），当前占用 DIMM1 与 DIMM3
- **物理通道拓扑**：Controller0/1 双通道（4 x 32-bit DDR5 子通道，128-bit 控制器总宽）
- **颗粒与模组硬件 (SPD 深度实测)**：
  - **颗粒原厂**：**SK Hynix（海力士）**（JEDEC ID `0x80AD`，DRAM 步进 `4Dh`，1 Die / 1 Rank，单面 8 颗 24Gb / 3GB 高密度颗粒）
  - **模组品牌**：雷神/机械革命 OEM（Qingdao Thunderobot / MACHENIKE，JEDEC ID `0x0E62`，料号 `JJ02HM002`，生产日期 2025 年第 10 周）
  - **板载 PMIC 芯片**：Richtek Power（立锜科技独立供电芯片）
  - **原生预设 JEDEC**：DDR5-5600（CL46-45-45-90-135 @ 1.10V VDD/VDDQ，1.8V VPP）
- **当前实跑调优参数 (Custom Profile)**：
  - **运行频率**：**DDR5-6400 MT/s**（100MHz 基频 × 64x 倍频）
  - **控制器模式**：**Gear 2 模式**（UCLK 1600MHz / MCLK 3200MHz，Ring 总线 4400MHz）
  - **核心主时序**：**CL40-40-40-76/77 2T @ 1.20V**
  - **AIDA64 抓取实跑副时序**：
    - tCWL (Write CAS Latency)：38T
    - tFAW (Four Activate Window)：32T
    - tREFI (Refresh Period)：22400T
    - tRFC (Row Refresh Cycle)：576T（tRFC2 576T / tRFC 824T）
    - tWR (Write Recovery)：81T
    - tRTP (Read To Precharge)：17T
    - tRRD (RAS To RAS)：Same Bank Group 12T / Diff Bank Group 8T
    - tWTR (Write To Read)：Same Bank Group 80T / Diff Bank Group 56T

---

## 4. 物理固态存储 (Storage & NVMe)

- **主硬盘型号**：**KINGSTON OM8PGP41024N-A0**（金士顿 OEM 客户端级 NVMe 固态）
- **标称与格式化容量**：1,024.2 GB（953.2 GB 可用，未格式化 976,762 MB）
- **主控与接口**：PCIe 4.0 x4 通道，符合 NVMe v1.4.0 协议标准（PCI Vendor ID `2646h`，固件版本 `ELFK7N.7`）
- **缓存策略**：支持 HMB（Host Memory Buffer 主机内存缓冲，推荐配置 64 MB）
- **运行健康与温控**：
  - 介质健康状态：Healthy，介质损耗程度 Wear: 0%
  - 临界温度阈值：Warning 74℃，Critical 76℃
- **物理分区结构**：
  - 分区 1：Windows 恢复分区（529 MB）
  - 分区 2：EFI 系统引导分区（100 MB，FAT32，挂载 `\EFI\Microsoft\Boot\bootmgfw.efi`）
  - 分区 3：MSR 保留分区（16 MB）
  - 分区 4：系统卷（C盘，150.37 GB，剩余约 70.8 GB）
  - 分区 5：数据卷（D盘，802.87 GB，剩余约 106.4 GB）

---

## 5. 显示设备与外接监视器 (Display & EDID)

- **笔记本内置显示屏**：
  - **制造商代号**：CSW（华星光电 / CSOT）
  - **面板型号**：`MNG007DA5-2`（16.0 英寸 16:10 / 16:9 电竞屏）
  - **制造时间**：2024 年
  - **色彩管理**：固件内嵌 `OemColorCalibrationDxe`，出厂载入专属原色校准 ICC / LUT
- **外部主力电竞显示器**（当前连接并作为主显示）：
  - **制造商代号**：HKC（惠科）
  - **显示器型号**：`G24H3SClassic`（HKC 神盾 / 经典系列超快 IPS 电竞屏）
  - **制造时间**：2025 年第 1 周
  - **当前分辨率与刷新率**：**1920 × 1080 @ 240 Hz 超高刷新率**（RGB 8-bit 全范围）

---

## 6. 音频解码与声卡硬件 (Audio Codec)

- **板载音频芯片**：**Conexant SN6140 / Synaptics HD Audio Codec**
  - **硬件 ID**：`HDAUDIO\FUNC_01&VEN_14F1&DEV_1F87&SUBSYS_1D05142D&REV_1001`（Conexant/Synaptics SN6140 高清音频解码芯片，同方笔记本专属子系统 ID `1D05142D`）
  - **功能集**：支持 Audio、Voice、Speech 多模式硬件降噪与立体声阵列
- **物理输出端点**：机身扬声器立体声单元（Speakers）、3.5mm 耳机/耳麦组合接口（Headphones）、数字阵列麦克风

---

## 7. 物理网络适配器 (Network Controllers)

- **有线千兆网卡**：**Realtek PCIe GbE Family Controller**
  - **芯片**：Realtek RTL8168/8111 PCI-E 千兆以太网芯片（硬件 ID: `PCI\VEN_10EC&DEV_8168&SUBSYS_12731D05&REV_15`）
  - **通道分配**：南桥 PCH PCIe 3.0 x1 独立通道
- **无线 Wi-Fi 6E 网卡**：**MediaTek Wi-Fi 6E MT7922 (RZ616) 160MHz Wireless LAN Card**
  - **芯片**：联发科 MT7922（硬件 ID: `PCI\VEN_14C3&DEV_7922&SUBSYS_380411AD&REV_00`）
  - **通道分配**：南桥 PCH PCIe 4.0 x1 独立通道
  - **无线规格**：支持 2.4GHz / 5GHz / 6GHz 三频段、160MHz 超大频宽、MU-MIMO、当前驱动稳定版本 `3.6.0.1427`
- **蓝牙适配器**：**MediaTek Bluetooth Adapter**（USB 接口，VID `04CA` PID `3804`）

---

## 8. 机身电池与供电规格 (Battery & Power)

- **电池类型**：可充电锂离子电池组（OEM Standard Lithium-Ion）
- **标称与设计容量**：**60,060 mWh**（约 60 Wh 标称容量）
- **最大容量与健康度**：**60,060 mWh**（损耗程度 0%，满血状态）
- **电池输出电压**：12.244 V
- **电源管理与保养**：Control Center 写入 `UniWillVariable` 实施充电阈值保护

---

## 9. 外设与输入输出总线 (Input & USB Hubs)

- **触摸板 (Touchpad)**：同方/Uniwill 专有 I2C HID 精密触控板（硬件 ID: `ACPI\VEN_UNIW&DEV_0001`）
- **机身键盘与背光**：
  - 标准笔记本薄膜电竞键盘（PS/2 内部总线 `ACPI\MSFT0001` + USB 全键无冲辅助）
  - 全彩 RGB 独立背光芯片（ACPI 节点 `\_SB.PC00.XHCI.RHUB.HS00.CRGB`）
- **板载摄像头 (Webcam)**：Chicony / OEM HD 720P/1080P 高清网络摄像头（硬件 ID: `USB\VID_04F2&PID_B78A`）
- **USB 拓扑与扩展坞 (Hub)**：
  - **主板根主控**：Intel PCH USB 3.2 Gen 2x1 / USB4 eXtensible Host Controller（`PCI\VEN_8086&DEV_7AE0`）
  - **外接高速集线器**：Genesys Logic USB 3.0 / USB 2.0 Hub（`USB\VID_05E3&PID_0620` / `PID_0610`）
  - **外接输入设备**：多模电竞鼠标与机械键盘（VID `258A` / `5253`）

---

## 10. CPU 降压调优与 FIVR 电源台账 (ThrottleStop 9.7.3)

### 10.1 调优运行态与最新稳态极限参数

- **控制程序**：`D:\ThrottleStop_9.7.3\ThrottleStop.exe`（后台常驻服务）
- **当前激活 Profile**：Profile 1 (`Performance`)，当前电源方案 `kirby`（GUID: `77cb9369-b0dd-495a-a757-f868dbf98545`）
- **BIOS 协同状态**：
  - **C-State 已在 BIOS 中彻底禁用**（全核全时处于 C0 运行态，不进入深度睡眠与休眠，彻底消除低功耗唤醒微卡顿与掉压风险）
  - **固件未启用 Undervolt Protection (UVP)**：出厂微码 `0x90672 rev 0x2C` 完全放行 MSR `0x150` 电压寄存器写入
- **FIVR 最新实盘电压参数**：
  - **CPU Core Offset**：**`-185.5 mV`**（FIVR 寄存器值 `0xE8400000`，由早期 -180.7mV 进一步深潜微调）
  - **CPU P-Cache Offset**：**`-185.5 mV`**（FIVR 寄存器值 `0xE8400000`）
  - **IccMax 电流上限**：`0x07FF` (2047A，彻底解锁电流墙)
  - **全核睿频倍频**：锁定 **46x (4.60 GHz)**（寄存器 `OneAD_EAX0/EDX0 = 0x2E2E2E2E`）
  - **Ring / Cache 频率**：锁定 **44x (4.40 GHz)**（寄存器 `CacheMinMax0 = 0x2C2C`）
- **TPL 功耗墙与温控设定**：
  - **长时功耗限制 (PL1)**：**180.0 W**（寄存器 `PowerLimitEAX0 = 0x002385A0`）
  - **短时爆发功耗 (PL2)**：**185.0 W**（寄存器 `PowerLimitEDX0 = 0x004285C8`，由早期 190W 收紧 5W 防瞬态冲击）
  - **MMIO 功耗锁同步 (`SyncMMIO`)**：**已启用 (`SyncMMIO=1`)**（硬件强制同步 MMIO 与 MSR 功耗限制，阻止驱动/系统在后台动态篡改功耗墙）
  - **PROCHOT 温度墙**：偏移 `0x5`（标称 105℃ - 5℃ = **100℃ 温度墙**，寄存器 `PROCHOT_Offset0 = 0x5`）

---

### 10.2 Intel 12 代移动端 (Alder Lake-HX) FIVR 硬件单轨铁律

1. **核心与缓存单轨绑定（Cache 决定论）**：
   - 12 代 Alder Lake-HX 物理电路上 Core 与 Ring Bus / Cache 共享同一套主供电平面（Co-voltage Rail）。
   - 硬件微码裁决规则：**整轨实际生效电压由 P-Cache 强制锁死**。
   - 现象实证：在 ThrottleStop 中单独调节 CPU Core，电压监控表中的实时 Offset 纹丝不动；只有调节 P-Cache 时，整颗 CPU 核心的实际物理电压才会联动跳变。
2. **功耗物理机制与降压收益**：
   - 动态功耗遵循 $P = C \cdot V^2 \cdot f$。
   - 笔记本散热模具上限受限，高电压会导致发热与功耗呈平方级暴增，瞬间撞满 100℃ 温度墙或 PL 功耗墙断崖式跌频；
   - 通过将 Core/Cache 负压深潜至 `-185.5 mV`，大幅压低动态发热，换取全核 4.60 GHz 高频长时间不衰减。

---

### 10.3 关键排障历史：0x0000000A (IRQL=255 HIGH_LEVEL) 崩溃闭环

- **崩溃现场转储**：`C:\Windows\Minidump\090726-9890-01.dmp`
- **故障特征**：
  - BugCheck 代码：`0x0000000A` (`IRQL_NOT_LESS_OR_EQUAL`)
  - 关键参数：`Param 2 = 0x00000000000000FF` (**`IRQL = 255 HIGH_LEVEL`**，最高硬件时钟/调度中断级)，非法内存访问位于 Windows 内核 `ntoskrnl.exe`。
- **根因机理剖析**：
  - 早期激进参数曾设为 Core -205.1mV / Cache -190.4mV，且 BIOS 关闭了 C-State。
  - 关闭 C-State 虽排除了休眠低压唤醒跌落，但使 Ring Bus（Cache）全程在 4.4GHz 极高频率下运转。
  - Alder Lake 架构的 Ring Bus 承担核心数据路由、L3 缓存与 IMC 调度；-190.4mV 超越了高频硅片晶体管在瞬态突发负载下的抗干扰阈值。
  - 在后台遭遇密集高并发（进程启动、多线程批量调度）时，CPU 在响应 `IRQL=255` 硬件时钟中断的极短纳秒内发生瞬态信号衰减（Bit-flip），寻址计算产生乱码指针，引发内核硬中断死机。
- **稳态处置结论**：
  - 将 Core/P-Cache 回收至稳定区间（-180.0mV ~ -185.5mV），补足高频 Ring Bus 容错余量，彻底根治 `HIGH_LEVEL` 寻址崩溃。

---

### 10.4 伴随系统驱动排查：GameViewer 虚拟显卡

- **设备实例**：`ROOT\DISPLAY\0000` (`GameViewer Virtual Display Adapter`)
- **驱动机制**：基于 `WUDFRd` 的 IddCx 间接显示驱动，作为 PnP 虚拟硬件常驻系统树。即便客户端软件未开启，Windows 开机和电源切换时仍会自动加载，曾引发 `0xC0000365` 卸载超时告警。
- **运维规范**：长期不使用远程串流时，建议在「设备管理器 → 显示适配器」中右键直接「禁用设备」。

---

### 10.5 完整配置恢复快照 (`D:\ThrottleStop_9.7.3\ThrottleStop.ini`)

*用于系统重装或配置还原的最新真实实盘快照：*

```ini
[ThrottleStop]
StartFailed=0
DTSAlarm=1
GPUAlarm=105
LowBattPercent=0
Profile=0
ProfileName1=Performance
ProfileName2=Game
ProfileName3=Internet
ProfileName4=Battery
LogFileDirectory=D:\ThrottleStop_9.7.3\Logs
Options1=0x01102080
Options2=0x81100080
Options3=0x81100080
Options4=0x81100080
DutyCycle1=16
DutyCycle2=16
DutyCycle3=16
DutyCycle4=16
EIST=0
DTSButton=0
ColorIndex=0
CPUColor=0xFFFFFF
GPUColor=0xFFFFFF
CPUMHzColor=0xFFFFFF
PowerColor=0xFFFFFF
MainIcon=1
CPUIcon=0
GPUIcon=0
CPUMHzIcon=0
PowerIcon=0
GridLines=0
BlackIcon=0
LogoMin=1
TaskBar=0
NoTitleBar=0
ZeroChipset=0
TimePeriodAC=16
NewWinProfile=0x000023
NewCStateLimit=0x0
HaswellOverclock=0
WDBoost=0
BatteryMonitoring=0
DCExitTime=0
BeforeRunProgram=15
BatteryButton=0
PSMinimum=35
Payload1=0x1400
Payload2=0x1400
Payload3=0x1400
Payload4=0x1400
DisableSafeStart=0
Color00=0x202020
Color01=0xFFFFFF
Color02=0x293DA3
Color03=0x1F199F
Color04=0x0000E8
Color05=0x303030
Color06=0xFFFFFF
Color07=0x293DA3
Color08=0x202020
Color09=0xFFFFFF
Color10=0x202020
Color11=0xFFFFFF
Color12=0xDD5496
Color13=0xDD3E8B
Color14=0xE85CA2
Color15=0x404040
Color16=0xFFFFFF
Color17=0xDD3E8B
Color18=0x202020
Color19=0xFFFFFF
Color20=0xF0F0F0
Color21=0x000000
Color22=0xDCDCDC
Color23=0xDCDCDC
Color24=0x000000
Color25=0xE1E1E1
Color26=0x000000
Color27=0xD77800
Color28=0xFFFFFF
Color29=0x000000
Color30=0x202020
Color31=0xFFFFFF
Color32=0x293DA3
Color33=0x1F199F
Color34=0x0000E8
Color35=0x303030
Color36=0xFFFFFF
Color37=0x293DA3
Color38=0x202020
Color39=0xFFFFFF
HotKey0=0x0
HotKey1=0x0
HotKey2=0x0
HotKey3=0x0
HotKey4=0x0
WinPowerPlan00=High Performance
WinPowerPlan01=8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
WinPowerPlan10=??oa
WinPowerPlan11=381b4222-f694-41f0-9685-ff5bb260df2e
WinPowerPlan20=Power Saver
WinPowerPlan21=a1841308-3541-4fab-bc81-f71556f20b4a
WinPowerPlan30=kirby
WinPowerPlan31=77cb9369-b0dd-495a-a757-f868dbf98545
WinPowerPlan40=
WinPowerPlan41=
WinPowerPlan50=
WinPowerPlan51=
WinPowerPlan60=
WinPowerPlan61=
WinPowerPlan70=
WinPowerPlan71=
WinPowerPlan80=
WinPowerPlan81=
WinPowerPlan90=
WinPowerPlan91=
WinPowerPlanA0=
WinPowerPlanA1=
WinPowerPlanB0=
WinPowerPlanB1=
FIVRRowHeight=24
OneAD_EAX0=0x2E2E2E2E
OneAD_EDX0=0x2E2E2E2E
OneAD_EAX1=0x2E2E3030
OneAD_EDX1=0x2A2A2C2C
OneAD_EAX2=0x2E2E3030
OneAD_EDX2=0x2A2A2C2C
OneAD_EAX3=0x2E2E3030
OneAD_EDX3=0x2A2A2C2C
OneAE_EAX0=0x04030201
OneAE_EDX0=0x08070605
OneAE_EAX1=0x04030201
OneAE_EDX1=0x08070605
OneAE_EAX2=0x04030201
OneAE_EDX2=0x08070605
OneAE_EAX3=0x04030201
OneAE_EDX3=0x08070605
Six50_EAX0=0x22222222
Six50_EDX0=0x00000000
Six50_EAX1=0x22222222
Six50_EDX1=0x1F1F1F1F
Six50_EAX2=0x22222222
Six50_EDX2=0x1F1F1F1F
Six50_EAX3=0x22222222
Six50_EDX3=0x1F1F1F1F
Six51_EAX0=0x04030201
Six51_EDX0=0x00000000
Six51_EAX1=0x04030201
Six51_EDX1=0x08070605
Six51_EAX2=0x04030201
Six51_EDX2=0x08070605
Six51_EAX3=0x04030201
Six51_EDX3=0x08070605
NonTurboRatio1=0x13
NonTurboRatio2=0x13
NonTurboRatio3=0x13
NonTurboRatio4=0x13
NonTurboRatioLock1=0x0
NonTurboRatioLock2=0x0
NonTurboRatioLock3=0x0
NonTurboRatioLock4=0x0
FIVRVoltage00=0xE8400000
UnlockVoltage00=1
FIVRVoltage01=0x00000000
UnlockVoltage01=0
FIVRVoltage02=0x00000000
UnlockVoltage02=0
FIVRVoltage03=0x00000000
UnlockVoltage03=0
FIVRVoltage10=0x00000000
UnlockVoltage10=0
FIVRVoltage11=0x00000000
UnlockVoltage11=0
FIVRVoltage12=0x00000000
UnlockVoltage12=0
FIVRVoltage13=0x00000000
UnlockVoltage13=0
FIVRVoltage20=0xE8400000
UnlockVoltage20=1
FIVRVoltage21=0x00000000
UnlockVoltage21=0
FIVRVoltage22=0x00000000
UnlockVoltage22=0
FIVRVoltage23=0x00000000
UnlockVoltage23=0
FIVRVoltage30=0x00000000
UnlockVoltage30=0
FIVRVoltage31=0x00000000
UnlockVoltage31=0
FIVRVoltage32=0x00000000
UnlockVoltage32=0
FIVRVoltage33=0x00000000
UnlockVoltage33=0
FIVRVoltage40=0x00000000
UnlockVoltage40=0
FIVRVoltage41=0x00000000
UnlockVoltage41=0
FIVRVoltage42=0x00000000
UnlockVoltage42=0
FIVRVoltage43=0x00000000
UnlockVoltage43=0
FIVRVoltage50=0x00000000
UnlockVoltage50=0
FIVRVoltage51=0x00000000
UnlockVoltage51=0
FIVRVoltage52=0x00000000
UnlockVoltage52=0
FIVRVoltage53=0x00000000
UnlockVoltage53=0
IccMaxNew00=0x000007FF
IccMaxNew01=0x000007FF
IccMaxNew02=0x000007FF
IccMaxNew03=0x000007FF
IccMaxNew10=0x000007FF
IccMaxNew11=0x000007FF
IccMaxNew12=0x000007FF
IccMaxNew13=0x000007FF
IccMaxNew20=0x000007FF
IccMaxNew21=0x000007FF
IccMaxNew22=0x000007FF
IccMaxNew23=0x000007FF
IccMaxNew30=0x000007FF
IccMaxNew31=0x000007FF
IccMaxNew32=0x000007FF
IccMaxNew33=0x000007FF
IccMaxNew40=0x000007FF
IccMaxNew41=0x000007FF
IccMaxNew42=0x000007FF
IccMaxNew43=0x000007FF
CacheMinMax0=0x2C2C
CacheMinMax1=0x82C
CacheMinMax2=0x82C
CacheMinMax3=0x82C
TVBoost=0x0
RingDownBin=0x0
VMaxStress=0x0
AVXOffset=0x000000
AVX512Offset=0x000000
SaveOnExit=2
OffsetRange=1
VCCOffsetRange=0
DefaultCache=0
SleepZeroVoltage=0
TSBRowHeight=23
Results00=0
Results01=0
Results02=0
Results10=0
Results11=0
Results12=0
Results20=0
Results21=0
Results22=0
Results30=10299
Results31=0
Results32=0
Results40=0
Results41=0
Results42=0
Results50=0
Results51=0
Results52=0
Results60=0
Results61=0
Results62=0
Results70=0
Results71=0
Results72=0
CheckSum=0xDCF9F77B
PowerLimitEAX0=0x002385A0
PowerLimitEDX0=0x004285C8
PowerLimitEAX1=0x002385A0
PowerLimitEDX1=0x004285F0
PowerLimitEAX2=0x002385A0
PowerLimitEDX2=0x004285F0
PowerLimitEAX3=0x002385A0
PowerLimitEDX3=0x004285F0
MSRLock=0x0
PROCHOT_Offset0=0x5
PROCHOT_Offset1=0x5
PROCHOT_Offset2=0x5
PROCHOT_Offset3=0x5
PROCHOT_Activate=0
PROCHOT_Lock=0
PP0POWERLIMITEAX=0x00000000
PP0Lock=0
TDPLevel=0x00000000
TDPLevelControl=0
PowerBalancePP0=16
PowerBalancePP1=16
PowerPolicy=0
PowerLimit4=0x00000000
NoSetPL=0xF
SyncMMIO=0x1
LockPowerLimits=0
VCCIN0=0x0
VCCIN1=0x0
VCCIN2=0x0
VCCIN3=0x0
PowerCutWarning=0x0
PowerCut=0x0
```
