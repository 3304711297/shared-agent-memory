#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Web Crawler & Content Extractor
Fetches web pages, removes boilerplate, and extracts clean Markdown or JSON.
"""

import os
import sys
import re
import json
import argparse
import requests
from urllib.parse import urljoin, urlparse

DEFAULT_PROXY = "http://127.0.0.1:3067"

def clean_html_to_markdown(html, base_url=""):
    # Simple, zero-dependency robust HTML to markdown cleaner
    # Remove script, style, head, noscript, svg, nav, footer
    html = re.sub(r'<(script|style|noscript|svg|iframe|canvas)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Extract title
    title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = title_m.group(1).strip() if title_m else ""
    
    # Convert headings
    html = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n\n# \1\n\n', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n\n## \1\n\n', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n\n### \1\n\n', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<h4[^>]*>(.*?)</h4>', r'\n\n#### \1\n\n', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert paragraphs & breaks
    html = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\n\1\n\n', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<br\s*/?>', r'\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<hr\s*/?>', r'\n---\n', html, flags=re.IGNORECASE)
    
    # Convert lists
    html = re.sub(r'<li[^>]*>(.*?)</li>', r'\n- \1', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert bold / italic / code
    html = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'**\2**', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', r'*\2*', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', r'\n```\n\1\n```\n', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert links
    def link_repl(match):
        href = match.group(1)
        text = match.group(2).strip()
        full_href = urljoin(base_url, href) if base_url else href
        return f'[{text}]({full_href})' if text else ''
        
    html = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', link_repl, html, flags=re.DOTALL | re.IGNORECASE)
    
    # Strip remaining HTML tags
    html = re.sub(r'<[^>]+>', ' ', html)
    
    # Normalize whitespace
    lines = []
    for line in html.splitlines():
        line = re.sub(r'[ \t]+', ' ', line).strip()
        if line:
            lines.append(line)
            
    content = '\n\n'.join(lines)
    # Decode basic HTML entities
    content = content.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
    
    return title, content

def fetch_url(url, proxy=None, timeout=20):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    
    proxies = None
    if proxy:
        proxies = {'http': proxy, 'https': proxy}
        
    res = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
    res.encoding = res.apparent_encoding or 'utf-8'
    return res.text

def main():
    parser = argparse.ArgumentParser(description="Smart Web Crawler & Extractor")
    parser.add_argument("url", help="Target webpage URL")
    parser.add_argument("--output", "-o", help="Output file path (optional)")
    parser.add_argument("--proxy", default=DEFAULT_PROXY, help="HTTP/HTTPS proxy")
    parser.add_argument("--no-proxy", action="store_true", help="Disable proxy")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    proxy = None if args.no_proxy else args.proxy
    
    try:
        html = fetch_url(args.url, proxy=proxy)
        title, md = clean_html_to_markdown(html, base_url=args.url)
        
        result = {
            "url": args.url,
            "title": title,
            "markdown": md
        }
        
        if args.json:
            output_str = json.dumps(result, ensure_ascii=False, indent=2)
        else:
            output_str = f"# {title}\n\nURL: {args.url}\n\n---\n\n{md}"
            
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_str)
            print(f"[OK] Extracted content saved to {args.output}")
        else:
            print(output_str)
            
    except Exception as e:
        print(f"[ERROR] Crawling failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
