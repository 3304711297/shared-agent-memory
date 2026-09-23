---
name: uefi-bios-firmware-analysis
description: "解析BIOS/固件/查NVRAM设置项时必用。AMI Aptio V 固件解包与设置核查。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [uefi, bios, nvram, ifr, firmware, aptio, spi-flash]
    category: devops
    related_skills: [windows-crash-diagnostics, hermes-agent]
---

# UEFI/BIOS 固件解析与设置项核查

## When to Use（触发场景）

- 用户给出 `.fd` / `.bin` / `.rom` 固件镜像（多为 16/32 MB SPI 全片 dump），要求「解析 BIOS」「看看某个设置项」「记忆里没记录这些当前值」。
- 需要把 BIOS 菜单里的选项名 → 变量落点（`VarStore:VarOffset`）→ 实际字节值三者对上。
- 用户改完某个 BIOS 选项，提取新镜像要求**验证改动是否落地**。
- 需要判断「某选项出厂默认是什么」「用户手动改过哪些项」。

## 工具链（一次性获取，常驻复用）

```bash
mkdir -p "$TOOLS" && cd "$TOOLS"
gh release download A75 --repo LongSoft/UEFITool --pattern "*win64.zip"
gh release download v1.6.1 --repo LongSoft/IFRExtractor-RS --pattern "*windows.zip"
unzip -o "*.zip" && rm -f "*.zip"
# 产出 UEFIExtract.exe / UEFITool.exe / UEFIFind.exe / ifrextractor.exe
```

## 标准流程

1. **全片解包**：`UEFIExtract.exe <fw.fd> dump` → 得 `fw.fd.dump/`（含 Descriptor / GbE / ME / BIOS 五大区，数万文件）与 `info.txt`。
2. **反编译 Setup 表单**：UEFIExtract 的 dump **不产 `.sct` 文件**；Setup 的表单段位于 `<fw>.dump\...\<n> Setup\1 PE32 image section\body.bin`（同一固件常有两个同名 `Setup` 模块——实测 13 KB 的桩 vs 1 MB 的主模块，**取体积最大的那个**）→ `ifrextractor.exe body.bin` 即得 IFR（含全部 `Form` / `OneOf` / `Question` 与 `VarStoreId` / `VarOffset` / `Size` / 选项 `Value`）。
3. **定位活跃 NVRAM**：AMI Aptio V 一般在 `0x1000000` 起（约 192 KB 的成对存储区）；根变量名 = `Setup` / `CpuSetup` / `SaSetup` / `PchSetup` / `MeSetup` / `SecureBootSetup`（长度固定，可直接搜名字）。
4. **变量体提取**：命中名字后向前回找最近的 `NVAR` 头，变量载荷 = `[名字结束+1 .. NVAR头+总长]`；载荷长度应与该 VarStore 声明长度完全一致（对齐自校验点）。
5. **交叉映射**：把每个 Question 的 `VarStoreId` 映射到根变量名，再按 `VarOffset` 取字节，用同一 Question 块内的 `OneOfOption Value:` 反查显示名 → 得「菜单路径 / 变量:偏移 / 当前值 / 出厂默认」四列表。
6. **菜单路径**：Form 之间有 `Ref` 引用，需按 FormId 建父子关系做 BFS，才能还原 `Chipset → PCH-IO Configuration → USB Configuration` 这类真实点选路径。

## AMI NVAR 记录格式（实测）

```
'NVAR' | 2B 总长(LE) | 3B 写入标记 | 1B 属性 | [1B 名字段 + NUL 结尾名字] | 载荷
```

- **名字为空（0x00）的记录 = 数据-only 追加记录**：名字复用同名变量的首条记录，其载荷长度恰好等于该变量的 VarStore 长度。
- 存储区是**日志式追加**：改动写在尾部新记录里，旧副本仍在原处保留**旧值**（垃圾回收前并存）。
- 因此判断「变量当前值」永远用**追加在最后的那条记录**；同一个变量在文件里通常有 2~4 份副本。

## 「BIOS 改动是否落地」核查法

