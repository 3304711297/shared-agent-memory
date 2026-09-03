---
name: smart-web-crawler
description: Fetch web pages, scrape online documentation, extract clean text, articles, tables, and convert HTML into clean Markdown or structured JSON. Trigger whenever the user asks to scrape a website, extract article content from a link, or analyze web page data.
---

# Smart Web Crawler Skill

Use this skill to fetch, scrape, clean, and convert web content into structured Markdown or JSON.

## How to execute

Run the crawler script via Bash:

```bash
python "C:/Users/VOS-User/.zcode/skills/smart-web-crawler/crawl.py" "TARGET_URL" --output "extracted.md"
```

### Options
- `--output <path>`: Save extracted clean markdown to a file.
- `--json`: Output as JSON containing metadata, title, and cleaned markdown.
- `--no-proxy`: Disable local proxy if crawling local network endpoints.

## Features
- Automatic proxy support (`127.0.0.1:3067`).
- Strips ads, scripts, navbars, and noise.
- Normalizes links, headings, tables, and lists.
