---
name: gemini-image-gen
description: Use this skill whenever the user asks to generate, draw, paint, or render an image, illustration, anime art, or photo using Google Gemini / Imagen 3 backend.
---

# Gemini Image Generation Skill

Use this skill to generate high quality images using Google's Imagen 3 / Gemini Image API and save them directly to the local workspace.

## How to execute

Run the generation script via Bash tool:

```bash
python "C:/Users/VOS-User/.zcode/skills/gemini-image-gen/generate_image.py" --prompt "YOUR_DETAILED_PROMPT" --aspect-ratio "1:1" --output-dir "generated_images"
```

### Parameters
- `--prompt` (Required): Detailed prompt describing the scene, style, lighting, composition. If the user prompt is in Chinese, it is best to enrich and translate or provide high-detail description for the model.
- `--aspect-ratio`: Options: `1:1`, `16:9`, `9:16`, `4:3`, `3:4` (Default: `1:1`).
- `--output-dir`: Target folder for the generated file (Default: `./generated_images` in current workspace).
- `--output-name`: Optional custom filename.
- `--model`: Default is `imagen-3.0-generate-002`.

### When Executing
1. Call the Bash tool with the python command.
2. Read the JSON output from the script.
3. If successful, present the saved image path as a clickable markdown image/link: `![image](path/to/image.png)`.
4. If missing API key error is returned, politely ask the user to provide their Google Gemini (AI Studio) API Key or set `GEMINI_API_KEY`.
