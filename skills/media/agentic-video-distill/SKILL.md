---
name: agentic-video-distill
description: "视频提炼/分析录屏时必用。优先当前会话直接分析视频+强制结合Whisper双轨比对避免误差。仅用户明确强调云端时走外部脚本。Use when analyzing videos."
version: 1.1.0
author: "Hermes & ZCode Dual-Agent Framework"
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [video-understanding, multimodal, gemini-agentic, whisper, dual-track-verification, bilibili, youtube, distillation]
  related_skills: [bilibili-content, youtube-content, whisper, cangjie-distill]
---

# Agentic Video Distill (视频高密度蒸馏与双轨校对)

基于当前会话原生多模态视频分析（`video_analyze`）与本地 **Whisper** 语音识别双轨交叉比对架构，实现对长视频、技术录屏、主板 UEFI/BIOS 操作教程以及公开网络视频的极限低 Token、零幻觉、高精度结构化蒸馏。

## 核心设计原则与架构演进（2026-09 落地）

1. **优先当前会话原生分析，严禁盲目调用外部云端脚本**：
   - **痛点与反思**：早期设计的外部云端子脚本/后台代理路线（如 `agentic-video-cpa.py` / `distill_openrouter.py`），初衷是为主会话节省上下文 Token。但在实际运行中，子脚本需要执行环境检查、多轮次 Shell 命令交互、繁琐重试与大段 Markdown 切片跨进程传输，**不仅没有节约 Token，反而因额外调用消耗了更多 Token**，且增加了网络中断与鉴权失败点。
   - **最新铁律**：**除非用户在指令中明确强调/要求使用外部云端模型，默认一律优先在当前会话内直接使用当前模型调用 `video_analyze` 分析视频**。
2. **强制双轨比对避免误差（video_analyze + Whisper 铁律）**：
   - **单轨弊端**：纯视频视觉分析在遇到快速跳帧、复杂 BIOS 缩写、小字参数时容易产生先验脑补（如误读或凭空编造不存在的参数）；纯音频转录对静音操作、仅画面展示的配置路径与跑分图表无能为力；
   - **双轨闭环**：
     - **画面轨**：调用 `video_analyze` 精准捕获屏幕画面、拓扑架构、菜单层级、选项键值与测试曲线；
     - **音频轨**：通过 `ffmpeg` 提取音频并调用本地 `whisper`（默认加载 `small` 模型）转录解说全貌；
     - **交叉验证**：将画面提取要点与 Whisper 时间戳文本逐段对齐，以音频消除画面小字漏读，以画面实证纠正同音错别字，彻底消灭单模态幻觉。

---

## When to Use

- 用户发送或指定本地视频文件路径（`.mp4`, `.mkv` 等）、B 站视频（BV 号/链接）或公开 YouTube URL；
- 需要从视频中精准提取**屏幕画面证据**（如 UEFI/BIOS 菜单层级路径、拓扑结构图、代码 12 等设备管理器报错、性能跑分曲线）；
- 需要将长视频/技术演讲高保真转化为 Markdown 学习笔记或供 `cangjie-distill` 提取方法论；
- **执行原则**：直接使用当前会话模型 + Whisper 本地双轨流。

---

## 路线选择（先看这张表，再动手）

**铁律：未明确强调云端时，坚决优先走「当前会话原生 + Whisper 双轨」路线。**

| 优先级 | 路线 | 适用条件 | 操作流程 / 命令 |
|---|---|---|---|
| **① 首选（默认）** | **当前会话直接分析 + Whisper 双轨比对** | **默认必走**（用户未强调云端时） | 1. `video_analyze(video_url=..., question=...)`<br>2. `ffmpeg` 提取音频 $\to$ `whisper` 本地转录<br>3. 视听双轨交叉核对交付 |
| ② 备选 | **cpa 端点工具集路线** | 仅在当前主模型不支持视频输入（报「内容已被过滤」）或用户明确指定 cpa 时 | `python scripts/agentic-video-cpa.py <视频>` |
| ③ 备选 | **OpenRouter 免费切片路线** | 用户显式指定 OpenRouter 渠道或配额告急时 | `python scripts/distill_openrouter.py <视频>` |
| ④ 备选 | **distill.py Google 官方直连** | 用户显式要求官方直连且持有有效 Key | `python scripts/distill.py <视频>` |
| ⑤ 保底 | 手搓抽帧 + `vision_analyze` | 仅在上述全部不可用时的终极保底 | 接触表 + 区域裁剪放大 |

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

### OpenRouter 免费多模态切片路线（Space Bunny / 视觉切片 fallback）

当用户显式要求**不调用云端 Gemini**、或 Gemini 路线配额耗尽/端点故障时，可切换至 OpenRouter 免费多模态模型（默认 `stealth/space-bunny-alpha`）：

```bash
python scripts/distill_openrouter.py "<视频路径>" -o "<输出.md>"
```

**实测三大避坑铁律与工程机理（2026-09-27 实测）：**

