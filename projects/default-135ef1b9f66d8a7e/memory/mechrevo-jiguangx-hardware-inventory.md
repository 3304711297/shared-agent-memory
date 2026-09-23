---
name: mechrevo-jiguangx-hardware-inventory
description: 机械革命极光X (GM6AQ7C) 整机全物理硬件设备规格全景台账 (脱敏硬件指纹)
metadata:
  node_type: memory
  type: reference
---

# 机械革命极光X (GM6AQ7C) 全物理硬件设备规格全景台账

本文档记录通过 Windows 物理底层探测（WMI、CIM、PCIe 配置空间、`nvidia-smi`、EDID 与 PnP 设备树）采集整理的**除操作系统软件层以外的所有物理硬件信息**。已严格执行硬件序列号与唯一识别码脱敏。

---

## 1. 核心计算与主板 (Processor & Motherboard)

- **主机型号**：MECHREVO JiguangX Series GM6AQ7C（机械革命 极光X）
- **主板 (BaseBoard)**：MECHREVO GM6AQ7C（同方模具 GM6AQ7C，版本 Standard，ODM 代号 `weiyang 327670412`）
- **处理器 (CPU) 与 AI 协处理器**：
  - 微架构：Alder Lake-HX（Intel 7 工艺，B0 步进，CPUID `90672`，插槽 `U3E1`）
  - 物理核心规格：物理 16 核 24 线程（8P 性能核 + 8E 能效核）
  - 缓存架构：L2 缓存 10MB（$8 \times 1.25\text{MB}$），L3 智能缓存 25.6MB
  - 基频与最大睿频：基准 2.30 GHz，P核最大单核睿频 4.80 GHz
  - **神经网络与语音加速单元**：**Intel GNA Scoring Accelerator**（Gaussian & Neural Accelerator 3.0，硬件 ID `PCI\VEN_8086&DEV_464F`）
  - 当前运行调优态：**8 核 8 线程**（BIOS 内关闭超线程 HT 与小核 E-cores，纯 8P 大核低微卡顿模式）
- **主板与芯片组拓扑 (Chipset & Topology)**：
  - PCH 芯片组：Intel 600 系列移动平台南桥 PCH（WM690/HM670，DeviceID `7A8C`）
  - 物理插槽与上限：2 组 DDR5 SO-DIMM 物理插槽，最大寻址支持 64GB
  - 传感器与温控区：ACPI ThermalZone `ECTZ_0` 与 `TZ00_0`（当前物理巡检温度 ~44℃ / 3172 dK）
  - 安全芯片状态：TPM 物理未激活 / 关闭状态（`TpmPresent: False`，BIOS 中未启用 PTT/dTPM）

---

## 2. 独立显示核心与显卡 (Discrete GPU)

- **显卡型号**：NVIDIA GeForce RTX 4070 Laptop GPU（移动端独立显卡）
- **GPU 架构**：Ada Lovelace（AD106 核心，GPU Part Number: `2820-775-A1`，Board ID: `0x100`）
- **显存规格**：8GB GDDR6（物理容量 8,188 MiB，显存速率 8,001 MHz，总带宽 256.0 GB/s）
- **功耗墙设定 (TGP)**：
  - **默认基础功耗 (Default Limit)**：115.00 W
  - **动态加速最大功耗 (Max Limit / Dynamic Boost)**：**140.00 W 满血功耗版**
- **核心频率规格**：最大 Boost 频率 3,105 MHz，CUDA 核心数 4,608
- **总线接口**：PCIe 4.0 x8（当前实跑 PCIe Gen4 x8 @ Gen4 速率）
- **VBIOS 版本**：`95.06.15.40.63`
- **显示直连拓扑**：硬件 MUX 开关 + NVIDIA Advanced Optimus（DDS 动态直连切换驱动支持，当前 BIOS 设置为 **`dGPU Only` 纯独显直连**）

---

## 3. 物理内存子系统 (RAM & SPD)

- **物理总容量**：**24 GB**（新一代非二进制 Non-Binary DDR5 组合：2 条 12GB）
- **物理通道拓扑**：Controller0/1 双通道（4 x 32-bit DDR5 子通道）
- **颗粒与模组硬件**：
  - **颗粒原厂**：**SK Hynix（海力士）**（JEDEC ID `0x80AD`，单面 1 Rank，8 颗 24Gb / 3GB 高密度颗粒）
  - **模组品牌**：雷神/机械革命 OEM（Qingdao Thunderobot，JEDEC ID `0x0E62`，料号 `JJ02HM002`）
  - **板载 PMIC 芯片**：Richtek Power（立锜科技独立供电芯片）
  - **JEDEC 原生规格**：DDR5-5600（CL46-45-45 @ 1.10V）
