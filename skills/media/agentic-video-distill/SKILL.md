---
name: agentic-video-distill
description: "视频提炼/分析录屏时必用。Gemini代理式抽帧蒸馏省88%Token。Use when distilling long videos or screen recordings."
version: 1.0.0
author: "Hermes & ZCode Dual-Agent Framework"
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [video-understanding, multimodal, gemini-agentic, youtube, uefi-screencast, distillation]
  related_skills: [bilibili-content, youtube-content, cangjie-distill]
---

# Agentic Video Distill (Gemini 代理式视频高密度蒸馏)

基于 Google Gemini 的 **Agentic Video Understanding** 架构（Think → Act → Observe 服务端工具回环），实现对长视频、技术录屏、主板 UEFI/BIOS 操作教程以及公开 YouTube 视频的极限低 Token、高精度结构化蒸馏。

## 架构解耦与核心机制

1. **主聊模型与重活解耦**：
   - 无论当前主会话模型是 Claude、DeepSeek、GLM 还是轻量模型，主模型无需（也无法）直接接收几百兆的原始视频流；
   - 本技能指导当前 Agent 作为「调度官」，调用内置后台脚本委托 **Gemini 3.8 Flash** 专职执行 Agentic 视频穿透；
   - 主模型接收后台返回的结构化 Markdown 切片，再结合用户诉求执行深度答疑、二次加工或编译进知识库。
2. **极速抽帧与 Token 节约 88%**：
   - **Pass by Reference**：初始仅传轻量元数据指针；
   - **Transcript-first**：优先全文检索带时间戳字幕定位锚点；
   - **Temporal Zooming & Adaptive FPS**：针对具体疑问区间（如 14~16秒）自适应提升至 5~10 FPS 高速抽帧，慢节奏 0.1 FPS 粗扫，按需拉取音频；
   - 杜绝传统 1 FPS 暴力灌帧导致的 20 万+ Token 膨胀与细节注意力稀释。

---

## When to Use

- 用户发送或指定本地视频文件路径（`.mp4`, `.mkv` 等）或公开 YouTube URL（`https://youtu.be/...`）；
- 需要从视频中精准提取**屏幕画面证据**（如 UEFI/BIOS 菜单层级路径、拓扑结构图、代码 12 等设备管理器报错、性能跑分曲线）；
- 需要将长视频/技术演讲高保真转化为 Markdown 学习笔记或供 `cangjie-distill` 提取方法论。

---

## Operating Workflow (执行规程)

当用户提出视频分析或提炼需求时，严格按以下步骤推进：

### 1. 确认视频源与先决条件
- **视频来源**：
  - 本地视频：确认为绝对路径（如 `D:/videos/uefi_test.mp4`）；
  - YouTube：确认为公开可访问链接（`https://youtu.be/...` 或 `https://www.youtube.com/watch?v=...`）；
  - B 站视频：若是 B 站长视频，优先使用 `bilibili-content` 抓取 360p 流或字幕，亦可下载为本地临时 MP4 后调用本技能深度提炼画面。
- **环境凭据**：
  - 脚本自动读取环境变量 `GEMINI_API_KEY`；若未配置，提示用户传入或设置；
  - 网络自动走本地代理 `http://127.0.0.1:3067`。

### 2. 调用内置执行器（后台执行，主会话非阻塞）
在终端中执行技能内置脚本：

```bash
# 优先使用当前技能目录下的 scripts/distill.py（或 ~/.hermes/scripts/distill_gemini_video.py）
python "<SKILL_DIR>/scripts/distill.py" "<VIDEO_SOURCE>" -o "<OUTPUT_MD_PATH>"
```

### 3. 获取输出与二次综合
读取脚本产出的 Markdown 结构化切片：
1. **时间线步骤与关键参数**；
2. **屏幕画面事实证据**（确切菜单、报错代码与配置键值）；
3. **底层原理与避坑红线**。

主模型根据用户当前的特定问题，以精炼有据的语言向用户呈现最终结论。
