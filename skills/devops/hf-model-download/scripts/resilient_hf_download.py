#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resilient Hugging Face Model Downloader via Domestic Mirrors
支持单文件/多文件绝对断点续传、抗弱网抖动超时重试、自动屏蔽外部代理直连国内镜像
"""

import os
import sys
import time
import json
import argparse
import urllib.request
import urllib.error

DEFAULT_ENDPOINT = "https://hf-mirror.com"
DEFAULT_TIMEOUT = 60  # 放宽单次读取超时到 60s，防弱网抖动断流
CHUNK_SIZE = 512 * 1024  # 512KB chunks


def format_size(b: float) -> str:
    if b >= 1e9:
        return f"{b / 1e9:.2f} GB"
    elif b >= 1e6:
        return f"{b / 1e6:.2f} MB"
    elif b >= 1e3:
        return f"{b / 1e3:.2f} KB"
    return f"{b} B"


def get_direct_opener():
    # 强制不走本地任何 HTTP/HTTPS/SOCKS 代理，直连国内镜像源
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def get_file_metadata(repo_id: str, filename: str, endpoint: str = DEFAULT_ENDPOINT):
    url = f"{endpoint.rstrip('/')}/{repo_id}/resolve/main/{filename}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Range": "bytes=0-0"
    }
    opener = get_direct_opener()
    req = urllib.request.Request(url, headers=headers)
    try:
        with opener.open(req, timeout=15) as resp:
            content_range = resp.headers.get("Content-Range", "")
            if "/" in content_range:
                total_size = int(content_range.split("/")[-1])
                return url, total_size
            content_length = resp.headers.get("Content-Length")
            if content_length:
                return url, int(content_length)
    except Exception as e:
        pass
    return url, None


def download_single_file(url: str, local_path: str, total_size: int = None, timeout: int = DEFAULT_TIMEOUT):
    part_path = local_path + ".part"
    os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)

    if os.path.exists(local_path):
        current_sz = os.path.getsize(local_path)
        if total_size is not None and current_sz == total_size:
            print(f"[已跳过] 文件已存在且完整: {os.path.basename(local_path)} ({format_size(current_sz)})")
            return True
        elif total_size is None and current_sz > 0:
            print(f"[已存在] 文件已存在: {os.path.basename(local_path)} ({format_size(current_sz)})")
            return True

    downloaded = os.path.getsize(part_path) if os.path.exists(part_path) else 0
    filename = os.path.basename(local_path)

    print("-" * 65)
    print(f"开始下载: {filename}")
    print(f"保存路径: {local_path}")
    if total_size:
        print(f"文件大小: {format_size(total_size)} ({total_size} 字节)")
    if downloaded > 0:
        if total_size:
            pct = downloaded / total_size * 100
            print(f"检测到断点: 已下载 {format_size(downloaded)} ({pct:.1f}%)，正在原地续传...")
        else:
            print(f"检测到断点: 已下载 {format_size(downloaded)}，正在原地续传...")
    print("-" * 65)

    opener = get_direct_opener()
    retry_count = 0

    while total_size is None or downloaded < total_size:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        if downloaded > 0:
            headers["Range"] = f"bytes={downloaded}-"

        req = urllib.request.Request(url, headers=headers)
        try:
            with opener.open(req, timeout=timeout) as resp:
                status = resp.status
                if status not in (200, 206):
                    raise urllib.error.HTTPError(url, status, f"Unexpected HTTP status {status}", resp.headers, None)

                # 如果没有预先拿到 total_size，从响应头中补全
                if total_size is None:
                    cr = resp.headers.get("Content-Range", "")
                    if "/" in cr:
                        total_size = int(cr.split("/")[-1])
                    else:
                        cl = resp.headers.get("Content-Length")
                        if cl:
                            total_size = downloaded + int(cl)

                with open(part_path, "ab") as f:
                    last_time = time.time()
                    last_downloaded = downloaded

                    while total_size is None or downloaded < total_size:
                        chunk = resp.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        now = time.time()
                        if now - last_time >= 1.0:
                            speed = (downloaded - last_downloaded) / (now - last_time)
                            if total_size:
                                percent = (downloaded / total_size) * 100
                                eta_s = (total_size - downloaded) / max(speed, 1)
                                eta_str = f"剩余: {eta_s / 60:.1f}分"
                                bar_len = 25
                                filled = int(bar_len * percent / 100)
                                bar = "█" * filled + " " * (bar_len - filled)
                                sys.stdout.write(
                                    f"\r[{bar}] {percent:.1f}% | {format_size(downloaded)} / {format_size(total_size)} | "
                                    f"{format_size(speed)}/s | {eta_str}   "
                                )
                            else:
                                sys.stdout.write(
                                    f"\r已下载: {format_size(downloaded)} | 速度: {format_size(speed)}/s   "
                                )
                            sys.stdout.flush()
                            last_time = now
                            last_downloaded = downloaded
                            retry_count = 0

            # 校验完成并落盘
            if total_size is not None and downloaded >= total_size:
                sys.stdout.write("\n")
                if os.path.exists(local_path):
                    os.remove(local_path)
                os.rename(part_path, local_path)
                print(f"[完成] 校验通过，成功落盘: {local_path}")
                return True
            elif total_size is None and downloaded > 0:
                sys.stdout.write("\n")
                if os.path.exists(local_path):
                    os.remove(local_path)
                os.rename(part_path, local_path)
                print(f"[完成] 下载完成: {local_path}")
                return True

        except KeyboardInterrupt:
            print("\n[中断] 用户手动暂停。断点进度已完整保存，下次运行原地继续。")
            sys.exit(0)
        except Exception as e:
            retry_count += 1
            print(f"\n[网络抖动重试 {retry_count}] {e}，2 秒后自动断点续传...")
            time.sleep(2)


def main():
    parser = argparse.ArgumentParser(description="Hugging Face / 国内镜像绝对断点续传下载器")
    parser.add_argument("--repo", "-r", required=True, help="模型仓库 ID，例如 Qwen/Qwen-Image-2.1")
    parser.add_argument("--file", "-f", default=None, help="指定下载的相对路径文件名，如 text_encoder/model-00001-of-00004.safetensors")
    parser.add_argument("--local-dir", "-o", required=True, help="本地保存目标目录")
    parser.add_argument("--endpoint", "-e", default=DEFAULT_ENDPOINT, help=f"镜像源地址（默认: {DEFAULT_ENDPOINT}）")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help="单次读取超时时间（秒，默认: 60）")

    args = parser.parse_args()

    repo_id = args.repo.strip()
    endpoint = args.endpoint.strip().rstrip("/")
    local_dir = os.path.abspath(args.local_dir.strip())

    if not args.file:
        print(f"[*] 未指定单个文件，正在通过镜像 API 查询 {repo_id} 仓库文件列表...")
        api_url = f"{endpoint}/api/models/{repo_id}"
        opener = get_direct_opener()
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with opener.open(req, timeout=15) as resp:
                data = json.loads(resp.read())
                siblings = data.get("siblings", [])
                files = [s["rfilename"] for s in siblings if s.get("rfilename")]
                print(f"[*] 发现 {len(files)} 个文件，开始逐个断点续传...")
                for rfilename in files:
                    url = f"{endpoint}/{repo_id}/resolve/main/{rfilename}"
                    dest = os.path.join(local_dir, rfilename)
                    # 查询大小
                    _, sz = get_file_metadata(repo_id, rfilename, endpoint)
                    download_single_file(url, dest, total_size=sz, timeout=args.timeout)
        except Exception as e:
            print(f"[错误] 查询仓库列表失败: {e}")
            print("[提示] 请使用 -f 参数指定具体文件名下载，例如: -f text_encoder/model-00001-of-00004.safetensors")
            sys.exit(1)
    else:
        filename = args.file.strip()
        url, total_size = get_file_metadata(repo_id, filename, endpoint)
        dest = os.path.join(local_dir, filename)
        download_single_file(url, dest, total_size=total_size, timeout=args.timeout)


if __name__ == "__main__":
    main()
