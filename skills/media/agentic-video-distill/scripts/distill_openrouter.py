#!/usr/bin/env python3
"""
distill_openrouter.py — 基于 OpenRouter 免费多模态模型（如 Space Bunny）的视频降维视觉切片蒸馏执行器。

适用场景与工程背景：
  - 用户指定不调用云端 Gemini、或 Gemini 端点被限流/反代不可用时的快速多模态替代；
  - OpenRouter 平台硬性门槛：直传 video_url 要求账户余额 ≥ $1.00（免费层报 HTTP 402），且大体积 base64 视频易报 10054 连接重置；
  - 破局方案：将长视频通过 ffmpeg 抽帧打包为接触表（Contact Sheet，3x4 网格 JPG），走零门槛、完全免费的 image_url 路线；
  - 针对思考模型（Reasoning Models）：强制配置 reasoning: {effort: "low"} 与 max_tokens: 4096+，防思考 token 吃满导致输出为空。
"""

import os
import sys
import json
import base64
import argparse
import subprocess
import tempfile
import urllib.request
from pathlib import Path

DEFAULT_MODEL = "stealth/space-bunny-alpha"
DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_PROXY = "http://127.0.0.1:3067"

DEFAULT_PROMPT = """这是视频的时序幻灯片/画面网格接触表（Contact Sheet）。请结合画面中的文字、图表、菜单与参数，进行高精度的结构化技术蒸馏：
1. 【视频全景概括】：一句话总结核心主题、目标与适用场景；
2. 【关键时间线与步骤导航】：按画面展示的时序梳理完整核心脉络；
3. 【屏幕细节与关键画面证据】：逐字符提取画面中出现的 BIOS 菜单路径、表格参数、图表曲线、报错代码或关键键值；
4. 【底层机制与避坑红线】：深入剖析底层硬件/系统原理，明确指出导致翻车、冲突或失效的硬性红线；
5. 【推荐配置与排错清单】：给出可直接对照执行的操作步骤、参数建议或排错检查清单。
输出需保持专业、客观、严密，拒绝无意义套话。"""


def load_openrouter_key(cli_key: str = None) -> str:
    """获取 OpenRouter API Key，按优先级回退"""
    if cli_key:
        return cli_key
    for env_var in ["HERMES_CUSTOM_OPENROUTERFREE_API_KEY", "OPENROUTER_API_KEY", "OPENROUTERFREE_API_KEY"]:
        val = os.environ.get(env_var)
        if val:
            return val
    # 尝试从 ~/.hermes/.env 读取
    candidates = [
        Path.home() / "AppData/Local/hermes/.env",
        Path.home() / ".hermes/.env",
        Path.home() / ".env"
    ]
    for env_path in candidates:
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("HERMES_CUSTOM_OPENROUTERFREE_API_KEY="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
                        if line.startswith("OPENROUTER_API_KEY="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
    return ""


def generate_contact_sheets(video_path: Path, temp_dir: Path, num_sheets: int = 3) -> list[Path]:
    """使用 ffmpeg 将视频平均分为 N 个阶段，生成 3x4 (12 帧) 的紧凑接触表"""
    # 探查时长
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        dur = float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        dur = 600.0  # 默认 10 分钟

    # 12帧/张，N张共 12*N 帧
    total_frames = 12 * num_sheets
    interval = max(2.0, dur / total_frames)
    fps_val = 1.0 / interval

    sheets = []
    for idx in range(1, num_sheets + 1):
        start_t = (idx - 1) * (dur / num_sheets) + 1.0
        out_sheet = temp_dir / f"sheet_{idx}.jpg"
        # 截取对应区间生成 3x4 tile
        ff_cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{start_t:.2f}",
            "-i", str(video_path),
            "-vf", f"fps={fps_val:.4f},scale=640:-1,tile=3x4",
            "-frames:v", "1",
            str(out_sheet)
        ]
        res = subprocess.run(ff_cmd, capture_output=True)
        if res.returncode == 0 and out_sheet.exists() and out_sheet.stat().st_size > 0:
            sheets.append(out_sheet)

    return sheets


def query_openrouter_multimodal(
    images: list[Path],
    prompt: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    proxy_url: str = DEFAULT_PROXY,
    timeout: int = 240
) -> str:
    """向 OpenRouter 发送带 image_url 的多模态请求"""
    image_contents = []
    for img_path in images:
        b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")
        image_contents.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{b64}"
            }
        })

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": image_contents + [{"type": "text", "text": prompt}]
            }
        ],
        "reasoning": {"effort": "low"},  # 关键：限制思考预算，防正文被吃光
        "max_tokens": 4096,
        "temperature": 0.2
    }

    handlers = []
    if proxy_url:
        handlers.append(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
    opener = urllib.request.build_opener(*handlers)

    req = urllib.request.Request(
        DEFAULT_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/NousResearch/hermes-agent",
            "X-Title": "hermes-agent-multimodal-distill"
        }
    )

    with opener.open(req, timeout=timeout) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        msg = res["choices"][0]["message"]
        content = msg.get("content") or ""
        reasoning = msg.get("reasoning") or ""
        return content, reasoning


