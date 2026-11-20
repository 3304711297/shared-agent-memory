# xos-playbook：上游迁移、看门分支与清单核查机制

## 仓库事实

- 旧库 `imribiy/XOS` 已降级为品牌/说明页（README + 壁纸 + PSD，无脚本）。
- 真正承载优化规则与脚本的是 `imribiy/xos-playbook`：`Configuration/custom.yml`（约 1750 行、808 个动作）+ `Executables/*.ps1|bat`（13 个）+ `playbook.conf`。
- **跟踪分支是 `dev`（开发者 beta），不是 main**。本机曾按 main 审计，漏掉了 dev 独有的 `WaitToKillServiceTimeout=2000`、`HiberbootEnabled=0`、`ReservedStorage.ps1`。看门基线写 `branches: ["dev"]`。
- 作者 ABI：`xos-beta`（beta 构建）、`xos-toolkit`（逐项应用/撤销的桌面工具）。旧库迁移结论登记在 `tools/upstream-sources.json` 的 `retired.XOS.migration_review`。

## 已吸收 vs 不吸收

已吸收（tweakbyjie）：TimerCoalescing、PageCombining（本仓 MMAgent 口径更严）、GPU TdrDelay（2026-11-20 跟随上游 10→12）、DWM 滚轮、PCIe MSI（含本轮新增删除 `Affinity Policy\DevicePriority`）、每接口 `TcpAckFrequency/TCPNoDelay` + 网卡/PCI/USB 节能关闭（仅有线+插电、只改已存在 DWORD、还原删值）。

明确不吸收：`PowerThrottlingOff`/`EnergyEstimationEnabled`、任务栏悬停 250ms + `SmoothScroll=0`、Segment Heap（上游把值名写成含空格的 `Segment Heap`，系统不识别，正确形态是子键下的 `Enabled`）、所有破坏性/安全削弱项（`Set-ProcessMitigation -SYSTEM -Disable`、`acpiex Start=4`、批量禁服务与计划任务）。

审计计数（dev @0ed60c3，808 动作）：已采纳/覆盖 33；未采纳 775（A 破坏性 431、B 安全削弱 27、C 范围外 123、D 无依据/重复/无效 191、E 未选 3）。

## 清单与看门的协作契约（重要）

用户裁定：**看门只核查，不自动改文件**。

- 人工清单：`docs/reference/XOS-PLAYBOOK-INVENTORY.md`；
- 指纹基线：`tools/xos-playbook-inventory.json`（每条动作 type/key/fingerprint/行号 + review_state + 上游文件 sha256）；
- 核查脚本 `tools/check-xos-inventory.ps1`：默认只读，输出 added/removed/changed 到 `xos-inventory-check.md`，退出码 0=一致、10=需更新、20=异常；`-Apply` 只在人工显式执行时写文档与基线；
- `upstream-watch.yml` 保持 `contents: read`，把核查结论贴进 issue；**绝不自动提交、不自动推进 `upstream-sources.json` 基线**——评估门槛由人把守。

## 踩过的坑

1. **不要用 `main` 判断上游现状**：本仓库的活体现在在 `dev`，先 `gh api repos/<r>/branches` 再定基线。
2. **playbook 的 YAML 是 AME Wizard 私有标签**（`!registryValue` 等），解析要按行/块处理；PowerShell 侧手写解析器需覆盖 flow map、块标量（`command: >-`）与引号风格。
3. **多行块行号会漂**：文档里 `custom.yml:行号` 指动作起始行，块内引用按值名检索核对；抽样发现过 7 处偏差，交付前要抽查。
4. **上游存在自相矛盾**：同一 playbook 里 `bam` 先置 4 又改回 3；`acpiex` 这类 Boot 级 ACPI 驱动被置 `Start=4`，照抄会直接开不了机——任何"全盘吸收"都不可接受。
5. 公开仓库里的清单文档要清掉本机绝对路径（`D:/...`），改成「本仓库」或占位符。
