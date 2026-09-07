#!/usr/bin/env python3
"""Edge Dev 浏览器书签本地极速检索工具。

直接读取本地 Edge Dev 原始书签 JSON 文件，零同步延迟、内存秒级检索（<20ms）。
严格本地运行，不上传任何私密链接，支持关键词检索、分类文件夹过滤与多格式输出。
"""

import argparse
import json
import os
import sys

BOOKMARKS_PATH = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\Edge Dev\User Data\Default\Bookmarks"
)


def load_bookmarks_raw(path=BOOKMARKS_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"未找到 Edge Dev 书签文件: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_bookmarks(node, folder_path=""):
    items = []
    if isinstance(node, dict):
        node_type = node.get("type")
        name = node.get("name", "")
        if node_type == "folder":
            current_folder = f"{folder_path}/{name}" if folder_path else name
            for child in node.get("children", []):
                items.extend(flatten_bookmarks(child, current_folder))
        elif node_type == "url":
            items.append({
                "title": name,
                "url": node.get("url", ""),
                "folder": folder_path,
                "date_added": node.get("date_added", ""),
            })
        if "roots" in node:
            for root_key, root_val in node["roots"].items():
                items.extend(flatten_bookmarks(root_val, root_key))
    return items


def search_bookmarks(query="", folder="", limit=20, path=BOOKMARKS_PATH):
    data = load_bookmarks_raw(path)
    all_bookmarks = flatten_bookmarks(data)
    
    q_lower = query.lower().strip()
    f_lower = folder.lower().strip()
    
    matches = []
    for b in all_bookmarks:
        # 文件夹过滤
        if f_lower and f_lower not in b["folder"].lower():
            continue
        # 关键词匹配（标题、URL、所属文件夹）
        if q_lower:
            text = f"{b['title']} {b['url']} {b['folder']}".lower()
            if q_lower not in text:
                continue
        matches.append(b)
        if limit and len(matches) >= limit:
            break
            
    return matches, len(all_bookmarks)


def list_top_folders(path=BOOKMARKS_PATH, min_count=5):
    data = load_bookmarks_raw(path)
    all_bookmarks = flatten_bookmarks(data)
    folder_counts = {}
    for b in all_bookmarks:
        f = b["folder"]
        folder_counts[f] = folder_counts.get(f, 0) + 1
    sorted_folders = sorted(
        [(k, v) for k, v in folder_counts.items() if v >= min_count],
        key=lambda x: x[1],
        reverse=True,
    )
    return sorted_folders, len(all_bookmarks)


def main():
    parser = argparse.ArgumentParser(description="Edge Dev 浏览器书签本地极速检索器")
    parser.add_argument("query", nargs="?", default="", help="搜索关键词（标题/URL/文件夹）")
    parser.add_argument("-f", "--folder", default="", help="按文件夹名称过滤")
    parser.add_argument("-n", "--limit", type=int, default=20, help="最多返回数量 (默认 20)")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    parser.add_argument("--folders", action="store_true", help="列出主要文件夹及其书签数量")
    
    args = parser.parse_args()
    
    if args.folders:
        folders, total = list_top_folders()
        print(f"总书签数: {total} | 核心分类文件夹 (>=5 条):")
        for f, count in folders[:40]:
            print(f"  {count:4d} | {f}")
        return

    matches, total = search_bookmarks(args.query, args.folder, args.limit)
    
    if args.json:
        print(json.dumps({
            "total_bookmarks": total,
            "matched_count": len(matches),
            "results": matches,
        }, ensure_ascii=False, indent=2))
        return

    print(f"已索引 {total} 个本地书签 | 检索词: '{args.query}' (文件夹: '{args.folder}') -> 匹配 {len(matches)} 条:\n")
    for idx, item in enumerate(matches, 1):
        print(f"{idx}. [{item['folder']}] {item['title']}")
        print(f"   URL: {item['url']}")


if __name__ == "__main__":
    main()