1. **`video_url` 全局余额门槛与 402 拦截**：
   - OpenRouter 对所有模型的 `video_url`（直传视频 base64/URL）设有硬性规则：**账户必须至少有 $1.00 余额**。即便模型本身单价为 0（如 space-bunny-alpha），免费层账户直传视频依然会直接抛出 `HTTPError 402: {"error":{"message":"This request requires at least $1.00 in balance for video","code":402}}`。
   - 此外，经由本地代理上传数兆 base64 视频容易发生 `WinError 10054` 连接重置。
   - **破局方案**：`image_url` 在 OpenRouter 免费模型上**完全零门槛免费**！脚本自动使用 ffmpeg 抽帧生成 3 张 3x4 (12 帧/张) 的紧凑时序接触表（Contact Sheet，每张仅约 100KB），通过 `image_url` 传入，彻底绕开 402 余额限制与大包断连。
2. **思考模型（Reasoning Models）参数三要素**：
   - 类似 `stealth/space-bunny-alpha` 这类自带深度思考的模型，默认 `reasoning_effort: max`；
   - 若设置了较小的 `max_tokens`（如 1500），思考 token 会耗尽全部预算导致最终 `content` 返回 `None`，引发脚本写入异常；
   - **必配参数**：显式指定 `"reasoning": {"effort": "low"}` 限制思考预算，并放宽 `"max_tokens": 4096`；解析响应时严格做 `content = msg.get("content") or ""` 空值保护。
3. **Hermes CLI 独立会话一键拉起**：
   - 若主会话模型不支持多模态，可通过 Hermes CLI 直接单次拉起 openrouterfree 供应商运行任务：
     ```bash
     hermes chat --provider openrouterfree -m stealth/space-bunny-alpha -q "请使用多模态能力分析本地切片..." --oneshot
     ```

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
  - B 站视频：优先使用 `bilibili-content` 抓取 360p 轻量流（`qn=16`，体积仅 5~15MB）保存至本地 scratch 临时目录（如 `$LOCALAPPDATA/Temp/bili_temp.mp4`）。

### 2. 执行双轨分析（当前会话原生 · 默认首选）
若用户未明确指定调用外部云端，**默认一律在当前会话执行视听双轨比对**，严禁擅自唤起外部云端子脚本：
1. **画面轨（video_analyze）**：
   调用 `video_analyze(video_url="<本地视频绝对路径>", question="<结构化提炼提示词>")`。
   结构化提炼提示词须涵盖：核心大纲、菜单层级路径、报错事件码/APIC ID、确切键值与操作红线。
2. **音频轨（Whisper 本地转录）**：
   提取音频并运行本地 Whisper（优先默认推荐 `small` 模型）：
   ```bash
   ffmpeg -y -v error -i "<视频路径>" -vn -acodec pcm_s16le -ar 16000 "<音频.wav>"
   python -c "import whisper; model=whisper.load_model('small'); res=model.transcribe(r'<音频.wav>', language='zh'); print(res['text'])"
   ```
3. **双轨交叉校对与消差**：
   对照 Whisper 语音转录与 `video_analyze` 提取的画面切片，以音频语义核准 OCR 画面模糊，以画面实据纠正同音生僻术语，彻底杜绝单模态脑补与幻觉。
4. **即时清理**：
   双轨提取完成后立即删除本地临时 `.mp4` 和 `.wav` 文件，保持环境零残留。

### 3. 备选云端脚本（仅在用户显式指定或主模型不支持视频时触发）
- 若用户明确要求走 cpa 端点或主模型报“已被过滤”：`python "<SKILL_DIR>/scripts/agentic-video-cpa.py" "<视频>" -o "<输出.md>"`
- 若用户明确要求 OpenRouter 渠道：`python "<SKILL_DIR>/scripts/distill_openrouter.py" "<视频>" -o "<输出.md>"`
- 若用户明确要求官方直连且提供有效 Key：`python "<SKILL_DIR>/scripts/distill.py" "<视频>" -o "<输出.md>"`

---

## 批量场景的配额纪律（务必遵守）

免费档 Gemini 配额为 **每模型 20 次/窗口**，因此：

- **绝不要并行跑多个 distill**：多路并发会在几秒内把配额打爆，此时 `gemini-3.8-flash` 与平替的 `gemini-3.7-flash` 会同时返回 `quota_exceeded`，脚本按 Key 轮询（Key #1 → Key #2）也救不回来，症状是「所有候选模型均未能返回有效分析内容」。
- **批量一律单路串行 + 间隔**：一个进程内 `for` 循环逐个跑，条目之间 `sleep 60`，失败重试之间 `sleep 180`，并让循环跳过已产出的文件（`[ -f "$OUT" ] && continue`）。这样即使中途被限流，已完成的结果也保住了。
- **已被配额挡住时不要硬等**：同一视频连续 3 次重试仍失败，就换 `vision_analyze` 抽帧拼图路线（见 `bilibili-content` 技能第 4 节），不要无限重试。
- 命中 `high demand`（`api_error`）也计入重试预算；它与 `quota_exceeded` 的处置相同，都是换路而不是加并发。
