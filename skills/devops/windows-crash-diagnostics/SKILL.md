---
name: windows-crash-diagnostics
description: "蓝屏/死机/崩溃排查时必用。Windows BSOD与意外重启诊断。Use when Windows crashes, BSODs, or reboots unexpectedly."
---

# Windows Crash & Minidump Diagnostics

当 Windows 遭遇蓝屏（BSOD）、黑屏死机、卡死重启或意外断电关机时，无需依赖笨重的 WinDbg 或 Windows SDK，使用原生 PowerShell 与 Python 标准库快速逆向分析转储文件并定位根本真凶。

**先分清两类故障，它们的取证路径完全不同**：有 dump = OS 崩溃（走第 2~3 节的 BugCheck 分析）；无 dump = 硬件/电源级硬断电（走第 6 节，重点看构建产物 mtime 与满载时间点）。把无 dump 当成「没线索」是最常见的误判——文件系统时间戳往往能精确定位到秒级。

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

### 6. 区分「硬断电」与「软件崩溃」：无 dump 不等于没线索

用户报告「更新/编译途中电脑自动关机」时，**先分清是 OS 崩溃还是硬件掉电**。
两者的取证路径完全不同，混淆会把你引到错误方向。

| 判据 | 硬件级硬断电 | BSOD / 内核崩溃 |
|---|---|---|
| `C:\Windows\Minidump\*.dmp` | 无新文件（转储根本来不及写） | 有新的 `.dmp` |
| `MEMORY.DMP` / LiveKernelReports | 无 | 可能有 |
| Event ID **41** (Kernel-Power) | **可能缺失**（见下方陷阱） | 通常有 |
| Event ID 1001 (BugCheck) | 无 | 有，含 BugCheck 码 |
| Event ID 6008（意外关机） | 有，但时间是**最后一次刷盘**而非断电时刻 | 有 |
| 断电后的首条日志 | 直接是 `Kernel-Boot`/`Kernel-General ID=12`（全新启动） | 可能有崩溃→重启的过渡记录 |

**陷阱一：Event 6008 的时间不是断电时刻。** 它报的是 Windows **最后一次把日志刷入磁盘**的时间，可能比实际断电早数分钟（本次实测：6008 报 `18:49:37`，而构建产物 mtime 证明直到 `18:54:30` 系统都在正常写盘）。**用文件系统 mtime 交叉验证真实时刻**：

```python
# 编译/构建中断的场景：看构建中间产物的最后写入时间
import pathlib, datetime
for f in sorted(target_dir.rglob("*.fingerprint/**/invoked.timestamp")):
    print(datetime.datetime.fromtimestamp(f.stat().st_mtime), f)
```

**陷阱二：Event 41 可能根本不存在。** 本次排查中近 90 天只有 2 条 ID=41（07-03、09-07），而 09-20 这次**完全没有 41** —— 但 6008 明确说「unexpected shutdown」。`fast startup` 关闭（`HiberbootEnabled=0`）+ 直接掉电时，41 的写入路径可能被跳过。**不要把「无 41」当成「没有意外关机」**；以 6008 + 无对应 6006（正常关机）为准。

**陷阱三：负载类型决定嫌疑方向。** 断电发生在**全核满载**时刻（`cargo build` / 编译 / 渲染）时，优先怀疑供电与降压稳定性，而不是软件：
- 满载瞬间电流尖峰让**欠压余量不足**的 CPU 直接掉电重启（无蓝屏，因为欠压发生在 VRM 层而非指令执行层）；
- 与 `0x0A` 类「欠压导致位翻转」不同，这类是**电源层直接切断**，什么都来不及记录。

排查顺序：① 确认降压值（见第 4 节 FIVR 解码）是否超过本机稳态极限；② 检查是否开着 `ultimate-performance` 电源计划（解除功耗墙后负载更突进）；③ 满负载复现测试（如 `cargo build` 或 Prime95）观察是否重复；④ 若偶发且仅在满载，先回调 10~25mV 降压再观察。

**降级排查（不重启的前提下）**：`powercfg /batteryreport` 在某些机型上报 `0x422 无法启动服务`（本次即如此，因电池相关服务被禁用）。此时改用 `root\wmi` 命名空间：`BatteryStaticData`（拿设计容量）与 `BatteryFullChargedCapacity`（拿满充容量）—— 两者相除就是健康度。注意 `Win32_Battery.DesignCapacity` 在这类机型上恒为空。

### 7. 第三方非微软驱动审查
核对崩溃时间点附近是否有卸载失败（如 `0xC0000365`）或可疑驱动：
```powershell
Get-CimInstance Win32_SystemDriver | Where-Object {
    $_.PathName -and
    $_.PathName -notlike 'C:\Windows\system32\drivers\*' -and
    $_.PathName -notlike 'C:\Windows\System32\DriverStore\FileRepository\ms*'
} | Select-Object Name, DisplayName, PathName
```
重点排查：远程桌面/虚拟显卡驱动（如 GameViewer `ROOT\DISPLAY`）、反作弊驱动（ACE / SGuard）、杀软过滤驱动。
