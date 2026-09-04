---
name: hermes-skills-and-mcp-optimization-2026-09-03
description: 2026-09-03 Hermes 技能库深度清理重构、41 项开源核心技能安装与 MCP 健康状态全景记录
metadata:
  node_type: memory
  type: project
---

# Hermes 技能库与 MCP 生态深度重构优化 (2026-09-03)

2026-09-03 对 Hermes Agent 的技能库（Skills）与模型上下文协议（MCP）进行了全方位的深度体检、去重、安装与配置对齐：

## 1. 技能库清理与冗余收敛 (70 个独立技能)
- **清理 14 个深层嵌套**：修复了从 ZCode 迁移时产生的 `superpowers/<skill>/<skill>/` 递归子目录副本。
- **消除跨分类重名冲突**：清理了 `software-development/` 下与 `superpowers/` 重复的 `requesting-code-review`、`systematic-debugging`、`test-driven-development`。
- **结果**：全量技能实现 0 重名冲突，结构清晰健壮。

## 2. 批量安装 41 项开源核心扩展技能 (总数增至 111 个)
严格按「100% 免费开源、无外部付费/绑定卡约束、领域最佳」原则完成了官方核心技能的增补：
- **开发与架构**：`ast-grep` (AST精准重构)、`code-wiki` (架构图与Wiki)、`grill-me` (方案残酷质询)、`rest-graphql-debug` (接口逆向调试)、`har-derived-api-client` (HAR转客户端)、`cloudflare-temporary-deploy` (免账号Worker部署)。
- **多 Agent 仲裁**：`agent-merge-conflict-arbiter` (Git 分支冲突中立仲裁协议)。
- **视觉与多媒体**：`concept-diagrams` (极简教学SVG)、`excalidraw` (手绘白板图)、`baoyu-comic` (知识漫画)、`baoyu-article-illustrator` (文章配图)、`sketch` (多方案HTML对比)、`comfyui` (本地生图/生视频)、`audiocraft-audio-generation` (Meta音乐与音效)、`tldraw-offline`、`draw-your-font`、`ascii-art`、`pixel-art`、`meme-generation`。
- **搜索与安全**：`duckduckgo-search` (免Key搜索)、`searxng-search` (70+多引擎聚合)、`scrapling` (智能反爬提取)、`qmd` (本地混合向量检索)、`blogwatcher` (RSS已读水印监控)、`gitnexus-explorer` (代码知识图谱)、`osint-investigation`、`oss-forensics` (供应链取证)、`sherlock` (用户名全网反查)、`web-pentest`、`1password`、`domain-intel`。
- **MLOps / AI 架构**：`unsloth` (大模型微调)、`serving-llms-vllm` (高吞吐Serving)、`instructor` (Pydantic结构化输出)、`dspy` (声明式Prompt编程)、`qdrant` (Rust向量数据库)、`evaluating-llms-harness` (官方跑分评测)、`segment-anything-model` (SAM抠图分割)、`nemo-curator` (预训练语料清洗脱敏)、`huggingface-tokenizers`。
- **Whisper 偏好调优**：`whisper` 技能已补齐 Windows 跨平台兼容，并**严格按用户环境习惯将 `small` 模型设定为默认首选主力**（2GB 显存占用，速度与中文断句最佳）。

## 3. MCP 生态健康与配置
- **4 个核心 MCP 服务器处于稳定在线与开启状态**：
  1. `Chrome-Devtools`（29 工具）：接管日常 Edge Dev（带扩展保护参数）；
  2. `Desktop-Commander`（26 工具 + 2 资源）：桌面与后台进程控制；
  3. `Serena`（29 工具）：大型代码库语义索引与符号跳转（静默离线模式）；
  4. `Context7`（2 工具）：实时最新开源库文档与代码样例查询。

## 4. 云端自动备份与主分支
- 所有技能安装、去重修复、README 文档与记忆变动均已 100% 同步并推送到 GitHub `3304711297/shared-agent-memory` 的 **`hermes` 默认主分支**。

## 5. 2026-09-04 对比与增补审计

- **技能总量核对**：
  - 磁盘物理总数：126 个（包含 41 个开源增补与 ZCode 迁移定制技能）；
  - 实际在册与激活：`hermes skills list` 显示 113 个启用（41 hub-installed, 52 builtin, 20 local）；
  - 差额 13 个的机制归因：
    - 12 个属于 Linux/macOS 专有依赖（`platforms: [linux, macos]`，如 `serving-llms-vllm`, `unsloth`, `audiocraft-audio-generation`, `searxng-search` 等），Hermes 根据 Windows 宿主环境原生机制自动安全过滤；
    - 1 个为 Kanban 流专属技能（`sdlc-review`，`environments: [kanban]`），仅在看板派遣流中按需激活；
  - 增补技能：新增 `obsidian`（知识库管理）与 `hermes-auxiliary-models`（辅助模型故障自愈与本地路由），状态均已完备。
- **MCP 协议扩展（4 → 5）**：
  - 新增在册 MCP 服务器 **`DeepWiki`**（`url: https://mcp.deepwiki.com/mcp`，提供 7 项 GitHub 仓库与架构深度知识库检索工具）；
  - 现有在线 MCP 共 5 个：`Chrome-Devtools` (29)、`Desktop-Commander` (30)、`Serena` (33)、`Context7` (6)、`DeepWiki` (7)，共计 105 项延时加载工具能力。
- **4 大插件状态**：`context7`, `desktop-commander`, `serena`, `superpowers` 严格锁定 Windows 启动参数与静默模式，配置未发生非受控漂移。

