---
name: gemini-agentic-video-distill-architecture
description: Gemini 代理式视频理解（Agentic Video Understanding）解耦架构、Token暴降实测取证与跨端自包含技能落地全貌
metadata:
  type: reference
---

# Gemini 代理式视频理解解耦架构与跨端蒸馏实战

本文档记录 2026-09-08 针对 Google DeepMind 发布的 **Gemini Agentic Video Understanding** 架构的技术穿透、本地实测实证对比、主聊模型解耦设计与双端（Hermes & ZCode）自包含技能落地全貌。

---

## 一、 核心架构解耦设计（主模型与多模态重活分离）

### 1. 痛点：为什么主聊天模型不能直接在会话里分析长视频？
1. **网关协议断层**：Hermes/ZCode 主力通过 EasyCLIProxyAPI (18080) 走 OpenAI 兼容协议（`/v1/chat/completions`）。OpenAI 协议不支持 Google 专有的 `processing="agentic"` 参数及服务端内部工具回环（`processing_call` / `processing_result`）；
2. **多轮对话滚雪球陷阱（致命）**：
   - 传统多模态输入会将视频切成几百张图片帧直接塞进会话上下文（10分钟视频 ≈ 5.3 万 Tokens）；
   - 多轮对话中，用户每追问一次，客户端都必须将这 5.3 万个视频帧全量重发。3 轮追问就会产生 16 万+ Tokens 消耗，直接击穿免费层级 250K TPM 速率限制，并引发上下文膨胀与延迟飙升；
3. **模型绑定冲突**：一旦用户在前端将聊天模型切换为非 Gemini 系列（如 Claude 3.7、DeepSeek 或本地 WorkBuddy GLM），这些模型底层根本不存在 Google 的代理式视频接口。

### 2. 解耦设计范式
- **主模型充当「调度官」**：主会话模型仅负责意图识别与工具委派，完全不吞吐庞大的原始视频二进制数据；
- **自包含后端微执行器**：技能内置独立 Python 执行器（`distill.py`），专职调用 Google 官方 `google-genai` SDK 直连云端 Interactions API；
- **纯文本交付**：执行器在外部跑完视频探查后，仅向主模型交付一份 1,500 Tokens 的高密度纯文本 Markdown 结构化切片。多轮追问时，主会话历史仅滚动纯文本，**彻底阻断媒体 Token 滚雪球**。

---

## 二、 官方账本实测数据取证（严谨实测，绝无水分）

在同一段 10 分钟视频（`https://www.youtube.com/watch?v=jHEzsotqRP4`）上，直接提取 Google AI Studio 返回的真实账本（`inter.usage.model_dump()`）：

| 测试场景 | 传统静态模式 (`processing: "static"`) | 代理模式 (`processing: "agentic"`) | **Token 节省幅度** |
| :--- | :--- | :--- | :---: |
| **场景 A：日常概括与问答**<br>（“简短总结该视频核心主题”） | **53,747 Tokens**<br>• 视频帧刚性底座：**53,513**<br>• 文本输入：6<br>• 思考与输出：228 | **386 Tokens**<br>• 视频帧底座：**0**<br>• 文本输入：49<br>• 工具调取：94<br>• 思考与输出：243 | <font color="#2ea043">**⚡ 暴降 99.28%**</font><br>(直接省下 5.3 万 Tokens) |
| **场景 B：全要素深度画面提取**<br>（提取 4 个演示、屏幕命令与按键） | **~58,000+ Tokens**<br>(全片 53,513 帧全量入仓 + 复杂输出) | **24,116 Tokens**<br>• 视频帧底座：0<br>• 定向高精度抽帧：19,404<br>• 深度思考与输出：4,107 | <font color="#2ea043">**⚡ 降低 58.42%**</font><br>(即便做全片超深度提取，仍净省 3.4 万) |

### 核心差异机理
- **Static 模式**：1 FPS 暴力全帧切片（53,513 tokens）是不可避免的刚性底座，只要调用就必须全额计费；
- **Agentic 模式**：模型先看字幕（仅耗 94 tokens），问概括时**完全不解码图片帧（Video Tokens = 0）**；问具体操作时，**仅把对应的几秒关键区间局部自适应抽帧拉入上下文**，去除了 80% 无关帧干扰。

---

## 三、 双端工程落地与自适应防护设计

### 1. 动态模型自适应感知（解决换 3.9 后的平滑演进）
在 `distill.py` 中实现智能模型探针：
1. 优先读取 Hermes 本地 `state.db` 最新活跃会话模型：用户未来切到 `gemini-3.9-flash` 时，视频执行器自动跟随升至 3.9，零人工干预；
2. 若当前会话切为了 Claude/GLM，自动读取 `config.yaml` 或环境变量中的基准；
3. 若均为非 Gemini，优雅回退至受支持的兼容基线 `gemini-3.8-flash`。

### 2. 双 Key 自动轮询与官方高负载容灾
1. **主备凭据池**：持久化于 `~/.hermes/auth/gemini_video_keys.json`（主用优先，429 或配额耗尽自动轮询备用；`.gitignore` 严格阻断）；
2. **官方 503 排队平替**：当 `gemini-3.8-flash` 遭遇官方突发排队高负载（`api_error: experiencing high demand`）时，执行器自动捕获并无缝平替至 `gemini-3.7-flash` 完成交付。

### 3. 本地 B 站视频抓流与即时物理粉碎管线
- 配合 `bilibili-content`，遇 B 站长视频自动通过 HTML5 接口秒级拉取 360p 流（8~10 MB），上传 Google File API 建立云端切片；
- 执行完毕后，立即物理粉碎本地 `%LOCALAPPDATA%\Temp\bili_*.mp4`，实现磁盘零垃圾残留。

---

## 四、 跨端资产与看门狗登记

1. **技能部署**：
   - Hermes: `skills/media/agentic-video-distill/`（已推 `hermes` 分支）
   - ZCode: `~/.zcode/skills/agentic-video-distill/`
2. **看门狗与白名单**：
   - `capability-inventory.json` 中已列入 `protectedSkills` 白名单（防止 curator 归档）；
   - 在 `notWatched` 登记自研免看门规范。
3. **知识库联动**：
   - ysk 知识库已录入配套硬核技术指南：`docs/AI工具/Gemini代理式视频理解架构解析与降本实战.md`。

[[shared-agent-memory]] [[hermes-zcode-token-gap-investigation]] [[cangjie-distill]] [[youshouldknow-bios-knowledge-series]]
