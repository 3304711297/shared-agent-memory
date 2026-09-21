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

# ModelScope 同时支持 Range 续传（实测最终响应为 206 + Accept-Ranges: bytes），
# 且其 302 重定向 URL 里直接嵌入了 sha256，因此可复用同一套断点续传逻辑。
MODELSCOPE_REPO_URL = "https://modelscope.cn/api/v1/models/{repo}/repo?Revision={rev}&FilePath={path}"
MODELSCOPE_LIST_URL = "https://modelscope.cn/api/v1/models/{repo}/repo/files?Revision={rev}&Root={root}"
PROVIDERS = ("hf", "modelscope")


def build_url(provider: str, repo_id: str, filename: str, endpoint: str, revision: str = "master") -> str:
    """Construct the direct-download URL for a given provider."""
    if provider == "modelscope":
        from urllib.parse import quote
        return MODELSCOPE_REPO_URL.format(
            repo=repo_id, rev=revision, path=quote(filename, safe="")
        )
    return f"{endpoint.rstrip('/')}/{repo_id}/resolve/main/{filename}"


def extract_sha256_from_response(resp, url: str) -> str:
    """ModelScope embeds the sha256 in the redirect chain, e.g.
    .../lfs-objects/bb/21/<sha256>?filename=...  Return it when present."""
    import re
    candidates = [getattr(resp, "url", "") or "", url]
    for c in candidates:
        m = re.search(r"lfs-objects/(?:[0-9a-f]{2}/)+([0-9a-f]{64})", c)
        if m:
            return m.group(1)
    return ""


def resolve_modelscope_file(repo_id: str, filename: str, revision: str = "master"):
    """Look up size and sha256 from the ModelScope file listing."""
    from urllib.parse import quote
    opener = get_direct_opener()
    parts = filename.split("/")
    root = "/".join(parts[:-1]) if len(parts) > 1 else ""
    name = parts[-1]
    api = MODELSCOPE_LIST_URL.format(repo=repo_id, rev=revision,
                                     root=quote(root, safe=""))
    req = urllib.request.Request(api, headers={"User-Agent": "Mozilla/5.0"})
    with opener.open(req, timeout=20) as resp:
        data = json.loads(resp.read())
    for f in data.get("Data", {}).get("Files", []):
        if f.get("Name") == name:
            return f.get("Size"), (f.get("Sha256") or "").lower()
    return None, ""


def sha256_of(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


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


def download_single_file(url: str, local_path: str, total_size: int = None, timeout: int = DEFAULT_TIMEOUT,
                         expect_sha256: str = ""):
    part_path = local_path + ".part"
    os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)

    if os.path.exists(local_path):
        current_sz = os.path.getsize(local_path)
        if total_size is not None and current_sz == total_size:
            if expect_sha256:
                got = sha256_of(local_path)
                if got != expect_sha256:
                    print(f"[校验失败] sha256 不符，重新下载: {os.path.basename(local_path)}")
                    print(f"  期望: {expect_sha256}\n  实际: {got}")
                    os.remove(local_path)
                    return download_single_file(url, local_path, total_size, timeout, expect_sha256)
                print(f"[已跳过] 文件已完整且 sha256 校验通过: {os.path.basename(local_path)}")
            else:
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
    MAX_RETRIES = 10  # 硬上限：防止服务端异常时不带 total_size 的无限重试挂起
    zero_progress = 0

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

                # ModelScope 对非 LFS 的普通小文件由网关直接返回，且不规范：
                #   1) 即使请求成功也回 200（而非 206），但带 Content-Range 头；
                #   2) 对开放式尾部 Range（bytes=N-）会声明错误的 Content-Length
                #      （例如声明 200 却发出 627 字节），触发 IncompleteRead。
                # LFS 大文件（即实际要下的权重）会 302 到 CDN 直链并正确返回 206，
                # 所以这里仅在"检测到 200 + 已有断点"时保守退化为整文件重下。
                if downloaded > 0 and status == 200:
                    print(f"\n[提示] 服务端以 200 响应（非 206）。该源可能不支持开放式尾部 Range，"
                          f"丢弃 {format_size(downloaded)} 断点，改为整文件下载。")
                    downloaded = 0
                    if os.path.exists(part_path):
                        os.remove(part_path)

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
                if expect_sha256:
                    got = sha256_of(local_path)
                    if got != expect_sha256:
                        print(f"[校验失败] sha256 不符: {local_path}")
                        print(f"  期望: {expect_sha256}\n  实际: {got}")
                        os.replace(local_path, part_path)  # 保留文件供排查，不静默删除
                        return False
                    print(f"[完成] sha256 校验通过，成功落盘: {local_path}")
                else:
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
            if retry_count > MAX_RETRIES:
                print(f"\n[放弃] 连续 {MAX_RETRIES} 次重试均失败，已停止。")
                print(f"  最后一次错误: {e}")
                print(f"  断点已保留在: {part_path}")
                print("  排查建议: 确认 -f 指定的文件在仓库中确实存在（ModelScope 上不存在时会")
                print("            返回 JSON 错误体而非 404）；确认 --repo / --revision 拼写正确。")
                return False
            print(f"\n[网络抖动重试 {retry_count}] {e}，2 秒后自动断点续传...")
            time.sleep(2)


