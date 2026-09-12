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

FENCE_LINE = re.compile(r'^\s*(```|~~~)')


def split_fences(text):
    """把文本切成 [(是否不可改, 内容), ...]。

    不可改区域 = YAML front matter + 代码围栏（含围栏行本身）。
    只有可改区域的正文才补空格——否则会破坏代码、URL、围栏语言标识。
    """
    lines = text.splitlines(keepends=True)
    chunks, buf = [], []
    in_fence = False
    in_fm = False

    for i, ln in enumerate(lines):
        # front matter：仅文件首个 --- 块
        if i == 0 and ln.strip() == '---':
            in_fm = True
        if in_fm:
            buf.append(ln)
            if i > 0 and ln.strip() == '---':
                in_fm = False
                chunks.append((True, ''.join(buf)))
                buf = []
            continue

        if FENCE_LINE.match(ln):
            if not in_fence:
                # 进入围栏：先把已积累的正文吐出去
                chunks.append((False, ''.join(buf)))
                buf = []
                in_fence = True
            buf.append(ln)
            # 判定闭合：同字符、长度 >= 开启时的长度（简化：同字符即可）
            if len(buf) > 1 and len(buf[-1].strip()) >= 3 and buf[-1].strip()[0] in '`~':
                closing = buf[-1].strip()
                opening = next((b for b in buf if FENCE_LINE.match(b)), '')
                if closing[0] == opening.strip()[0] and len(closing) >= len(opening.strip().split()[0]) and closing.strip().strip('`~') == '':
                    in_fence = False
                    chunks.append((True, ''.join(buf)))
                    buf = []
            continue

        buf.append(ln)

    if buf:
        chunks.append((in_fence, ''.join(buf)))
    return chunks


def format_pangu(text, fix_casing=False):
    """对正文补盘古之白；代码围栏与 front matter 原样保留。

    重要教训（2026-09-11）：
      · 绝不能对整篇做处理——朴素的全局正则会把代码里的 `C:/Users/name`
        也加上空格，并可能改动围栏语言标识。
      · 术语大小写纠正会误伤代码（```python → ```Python 破坏语法高亮）、
        链接锚文本与文件名，因此默认关闭（fix_casing=False）。
        如确需纠正，应只处理正文且逐条人工复核。
    """
    cjk = r'[\u4e00-\u9fa5\u3040-\u30ff\u3400-\u4dbf]'
    ans = r'[a-zA-Z0-9$#%@]'

    out = []
    for is_code, chunk in split_fences(text):
        if is_code:
            out.append(chunk)
            continue
        chunk = re.sub(f'({cjk})({ans})', r'\1 \2', chunk)
        chunk = re.sub(f'({ans})({cjk})', r'\1 \2', chunk)
        if fix_casing:
            for pattern, correct in TERMS_MAP.items():
                chunk = re.sub(pattern, correct, chunk, flags=re.IGNORECASE)
        out.append(chunk)
    return ''.join(out)

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
