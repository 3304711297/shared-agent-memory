---
name: hermes-desktop-plugin-sdk-cycle-crash
description: Hermes Desktop v0.21.1 全部 disk/runtime 插件加载失败的根因（#107212 引入模块环致 SDK GLOBALS 先于命名空间求值）与本地修复 SOP + 上游修复已合并状态
metadata:
  type: feedback
---

**Hermes Desktop「所有本地插件失效」的根因链与修复 SOP**（2026-09-10/11 实战闭环。上游权威单 NousResearch/hermes-agent#107288，另有 5 个同因单被打 duplicate 标；已向 #107288 贡献 Windows 打包产物端到端验证，comment 5622594245）。

**症状**：更新后（v0.21.1，桌面 0.17.2）状态栏插件全部消失，日志每个 disk 插件一条：

```
[plugins] runtime load failed (<plugin>) TypeError: Cannot convert undefined or null to object (…/assets/sdk-<hash>.js:5)
```

**Why:** 上游 PR #107212（`61afcde8f9`，合并 2026-09-10T09:30:50Z，Capabilities→Plugins 单页重构）把 `plugins-settings.tsx` 移到 `app/skills/` 下，而 `sdk/index.ts` 已 re-export `SkillsView`，于是闭合出一条此前不存在的模块环：

```
sdk/index.ts → app/skills/index.tsx → app/skills/plugins-tab.tsx
  → app/skills/desktop-plugins-section.tsx → contrib/runtime-loader.ts
  → sdk/runtime.ts → sdk/index.ts
```

rolldown 在环上产出的 sdk chunk 里 `GLOBALS` 对象字面量（本机 offset 156995）早于命名空间赋值（offset 231551）被求值——`var` 只会提升不会预赋值，字面量按值捕获 `undefined`，`shimUrl()` 的 `Object.keys(undefined)` 即抛该 TypeError，且发生在插件源码被读取之前，**插件内容完全无关**（零 import 插件同样复现）。旁证：不同机器 chunk 哈希各异（`sdk-RKHbz2ri.js` / `sdk-B6X_oHhs.js` / `sdk-_WH0yJst.js`）但失败形状完全一致。另注意此构建同时移除了旧 Settings→Plugins 页，用户观感是「功能被删」而非崩溃，易被误报。

**How to apply:** ① 判据：日志出现 `runtime load failed` + `Cannot convert undefined or null to object` + `sdk-*.js:5`，且多个插件同偏移，即可判定为宿主层回归，不必排查插件自身；② 修复方向必须是**惰性读取**——`apps/desktop/src/sdk/runtime.ts` 的 `GLOBALS` 改惰性 getter（或 call-time 解析函数，等价）；**仅给 `Object.keys` 加 null 守卫不够**：`globalThis.__HERMES_PLUGIN_SDK__` 仍会是 undefined，shim 退化成 `{}`，把失败推到插件的 import 链接期并丢失全部命名导出；③ 改源码后 `vite build` 重建，然后把 `apps/desktop/dist/` 同步到打包版实际加载路径 `release/win-unpacked/resources/app.asar.unpacked/dist/`（**不是** `apps/desktop/dist/`），并刷新 `$HERMES_HOME/desktop-build-stamp.json`（其 `contentHash` = 源码树 SHA-256，跳过 dist/），否则启动器会判定 stale 并重建覆盖补丁；④ 验证：重启后该启动块零 `[plugins] runtime load failed` 行即为通过（成功路径不打日志）。⑤ **与 `hermes update` 的交互（关键）**：桌面更新器调用 `hermes update --keep-stash`——本地源码改动会被 stash 且**不自动恢复**，更新后按新源码重建 bundle。上游修复合并前，每次更新都会：stash 掉补丁 → 重建出坏 bundle → 插件再次全挂；当时的恢复步骤 = `git stash pop`（取回 runtime.ts）→ `vite build` → 同步 `app.asar.unpacked/dist/` → 刷 build-stamp → 重启。

