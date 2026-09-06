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

### 3. Multimodal Path: Wbi Stream Extraction & `video_analyze`

If subtitles are disabled or missing, extract a lightweight video stream for multimodal model inspection:

1. **Wbi Signing**: Fetch `img_url` and `sub_url` from `https://api.bilibili.com/x/web-interface/nav`, combine keys using the standard Bilibili 32-char mixin table, add `wts` timestamp, and compute MD5 hash `w_rid`.
2. **Request Mobile Stream (`qn=16`)**: Query `https://api.bilibili.com/x/player/wbi/playurl?bvid={bvid}&cid={cid}&qn=16&fnval=0&fnver=0&fourk=0&wts={wts}&w_rid={w_rid}`. `qn=16` yields 360p video (typically 10~20MB for 10-minute videos), staying safely below the 50MB model limit.
3. **Stream Download with Referer**:
   ```python
   # Headers MUST include Referer to avoid 403 Forbidden from CDN
   dl_req = urllib.request.Request(durl, headers={
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
       "Referer": "https://www.bilibili.com"
   })
   ```
4. **Remux & Validate**:
   Run `ffmpeg -i temp_raw.mp4 -c copy -y temp.mp4` to fix container atom headers.
5. **Multimodal Analysis**:
   Call `video_analyze(video_url="C:/.../temp.mp4", question="...")` to perform holistic audio, visual UI, and slide text analysis.
6. **Mandatory Cleanup**:
   Immediately delete temporary `.mp4` files from disk after `video_analyze` finishes.

## Pitfalls & Guidelines

- **Anti-Scraping 412**: Direct `urllib` or `curl` on the HTML video page will trigger HTTP 412 (Precondition Failed). Always use the JSON API endpoints (`api.bilibili.com/x/web-interface/view` and Wbi playurl).
- **CDN 403 Forbidden**: Bilibili media CDNs (`upos-sz-*`) reject requests missing the `Referer: https://www.bilibili.com` header.
- **File Size Bounding**: Multimodal video models degrade or reject files above 50MB. Never request high quality (`qn=80/64`) without user explicit ask; always default to `qn=16` (360p) for analysis.