1. **全片字节 diff**：两代镜像逐字节比对，差异应全部落在 NVRAM 区 —— 说明「只改了设置，没动固件本体」。
2. **只比载荷，忽略 3 字节写入标记**：该标记随任何写入/访问刷新，拿它推断「哪个副本更新」必错。
3. **单一改动判定**：新旧载荷对齐后若**只差 1 字节**，说明只动了一个选项，且该偏移即 IFR 的 `VarOffset`。对齐自检：错位对齐会产生数百处差异，一眼可辨。
4. **OS 侧交叉验证**（最强佐证）：设置项若对应 PCI/USB 功能，重启后直接看设备树——功能消失/出现即生效。
   - 只枚举**当前存在**设备：`Get-PnpDevice -PresentOnly`；隐藏态可用 `Get-PnpDevice | Where InstanceId -like '*DEV_xxxx*'`（看 `Status=Unknown, Present=False`）。
   - 历史记录留在 `HKLM\SYSTEM\CurrentControlSet\Enum\PCI`，可作「改前曾存在」的佐证（键里的 `DeviceDesc` 直接给出驱动/设备名）。

## 坑位

- **AMITSE 表单引用表（菜单可见性机制）**：`AMITSE` 模块里有「Setup FormSet GUID + 2 字节 Form ID」的**定长（32 字节）**表项，分组决定哪些顶层菜单出现；未使用的表单集合仍完整留在固件里（“屏蔽”是引用不指向，不是删除）。**公开教程的紧凑字节签名/绝对偏移在本机镜像上往往不存在**，必须按 GUID + 步长在镜像上重新定位。
- **ifrextractor 的输出不落在 stdout**：它写在**输入文件所在目录**，文件名形如 `<输入名>.0.0.en-US.uefi.ifr.txt`，屏幕上只有一行横幅（看不到内容 ≠ 失败）。**且重复运行会向同一文件追加**（实测跑两次 → 3.2 MB = 2.1 + 1.1 MB 叠在一起），重跑前必须先删旧输出。
- **默认模式 vs `verbose`**：默认输出无偏移（2.1 MB 级）；`verbose` 额外附 opcode 偏移与原始字节（3.2 MB 级）。要跟已有台账逐字节对齐，用默认模式。
- **NE 版不含 UEFIPatch/UEFIReplace**：改固件本体（打补丁 / 替换模块）必须用经典 0.28.0 套件的对应 exe；NE A7x 只提供查看/解包/检索三件。
- **原生 Windows 程序不认 MSYS 路径**：`UEFIExtract.exe` 等必须传 `C:/...` 正斜杠原生路径；`git -C /c/...`、`node /tmp/x.js` 同理会报 not found。
- **`search_files` 的 pattern 反斜杠会被转成 `/`**，`\(`、`\d` 静默 0 命中；搜固件相关正则改字符类 `[(]` / `[0-9]`，或直接在 Python 里 `str.find`。
- **`gh release download` 的 `--pattern` 用 glob**（`*win64.zip`），别按正则写。
- **别把台式机超频经验套进笔记本**：内存时序受平台与散热现实约束，未经验证的「更大更松」不是优化而是负优化；改任何电压/时序前先确认该平台的真实容错窗口。
- **BIOS 内导出镜像 ≠ 出厂镜像**：`1、备份原版本bios` 一类目录名容易误导，判断代次看 `mtime` + NVRAM 内容，而非文件名。
- **Windows 固件变量读取**：`GetFirmwareEnvironmentVariableW` 需要 `SeSystemEnvironmentPrivilege`（管理员提升 + `AdjustTokenPrivileges`）；多数 OEM 的 `PchSetup` 类变量根本不向 OS 暴露（返回 203 ERROR_ENVVAR_NOT_FOUND），别在这条路上死磕——回到镜像解析。

## 本机既有产物（Hermes 环境）

- **工具链只在 U 盘**：`E:\download\机械革命\bios tools\` —— `bin\` 内为解压好的 A75/1.6.1 四件套；`fw2ifr.bat` 拖入固件即全自动（UEFIExtract dump → 定位 Setup 主模块 → 出 `<固件名>.setup.ifr.txt`）；`ifrextractor.bat` 处理单个段文件；`工具版本.txt` 记版本台账与坑位；经典 0.28.0 三件套（UEFITool/UEFIPatch/UEFIReplace）留档。**本机 `D:\ai coding\tools\bios_tools\` 副本与解包产物已于 2026-09-23 清理，用前从 U 盘取，不要假设本机常驻**
- **固件镜像在 U 盘整合包目录**：`…\aq升级极光pro完整整合包\`（`原bios\`、`2、刷入极光pro低版本bios\`、`4、解锁bios\`、`最新bios包括修改过的设置\`），不要在 `C:\` 盘找旧路径
- 解包与 IFR 文本：`D:\ai coding\backup.fd.dump\`、`D:\ai coding\backup.fd.setup.ifr.txt`
- 项目结论落在共享记忆库：`projects/default-*/memory/mechrevo-jiguangx-bios-firmware-reference.md`（按菜单路径的索引台账）与 `mechrevo-jiguangx-hardware-inventory.md`
