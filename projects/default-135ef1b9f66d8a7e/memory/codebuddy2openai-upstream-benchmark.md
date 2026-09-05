---
name: codebuddy2openai-upstream-benchmark
description: 2026-09-05 codebuddy2openai 对标 EasyCLIProxyAPI：三批采纳已推送（6 提交 CI
  全绿）；批次4 遗留处理中——自动拉起+双端拆分已本地提交待 Hermes 验收，4C 压后
metadata:
  node_type: memory
  type: project
  originSessionId: sess_656a8367-2a67-4b01-be2c-f06bb80ecba5
---

2026-09-05 对标 EasyCLIProxyAPI v0.2.72 并**三批全部落地推送**（6 提交，三次 CI 全绿，版本 0.2.0）：

**批次1（a75b68e 前端 + 040c441 Rust）**：①动态插值全量 esc()+事件委托修 XSS（inline onclick 改 data-act 委托，因 JS 上下文 HTML 转义防不住单引号逃逸）；②全局错误兜底 error/unhandledrejection+面板；③Promise 版 showConfirm 替代原生 confirm；④renderFallbackModels 仍被降级路径引用故改写成 4 列而非删除；⑤AppConfig 增 port/desensitize 持久化+托盘每次现读 settings.json；⑥tauri-plugin-single-instance 2.4.4（二次启动聚焦已有窗口）；⑦版本对齐 0.2.0（Cargo.lock 须随 CI --locked 提交）；⑧清理 C:\Users\VOS-User 残留（dirs::data_local_dir 兜底）。

**批次2（2e8e97e + 8926b3c）**：明暗双主题（head 内联防闪烁脚本+[data-theme=light] 仅覆盖变量+原生 setBackgroundColor 同步+日志控制台刻意保持黑底）；响应式断点 1080/820/700/560（≤700 侧栏 56px 仅图标）；proxy_test_chat 改流式 SSE 探 TTFT（reqwest stream feature+futures-util，行缓冲解析防 UTF-8 截断，max_tokens=100）；日志超 1MB 在 proxy_start 前与 proxy_stop 后轮转 .1（避免进程运行中 rename 失败）；open_logs_dir；窗口尺寸记忆独立 window.json（500ms 去抖+代数计数，不并入 AppConfig 免契约纠缠）。

**批次3（f39b25b + 3e13385）**：converter.py `--usage-log`（env CODEBUDDY2OPENAI_USAGE_LOG）逐请求 JSONL（ts/model/ok/tokens/latency/ttft/error，整体 try/except 不影响响应）；Rust usage_summary 聚合（>10MB 读尾部、UTC 整点 48 桶、today 按本地零点、TPS=Σout*1000/Σ(latency−ttft) 仅 ok+ttft 有效样本，#[cfg(test)] 单测 2 条）；check_app_update（GitHub releases/latest，直连失败回退 127.0.0.1:3067，版本比较手写分段）；前端第 8 Tab 用量统计页（5 卡+手写 SVG 柱状趋势 30s 静默刷新）+侧栏更新入口（update_available 圆点+shell.open，capabilities 已有 shell:allow-open）。

**批次4（用户拍板「遗留的也处理了」，进行中）**：
- auto_start_proxy 已接 UI（e7fddb7 本地）：设置页 chk-auto-start 开关接入 payload/get_app_settings，启动后 800ms 延迟自动拉起（state.running 守卫，proxy_start 本身幂等）。
- 4A 拆分（3619d59 本地）：main.js 1540 行 → 14 个 ES modules（state/utils/error-handler/tabs/service/accounts/agents/oauth/models/settings/logs/usage/update-check+入口 71 行），代码本体零增删，npm build 17 modules 零警告+node --check 全过，无循环依赖。
- 4B 拆分（ffa35ea 本地）：commands.rs 1650 行 → commands/ 目录 7 文件（mod.rs pub use 再导出 **lib.rs 零改动**/shared/auth/billing/agents/proxy/update），usage_tests 2 条随聚合迁 proxy.rs，cargo check 零警告。
- **两个拆分提交未推送，等 Hermes 旁路验收后再推**（流程见 [[hermes-side-verification-handoff]]）；树已冻结，4C（CSP 加固+CI 加 cargo test/pytest+requirements.txt+pytest 用例）刻意压后待验收。
- Hermes 审查重点三决策：①window.switchAccount/deleteAccount/saveModelConfig/openModelEdit 四处全局挂载保留；②main.js 动态 HTML「刷新积分」onclick="loadAccountsData()" 是原有缺陷（模块作用域函数 window 无此名，点击抛错走全局兜底）按机械拆分原则逐字节保留未修；③logs.js 保留未使用的 let logInterval。

**教训**：子代理撞网关并发限制时可能「编辑已完成但无报告」——先 git status/diff 审计残骸再决定重做（4B 即如此）；后台长命令可能重复执行致冗余 push 报错，先核对 rev-parse 两端是否一致；并行派代理遵循并发上限≈2 按批排队。

**明确排除（不采纳）**：agent 适配全套（codex/claude 目录、OAuth providers、agent 终端）、完整便携自更新器、RESP 双模采集、i18n。

相关：[[codebuddy2openai-tauri-gui]] [[gateway-migration-easycliproxyapi-and-browser-protection]]
