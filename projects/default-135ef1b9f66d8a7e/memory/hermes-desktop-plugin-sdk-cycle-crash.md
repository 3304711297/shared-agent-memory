---
name: hermes-desktop-plugin-sdk-cycle-crash
description: Hermes Desktop v0.21.1 全部 disk/runtime 插件加载失败的根因（#107212 引入模块环致 SDK GLOBALS 先于命名空间求值）与本地修复 SOP + 上游状态
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

**How to apply:** ① 判据：日志出现 `runtime load failed` + `Cannot convert undefined or null to object` + `sdk-*.js:5`，且多个插件同偏移，即可判定为宿主层回归，不必排查插件自身；② 修复方向必须是**惰性读取**——`apps/desktop/src/sdk/runtime.ts` 的 `GLOBALS` 改惰性 getter（或 call-time 解析函数，等价）；**仅给 `Object.keys` 加 null 守卫不够**：`globalThis.__HERMES_PLUGIN_SDK__` 仍会是 undefined，shim 退化成 `{}`，把失败推到插件的 import 链接期并丢失全部命名导出；③ 改源码后 `vite build` 重建，然后把 `apps/desktop/dist/` 同步到打包版实际加载路径 `release/win-unpacked/resources/app.asar.unpacked/dist/`（**不是** `apps/desktop/dist/`），并刷新 `$HERMES_HOME/desktop-build-stamp.json`（其 `contentHash` = 源码树 SHA-256，跳过 dist/），否则启动器会判定 stale 并重建覆盖补丁；④ 验证：重启后该启动块零 `[plugins] runtime load failed` 行即为通过（成功路径不打日志）。⑤ **与 `hermes update` 的交互（关键）**：桌面更新器调用 `hermes update --keep-stash`——本地源码改动会被 stash 且**不自动恢复**，更新后按新源码重建 bundle。因此上游修复未合并前，每次更新都会：stash 掉补丁 → 重建出坏 bundle → 插件再次全挂；恢复步骤 = `git stash pop`（取回 runtime.ts）→ `vite build` → 同步 `app.asar.unpacked/dist/` → 刷 build-stamp → 重启。上游 #107303（惰性读）/ #107301（破环）任一合并后即无需再补，stash 可弃。

**备查**：备份位于 `$HERMES_HOME/backups/sdk-cycle-fix-20260911/`（`runtime.ts.bak-20260911-011040` 原版 + `runtime.ts.PATCHED` 补丁版）；补丁后 chunk 名由 `sdk-RKHbz2ri.js` 变为 `sdk-0_CXTI5X.js`。
