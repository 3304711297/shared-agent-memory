---
name: workbuddy2api-rebrand-and-dual-source
description: 2026-09-11 codebuddy2openai 全面升级为 workbuddy2api：原生双协议、双端模型并发聚合接入 gpt-6-astra、排序与标签筛选
metadata:
  tags: [workbuddy2api, codebuddy, proxy, tauri, tencent, gpt-6-astra, models]
---

# WorkBuddy2API 品牌升级与核心能力演进

## 1. 仓库与工作区重命名 (2026-09-11)
- **GitHub 远端**：`3304711297/codebuddy2openai` 重命名为 `3304711297/workbuddy2api`。
- **本地工作区**：由 `D:\ai coding\GitRepos\codebuddy2openai` 重命名为 `D:\ai coding\GitRepos\workbuddy2api`。
- **本地应用数据与凭据存储**：迁移至 `%LOCALAPPDATA%\workbuddy2api`，并内建向前兼容迁移机制（优先读取 `workbuddy2api`，自动读取/迁移历史 `codebuddy2openai` 凭据和用量日志）。
- **桌面快捷方式**：生成 `WorkBuddy2API.lnk` 指向 `src-tauri\target\release\workbuddy2api.exe`。

## 2. 原生双协议支持
- **OpenAI 兼容协议**：`POST /v1/chat/completions`、`GET /v1/models`。
- **Anthropic Messages 兼容协议**：原生支持 `POST /v1/messages`，终端直接配置 `ANTHROPIC_BASE_URL="http://127.0.0.1:8787"` 即可直连官方 Claude Code CLI，双向透明转换并完整支持流式与 tool_calls。

## 3. 国内 CodeBuddy + 国际 WorkBuddy 双源模型并发聚合
- **背景**：腾讯国内端点（`copilot.tencent.com/v2/enterprises/personal/models`）仅下发国产模型，缺少海外前沿模型。同一订阅凭据在海外端点（`codebuddy.ai/v3/config`）下完全有效。
- **并发拉取机制**：
  - Python 内核与 Rust 桌面后端分别通过 `asyncio.gather` 与 `futures_util::join!` 并发请求两端；
  - 自动注入 WorkBuddy 客户端特征，两端模型去重合并（合计 44+ 模型）；
  - 全面接入 `gpt-6-astra`（倍率 6.67x，1M 上下文窗口，思考档位全量支持 `low` ~ `max`，可关闭思考）以及 GPT-5.6 系列；
  - 模型打上来源标签：`双端`、`WorkBuddy`、`CodeBuddy`。

## 4. 模型表格交互增强
- **计费倍率排序**：点击「计费倍率」表头，第 1 次按倍率从大到小排序（如 6.67x → 0.00x），第 2 次从小到大排序，第 3 次恢复默认顺序。
- **模型首字母排序**：点击「模型」表头，支持 A → Z 升序与 Z → A 降序切换。
- **内部标签清理**：移除腾讯 IDE 内部无实际分类意义的 `craft` 标签。
- **标签筛选**：点击「标签」表头唤起分类菜单（全部、双端、WorkBuddy、CodeBuddy 等），支持即时筛选与一键清空；表格行内标签徽章支持点击快速筛选。
