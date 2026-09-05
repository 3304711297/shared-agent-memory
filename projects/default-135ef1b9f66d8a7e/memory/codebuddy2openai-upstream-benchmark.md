---
name: codebuddy2openai-upstream-benchmark
description: 2026-09-05 codebuddy2openai 对标 EasyCLIProxyAPI：四批全部落地推送（11 提交，CI 全绿含
  pytest/cargo test），遗留清零；批次4 由 Hermes 旁路验收通过后合流
metadata:
  node_type: memory
  type: project
  originSessionId: sess_656a8367-2a67-4b01-be2c-f06bb80ecba5
---

2026-09-05 对标 EasyCLIProxyAPI v0.2.72 并**四批全部落地推送**（11 提交，多次 CI 全绿，版本 0.2.0）：

**批次1（a75b68e 前端 + 040c441 Rust）**：①动态插值全量 esc()+事件委托修 XSS（inline onclick 改 data-act 委托，因 JS 上下文 HTML 转义防不住单引号逃逸）；②全局错误兜底 error/unhandledrejection+面板；③Promise 版 showConfirm 替代原生 confirm；④renderFallbackModels 仍被降级路径引用故改写成 4 列而非删除；⑤AppConfig 增 port/desensitize 持久化+托盘每次现读 settings.json；⑥tauri-plugin-single-instance 2.4.4（二次启动聚焦已有窗口）；⑦版本对齐 0.2.0（Cargo.lock 须随 CI --locked 提交）；⑧清理 C:\Users\VOS-User 残留（dirs::data_local_dir 兜底）。

**批次2（2e8e97e + 8926b3c）**：明暗双主题（[data-theme=light] 仅覆盖变量+原生 setBackgroundColor 同步+日志控制台刻意保持黑底）；响应式断点 1080/820/700/560（≤700 侧栏 56px 仅图标）；proxy_test_chat 改流式 SSE 探 TTFT（reqwest stream feature+futures-util，行缓冲解析防 UTF-8 截断，max_tokens=100）；日志超 1MB 在 proxy_start 前与 proxy_stop 后轮转 .1（避免进程运行中 rename 失败）；open_logs_dir；窗口尺寸记忆独立 window.json（500ms 去抖+代数计数，不并入 AppConfig 免契约纠缠）。

**批次3（f39b25b + 3e13385）**：converter.py `--usage-log`（env CODEBUDDY2OPENAI_USAGE_LOG）逐请求 JSONL（ts/model/ok/tokens/latency/ttft/error，整体 try/except 不影响响应）；Rust usage_summary 聚合（>10MB 读尾部、UTC 整点 48 桶、today 按本地零点、TPS=Σout*1000/Σ(latency−ttft) 仅 ok+ttft 有效样本，#[cfg(test)] 单测 2 条）；check_app_update（GitHub releases/latest，直连失败回退 127.0.0.1:3067，版本比较手写分段）；前端第 8 Tab 用量统计页（5 卡+手写 SVG 柱状趋势 30s 静默刷新）+侧栏更新入口（update_available 圆点+shell.open，capabilities 已有 shell:allow-open）。

**批次4（e7fddb7 + 3619d59 + ffa35ea + 97a6985 + 2041398，Hermes 验收通过后已推送，CI 全绿）**：
- auto_start_proxy 接 UI（e7fddb7）：设置页 chk-auto-start 开关接入 payload/get_app_settings，启动后 800ms 延迟自动拉起（state.running 守卫，proxy_start 本身幂等）。
- 4A 拆分（3619d59）：main.js 1540 行 → 14 个 ES modules（state 共享引用/tabs 单向依赖零循环/utils+error-handler 先行注册），代码本体零增删，npm build 17 modules 零警告+node --check 全过。
- 4B 拆分（ffa35ea）：commands.rs 1650 行 → commands/ 目录 7 文件（mod.rs pub use 再导出 **lib.rs 零改动**/shared/auth/billing/agents/proxy/update），usage_tests 2 条随聚合迁 proxy.rs。
- Hermes 3 路并行子代理全量验收通过（前端 build/后端 cargo check --locked -D warnings+单测 2/2/24 个 Tauri Command 与 generate_handler!+前端 invoke() 双射 100%），验收结论：window 四挂载与 logInterval 保留合理；「刷新积分」onclick 缺陷批准在 4C 顺手修。
- 4C（97a6985+2041398）：**CSP 启用**（script-src 'self'，主题脚本外置 public/theme-preset.js 免 hash 脆弱；style 需 'unsafe-inline'；ipc: http://ipc.localhost 必带；devCsp:null 保 HMR）；「刷新积分」inline onclick 缺陷修复（原引模块作用域函数必抛错，改 id 监听）；requirements.txt+requirements-dev.txt；tests/ pytest **24 用例**（converter 映射/Host 校验/用量写盘契约/透传白名单 + desensitize 角色过滤/不污染原对象；注意 _zero_width_split 是第 1 字符后插 ZWSP）；CI 增 Setup Python+pytest 与 cargo test 步骤（run 33972732991 四步全 success）。

**教训**：子代理撞网关并发限制时可能「编辑已完成但无报告」——先 git status/diff 审计残骸再决定重做（4B 即如此，被取消时文件已全部写完且一次通过编译）；后台长命令可能重复执行致冗余 push 报错，先核对 rev-parse 两端是否一致；并行派代理遵循并发上限≈2 按批排队；gh run watch/list 须加 --repo 3304711297/codebuddy2openai（否则解析到 HanHan666666 upstream 报 404），且 --limit 1 会混入 Dependabot run，认准 --workflow ci.yml。

**明确排除（不采纳）**：agent 适配全套（codex/claude 目录、OAuth providers、agent 终端）、完整便携自更新器、RESP 双模采集、i18n。

**遗留清零，无待办**。CSP 运行时效果已过 schema+构建+CI 验证，打包新 exe 后首启（主题无闪白、控制台无 CSP 报错）值得顺手看一眼。

相关：[[codebuddy2openai-tauri-gui]] [[gateway-migration-easycliproxyapi-and-browser-protection]] [[hermes-side-verification-handoff]]
