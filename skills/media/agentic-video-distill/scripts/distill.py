#!/usr/bin/env python3
"""
distill.py — 基于 Gemini Agentic Video Understanding 的长视频/屏幕录制高密度知识蒸馏执行器
（集成当前会话模型动态感知、SSE流式保活防断连、主备API Key自动故障转移）
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path

DEFAULT_PROMPT = """请对该视频进行高精度的结构化技术蒸馏：
1. 【视频全景概括】：一句话总结核心主题、目标与适用场景；
2. 【关键时间线与步骤导航】：按时间戳（格式 MM:SS）梳理完整核心脉络；
3. 【屏幕细节与关键画面证据】（重点）：
   - 提取视频中出现的主板 UEFI/BIOS 菜单、软件界面、架构拓扑图、关键参数数值或报错代码；
   - 明确指出屏幕画面的具体层级路径或报错根因；
4. 【底层机制与避坑红线】：深入剖析底层硬件/系统原理，明确指出可能导致翻车、冲突或失效的硬性红线；
5. 【结构化配置/操作清单】：给出可直接抄作业的最终推荐配置、命令或排错检查清单。
输出需保持专业、客观、严密，拒绝无意义的客套与套话。"""

AUTH_FILE = Path.home() / "AppData/Local/hermes/auth/gemini_video_keys.json"

def ensure_proxy():
    """自动对齐本地代理，确保连接 Google 服务"""
    if not os.environ.get("HTTPS_PROXY") and not os.environ.get("ALL_PROXY"):
        proxy_url = "http://127.0.0.1:3067"
        os.environ["HTTP_PROXY"] = proxy_url
        os.environ["HTTPS_PROXY"] = proxy_url
        os.environ["ALL_PROXY"] = proxy_url

def load_keys(cli_key: str = None) -> list[str]:
    """获取可用 API Key 列表（优先级：CLI传参 > 环境变量 > 本地凭据文件）"""
    keys = []
    if cli_key:
        keys.append(cli_key)
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key and env_key not in keys:
        keys.append(env_key)
    env_backup = os.environ.get("GEMINI_API_KEY_BACKUP")
    if env_backup and env_backup not in keys:
        keys.append(env_backup)

    if AUTH_FILE.exists():
        try:
            with open(AUTH_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                if isinstance(d, dict):
                    primary = d.get("primary")
                    backup = d.get("backup")
                    if primary and primary not in keys:
                        keys.append(primary)
                    if backup and backup not in keys:
                        keys.append(backup)
        except Exception:
            pass

    return keys

def detect_current_gemini_model() -> str:
    """智能动态探测当前环境首选的 Gemini 模型"""
    state_db = Path.home() / "AppData/Local/hermes/state.db"
    if state_db.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(str(state_db))
            cur = conn.cursor()
            cur.execute("SELECT model FROM sessions ORDER BY last_activity_at DESC LIMIT 1")
            row = cur.fetchone()
            if row and row[0] and "gemini" in row[0].lower():
                return row[0].strip()
        except Exception:
            pass

    cfg_path = Path.home() / "AppData/Local/hermes/config.yaml"
    if cfg_path.exists():
        try:
            import yaml
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            m = cfg.get("model", {}).get("default", "")
            if "gemini" in m.lower():
                return m
        except Exception:
            pass

    return os.environ.get("GEMINI_VIDEO_MODEL", "gemini-3.8-flash")

def main():
    detected_model = detect_current_gemini_model()
    parser = argparse.ArgumentParser(description="Gemini Agentic Video 知识蒸馏工具")
    parser.add_argument("source", help="本地视频文件路径（MP4/MKV等）或公开 YouTube URL（https://youtu.be/...）")
    parser.add_argument("-m", "--model", default=detected_model, help=f"指定模型，默认自适应探测当前活跃模型: {detected_model}（支持显式覆盖）")
    parser.add_argument("-p", "--prompt", default=DEFAULT_PROMPT, help="自定义提炼提示词")
    parser.add_argument("-o", "--output", help="输出 Markdown 文件路径，默认输出到同名 .md 或 stdout")
    parser.add_argument("--key", help="Google AI Studio API Key（默认从环境变量或本地凭据池读取）")
    parser.add_argument("--dry-run", action="store_true", help="测试参数与环境连通性，不实际提交分析请求")
    args = parser.parse_args()

    ensure_proxy()
    keys = load_keys(args.key)

    try:
        from google import genai
        import httpx
    except ImportError:
        print("[错误] 依赖缺失。请运行：pip install google-genai httpx", file=sys.stderr)
        sys.exit(1)

    is_youtube = args.source.startswith("http://") or args.source.startswith("https://")
    
    if args.dry_run:
        print(f"[Dry-Run] 模式: {'YouTube 直连' if is_youtube else '本地文件上传'}")
        print(f"[Dry-Run] 目标: {args.source}")
        print(f"[Dry-Run] 模型: {args.model}")
        print(f"[Dry-Run] 代理: {os.environ.get('HTTPS_PROXY')}")
        print(f"[Dry-Run] 发现可用 API Key 数量: {len(keys)}")
        print(f"[Dry-Run] 代理式视频理解 processing='agentic' 参数就绪。")
        return

    if not keys:
        print("[错误] 未检测到 Google API Key。请设置 GEMINI_API_KEY 环境变量或通过 --key 参数传入。", file=sys.stderr)
        print("提示：可在 https://aistudio.google.com/app/apikey 获取个人免费/开发凭据。", file=sys.stderr)
        sys.exit(1)

    # 尝试轮询 Key（主用优先，429/配额不足时自动顺延备用）
    last_err = None
    for idx, current_key in enumerate(keys):
        masked_key = current_key[:6] + "..." + current_key[-4:]
        print(f"[1/4] 初始化 Google GenAI 客户端 (Key #{idx+1}: {masked_key}, Model: {args.model})...")
        client = genai.Client(api_key=current_key)

        try:
            if is_youtube:
                print(f"[2/4] 识别为 YouTube 远程视频，启用云端直接流式解析: {args.source}")
                video_input = {
                    "type": "video",
                    "uri": args.source,
                    "processing": "agentic"
                }
            else:
                video_path = Path(args.source).resolve()
                if not video_path.exists():
                    print(f"[错误] 本地视频文件不存在: {video_path}", file=sys.stderr)
                    sys.exit(1)

                file_size_mb = video_path.stat().st_size / (1024 * 1024)
                print(f"[2/4] 上传本地视频至 Google File API ({file_size_mb:.1f} MB): {video_path.name}...")
                
                video_file = client.files.upload(file=str(video_path))
                print(f"      文件 ID: {video_file.name}, 等待服务端切片就绪...")
                
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = client.files.get(name=video_file.name)
                    
                if video_file.state.name != "ACTIVE":
                    raise RuntimeError(f"视频服务端切片失败，状态为: {video_file.state.name}")
                    
                print("      服务端索引准备完毕。")
                video_input = {
                    "type": "video",
                    "uri": video_file.uri,
                    "mime_type": video_file.mime_type or "video/mp4",
                    "processing": "agentic"
                }

            # 自动探测或传参的模型，支持高负载时的动态平替 fallback
            models_to_try = [args.model]
            if "3.8" in args.model:
                models_to_try.append("gemini-3.7-flash")
            elif "3.7" in args.model:
                models_to_try.append("gemini-3.8-flash")

            success = False
            for target_model in models_to_try:
                print(f"[3/4] 提交 Interactions API (Model: {target_model}, SSE 流式长连接)...")
                print("      模型启动 Think-Act-Observe 自主多模态探查循环...\n" + "-"*60)
                start_time = time.time()
                
                try:
                    stream = client.interactions.create(
                        model=target_model,
                        input=[
                            video_input,
                            {"type": "text", "text": args.prompt}
                        ],
                        stream=True,
                        timeout=httpx.Timeout(600.0, connect=60.0)
                    )
                    
                    collected_text = []
                    usage_info = None

                    for event in stream:
                        # 捕获实时生成的文字增量 (TextDelta)
                        delta = getattr(event, "delta", None)
                        if delta:
                            chunk = getattr(delta, "text", None)
                            if chunk:
                                print(chunk, end="", flush=True)
                                collected_text.append(chunk)
                        
                        # 捕获异常事件
                        if type(event).__name__ == "ErrorEvent":
                            err_obj = getattr(event, "error", None)
                            raise RuntimeError(f"Google 服务端事件报错: {err_obj}")

                        # 捕获最终完成事件与使用量
                        interaction = getattr(event, "interaction", None)
                        if interaction:
                            usage = getattr(interaction, "usage", None)
                            if usage:
                                usage_info = usage

                    elapsed = time.time() - start_time
                    print("\n" + "-"*60)
                    print(f"      分析完成！耗时: {elapsed:.1f} 秒。")

                    full_output = "".join(collected_text).strip()
                    if full_output:
                        success = True
                        break
                except Exception as model_err:
                    print(f"\n[提示] 模型 {target_model} 遇到服务端波动: {model_err}，尝试候选模型...", file=sys.stderr)

            if not success:
                raise RuntimeError("所有候选模型均未能返回有效分析内容")

            if args.output:
                out_path = Path(args.output).resolve()
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(full_output, encoding="utf-8")
                print(f"[4/4] 结构化 Markdown 已写入: {out_path}")

            return  # 成功，结束退出

        except Exception as e:
            print(f"\n[警告] Key #{idx+1} 调用异常: {e}", file=sys.stderr)
            last_err = e
            if idx + 1 < len(keys):
                print("[重试] 自动切换至备用 API Key 重新执行...\n", file=sys.stderr)
                time.sleep(1)

    print(f"\n[失败] 所有可用 API Key 均执行失败。最终错误: {last_err}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
