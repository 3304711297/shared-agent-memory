---
name: hermes-custom-provider-models
description: "Use when custom provider 模型不显示或缺新模型。双真源写入要点。"
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

## codebuddy2openai 侧实现（126575d）

- 写入时用 local_client（显式 no_proxy，防 ALL_PROXY 劫持回环）GET http://127.0.0.1:{port}/v1/models，失败回退静态表保证离线可用。
- patch_hermes_config_content 的已有块替换条件 = 端口变化 OR 清单缺项（否则重跑写入无法补新模型）。
- Tauri command 要做网络拉取时用 pub async fn command（Tauri 2 原生支持），禁止在同步 command 里 block_on。

## 相关坑

- 仓库 core.autocrlf=true：python/外部脚本改 .rs 文件时必须 newline="" + 显式统一 LF 写回；混入 CRLF 会让 rustc raw string 字面量带 \r，测试断言大面积假失败（文件本源是 LF）。
- patch 工具替换含转义序列（\r\n 等）的代码行时，转义符可能被变成真实控制字符，替换后必须 read_file 回读确认。