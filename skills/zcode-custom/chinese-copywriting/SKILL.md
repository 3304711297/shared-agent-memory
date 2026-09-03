---
name: chinese-copywriting
description: Professional Chinese copywriting, typography, terminology standardization, and CJK-English spacing (Pangu spacing). Trigger whenever the user asks to polish, format, proofread, or standardize Chinese text, markdown documentation, or technical articles.
---

# Chinese Copywriting & Typography Skill

Use this skill to ensure all Chinese technical documentation, articles, and user-facing copy adhere to the highest standards of clarity, typography, and professional formatting.

## Typography & Formatting Rules

1. **CJK-English Spacing (盘古之白)**
   - Always insert a half-width space between Chinese characters and English words, numbers, or code identifiers:
     - ❌ `使用Gemini模型生成3张图片`
     - ✅ `使用 Gemini 模型生成 3 张图片`
   - Exception: Do not add spaces between full-width punctuation and English/numbers.

2. **Proper Casing of Technical Terms**
   - Correctly capitalize industry trademarks and terms:
     - `GitHub`, `Git`, `macOS`, `iOS`, `Android`, `Windows`, `Linux`
     - `JavaScript`, `TypeScript`, `Node.js`, `Python`, `VS Code`
     - `API`, `URL`, `JSON`, `HTML`, `CSS`, `SQL`, `MCP`, `ZCode`

3. **Punctuation Standards**
   - Use full-width punctuation in Chinese sentences (`，`、`。`、`！`、`？`、`：`、`；`、`「`、`」`、`（`、`）`)。
   - In lists or markdown inline references, maintain consistent punctuation at line ends.

## Automated Formatter Tool

A helper formatting script is bundled in this skill:

```bash
python "C:/Users/VOS-User/.zcode/skills/chinese-copywriting/pangu_format.py" path/to/document.md -i
```
