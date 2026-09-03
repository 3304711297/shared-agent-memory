---
name: bilibili-video-transcription-pipeline
description: B站视频→逐字稿的完整本地管线（直连API+ffmpeg whisper），已用于 BIOS 选项科普 41 集整理
metadata:
  node_type: memory
  type: reference
  originSessionId: sess_d3d1e7a7-cc14-4c9d-b4d1-95ca720952e9
---

把 B 站视频内容喂给模型的省 token 方案（用户认可）：提取音频轨 → 本地 whisper 转录 → 按领域知识校对总结。2026-09-02 已跑通并用于整理「所盼皆欣然」两个 BIOS 合集共 41 集。

**可复用管线**（脚本在 `D:\ai coding\.zcode\workspace\default\bios_knowledge\`：download_audio.py / batch_transcribe.py / fetch_lists.py）：

1. **直连 B 站 API（无需浏览器）**：请求带完整浏览器头（UA+Accept+Accept-Language+Referer）并先 GET 首页拿 buvid3 cookie，否则 412。view API 拿 cid → `x/player/playurl?fnval=16` 拿 DASH 音频流（选 bandwidth 最大的 30280），下载时带 Referer+UA。
2. **转录**：ffmpeg（gyan.dev full build 自带 `--enable-whisper`）的 whisper filter：`ffmpeg -i in.wav -af "whisper=model=ggml-small.bin:language=zh:format=srt:destination=out.srt" -f null -`。注意 **destination 路径必须用正斜杠**（反斜杠会被 filter 参数解析吃掉，文件会写到错误名字）。
3. **模型**：ggml-small（465MB）比 base 明显准且本机速度相同（RTX 4070 GPU 生效，6 分钟音频约 25 秒）。HF 直连超时，用 `https://hf-mirror.com/ggerganov/whisper.cpp/resolve/main/ggml-small.bin`。
4. **ASR 误听对照**：AI 语音里 UEFI→"新接口"、CSM→"老显卡兼容模块"、Secure Boot→"SQ Boot"、XMP→"XNP/X3P"、JEDEC→"JDC"、SATA→"串行硬盘口"、AHCI→"现代硬盘接口"、VMD→"英特尔硬盘管家"、Clear CMOS→"清设置芯片"；视频含水印污染行（"字幕製作:貝爾"等）直接忽略。总结可派子代理并行做（每agent 7-13 集，给误听对照表）。

[[youshouldknow-bios-knowledge-series]]
