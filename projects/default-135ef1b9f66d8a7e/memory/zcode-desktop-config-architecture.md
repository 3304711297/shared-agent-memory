---
name: zcode-desktop-config-architecture
description: ZCode Desktop/CLI 双体系配置架构实测：v2 provider family OAuth
  为现行模型选择，config.json provider map 为旧体系不读，Desktop 自定义供应商只认 UI 内添加
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_91c8484d-0d81-48d1-89e3-b7d52ed11653
---

2026-09-05 为排查 c2o（codebuddy2openai）接入 ZCode 后模型不显示，实测得出的 ZCode 配置体系结构（ZCode Desktop = Electron 应用，exe 在 `D:\zcode\ZCode.exe`，本体闭源，zai-org 下仅有 zcode-plugins 插件市场与 feedback 反馈仓）：

**~/.zcode/cli/config.json（旧体系）**
- 顶层 `provider` map：每条含 `apiFormat`/`defaultKind`/`kind`/`models{name:{limit.context}}`/`name`/`options{apiKey,baseURL}`/`source:"custom"`；另有 `model.main` 字段。
- **现行模型选择已不读它**（实测：`model.main` 写 `cpa-gui/gemini-3.8-flash`，但 CLI 会话实际用 `builtin:bigmodel-start-plan/GLM-5.3-Flash`）。

**~/.zcode/v2/（Desktop v2 体系，现行）**
- `config.json`：provider map（条目多 `"npm": "@ai-sdk/openai-compatible"` 字段），含 `builtin:bigmodel*`/`builtin:zai*` 家族与 custom 条目。
- `setting.json`：**Desktop 应用设置真源**——`enabledBuiltinAgentCliProviders`、`modelProviderFamilyModes`（如 bigmodel:oauth）、`modelProviderFamilySelectedKeys`（如 coding-plan:builtin:bigmodel-start-plan）= **现行生效的模型选择**（OAuth 套餐直连智谱，不经 18080 网关；18080/8787 均未监听时会话仍可用即为佐证）。
- `model-provider-display-order.json`：显示顺序；`coding-plan-cache.json`/`credentials.json` 等同级。

**%APPDATA%/ZCode（Desktop userData）**
- `session/`（Cache/Local Storage/IndexedDB 等）：Desktop「模型设置」页的**自定义供应商列表存内部 leveldb**（UTF-16LE + snappy 压缩），**只认 UI 内添加，直接写 JSON 配置文件无效**；明文 grep 不可行（已用已知词 bigmodel 验证）。要程序化感知只能探测服务端口连通性。
- `~/.zcode/config/` 仅剩 gemini.json；`%APPDATA%/zcode-antigravity-control-center` 是已删 fork 配套控制中心的 Electron 数据（与 ZCode Desktop 无关）。

**How to apply:** 给 ZCode 做自动配置（provider/模型注入）前先认清现行体系是 v2 provider family；写 cli/config.json 的 provider map 对 Desktop 模型选择无效；自定义供应商只能引导用户在 Desktop「模型设置 → 添加供应商」UI 内添加（Chat Completions 格式对应 OpenAI 兼容服务）；判断服务可用性用端口探测而非文件检查。关联 [[codebuddy2openai-tauri-gui]]（c2o 接入根因与引导式改造）、[[gateway-migration-easycliproxyapi-and-browser-protection]]。
