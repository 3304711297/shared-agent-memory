#!/usr/bin/env python3
"""
distill.py — 基于 Gemini Agentic Video Understanding 的长视频/屏幕录制高密度知识蒸馏执行器
（已集成当前会话模型智能感知与动态探测）
"""

import os
import sys
import time
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

def ensure_proxy():
    """自动对齐本地代理，确保连接 Google 服务"""
    if not os.environ.get("HTTPS_PROXY") and not os.environ.get("ALL_PROXY"):
        proxy_url = "http://127.0.0.1:3067"
        os.environ["HTTP_PROXY"] = proxy_url
        os.environ["HTTPS_PROXY"] = proxy_url
        os.environ["ALL_PROXY"] = proxy_url

def detect_current_gemini_model() -> str:
    """
    智能动态探测当前环境首选的 Gemini 模型：
    1. 优先读取 Hermes state.db 当前活跃会话的模型（若你切成了 3.9，自动跟随 3.9）；
    2. 若当前会话是非 Gemini 模型（如切到 Claude/GLM），自动读取 config.yaml 或环境变量中的 Gemini 基准；
    3. 若均为非 Gemini 模型，智能回退至最新兼容基线 gemini-3.8-flash。
    """
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
    parser.add_argument("--key", help="Google AI Studio API Key（默认从 GEMINI_API_KEY 环境变量读取）")
    parser.add_argument("--dry-run", action="store_true", help="测试参数与环境连通性，不实际提交分析请求")
    args = parser.parse_args()

    ensure_proxy()

    api_key = args.key or os.environ.get("GEMINI_API_KEY")

    try:
        from google import genai
    except ImportError:
        print("[错误] 未安装 google-genai SDK。请运行以下命令安装：", file=sys.stderr)
        print("  pip install google-genai", file=sys.stderr)
        sys.exit(1)

    is_youtube = args.source.startswith("http://") or args.source.startswith("https://")
    
    if args.dry_run:
        print(f"[Dry-Run] 模式: {'YouTube 直连' if is_youtube else '本地文件上传'}")
        print(f"[Dry-Run] 目标: {args.source}")
        print(f"[Dry-Run] 模型: {args.model}")
        print(f"[Dry-Run] 代理: {os.environ.get('HTTPS_PROXY')}")
        print(f"[Dry-Run] API Key: {'已配置' if api_key else '未配置（运行时需传入）'}")
        print(f"[Dry-Run] 代理式视频理解 processing='agentic' 参数就绪。")
        return

    if not api_key:
        print("[错误] 未检测到 Google API Key。请设置 GEMINI_API_KEY 环境变量或通过 --key 参数传入。", file=sys.stderr)
        print("提示：可在 https://aistudio.google.com/app/apikey 获取个人免费/开发凭据。", file=sys.stderr)
        sys.exit(1)

    print(f"[1/4] 初始化 Google GenAI 客户端 (Model: {args.model})...")
    client = genai.Client(api_key=api_key)

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
            print(f"[错误] 视频服务端处理失败，状态为: {video_file.state.name}", file=sys.stderr)
            sys.exit(1)
            
        print("      服务端索引准备完毕。")
        video_input = {
            "type": "video",
            "uri": video_file.uri,
            "mime_type": video_file.mime_type or "video/mp4",
            "processing": "agentic"
        }

    print("[3/4] 提交 Interactions API，模型启动 Think-Act-Observe 自主多模态探查循环...")
    start_time = time.time()
    
    interaction = client.interactions.create(
        model=args.model,
        input=[
            video_input,
            {"type": "text", "text": args.prompt}
        ]
    )
    
    elapsed = time.time() - start_time
    print(f"      分析完成！耗时: {elapsed:.1f} 秒。")

    output_content = interaction.output_text
    
    usage = getattr(interaction, "usage", None)
    if usage:
        print(f"      Token 消耗: 思考/推理={getattr(usage, 'total_thought_tokens', 0)}, 工具调取={getattr(usage, 'total_tool_use_tokens', 0)}, 总计={getattr(usage, 'total_tokens', 0)}")

    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_content, encoding="utf-8")
        print(f"[4/4] 结构化 Markdown 已写入: {out_path}")
    else:
        print("\n" + "="*50 + " 提炼结果 " + "="*50)
        print(output_content)
        print("="*108)

if __name__ == "__main__":
    main()
