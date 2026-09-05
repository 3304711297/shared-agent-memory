---
name: codebuddy2openai-upstream-benchmark
description: 2026-09-05 codebuddy2openai 对标 EasyCLIProxyAPI v0.2.72 的可采纳清单（三档）与排除项，含本地缺陷发现
metadata:
  node_type: memory
  type: project
  originSessionId: sess_656a8367-2a67-4b01-be2c-f06bb80ecba5
---

2026-09-05 对标结论（用户要求：先不做其他 agent 适配，聚焦 UI 改进与代码精炼）：

**底子**：两仓非 fork 关系。本地 codebuddy2openai = Python converter(750行)+vanilla JS Tauri GUI(约4.8k行)；上游 EasyCLIProxyAPI = React19+TS(前端18.5k行)+Rust 管理 CPA 内核。用户上次对标重构 bd21c0e=09-04（上游 v0.2.71 时点），上游 09-05 新增仅 codex 目录编辑器（排除项）。上游浅克隆留存在 %TEMP%\easycliproxyapi 可作移植参考。

**第一档（尽快采纳，含本地实缺陷）**：①三个 render 函数 innerHTML 未转义（昵称/UID/模型名，XSS）；②端口/脱敏设置不持久化+托盘硬编码 8787/脱敏true 无视 UI 设置(lib.rs:180,189)；③无全局错误兜底(window.onerror/unhandledrejection)；④无单实例锁(上游 instance_lock.rs 命名互斥量模式)；⑤原生 confirm() 换自定义确认弹窗；⑥死代码清理(renderFallbackModels 6列旧版/重复min-width/--mono未定义/版本号 0.2.0 vs 0.1.0/agent_configure 双参数)。

**第二档（UI 感知）**：聚光灯引导(固定DOM id+getBoundingClientRect+视口clamp，推进门槛绑真实结果，EasyModePage.tsx 1203行)、明暗主题(prefers-color-scheme+原生窗口背景同步防闪烁)、响应式断点(上游24处@media，本地0处)、导航门禁(内核未运行锁页)、TTFT 首字时延探测(provider_health.rs 流式SSE判首个delta)、窗口尺寸记忆、日志轮转+打开日志目录。

**第三档（中型功能）**：本地用量统计(SQLite/JSONL+概览6卡+TPS=Σout/(Σlatency−ttft)+手写SVG趋势48小时桶)、轻量更新检查(release API+侧栏圆点，勿搬完整自更新器)、凭据/配置热监听+草稿脏标记保护(notify+500ms去抖)、模型双轨合一(GUI云端矩阵 vs Python静态DEFAULT_MODELS)。

**工程化**：拆 main.js(1047行,15处innerHTML,4个window全局)与 commands.rs(1165行,4处硬编码C:\Users\VOS-User残留)、测试(上游 *_at(root) 参数化模式+12测试文件，本地零测试)、CI 加 cargo test/pytest、requirements.txt 缺失、CSP null。

**明确排除**：agent 适配全套(codex/claude 目录、OAuth providers、agent 终端启动)、完整便携自更新器(staged updater+多源下载)、RESP 双模采集(依赖 CPA 管理API)、i18n(纯中文使用，暂无价值)。

相关：[[codebuddy2openai-tauri-gui]] [[gateway-migration-easycliproxyapi-and-browser-protection]]
