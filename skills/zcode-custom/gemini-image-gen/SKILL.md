---
name: gemini-image-gen
description: "用Gemini生图时必用。画图/插画/动漫/照片。Use when generating images via Google Gemini / Imagen."
---

# Gemini Image Generation Skill

Use this skill to generate high quality images using Google's Imagen 3 / Gemini Image API and save them directly to the local workspace.

## How to execute

Run the generation script via Bash tool:

```bash
python "%LOCALAPPDATA%/hermes/skills/zcode-custom/gemini-image-gen/generate_image.py" --prompt "YOUR_DETAILED_PROMPT" --aspect-ratio "1:1" --output-dir "generated_images"
```

### Parameters
- `--prompt` (Required): Detailed prompt describing the scene, style, lighting, composition. If the user prompt is in Chinese, it is best to enrich and translate or provide high-detail description for the model.
- `--aspect-ratio`: Options: `1:1`, `16:9`, `9:16`, `4:3`, `3:4` (Default: `1:1`).
- `--output-dir`: Target folder for the generated file (Default: `./generated_images` in current workspace).
- `--output-name`: Optional custom filename.
- `--model`: Default is `imagen-3.0-generate-002`.

### When Executing
1. Call the generation script via python command (supports `--aspect-ratio`, `--output-dir`, `--model gemini-3.1-flash-image`).
2. The script automatically uses `HERMES_CUSTOM_CPA_API_KEY` to authenticate with the local CPA bridge (`http://127.0.0.1:18080`).
3. If successful, present the saved image path using Hermes Desktop `MEDIA:/absolute/path/to/image.jpg` format (markdown `![]()` local images are blocked).
4. If missing API key error is returned, check `HERMES_CUSTOM_CPA_API_KEY` or `~/.zcode/config/gemini.json`.
