---
name: agentic-video-distill
description: "视频提炼/分析录屏时必用。Gemini代理式抽帧蒸馏省88%Token。B站无字幕视频与video_analyze失败时走本技能。Use when distilling long videos or screen recordings."
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
- B 站无字幕视频，或 `video_analyze` 不可用/调用失败（401 等）时的指定 fallback——先于任何手搓 whisper/抽帧方案；
- 需要从视频中精准提取**屏幕画面证据**（如 UEFI/BIOS 菜单层级路径、拓扑结构图、代码 12 等设备管理器报错、性能跑分曲线）；
- 需要将长视频/技术演讲高保真转化为 Markdown 学习笔记或供 `cangjie-distill` 提取方法论。

---

## 路线选择（先看这张表，再动手）

**铁律：`video_analyze` 失败时不要立刻手搓 ffmpeg 抽帧 + 拼图。**低分辨率小字经抽帧拼接后只剩十几像素，视觉模型会互相打脸（同一区域两次读出不同文字），既烧轮次又得不出可信结论。按下列顺序走：

| 优先级 | 路线 | 适用条件 | 命令 |
|---|---|---|---|
| ① | `video_analyze` 工具 | 默认先试 | 直接调用 |
| ② | **cpa 端点工具集路线**（本机首选 fallback） | ① 报「视频内容已被过滤」时 | `python scripts/agentic-video-cpa.py <视频>` |
| ③ | `distill.py` Google 官方直连 | 持有有效 `GEMINI_API_KEY` 且官方模型 ID 可用 | `python scripts/distill.py <视频>` |
| ④ | 手搓抽帧 + `vision_analyze` | 仅在 ②③ 均不可用时，且接受精度损失 | 自建，勿作为默认 |

### `video_analyze` 的失效模式（本机实测）

`video_analyze` 把视频交给**主聊天模型链路**，而非 `auxiliary.vision`。主模型是 deepseek-v4.1-flash 时不支持视频输入，直接返回「当前模型不支持视频输入，视频内容已被过滤」。**这与图片不同**——`vision_analyze` 走 `auxiliary.vision`（provider=auto），能正常看图，所以「图片能看」不代表「视频能看」，不要据此误判工具坏了。

### cpa 端点工具集路线（本机首选 fallback）

`scripts/agentic-video-cpa.py` 让本地反代端点（默认 `http://127.0.0.1:18080/v1`）的 `gemini-3.8-flash-high` **带着工具集自主分析**视频：模型自己决定抽哪一帧、放大哪块区域、要不要听音频。

```bash
python scripts/agentic-video-cpa.py "<视频路径>" -o "<输出.md>"
python scripts/agentic-video-cpa.py "<视频路径>" --question "这次点击触发了什么？" --budget 6
```

该端点实测同时具备**视频输入**与**工具调用**两项能力（`tool_calls` 正常返回）。

**三条设计要点，改脚本时勿删**：

1. **收敛纪律必须有**：不设预算上限时模型会无限次重复放大同一区域——实测 14 轮不收敛、上下文滚到 63 万 token，仍未给结论。脚本的 `TOOL_BUDGET`（默认 8）+ 只回带最近 `KEEP_RECENT_SETS`（3）组工具结果 + 强制每轮写「已确认」笔记，三件套共同保证第 5 轮左右收口。
2. **防幻觉锚点必须写进 SYSTEM**：低分辨率小字极易诱发先验填补。实测 `gemini-3-flash-preview` 分析本机录屏时，凭空编出 `GPT-4o` / `o1-preview` / `Llama 3.1 405B` / `0 / 2000` 等画面中**根本不存在**的 UI。SYSTEM 里必须显式禁止用常见 AI 界面先验去补全，并要求「小于 14px 的文字先放大再读」。
3. **交叉验证仍不可省**：即使模型声称「已放大核对」，低分辨率下不同轮次仍可能给出互相矛盾的具体读数（如鼠标移动方向、最右端图标形状）。交付前用 `vision_analyze` 对**原始帧的裁剪区域**独立复核关键结论，不要直接采信单一叙述。

### `distill.py`（Google 官方直连）的已知坑

- **中文文件名必失败**：`files.upload` 的 multipart 头按 ascii 编码，路径含中文报 `'ascii' codec can't encode characters in position 0-3`。先复制成 ASCII 文件名（如 `clip.mp4`）再上传。
- **候选模型名可能全部失配**：脚本内置候选队列是 `gemini-3.8/3.7/3.6-flash` 等，但**实际 Key 上可用的模型 ID 需现查**（`client.models.list()`）。曾实测某 Key 只有 `gemini-3.5-flash` / `gemini-3-flash-preview` / `gemini-3.1-pro-preview`，候选队列全落空。
- **`g​emini-3.1-pro-preview` 可能返回空串**（上传成功、`LEN 0`），而 `g​emini-3-flash-preview` 会返回内容但幻觉严重（见上）。官方直连路线对本机屏录的可靠性低于 cpa 路线。
- **出口 SSL 不稳**：经本地代理访问 `generativelanguage.googleapis.com` 时实测间歇性 `SSL: UNEXPECTED_EOF_WHILE_READING`，需退避重试（脚本已含 Key 轮询，但同一 Key 内的连接抖动仍需外层重试）。

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

**首选 cpa 工具集路线**（见「路线选择」表）：

```bash
python "<SKILL_DIR>/scripts/agentic-video-cpa.py" "<VIDEO_SOURCE>" -o "<OUTPUT_MD_PATH>"
```

**备选 Google 官方直连**（需有效 Key，且注意中文文件名坑）：

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

---

## 批量场景的配额纪律（务必遵守）

免费档 Gemini 配额为 **每模型 20 次/窗口**，因此：

- **绝不要并行跑多个 distill**：多路并发会在几秒内把配额打爆，此时 `gemini-3.8-flash` 与平替的 `gemini-3.7-flash` 会同时返回 `quota_exceeded`，脚本按 Key 轮询（Key #1 → Key #2）也救不回来，症状是「所有候选模型均未能返回有效分析内容」。
- **批量一律单路串行 + 间隔**：一个进程内 `for` 循环逐个跑，条目之间 `sleep 60`，失败重试之间 `sleep 180`，并让循环跳过已产出的文件（`[ -f "$OUT" ] && continue`）。这样即使中途被限流，已完成的结果也保住了。
- **已被配额挡住时不要硬等**：同一视频连续 3 次重试仍失败，就换 `vision_analyze` 抽帧拼图路线（见 `bilibili-content` 技能第 4 节），不要无限重试。
- 命中 `high demand`（`api_error`）也计入重试预算；它与 `quota_exceeded` 的处置相同，都是换路而不是加并发。
