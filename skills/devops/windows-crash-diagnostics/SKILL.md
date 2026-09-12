---
name: windows-crash-diagnostics
description: "蓝屏/死机/崩溃排查时必用。Windows BSOD与意外重启诊断。Use when Windows crashes, BSODs, or reboots unexpectedly."
---

# Windows Crash & Minidump Diagnostics

当 Windows 遭遇蓝屏（BSOD）、黑屏死机、卡死重启或意外断电关机时，无需依赖笨重的 WinDbg 或 Windows SDK，使用原生 PowerShell 与 Python 标准库快速逆向分析转储文件并定位根本真凶。

## 标准排查流程 (Triaging SOP)

### 1. 提取内核事件时间线与崩溃签名
通过系统事件日志确认异常关机时间与系统错误报告（WER）：

```powershell
# 1. 检查最近系统崩溃事件（BugCheck 1001 与 Kernel-Power 41）
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-WER-SystemErrorReporting'} -MaxEvents 5 -ErrorAction SilentlyContinue | Format-List TimeCreated, Message

# 2. 检查意外断电前最后一次系统记录时间与前后错误
Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2,3} -MaxEvents 30 | ForEach-Object {
    "{0} [{1}] ({2}) {3}" -f $_.TimeCreated.ToString('HH:mm:ss'), $_.LevelDisplayName, $_.ProviderName, ($_.Message -replace '\r?\n', ' ')
}
```

### 2. 免调试器直接解析 Minidump (`DUMP_HEADER64`)
Windows 64 位内核崩溃转储文件（`C:\Windows\Minidump\*.dmp`）以 `PAGE` 签名开头（ValidDump: `DU64`）。
运行附带脚本 `scripts/parse_minidump.py` 可直接解析：

```bash
python -c "
import struct, glob, os
dumps = sorted(glob.glob(r'C:\Windows\Minidump\*.dmp'), key=os.path.getmtime)
if not dumps: print('No minidump found'); exit()
data = open(dumps[-1], 'rb').read(0x1000)
sig, valid = struct.unpack_from('<4s4s', data, 0)
bc = struct.unpack_from('<I', data, 0x38)[0]
p1, p2, p3, p4 = struct.unpack_from('<4Q', data, 0x40)
print(f'Latest: {dumps[-1]} | {sig.decode()} {valid.decode()}')
print(f'BugCheck: 0x{bc:08X} (Param1: 0x{p1:016X}, Param2: 0x{p2:016X}, Param3: 0x{p3:016X}, Param4: 0x{p4:016X})')
"
```

### 3. 常见 BugCheck 根因判断矩阵

| BugCheck 代码 | 典型名称 | 核心特征与机制 | 首要排查方向 |
|---|---|---|---|
| `0x0000000A` | `IRQL_NOT_LESS_OR_EQUAL` | Param2 为高中断级别（如 `0xFF` HIGH_LEVEL），CPU 在极高优先级尝试访问无效内存地址（Param1）。在页面调度器无法工作的 IRQL 下只能硬崩溃。 | **硬件欠压不稳定（高发）**：ThrottleStop/BIOS 核心或缓存 Undervolt 过于激进，在突发瞬态负载或 C-State 切换瞬间欠压触发位翻转；其次为第三方过滤驱动/反作弊驱动踩内存。 |
| `0x0000001E` | `KMODE_EXCEPTION_NOT_HANDLED` | 内核模式发生未处理异常（如内存越界 0xC0000005）。Param2 为故障指令地址。 | 驱动空指针调用、内存条物理接触不良、XMP 频率不稳。 |
| `0x00000050` | `PAGE_FAULT_IN_NONPAGED_AREA` | 系统引用了非分页池中的无效系统内存。 | 故障驱动程序、损坏的分页文件或有缺陷的 RAM。 |
| `0x0000003B` | `SYSTEM_SERVICE_EXCEPTION` | 执行从用户模式切换到内核模式的系统服务例程时异常。 | 显卡驱动（`nvlddmkm.sys` / `dxgkrnl.sys`）或 GUI 挂钩工具。 |
| `0x00000124` | `WHEA_UNCORRECTABLE_ERROR` | Windows 硬件错误架构捕获到的 CPU/PCIe/总线硬件不可纠正错误。 | CPU 电压不足、过热保护、PCIe 通道掉盘或电源供电跌落。 |

### 4. 硬件调优与过激降压（Undervolt）深度溯源
当出现 `0x0000000A` 且 Param2 为 `0xFF` (HIGH_LEVEL) 时，必须优先排查 CPU 降压与功耗调控工具（如 ThrottleStop、XTU 或 BIOS 调压）：

1. **检查正在运行的调压工具配置**（如 `ThrottleStop.ini`）：
   - `FIVRVoltage00`：CPU Core 电压偏移。
   - `FIVRVoltage20`：CPU Cache 电压偏移。
2. **解码 FIVR MSR 0x150 电压偏移**：
   - 寄存器高 11 位为 11 位补码整数（以 $1/1024\text{ V} \approx 0.976\text{ mV}$ 为步进）。
   - 公式：`offset_mv = ((raw - 0x800) * 1000 / 1024) if (raw & 0x400) else (raw * 1000 / 1024)`。
3. **Alder Lake-HX (12代+) 硬件物理铁律**：
   - **单轨供电与 Cache 裁决律（Single-Rail Binding）**：12代移动端 CPU Core 与 Ring Bus/Cache 物理共享同一供电轨（Co-voltage Rail），微码通常严格以 **P-Cache 电压为整轨真源**。若单独在 ThrottleStop 中调节 Core，监控表中实时电压完全不变，唯有调节 P-Cache 才会真实改变芯片整轨物理电压。
   - **C-State 关闭下的高频总线稳定性**：BIOS 关闭 C-State 后核心全程保持 C0 活跃，虽杜绝了休眠唤醒时的瞬态欠压，但 Ring Bus（Cache）也随之全时处于高频重压之下。此时 Cache 若降压过激（如超过 -180mV），在处理最高优先级时钟中断（`IRQL=255 HIGH_LEVEL`）与跨核高频调度时，极易因纳秒级信号衰减触发寻址位翻转（Bit-flip），直接造成 `0x0A` 非法地址读。
   - **动态功耗机制**：降压的本质收益遵循 $P = C \cdot V^2 \cdot f$ 的平方律。过高电压会导致动态功耗迅速击穿功耗墙与电流墙，导致高负载下“使不上劲”而断崖式降频；但过激负压（如 -190mV+）又会导致总线指针翻转死机。稳态极限通常在 **`-170mV ~ -180mV`** 甜点区间。
4. **对策**：立即将 P-Cache 与 Core 联动微调回拉 $10\text{mV} \sim 25\text{mV}$ 安全余量（如从 -190mV 收回至 -180mV），在维持全核低温高频的同时消除瞬态寻址黑屏。

### 5. 第三方非微软驱动审查
核对崩溃时间点附近是否有卸载失败（如 `0xC0000365`）或可疑驱动：
```powershell
Get-CimInstance Win32_SystemDriver | Where-Object {
    $_.PathName -and
    $_.PathName -notlike 'C:\Windows\system32\drivers\*' -and
    $_.PathName -notlike 'C:\Windows\System32\DriverStore\FileRepository\ms*'
} | Select-Object Name, DisplayName, PathName
```
重点排查：远程桌面/虚拟显卡驱动（如 GameViewer `ROOT\DISPLAY`）、反作弊驱动（ACE / SGuard）、杀软过滤驱动。
