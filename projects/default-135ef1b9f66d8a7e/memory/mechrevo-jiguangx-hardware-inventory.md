---
name: mechrevo-jiguangx-hardware-inventory
description: 机械革命极光X (GM6AQ7C) 整机全物理硬件设备规格全景台账 (AIDA64/图吧工具箱底层实测)
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
  - **当前运行调优态**：**8 核 8 线程**（BIOS 内关闭超线程 HT 与能效小核 E-cores，纯 8P 大核低微卡顿模式）
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
