---
name: vision-ocr-pipeline
description: I cannot see images directly; use local Windows OCR first, remote
  vision only for layout, and the .jpg CDN workaround
metadata:
  node_type: memory
  type: project
  originSessionId: sess_7ad7ae87-25fb-45bb-916e-807424ab1e84
---

I (this agent) have **no native vision** — the Read tool returns only a CDN URL for an image, not pixels. Image understanding requires an external vision-model call, which is slow and rate-limited. Established two-tier pipeline for extracting image content:

1. **Local Windows OCR first** — Windows.Media.Ocr.OcrEngine (zh-Hans-CN) via PowerShell WinRT interop. Runs in seconds, no rate limits, good for text-heavy screenshots under ~4096px. Needs UTF-8 BOM on the .ps1 (prepend `\xef\xbb\xbf`), `[Parameter(ValueFromRemainingArguments=$true)]` for multi-file args, and post-processing to strip inter-character spaces in Chinese output. Limitation: text only — can't see checkbox states or describe layout.
2. **Remote vision model only for layout/checkbox states** — otherwise avoid it. Rate-limit 429s need 20–30s waits between calls.

**CDN format mismatch workaround:** Read uploads PNG but the CDN serves it as JPEG with a `.png` URL suffix, causing analyze_image 400 "图片输入格式错误". Fix: copy the file to a temp path with a `.jpg` extension, re-upload, use the new URL.

User confirmed this understanding after asking why image recognition was so slow. Related: [[glm-vision-naming]].