def main():
    parser = argparse.ArgumentParser(description="基于 OpenRouter 免费多模态模型的视频视觉切片蒸馏执行器")
    parser.add_argument("source", help="本地视频文件路径（.mp4/.mkv）或图像接触表路径")
    parser.add_argument("-o", "--output", help="输出 Markdown 报告路径（默认打印到 stdout）")
    parser.add_argument("-p", "--prompt", default=DEFAULT_PROMPT, help="自定义提示词")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help=f"OpenRouter 模型 ID（默认 {DEFAULT_MODEL}）")
    parser.add_argument("--key", help="OpenRouter API Key（默认自动从环境或 .env 读取）")
    parser.add_argument("--proxy", default=DEFAULT_PROXY, help=f"代理地址（默认 {DEFAULT_PROXY}）")
    parser.add_argument("--keep-sheets", action="store_true", help="保留生成的临时接触表图片")
    parser.add_argument("--sheets", type=int, default=3, help="切片网格张数（默认 3 张，每张 12 帧）")
    args = parser.parse_args()

    src_path = Path(args.source).resolve()
    if not src_path.exists():
        print(f"[错误] 源文件不存在: {src_path}", file=sys.stderr)
        return 1

    api_key = load_openrouter_key(args.key)
    if not api_key:
        print("[错误] 未找到有效的 OpenRouter API Key，请设置 HERMES_CUSTOM_OPENROUTERFREE_API_KEY", file=sys.stderr)
        return 1

    temp_dir = Path(tempfile.mkdtemp(prefix="or-distill-"))
    try:
        # 判断是视频还是现成图片
        if src_path.suffix.lower() in [".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv"]:
            print(f"[信息] 正在提取视频视觉接触表（{args.sheets} 张网格）...", file=sys.stderr)
            sheets = generate_contact_sheets(src_path, temp_dir, num_sheets=args.sheets)
            if not sheets:
                print("[错误] 无法从视频生成接触表，请检查 ffmpeg 安装", file=sys.stderr)
                return 1
        else:
            sheets = [src_path]

        print(f"[信息] 正在调用 OpenRouter 模型 {args.model} 进行多模态图文解析...", file=sys.stderr)
        content, reasoning = query_openrouter_multimodal(
            sheets, args.prompt, api_key, model=args.model, proxy_url=args.proxy
        )

        if not content and reasoning:
            content = f"<!-- REASONING ONLY -->\n{reasoning}"

        if args.output:
            out_file = Path(args.output).resolve()
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(content, encoding="utf-8")
            print(f"[成功] 蒸馏报告已写入: {out_file}", file=sys.stderr)
        else:
            print(content)

    finally:
        if not args.keep_sheets:
            for f in temp_dir.glob("*"):
                try:
                    f.unlink()
                except Exception:
                    pass
            try:
                temp_dir.rmdir()
            except Exception:
                pass


if __name__ == "__main__":
    sys.exit(main())
