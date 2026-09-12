---
name: chinese-copywriting
description: "润色中文/排版校对时必用。中英空格与术语规范。Use for Chinese copywriting, typography, and Pangu spacing."
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
python "%LOCALAPPDATA%/hermes/skills/zcode-custom/chinese-copywriting/pangu_format.py" path/to/document.md -i
```

**Pitfalls (learned the hard way) — the script only touches prose by design:**

- Code fences and YAML front matter are **never** modified. A naive global regex would insert spaces into code (`C:/Users/name` → `C :/ Users/name`) and corrupt them.
- Fence language identifiers must not be case-corrected: ` ```python ` → ` ```Python ` silently breaks syntax highlighting. The TERMS_MAP casing pass is therefore **off by default** (`fix_casing=False`); enable it only for prose you have reviewed.
- For a project with its own CI gates (MkDocs `--strict`, custom link/front-matter checkers), prefer running the formatter on a copy first and diffing — bulk whitespace edits can trip unrelated checks.
- When auditing for spacing issues programmatically, **strip markdown syntax with sentinel characters, not spaces**. Using spaces as the replacement creates phantom "missing space" reports: emphasis markers (`**bold**`) and inline code removal both produce false positives. Always sample-check reported numbers by hand before acting on them.
