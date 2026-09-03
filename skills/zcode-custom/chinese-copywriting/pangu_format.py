#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Copywriting & Typography Formatter
Implements Pangu spacing (CJK-English spacing), technical term casing correction, and markdown punctuation normalization.
"""

import sys
import re
import argparse

TERMS_MAP = {
    r'\bgithub\b': 'GitHub',
    r'\bmacos\b': 'macOS',
    r'\bios\b': 'iOS',
    r'\biphone\b': 'iPhone',
    r'\bandroid\b': 'Android',
    r'\bjavascript\b': 'JavaScript',
    r'\btypescript\b': 'TypeScript',
    r'\bnodejs\b': 'Node.js',
    r'\bnode\.js\b': 'Node.js',
    r'\bpython\b': 'Python',
    r'\bvscode\b': 'VS Code',
    r'\bvs\s*code\b': 'VS Code',
    r'\bjson\b': 'JSON',
    r'\bhtml\b': 'HTML',
    r'\bcss\b': 'CSS',
    r'\bapi\b': 'API',
    r'\bapis\b': 'APIs',
    r'\bmcp\b': 'MCP',
    r'\burl\b': 'URL',
    r'\burls\b': 'URLs',
    r'\bsql\b': 'SQL',
    r'\bgit\b': 'Git',
    r'\bwindows\b': 'Windows',
    r'\blinux\b': 'Linux'
}

def format_pangu(text):
    # CJK regex
    cjk = r'[\u4e00-\u9fa5\u3040-\u30ff\u3400-\u4dbf]'
    ans = r'[a-zA-Z0-9$#%@]'
    
    # 1. CJK followed by Latin/Number
    text = re.sub(f'({cjk})({ans})', r'\1 \2', text)
    # 2. Latin/Number followed by CJK
    text = re.sub(f'({ans})({cjk})', r'\1 \2', text)
    
    # Fix technical term casings
    for pattern, correct in TERMS_MAP.items():
        text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
        
    return text

def format_file(file_path, in_place=False):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    formatted = format_pangu(content)
    
    if in_place:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted)
        print(f"[OK] Formatted {file_path}")
    else:
        sys.stdout.write(formatted)

def main():
    parser = argparse.ArgumentParser(description="Chinese Copywriting & Typography Formatter")
    parser.add_argument("file", nargs="?", help="Markdown or text file to format")
    parser.add_argument("-i", "--in-place", action="store_true", help="Modify file in place")
    
    args = parser.parse_args()
    if args.file:
        format_file(args.file, in_place=args.in_place)
    else:
        input_text = sys.stdin.read()
        sys.stdout.write(format_pangu(input_text))

if __name__ == "__main__":
    main()