**上游收口状态（2026-09-11 已落地本机）**：修复**已合并并已装机**——PR **#107303**（`fix(desktop): resolve plugin SDK namespaces lazily so disk plugins load in production builds`）由 owner Teknium 于 2026-09-10T22:35:32Z 合入 main，merge commit `6c3d4a4`；实现为 `pluginNamespaces()` 函数（把对象字面量移入函数体，调用点 `installPluginSdk()` / `shimUrl` 改为 call-time 解析），与本文 getter 方案同源同效但更彻底（连带修掉类型签名 `type PluginGlobalKey = keyof ReturnType<typeof pluginNamespaces>`）。同批竞争 PR：`#107301`（破环）仍 OPEN 未被采纳，`#107309`（空守卫，本文判定为错误修法）已 CLOSED 未合并。注意 `gh pr view` 返回的 `merged: true` 是可信的，但**不要用 `compare/<sha>...main` 的方向判断是否包含**——`ahead_by: N` 表示 main 从该 commit 往前走了 N 步（即 main 已包含它），读反会得出"未合并"的错误结论；权威判据是 `gh api "repos/.../commits?path=<file>&sha=main"` 能否命中，或 `git merge-base --is-ancestor <sha> HEAD`。

**升级流程的逆向判据（2026-09-11 已执行完毕）**：修复合并前，`hermes update` 后要 `git stash pop` **恢复**本地补丁；修复随 main 下发后，改为**丢弃**本地补丁——本次即以 `git stash drop` 收口（丢弃前用 sha256 三方比对 stash 内容与备份，确认一致）。判别当前属于哪一阶段：`hermes --version` 的版本号是否 > 0.21.1，或本地 HEAD 是否已包含 `6c3d4a4`。

**桌面更新器行为（源码实证，`scripts/desktop-update/windows.ps1`）**：更新器恒传 `--keep-stash`（本地改动只进 stash、不自动恢复）；`hermes update` 自身包含 desktop 构建阶段，**条件性重建**仅在其输出含 `Desktop build failed` 时触发（`hermes desktop --force-build --build-only`）；退出码语义：4=桌面未在 30s 内退出（零改动）、5=venv 被占用（零改动）、6=代码已更新但 desktop 重建失败（仍在跑旧 exe，需手动 `hermes desktop --force-build`）。**产物路径判据**：打包版实际加载 `release/win-unpacked/resources/app.asar.unpacked/dist/`，与 `apps/desktop/dist/` 需同哈希；`bundle-skew.ts` 每次启动以 `install-stamp.json` 的 commit 做 `merge-base --is-ancestor` + `rev-list --count <stamp>..HEAD -- <RUNTIME_PATHS>`（含 `apps/desktop/src`）判定渲染器是否落后源码树。**验证实操**：新 chunk 里 `pluginNamespaces` 会被压缩改名（如 `Sg()`），**按函数名 grep 计数为 0 属正常**——应转为验证 `function Sg(){return{__HERMES_PLUGIN_SDK__:...}}` 形态：对象字面量位于函数体内、调用点写 `Sg()[key]`，且该形态不再依赖模块求值顺序。更新后实测通过：chunk `sdk-0_CXTI5X.js` → `sdk-BL3iH9EP.js`（247592B，dist 与 packed 同 sha256 `717865f4…`），stamp commit `073c5787` → `05d705dd`、`dirty:false`，日志零新增 `runtime load failed`（更新后启动块干净，历史 16 条最晚为 09-10T16:36Z），插件后端路由 `/api/plugins/token-stats/quota` 与 `/api/plugins/config-guard/result` 均返回 401（= 路由已注册、要求鉴权，非 404；401 出现正说明未崩）。

**备查**：备份位于 `$HERMES_HOME/backups/sdk-cycle-fix-20260911/`（`runtime.ts.bak-20260911-011040` 原版 + `runtime.ts.PATCHED` 补丁版）；更新前完整快照在 `$HERMES_HOME/backups/sdk-cycle-fix-20260911-preupdate/`（补丁版 runtime.ts、新旧 chunk、双 stamp、packed dist 全清单 408 项、基线 JSON、插件日志基线）。补丁后 chunk 名由 `sdk-RKHbz2ri.js` 变为 `sdk-0_CXTI5X.js`，上游修复装机后为 `sdk-BL3iH9EP.js`。**本机状态（2026-09-11 13:13 更新后）：工作树干净、stash 已清空、本地补丁已退役，不再需要任何手工维护步骤。**
