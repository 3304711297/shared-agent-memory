---
name: openrevo-build-and-upstream-contribution
description: OpenRevo 更新与构建（必须显式拉 dev）、pnpm 版本协商实情、上游 PR #183 已合并
metadata:
  type: project
---

# OpenRevo 本地构建与上游共建

**工程位置**：`D:\ai coding\open-revo`（上游 `faintonce/open-revo`，fork `3304711297/open-revo`）。本地仓库视为**只读构建副本**——不要在里面提交或改文件；要给上游做事另开克隆。

**分支口径（用户明确要求）**：上游默认分支是 `main`，但本项目开发在 **`dev`**。更新必须显式拉 dev，不能靠默认分支。

## 更新 + 构建（一条命令，PowerShell）

```powershell
cd "D:\ai coding\open-revo"; git pull --ff-only origin dev; pnpm install; pnpm tauri build --no-bundle
```

产物：`src-tauri\target\release\open-revo.exe`（单文件，**不生成安装包**；用户明确不要安装包）。

## ⚠️ pnpm 固定版本的真相（2026-11-19 实测纠正）

`package.json` 里 `"packageManager": "pnpm@10.32.1+sha512..."` **不是**报错原因，也**不需要**改成不固定。

- corepack 作为 pnpm 启动器时会读这个字段并**自动切到 10.32.1**：干净环境实测 `pnpm install` 输出 `Done in 19.7s using pnpm v10.32.1`，随后 `pnpm build`、`pnpm tauri build --no-bundle` 全部正常。本机全局虽是 pnpm 12.x，走 corepack 时由它协商，不冲突。
- `ERR_PNPM_BAD_PM_VERSION` 只在 **`export COREPACK_ENABLE_PROJECT_SPEC=0`** 时出现：该变量让 corepack 不再按项目切版本，于是 pnpm 12 直接运行、又因处于 corepack 下而拒绝自我切换，才硬报错。**永远不要设这个变量**——它曾被误当成"绕过版本检查"的手段，实际是制造错误的根源。
- 另一真实但瞬时的坑：corepack 首次下载 10.32.1 可能因 IPv6 路由失败（`UND_ERR_CONNECT_TIMEOUT`，连 `2606:4700::...`），重试或 `NODE_OPTIONS=--dns-result-order=ipv4first` 即可。属网络问题，不是仓库问题，不值得向上游提 issue。
- `pnpm install` 有时会提示“modules directory 将被删除重装，Proceed? (Y/n)”——这是 `.npmrc` 的 `node-linker=hoisted` 与现存 `node_modules` 布局不一致时的正常重建，默认 Y 就用 store 秒级重建完，不是错误。

## 仍然成立的坑：tauri CLI 要求 TTY

`tauri build`（v2.11.4）要求 **stdin 和 stdout 都是终端**：后台运行或以 `> log 2>&1` 重定向，会以 `stdin is not a tty` / `stdout is not a tty` 立即 exit 1，且不打印其他信息。真实终端里手敲没问题；自动化则用 pty 且**不要重定向**。

## 上游贡献状态

- **Issue #182**（2026-11-13 提交）：release 构建 6m19s、仅改一个前端资源后重编 3m12s。根因是 `lto = true`（fat LTO）+ `codegen-units = 1` 把全程序优化压成单核，且 Tauri 在编译期把 `frontendDist` 嵌进主 crate，所以改前端也要重跑整包 LTO。附三档方案：改 release profile / 环境变量覆盖（零仓库改动）/ probe 探针退出默认构建。
- **PR #183**（2026-11-17 由 faintonce 合并进 `dev`）：`lto = "thin"` + `codegen-units = 16` + `incremental = true`；`opt-level = "z"`、`panic = "abort"`、`strip = true` 保持不变。
- 合并后实测（0.9.8，`dev@1320a09`，该版本还叠加了 173 个 Rust 文件的重构）：冷构建 **4m31s**（原 6m21s），exe **24.98 MiB**（原 22.81 MiB，+11.6%）。+11.6% 是 thin LTO/16 CGU 的既定代价，已在 PR 里交维护者权衡。
- 未做的可选项：Issue #182 的方案 C（4 个 `src/bin/*_probe.rs` 用 `required-features` 退出默认构建）与 `release.yml` 里两次全量编译（`--no-bundle` 那一步可省，`--bundles nsis` 本来就会产出同一个 exe）。
- **Issue #197 / #198**（2026-11-19 提交，OPEN）：把上面两条拆成独立 issue 并附实测——#197 是 `release.yml` 两次 `tauri build`，实测第二步 `--bundles nsis` 仍会重编 app crate 并重链接 53.9s（`--bundles` 改变构建指纹，Tauri 打 bundle type 标记），建议合并为一次；#198 是 4 个探针 bin 每次都参与链接（日志末尾 804-807 单元），建议加 `required-features = ["probes"]`。两条都只提 issue 未提 PR，等维护者表态。

## 验证 exe 是否正常（不要只看体积）

`strip = true` 会抹掉版本字符串，所以判据是 hashed 资源名：`dist/assets/index-*.js` 的文件名能在 exe 里命中即正常嵌入；缺失说明是 dev 模式空壳（`ERR_CONNECTION_REFUSED`）。0.9.8 构建命中 `index-BIQAVADb.js` + `index-DPxCmVs7.css`，旧 hash 不再出现。

## 上游 PR 的低成本做法（本次验证过）

先实测基线（冷构建 / 改前端 / 改一行 Rust 三组，`CARGO_TARGET_DIR` 指到临时目录避免污染发布产物），再用环境变量 `CARGO_PROFILE_RELEASE_LTO=thin`、`_CODEGEN_UNITS=16`、`_INCREMENTAL=true` 测同一组对照，最后才动 `Cargo.toml`。这样 Issue 里有对照表、PR 里只有 3 行 diff，维护者能直接判断取舍。

**教训**：给上游提 issue 前，必须先把"复现步骤"在干净环境里走一遍——本次差点就"`packageManager` 固定版本导致报错"提了一个假前提的 PR，实际是我自己导出的 `COREPACK_ENABLE_PROJECT_SPEC=0` 造成的。
