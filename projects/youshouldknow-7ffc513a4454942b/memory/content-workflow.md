---
name: content-workflow
description: The strict end-to-end workflow the user requires for every new
  youshouldknow article
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_7ad7ae87-25fb-45bb-916e-807424ab1e84
---

For every article added to [[youshouldknow-repo]], the user requires this exact workflow. **Why:** the user said "我的GitHub不接受缺斤少两" (won't accept incomplete/sloppy content) and "补充的前提下你需要先去检索内容可靠性而不是直接套用" — reliability must be verified, not assumed. **How to apply:**

1. Extract full content — links via WebFetch/webReader; images via OCR transcription to text (see [[vision-ocr-pipeline]]).
2. **Verify reliability via web search BEFORE writing** — do not paste the user's draft as-is.
3. Write the article with a 事实核查记录 table using markers ✅属实 / ⚠️部分 / ❌勘误 / 💡经验建议, plus a 参考来源 list. References must be **external authoritative sources only — never attribute the user's own channel/links**.
4. Place in the right category folder and add a `<br>`-separated link in the README.md table-of-contents row for that category.
5. `git add` only the specific .md files (never images), commit with a conventional message `feat|fix|docs(分类): 描述`, then push.
6. Clean up source images and temp files from both the project folder and the Desktop.

**Filename rule:** never use URL-special characters (`%`, `#`, `?`) in article filenames — a file named `...跳升至100%现象解析.md` made its GitHub page fail to load ("An unexpected error occurred") because `%` starts an invalid percent-encoding in the URL. Display text/titles may keep `%`, but the filename and README link path must avoid it (e.g. rename 100% → 满电).