def main():
    parser = argparse.ArgumentParser(description="Hugging Face / ModelScope 绝对断点续传下载器")
    parser.add_argument("--provider", "-p", default="hf", choices=PROVIDERS,
                        help="下载源：hf=国内镜像 hf-mirror.com（默认）；modelscope=魔搭（镜像站也挂时的备选，带 sha256 自动校验）")
    parser.add_argument("--repo", "-r", required=True, help="模型仓库 ID，例如 Qwen/Qwen-Image-2.1 或 Comfy-Org/Qwen-Image-2.1")
    parser.add_argument("--file", "-f", default=None, help="指定下载的相对路径文件名，如 text_encoder/model-00001-of-00004.safetensors")
    parser.add_argument("--local-dir", "-o", required=True, help="本地保存目标目录")
    parser.add_argument("--endpoint", "-e", default=DEFAULT_ENDPOINT, help=f"HF 镜像源地址（默认: {DEFAULT_ENDPOINT}，仅 --provider hf 时生效）")
    parser.add_argument("--revision", "-R", default="master", help="ModelScope 分支名（默认: master）")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help="单次读取超时时间（秒，默认: 60）")

    args = parser.parse_args()

    repo_id = args.repo.strip()
    endpoint = args.endpoint.strip().rstrip("/")
    local_dir = os.path.abspath(args.local_dir.strip())
    provider = args.provider

    if provider == "modelscope":
        if not args.file:
            print("[提示] ModelScope 逐目录列举与 HF 语义不同，请用 -f 指定具体文件；"
                  "批量时用 repo/files 接口取出路径后循环调用。")
            sys.exit(1)
        filename = args.file.strip()
        # 若 --local-dir 已经包含该文件的相对父目录（例如 -f a/b.safetensors 且
        # -o .../a），不再拼接，否则会写出 .../a/a/b.safetensors 这种双写路径。
        norm = local_dir.replace("\\", "/").rstrip("/")
        parent = "/".join(filename.split("/")[:-1]).strip("/")
        if parent and norm.endswith("/" + parent):
            dest = os.path.join(local_dir, os.path.basename(filename))
        else:
            dest = os.path.join(local_dir, filename)

        try:
            size, sha = resolve_modelscope_file(repo_id, filename, args.revision)
        except Exception as e:
            size, sha = None, ""
            print(f"[警告] 列表接口查询失败（{e}），将依赖重定向链提取 sha256")

        # 拿不到 size 时无法判断完成条件，脚本会退化为“读到 EOF 为止”。
        # ModelScope 对不存在的文件返回 200+JSON 错误体而非 404，因此预检一次，
        # 避免把错误体当数据写入，或在不存在的文件上无谓重试。
        if size is None:
            try:
                size, sha2 = resolve_modelscope_file(repo_id, filename, args.revision)
                if not sha:
                    sha = sha2
            except Exception:
                pass
        if size is None:
            print(f"[错误] 无法确认 {filename} 在该仓库中存在（列表接口未返回其 Size）。")
            print("  请先用列表接口核对文件名确实存在，例如：")
            print(f"  curl -sS \"https://modelscope.cn/api/v1/models/{repo_id}/repo/files?Revision={args.revision}&Root=\"")
            print("  ModelScope 请求不存在的文件时返回 200 + JSON 错误体（非 404），盲下会写出垃圾文件。")
            sys.exit(2)

        url = build_url(provider, repo_id, filename, endpoint, args.revision)
        if sha:
            print(f"[*] 已从 ModelScope 列表取得 sha256: {sha}")
        ok = download_single_file(url, dest, total_size=size, timeout=args.timeout,
                                  expect_sha256=sha)
        sys.exit(0 if ok else 4)

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
