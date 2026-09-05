---
name: codebuddy2openai-upstream-benchmark
description: 2026-09-05 codebuddy2openai 对标 EasyCLIProxyAPI：三批采纳已全部落地推送（6 提交，CI
  全绿），含实现要点与遗留清单
metadata:
  node_type: memory
  type: project
  originSessionId: sess_656a8367-2a67-4b01-be2c-f06bb80ecba5
---

2026-09-05 对标 EasyCLIProxyAPI v0.2.72 并**三批全部落地**（6 提交，三次 CI 全绿，版本 0.2.0）：

**批次1（a75b68e 前端 + 040c441 Rust）**：①动态插值全量 esc()+事件委托修 XSS（inline onclick 改 data-act 委托，因 JS 上下文 HTML 转义防不住单引号逃逸）；②全局错误兜底 error/unhandledrejection+面板；③Promise 版 showConfirm 替代原生 confirm；④renderFallbackModels 仍被降级路径引用故改写成 4 列而非删除；⑤AppConfig 增 port/desensitize 持久化+托盘每次现读 settings.json；⑥tauri-plugin-single-instance 2.4.4（二次启动聚焦已有窗口）；⑦版本对齐 0.2.0（Cargo.lock 须随 CI --locked 提交）；⑧清理 C:\Users\VOS-User 残留（dirs::data_local_dir 兜底）。

**批次2（2e8e97e + 8926b3c）**：明暗双主题（head 内联防闪烁脚本+[data-theme=light] 仅覆盖变量+原生 setBackgroundColor 同步+日志控制台刻意保持黑底）；响应式断点 1080/820/700/560（≤700 侧栏 56px 仅图标）；proxy_test_chat 改流式 SSE 探 TTFT（reqwest stream feature+futures-util，行缓冲解析防 UTF-8 截断，max_tokens=100）；日志超 1MB 在 proxy_start 前与 proxy_stop 后轮转 .1（避免进程运行中 rename 失败）；open_logs_dir；窗口尺寸记忆独立 window.json（500ms 去抖+代数计数，不并入 AppConfig 免契约纠缠）。

**批次3（f39b25b + 3e13385）**：converter.py `--usage-log`（env CODEBUDDY2OPENAI_USAGE_LOG）逐请求 JSONL（ts/model/ok/tokens/latency/ttft/error，整体 try/except 不影响响应）；Rust usage_summary 聚合（>10MB 读尾部、UTC 整点 48 桶、today 按本地零点、TPS=Σout*1000/Σ(latency−ttft) 仅 ok+ttft 有效样本，#[cfg(test)] 单测 2 条）；check_app_update（GitHub releases/latest，直连失败回退 127.0.0.1:3067，版本比较手写分段）；前端第 8 Tab 用量统计页（5 卡+手写 SVG 柱状趋势 30s 静默刷新）+侧栏更新入口（update_available 圆点+shell.open，capabilities 已有 shell:allow-open）。

**教训**：子代理撞网关并发限制时可能「编辑已完成但无报告」——先 git diff 审计残骸再决定重做；后台长命令可能重复执行致冗余 push 报错，先核对 rev-parse 两端是否一致。

**遗留（未采纳，待拍板）**：main.js/commands.rs 拆文件模块化；测试扩面（converter pytest、CI 加 cargo test/pytest 步骤——现 CI 仍只 build+check）；auto_start_proxy 字段仍未接 UI；requirements.txt 仍缺；CSP 仍为 null。明确排除：agent 适配全套、完整自更新器、RESP 采集、i18n。

相关：[[codebuddy2openai-tauri-gui]] [[gateway-migration-easycliproxyapi-and-browser-protection]]
