---
name: CPA Core Update 1175 and Upstream Issue 241
description: EasyCLIProxyAPI 内核更新 os error 1175（ReplaceFile 瞬态锁）排错闭环、手动装核流程与上游 issue #241 跟踪
metadata:
  type: reference
---

# CPA 内核更新 os error 1175 排错闭环（2026-09-09）

## 事件全貌

用户报「无法更新 cpa 内核」：cpa-gui v0.2.80 版本管理页「停止并更新」v7.2.154→v7.2.155 报「覆盖内核文件失败 cpa-core\cpa-gui-meta.json: 无法删除要被替换的文件 (os error 1175)」。

- **根因**：os error 1175 = Win32 `ReplaceFile` 的 `ERROR_UNABLE_TO_REMOVE_REPLACED`（微软文档核实）——新文件已解压就位、删旧文件时被第三方进程瞬时句柄阻断（杀软/索引器按访问扫描或 GUI 自身句柄），GUI 自动回滚（旧 zip 重解压）。
- **特征指纹**：exe 时间戳是新的但版本串仍是旧版 + meta.json 停在旧版本 = 更新部分完成被回滚。
- **源码定位**（main HEAD `895bff0`，含 v0.2.81/PR#240 均未修）：`core_runtime.rs` `copy_core_file_replace`（报错文案出处）→ `core_config/settings.rs` `replace_file_atomically` Windows 分支裸调 `ReplaceFileW(flags=0)`，无重试无降级。Restart Manager API 实测报错 20 分钟后全部文件无句柄 = 瞬态锁。
- **上游 issue 已发**：router-for-me/EasyCLIProxyAPI**#241**（账号 3304711297，2026-09-09，含源码定位+三条修复建议：退避重试 1175/32/5、fs::rename 降级、meta 等非关键文件降级警告；否决 MOVEFILE_DELAY_UNTIL_REBOOT）。查重 4 组关键词 0 命中。**后续：上游发修复版后关 #241 验证；被标 cannot-reproduce 则补 Procmon trace。**

## 手动装核 SOP（GUI 更新失败时的兜底）

1. 预检：无 `cli-proxy` 进程 + 18080 无监听（`netstat -ano | grep :18080`）。
2. 备份 `cpa-core/` 下 config.yaml + cpa-gui-meta.json + exe 到 `backup-pre-*` 目录。
3. 官方 release zip 覆盖 exe/config.example.yaml/LICENSE/README*（**zip 内无 config.yaml，用户配置不会被碰**）。
4. 重写 `cpa-gui-meta.json`（version/assetName/installedAtUnix 三字段）+ 同步 `core-version.txt`（GUI 版本状态双真源）。
5. 验证：`cli-proxy-api.exe --version` 自报版本 + 带 config 冒烟启动（`GET /`=200、`/v1/models`=401 即认证层正常）→ Stop-Process 停止。

## 排错工具箱

- **Restart Manager 探针**（PowerShell Add-Type 内联 RmStartSession/RmRegisterResources/RmGetList）比 handle.exe 原生精确，逐文件列占用 PID；脚本模式优于内联（bash 会吞 `$_`）。
- exe 版本串核验：`grep -ao "7\.2\.15[0-9]" cli-proxy-api.exe`。
- 上游资产核验走 `releases/expanded_assets/vX.Y.Z` 页面（API 匿名 403 时）；源码用 raw.githubusercontent.com 直拉 + `gh api search/code`（认证）定位函数文件。
- 09-06 教训（os error 1175 实测同款病灶再现）：GUI「句柄未释放」也会锁自身产物——09-09 清理 Temp 155 zip 时正被运行中 GUI（PID 1352）锁定删不掉，退出 GUI 后才能删。

## 关联

[[Skills and Tools Slimming and EasyCLIProxy Update Troubleshooting]]（同日：science-skills 五步评估→第 13 号雷达源收录 skill-plugin-resources.md + capability-inventory.json notWatched，predictingthepast 因 pickle.load 反序列化永久禁用）
