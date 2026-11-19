---
name: openrevo-build-and-upstream-contribution
description: OpenRevo 本地构建一条命令、pnpm/TTY 三处绕法，上游 PR #183 已合并与前后实测
metadata:
  type: project
---

# OpenRevo 本地构建与上游共建

**工程位置**：`D:\ai coding\open-revo`（上游 `faintonce/open-revo`，发布分支 `dev`；fork `3304711297/open-revo`）。本地仓库视为**只读构建副本**——不要在里面提交或改文件；要给上游做事另开克隆，改完把本地切回 `dev`、`origin` 指回原作者。

## 更新 + 构建（一条命令，PowerShell）

```powershell
cd "D:\ai coding\open-revo"; git pull --ff-only; pnpm install --frozen-lockfile --pm-on-fail=ignore; node node_modules/typescript/bin/tsc; node node_modules/vite/bin/vite.js build; node node_modules/@tauri-apps/cli/tauri.js build --no-bundle --config '{"build":{"beforeBuildCommand":""}}'
```

产物：`src-tauri\target\release\open-revo.exe`（单文件，**不生成安装包**；用户明确不要安装包）。

三处必要绕法：

1. `pnpm build` / `pnpm tauri build` 会被 `ERR_PNPM_BAD_PM_VERSION` 拦住（`package.json` 钉 `pnpm@10.32.1`，本机全局 12.x），所以前端直接用 node 跑 tsc/vite；`--pm-on-fail=ignore` 只对 `pnpm install` 有效，对环境变量无效。
2. `--config '{"build":{"beforeBuildCommand":""}}'` 清空内建 `pnpm.cmd build` 钩子（前端已单独构建）。PowerShell 里必须用单引号，已实测 JSON 不被吞。
3. tauri CLI 要求 stdin **和** stdout 都是 TTY——后台跑或把输出重定向到文件会以 `stdin is not a tty` / `stdout is not a tty` 直接 exit 1，且不打印其他信息。

## 上游贡献状态

- **Issue #182**（2026-11-13 提交）：release 构建 6m19s、仅改一个前端资源后重编 3m12s。根因是 `lto = true`（fat LTO）+ `codegen-units = 1` 把全程序优化压成单核，且 Tauri 在编译期把 `frontendDist` 嵌进主 crate，所以改前端也要重跑整包 LTO。附三档方案：改 release profile / 环境变量覆盖（零仓库改动）/ probe 探针退出默认构建。
- **PR #183**（2026-11-17 由 faintonce 合并进 `dev`）：`lto = "thin"` + `codegen-units = 16` + `incremental = true`；`opt-level = "z"`、`panic = "abort"`、`strip = true` 保持不变。
- 合并后实测（0.9.8，`dev@1320a09`，该版本还叠加了 173 个 Rust 文件的重构）：冷构建 **4m31s**（原 6m21s），exe **24.98 MiB**（原 22.81 MiB，+11.6%）。+11.6% 是 thin LTO/16 CGU 的既定代价，已在 PR 里交维护者权衡。
- 未做的可选项：Issue #182 的方案 C（4 个 `src/bin/*_probe.rs` 用 `required-features` 退出默认构建）与 `release.yml` 里两次全量编译（`--no-bundle` 那一步可省，`--bundles nsis` 本来就会产出同一个 exe）。

## 验证 exe 是否正常（不要只看体积）

`strip = true` 会抹掉版本字符串，所以判据是 hashed 资源名：`dist/assets/index-*.js` 的文件名能在 exe 里命中即正常嵌入；缺失说明是 dev 模式空壳（`ERR_CONNECTION_REFUSED`）。0.9.8 构建命中 `index-BIQAVADb.js` + `index-DPxCmVs7.css`，旧 hash 不再出现。

## 上游 PR 的低成本做法（本次验证过）

先实测基线（冷构建 / 改前端 / 改一行 Rust 三组，`CARGO_TARGET_DIR` 指到临时目录避免污染发布产物），再用环境变量 `CARGO_PROFILE_RELEASE_LTO=thin`、`_CODEGEN_UNITS=16`、`_INCREMENTAL=true` 测同一组对照，最后才动 `Cargo.toml`。这样 Issue 里有对照表、PR 里只有 3 行 diff，维护者能直接判断取舍。
