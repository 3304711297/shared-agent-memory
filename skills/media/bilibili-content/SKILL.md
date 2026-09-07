---
name: bilibili-content
description: "Use when analyzing Bilibili videos. Extract and summarize."
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Bilibili, Video, Multimodal, Media, Summary]
    related_skills: [youtube-content]
---

# Bilibili Content & Video Analysis

Extract, summarize, and multimodally analyze Bilibili videos (BV IDs, short links, or video URLs).

## When to Use

Use when the user shares a Bilibili URL (`https://www.bilibili.com/video/BV...` or `b23.tv`), asks to summarize a Bilibili video, inspects chapters/slides, or asks technical questions about video content.

## Workflow

### 1. Extract BVID and Metadata

Parse the `BV...` identifier from the URL and fetch video details (title, description, duration, and `cid`):

```python
import urllib.request, json

bvid = "BV1RS3n6UEXS"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
meta_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
req = urllib.request.Request(meta_url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode("utf-8"))["data"]
cid = data["cid"]
title = data["title"]
desc = data["desc"]
```

### 2. Fast Path: Check Subtitles

Probe if official or community subtitles exist:

```python
sub_url = f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}"
req = urllib.request.Request(sub_url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    sdata = json.loads(resp.read().decode("utf-8"))
subtitles = sdata.get("data", {}).get("subtitle", {}).get("subtitles", [])
```

If subtitles exist, fetch the JSON subtitle URL directly, format timestamps and dialogue, and analyze text directly without downloading video.

### 3. Multimodal Path: Stream Extraction & `video_analyze`

If subtitles are disabled or missing, extract a lightweight video stream for multimodal model inspection:

1. **Fast HTML5 Stream (Zero-Signing, Preferred)**:
   Query the HTML5 endpoint directly without Wbi signing complexity:
   ```python
   play_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=16&platform=html5&high_quality=1"
   req = urllib.request.Request(play_url, headers=headers)
   with urllib.request.urlopen(req, timeout=10) as resp:
       pdata = json.loads(resp.read().decode("utf-8"))
       if pdata.get("code") == 0:
           durl = pdata["data"]["durl"][0]["url"]
   ```
   `qn=16` yields 360p mp4 (typically 5~15MB for 10-minute videos), ready to download directly without container remuxing.

2. **Fallback Wbi Signing**:
   If the HTML5 endpoint returns non-zero, fall back to Wbi signing: fetch `img_url` and `sub_url` from `https://api.bilibili.com/x/web-interface/nav`, combine keys using the 32-char mixin table, and query `https://api.bilibili.com/x/player/wbi/playurl?bvid={bvid}&cid={cid}&qn=16&...`.

3. **Stream Download with Referer**:
   ```python
   # Headers MUST include Referer to avoid 403 Forbidden from CDN
   dl_req = urllib.request.Request(durl, headers={
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
       "Referer": "https://www.bilibili.com"
   })
   # Save to scratch folder, e.g. $LOCALAPPDATA/Temp/bili_temp.mp4
   ```

4. **Multimodal Analysis**:
   Call `video_analyze(video_url="C:/.../bili_temp.mp4", question="...")` to perform holistic audio, visual UI, and slide text analysis.

5. **Mandatory Immediate Cleanup**:
   Immediately delete temporary `.mp4` files from disk as soon as `video_analyze` returns to prevent disk bloat.

## Pitfalls & Guidelines

- **Anti-Scraping 412**: Direct `urllib` or `curl` on the HTML video page will trigger HTTP 412 (Precondition Failed). Always use the JSON API endpoints (`api.bilibili.com/x/web-interface/view` and HTML5/Wbi playurl).
- **CDN 403 Forbidden**: Bilibili media CDNs (`upos-sz-*`) reject requests missing the `Referer: https://www.bilibili.com` header.
- **File Size Bounding**: Multimodal video models degrade or reject files above 50MB. Never request high quality (`qn=80/64`) without user explicit ask; always default to `qn=16` (360p) for analysis.
- **Cross-Platform Scratch Path**: On Windows, never save temporary streams to bare `/tmp/...` paths. Native multimodal analyzers cannot resolve MSYS virtual paths. Always construct absolute native paths using `os.environ.get("LOCALAPPDATA") + "/Temp/..."` or `tempfile.gettempdir()`.
- **Zero-Remux Direct MP4**: Streams fetched from the HTML5 endpoint (`platform=html5&qn=16`) are standard MP4 containers ready for consumption; do not run unnecessary `ffmpeg` remuxing passes unless the stream is corrupted.
- **Structured Multimodal Prompts**: For technical, tutorial, or news videos without subtitles, avoid vague prompts like "summarize the video". Explicitly ask for: 1. Core event/phenomenon; 2. Root technical cause or architecture; 3. Exact parameters, commands, or registry paths; 4. Limitations and actionable steps. This forces the model to extract high-density factual evidence.
