---
name: tuba-toolbox-ai-empty-model-400
description: 图吧工具箱 AI 服务（TubaWinUi3）指向本地反代报 400 /「连接失败」= 自定义提供商的模型列表为空，测试连接拿空模型名发出请求
metadata:
  node_type: memory
  type: feedback
---

2026-09-18，用户报告「图吧工具箱的 AI 服务配置 400 报错」。

**根因**：客户端侧**自定义提供商的模型列表为空**（`models: []`、`defaultModel: ""`），其「测试连接」按钮直接向 `<baseUrl>/chat/completions` 发 `model: ""` 的探测请求；反代把空模型名原样透传上游，上游返回 HTTP 400 `11102 model [] service info not found`（= 找不到名为空串的模型），客户端因此显示「连接失败」。地址、密钥、网络全部无关。

**证据链（复现手法，下次照做）**：
- 客户端配置在 `%LOCALAPPDATA%\TubaWinUi3\ai_providers.json`（providers 数组：baseUrl / apiKey / models / defaultModel 全在里面），同目录另有 `settings.json`。
- 反代侧看 `%LOCALAPPDATA%\workbuddy2api\converter.log`：`▶ REQUEST  | stream=False | msgs=2` → `✗ HTTP 400 |  | model [] service info not found`。**同一 rid 下出现多个不同上游 requestId = 反代内部账号重试**，不是用户点了多次。
- 直接复现：`model:""` → 400 同报文；`model:"auto"` / `"deepseek-v4.1-flash"` → 200。反代 `/v1/models` 正常 200。

**通用规则**：
- 客户端「连接失败」≠ 网络/密钥问题，先确认**探测请求实际发出的 body**（模型名是否为空）——空模型名必被上游判为不存在。
- baseUrl 填对只是第一步：**必须从反代 `/v1/models` 抄真实模型 id 填进客户端的模型列表并设为默认模型**，测试连接才会过。
- 上游只认自家模型名：教程常见的 `deepseek-chat` / `claude-sonnet-4-5` / `gpt-3.5-turbo` 实测一律 400 `11102`；`gpt-4o` 能通是内置降级映射的个例，不可当范例。

**处置**：客户端侧添加模型（如 `auto` 或 `deepseek-v4.1-flash`）并设为默认，重测即通；反代侧无需改动。