- **当前实跑调优参数**：
  - **频率模式**：**DDR5-6400 MT/s**（Custom Profile，100MHz 基频 × 64x 倍频）
  - **控制器模式**：**Gear 2 模式**（UCLK 1600MHz / MCLK 3200MHz，Ring 总线 4400MHz）
  - **核心主时序**：**CL40-40-40-77 2T @ 1.20V**
  - **核心副时序**：tCWL 38、tFAW 32、tREFI 22400、tRFC 824、tRFC2 576、tRFCpb 432、tWR 78、tRTP 18

---

## 4. 物理固态存储 (Storage & NVMe)

- **主硬盘型号**：**KINGSTON OM8PGP41024N-A0**
- **硬盘总容量**：1,024.2 GB（标称 1TB NVMe M.2 2280 SSD）
- **总线类型**：NVMe（PCIe 4.0 x4 通道）
- **扇区格式**：512 字节 / 逻辑扇区，GPT 分区表
- **运行健康状态**：Healthy / Online，无物理介质损耗（Wear 0）
- **物理分区结构**：
  - 分区 1：Windows 恢复分区（529 MB）
  - 分区 2：EFI 系统引导分区（100 MB，FAT32，挂载 `\EFI\Microsoft\Boot\bootmgfw.efi`）
  - 分区 3：MSR 保留分区（16 MB）
  - 分区 4：系统卷（C盘，150.37 GB，剩余约 70.8 GB）
  - 分区 5：数据卷（D盘，802.87 GB，剩余约 106.4 GB）

---

## 5. 显示面板与外部显示器 (Display & EDID)

- **笔记本内置显示屏**：
  - **制造商代号**：CSW（华星光电 / CSOT）
  - **面板型号**：`MNG007DA5-2`
  - **制造时间**：2024 年
  - **屏幕规格**：16.0 英寸 16:10 / 16:9 电竞屏，出厂写入专有色彩校准 ICC / LUT
- **外部主力电竞显示器**（当前连接并作为主显示）：
  - **制造商代号**：HKC（惠科）
  - **显示器型号**：`G24H3SClassic`（HKC 神盾 / 经典系列超快 IPS 电竞屏）
  - **制造时间**：2025 年第 1 周
  - **当前分辨率与刷新率**：**1920 × 1080 @ 240 Hz 超高刷新率**（RGB 8-bit 全范围）

---

## 6. 音频解码与声卡硬件 (Audio Codec)

- **板载音频芯片**：**Conexant / Synaptics HD Audio Codec**
  - **硬件 ID**：`HDAUDIO\FUNC_01&VEN_14F1&DEV_1F87&SUBSYS_1D05142D`（Conexant/Synaptics CX 系列高清音频解码芯片，同方笔记本专属子系统 ID `1D05142D`）
- **物理输出端点**：
  - 机身扬声器立体声单元（Speakers）
  - 3.5mm 耳机/耳麦组合接口（Headphones）
  - 阵列式降噪数字麦克风（Microphone Array）

---

## 7. 物理网络适配器 (Network Controllers)

- **有线千兆网卡**：**Realtek PCIe GbE Family Controller**
  - **硬件芯片**：Realtek RTL8168/8111 PCI-E 千兆以太网芯片（硬件 ID: `PCI\VEN_10EC&DEV_8168&SUBSYS_12731D05&REV_15`）
  - **接口速率**：10/100/1000 Mbps 自适应
- **无线 Wi-Fi 6E 网卡**：**MediaTek Wi-Fi 6E MT7922 (RZ616) 160MHz Wireless LAN Card**
  - **硬件芯片**：联发科 MT7922（PCIe M.2 2230 接口，硬件 ID: `PCI\VEN_14C3&DEV_7922&SUBSYS_380411AD&REV_00`）
  - **规格特性**：支持 2.4GHz / 5GHz / 6GHz 三频段、160MHz 频宽、MU-MIMO、当前驱动稳定版本 `3.6.0.1427`
- **蓝牙适配器**：**MediaTek Bluetooth Adapter**（USB 接口，VID `04CA` PID `3804`）

---

## 8. 机身电池与供电规格 (Battery & Power)

- **电池类型**：锂聚合物电池组（OEM Standard Lithium-Ion/Polymer）
- **电池满充容量 (Full Charged Capacity)**：**60,060 mWh**（约 60 Wh 标称容量）
- **电池健康与保养**：Control Center 写入 `UniWillVariable` 实施充电阈值保护

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
