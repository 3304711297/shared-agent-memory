---
name: hermes-custom-provider-models
description: "模型不显示/缺新模型时必用。custom provider双真源写入要点。Use when custom provider models are missing or new models absent."
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Hermes custom provider 模型配置写入

## 双真源机制（写一处不够）

Hermes 消费 custom provider 模型清单有两条独立路径，必须都覆盖：

1. **config.yaml custom_providers[].models** — TUI/CLI（/model 切换器、model: 运行时）的真源。
2. **%LOCALAPPDATA%/hermes/provider_models_cache.json** — 桌面端模型下拉框的真源之一。键格式 `custom:{base_url小写去尾斜杠}#{fp}`；fp = blake2b("{api_key}|{api_mode}|{json.dumps(headers, sort_keys=True)}", digest_size=8) 的 hex。api_key="local"、无 headers/api_mode 时 fp 为常量 cbe4e4162cb98225。

桌面 picker 默认不做后台探测（for_picker=True 时 probe_custom_providers=False，仅当前选中项探测），缓存没有的模型就看不到——只写 config.yaml 不够。

## models 字段格式与覆盖语义

- 字典格式 model_id: {} 视为用户策展元数据，models_discovered: true 也不许 Hermes 自动覆盖（model_switch_providers.py _discovered_catalog_stale）；纯 id 列表格式才允许发现机制刷新。
- 外部写入方要更新清单，必须自己重写整个 models 映射（字典格式），并同步更新缓存文件。
- 列表项 auto 是合法路由别名保留；default 是 converter 兜底别名应剔除。

## 排障检查单（新模型不显示）

1. 反代 /v1/models 是否已返回该模型。
2. config.yaml 对应 provider 的 models: 是否含该模型。
3. provider_models_cache.json 是否有 custom:...#... 条目且 models 数组含该模型。
4. 仍不显示则让用户在桌面端执行一次「刷新模型」或重启桌面端。

## workbuddy2api 侧实现（126575d）

- 写入时用 local_client（显式 no_proxy，防 ALL_PROXY 劫持回环）GET http://127.0.0.1:{port}/v1/models，失败回退静态表保证离线可用。
- patch_hermes_config_content 的已有块替换条件 = 端口变化 OR 清单缺项（否则重跑写入无法补新模型）。
- Tauri command 要做网络拉取时用 pub async fn command（Tauri 2 原生支持），禁止在同步 command 里 block_on。

## 上下文窗口解析链与「家族通配」陷阱

解析优先级（agent/model_metadata.py::get_model_context_length）：config per-model `context_length` → context_length_cache.yaml → 端点 live /v1/models 的 context_length 字段 → 本地/Ollama 探测 → provider 元数据（models.dev / OpenRouter）→ **内置目录（DEFAULT_CONTEXT_LENGTHS）最长子串匹配** → 256K 静默兜底。

- 端点不报窗口字段时，兜底靠「名字里含哪个家族关键词」猜：deepseek→128K、kimi→262144、glm→202752、qwen→131072、grok→131072、minimax→204800…；不含任何已知关键词 → 256,000 默认兜底。
- 猜中家族值不一定错，但新模型会静默错：实测 `deepseek-v4.1-flash` 解析 128,000（真实 1M）；未来 `deepseek-v5-*` 同样吃 128K。判定来源：抓日志 `catalog match on '<key>'` / `defaulting to 256,000`（logging handler 挂 agent.model_metadata 的 logger 即可捕获）。
- 修复 A（Hermes 侧，逐模型显式声明）：`providers.<id>.models.<model>: {context_length: N}` — step 0c 覆盖；字典格式条目不会被模型发现机制自动覆盖。
- 修复 B（端点侧，根治）：让 /v1/models 每项带顶层 `context_length`（或 `max_input_tokens`，1024≤值≤10,000,000 才被采纳）。实测假端点带该字段时，含全新模型名也精确命中，目录不再参与。
- 修复 B 已在 workbuddy2api 反代落地（commit 9da98a2）：`list_models` 为每条注入顶层 `context_length`＝控制台手改值（model_settings.json 的 `context_window`）> 上游 maxInputTokens；别名行（MODEL_MAP 中映射到其他正式名的键，如 hy3/hy4/kimi-k3）已从列表剔除（只报正式名，避免同一模型多行），但作为请求侧模型名仍可用（chat 路径仍按 MODEL_MAP 映射）；改源码后需重启反代进程生效；控制台改值对新开 Hermes 会话即时生效；config.yaml per-model 覆盖会压过端点值——要跟随控制台就别写覆盖。

## 相关坑

- 仓库 core.autocrlf=true：python/外部脚本改 .rs 文件时必须 newline="" + 显式统一 LF 写回；混入 CRLF 会让 rustc raw string 字面量带 \r，测试断言大面积假失败（文件本源是 LF）。
- patch 工具替换含转义序列（\r\n 等）的代码行时，转义符可能被变成真实控制字符，替换后必须 read_file 回读确认。