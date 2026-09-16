#!/usr/bin/env python3
"""
agentic-video-cpa.py — 让 cpa 端点（本地反代）的 gemini-3.8-flash-high 用「工具集」自主分析视频。

为什么需要这个脚本：
  - Hermes 内置 video_analyze 走主聊天模型链路；主模型不支持视频输入时直接返回「视频内容已被过滤」，不可用。
  - Google 官方直连（distill.py）依赖 GEMINI_API_KEY 与官方模型 ID，且本机出口 SSL 不稳、模型名易失配。
  - 本脚本改走本地 cpa 反代端点，模型自带视觉 + 工具调用能力，能自己决定抽哪一帧、放大哪块区域。

设计要点（实测沉淀，勿删）：
  1. 【收敛纪律】不给预算上限时模型会无限次重复放大同一区域（实测 14 轮不收敛、上下文滚到 63 万 token）。
     因此：限定 TOOL_BUDGET 次工具调用 + 只回带最近 KEEP_RECENT_SETS 组工具结果 + 强制每轮写「已确认」笔记。
  2. 【防幻觉锚点】低分辨率小字极易诱发先验填补（实测 gemini-3-flash-preview 编出 GPT-4o/o1-preview/Llama 405B 等画面中根本不存在的 UI）。
     SYSTEM 里必须显式禁止用常见 AI 界面先验去补全，并要求小字先放大再读。
  3. 【ASCII 文件名】Google GenAI 上传路径含中文会报 'ascii' codec can't encode（multipart 头编码）。
     走本脚本的 base64 内联方式不受影响，但若改用官方上传仍须切 ASCII 文件名。

用法：
  python agentic-video-cpa.py <视频路径> [-o 输出.md] [--endpoint http://127.0.0.1:18080/v1/chat/completions]
  python agentic-video-cpa.py <视频路径> --question "这次点击触发了什么？"
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_ENDPOINT = "http://127.0.0.1:18080/v1/chat/completions"
DEFAULT_MODEL = "gemini-3.8-flash-high"
TOOL_BUDGET = 8          # 工具调用总预算（超出即强制收口）
KEEP_RECENT_SETS = 3     # 只回带最近 N 组工具结果，防上下文滚雪球
MAX_ROUNDS = 10


def b64_data_uri(p: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def ffprobe_info(video: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-show_entries", "stream=width,height,codec_type,r_frame_rate",
                        "-of", "json", str(video)], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return {"duration": None, "width": None, "height": None, "fps": 30.0}
    w = h = None
    for s in d.get("streams", []):
        if s.get("codec_type") == "video":
            w, h = s.get("width"), s.get("height")
            break
    fps = 30.0
    for s in d.get("streams", []):
        if s.get("codec_type") == "video":
            fr = s.get("r_frame_rate", "30/1")
            try:
                num, den = fr.split("/"); fps = float(num) / float(den or 1)
            except Exception:
                pass
            break
    try:
        dur = float(d.get("format", {}).get("duration"))
    except Exception:
        dur = None
    return {"duration": dur, "width": w, "height": h, "fps": fps}


class Analyzer:
    def __init__(self, video: Path, workdir: Path):
        self.video = video
        self.workdir = workdir
        self.frames = workdir / "frames"
        self.frames.mkdir(parents=True, exist_ok=True)
        self.info = ffprobe_info(video)
        self._prepare_all_frames()

    def _prepare_all_frames(self):
        if not list(self.frames.glob("all_*.png")):
            subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-i", str(self.video),
                            "-fps_mode", "passthrough", "-y", str(self.frames / "all_%04d.png")],
                           capture_output=True)
        self.ALL = sorted(self.frames.glob("all_*.png"))

    def frame_at(self, t: float) -> Path:
        out = self.frames / f"t{t:.3f}.png"
        if not out.exists():
            subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-ss", f"{t:.3f}",
                            "-i", str(self.video), "-frames:v", "1", "-y", str(out)], capture_output=True)
        return out

    # ---------- tools ----------
    def t_duration(self):
        i = self.info
        return {"text": f"时长 {i['duration']}s，{i['fps']:.0f}fps，分辨率 {i['width']}x{i['height']}，共 {len(self.ALL)} 帧。"}

    def t_change_segments(self):
        try:
            from PIL import Image
            import numpy as np
        except ImportError:
            return {"text": "PIL/numpy 缺失，无法计算变化点；请直接抽帧观察。"}
        arrs = [np.asarray(Image.open(p).convert("L"), dtype=np.int16) for p in self.ALL]
        segs = []
        for i in range(1, len(arrs)):
            d = int(np.abs(arrs[i] - arrs[i - 1]).sum())
            if d > 30000:
                segs.append(f"{i/self.info['fps']:.2f}s(强度{d})")
        return {"text": f"画面显著变化时刻（{len(segs)} 个）：" + ("，".join(segs)[:900] if segs else "无明显变化")}

    def t_extract(self, t):
        p = self.frame_at(float(t))
        return {"img": b64_data_uri(p, "image/png"),
                "note": f"t={t}s 整帧 {self.info['width']}x{self.info['height']}（未放大）"}

    def t_crop(self, t, x, y, width, height, zoom=4):
        W, H = self.info["width"] or 1318, self.info["height"] or 120
        t, x, y, w, h = float(t), int(x), int(y), int(width), int(height)
        z = max(1, min(int(zoom), 8))
        src = self.frame_at(t)
        x = max(0, min(x, W - 1)); y = max(0, min(y, H - 1))
        w = max(8, min(w, W - x)); h = max(8, min(h, H - y))
        out = self.frames / f"cz_{t:.3f}_{x}_{y}_{w}_{h}_{z}.png"
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-i", str(src),
                        "-vf", f"crop={w}:{h}:{x}:{y},scale=iw*{z}:ih*{z}:flags=lanczos",
                        "-y", str(out)], capture_output=True)
        return {"img": b64_data_uri(out, "image/png"),
                "note": f"t={t}s 区域 x{x}-{x+w},y{y}-{y+h} 放大 {z}x"}

    def t_audio(self):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(self.video), "-af", "volumedetect",
                            "-f", "null", "NUL"], capture_output=True, text=True)
        out = (r.stdout or "") + (r.stderr or "")
        keep = [ln.strip() for ln in out.splitlines() if "mean_volume" in ln or "max_volume" in ln]
        return {"text": "音轨：" + ("；".join(keep) if keep else "无音轨信息")}

    def schema(self):
        W, H = self.info["width"] or 1318, self.info["height"] or 120
        return [
            {"type": "function", "function": {"name": "change_segments",
             "description": "列出画面显著变化的时间点，用于定位交互/动画发生的时刻",
             "parameters": {"type": "object", "properties": {}}}},
            {"type": "function", "function": {"name": "extract",
             "description": f"抽取某时间点的完整帧（{W}x{H}）",
             "parameters": {"type": "object", "properties": {"t": {"type": "number", "description": "秒"}}, "required": ["t"]}}},
            {"type": "function", "function": {"name": "crop",
             "description": f"把某时间点的矩形区域裁剪放大以看清小字。画面宽 {W} 高 {H}，原点左上。",
             "parameters": {"type": "object", "properties": {
                 "t": {"type": "number"}, "x": {"type": "integer"}, "y": {"type": "integer"},
                 "width": {"type": "integer"}, "height": {"type": "integer"},
                 "zoom": {"type": "integer", "description": "放大倍数 1-8，默认 4"}},
                 "required": ["t", "x", "y", "width", "height"]}}},
            {"type": "function", "function": {"name": "audio",
             "description": "分析音轨电平，判断是否静音或有声音事件",
             "parameters": {"type": "object", "properties": {}}}},
        ]

    def dispatch(self, name, args):
        table = {"change_segments": self.t_change_segments, "extract": self.t_extract,
                 "crop": self.t_crop, "audio": self.t_audio, "duration": self.t_duration}
        fn = table.get(name)
        if not fn:
            return {"text": f"未知工具 {name}"}
        try:
            return fn(**args)
        except Exception as e:
            return {"text": f"工具错误 {type(e).__name__}: {e}"}


SYSTEM_TMPL = """你是屏幕录制取证分析专家，正在分析一段 {dur} 秒、{w}x{h} 的视频。

【铁律】
1. 只报告像素上真正看到的内容。分辨不清就写「无法辨认」。
2. 严禁用常见软件界面的先验知识去填补或猜测画面内容（例如凭空写出某产品的默认菜单项、
   默认数值、其他厂商的模型名）。若画面与你的先验不符，以画面为准。
3. 所有文字、数字必须逐字符原样抄写，不翻译、不同义替换、不补全单位。
4. 小于 14px 的文字必须先用 crop 放大 4-8 倍之后再读，读之前不要猜。

【证据配额与收口纪律——必须遵守】
- 你总共只有 {budget} 次工具调用预算，用完后必须立刻输出最终结论。
- 建议分配：1 次 change_segments 定位 → 1 次 extract 看整体 → 最多 5 次 crop 放大核对 → 收口。
- 每轮回复正文先写一行「已确认：…」累积已核实事实，再决定是否继续调用工具。
- 同一区域不要重复放大；信息已足够时立即给结论，不要为用完预算而调用。
"""


def call_model(msgs, schema, endpoint, model, workdir: Path):
    payload = {"model": model, "messages": msgs, "tools": schema,
               "tool_choice": "auto", "max_tokens": 4000}
    req = workdir / "_req.json"
    req.write_text(json.dumps(payload), encoding="utf-8")
    r = subprocess.run(["curl", "-sS", "--max-time", "300", "--noproxy", "*",
                        "-H", "Content-Type: application/json",
                        "-H", "Authorization: Bearer local",
                        "-X", "POST", endpoint, "-d", "@" + str(req)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl 失败: {r.stderr[:300]}")
    return json.loads(r.stdout)


def trim(msgs, keep=KEEP_RECENT_SETS):
    head, rest = msgs[:2], msgs[2:]
    groups, cur = [], []
    for m in rest:
        cur.append(m)
        if m.get("role") == "tool":
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    if len(groups) <= keep:
        return msgs
    kept = []
    for g in groups[:-keep]:
        names = [tc["function"]["name"] for m in g if m.get("role") == "assistant" for tc in (m.get("tool_calls") or [])]
        kept.append({"role": "assistant", "content": f"[已完成工具调用：{', '.join(names) or '无'}]（图像结果已省略）"})
    return head + kept + [m for g in groups[-keep:] for m in g]


def main():
    ap = argparse.ArgumentParser(description="让 cpa 端点的 Gemini 用工具集自主分析视频")
    ap.add_argument("video", help="视频文件路径")
    ap.add_argument("-o", "--output", help="结论输出 Markdown 路径")
    ap.add_argument("--endpoint", default=os.environ.get("CPA_ENDPOINT", DEFAULT_ENDPOINT))
    ap.add_argument("-m", "--model", default=os.environ.get("CPA_MODEL", DEFAULT_MODEL))
    ap.add_argument("--question", default=None, help="替换默认四问，聚焦某个具体问题")
    ap.add_argument("--budget", type=int, default=TOOL_BUDGET)
    ap.add_argument("--workdir", default=None, help="工作目录（默认临时目录）")
    args = ap.parse_args()

    video = Path(args.video).resolve()
    if not video.exists():
        print(f"[错误] 视频不存在: {video}", file=sys.stderr); return 1
    workdir = Path(args.workdir).resolve() if args.workdir else Path(tempfile.mkdtemp(prefix="vid-cpa-"))
    workdir.mkdir(parents=True, exist_ok=True)

    an = Analyzer(video, workdir)
    i = an.info
    question = args.question or (
        "请用工具逐步放大取证并回答：\n"
        "1) 画面上出现的每个 UI 元素与文字（逐字符原样抄写）；\n"
        "2) 按时间顺序发生了什么交互（鼠标位置、悬停、点击、任何弹出层及其内容）；\n"
        "3) 关键数值/状态在整段里有没有变化，各自读数是多少；\n"
        "4) 明确列出你无法辨认的部分。")

    system = SYSTEM_TMPL.format(dur=i["duration"], w=i["width"], h=i["height"], budget=args.budget)
    msgs = [{"role": "system", "content": system},
            {"role": "user", "content": [
                {"type": "text", "text": question + f"\n\n记住：{args.budget} 次工具调用预算，用完必须收口。"},
                {"type": "video_url", "video_url": {"url": b64_data_uri(video, "video/mp4")}}]}]

    used = 0
    for rnd in range(1, MAX_ROUNDS + 1):
        print(f"\n{'='*70}\n[第 {rnd} 轮 | 已用工具 {used}/{args.budget}]", flush=True)
        try:
            resp = call_model(trim(msgs), an.schema(), args.endpoint, args.model, workdir)
        except Exception as e:
            print(f"[错误] {e}", file=sys.stderr); return 1
        if "choices" not in resp:
            print("异常响应:", json.dumps(resp, ensure_ascii=False)[:600], file=sys.stderr); return 1
        m = resp["choices"][0]["message"]
        tcs = m.get("tool_calls") or []
        note = (m.get("content") or "").strip()
        if note:
            print("  笔记: " + note.replace("\n", " ")[:300], flush=True)
        print(f"  finish={resp['choices'][0].get('finish_reason')} tokens={resp.get('usage',{}).get('total_tokens')} 本轮工具={len(tcs)}", flush=True)

        if not tcs:
            print("\n" + "─"*70 + "\n【最终结论】\n" + "─"*70)
            print(note)
            if args.output:
                Path(args.output).write_text(note, encoding="utf-8")
                print(f"\n[已保存] {args.output}")
            return 0

        if used >= args.budget:
            msgs.append({"role": "assistant", "content": m.get("content")})
            msgs.append({"role": "user", "content": "工具预算已用尽，请立刻基于已获取证据输出最终结论。"})
            resp2 = call_model(trim(msgs), an.schema(), args.endpoint, args.model, workdir)
            txt = resp2["choices"][0]["message"].get("content") or ""
            print("\n" + "─"*70 + "\n【最终结论（预算收口）】\n" + "─"*70)
            print(txt)
            if args.output:
                Path(args.output).write_text(txt, encoding="utf-8")
                print(f"\n[已保存] {args.output}")
            return 0

        msgs.append({"role": "assistant", "content": m.get("content"), "tool_calls": tcs})
        for tc in tcs:
            used += 1
            fn = tc["function"]["name"]
            try:
                targs = json.loads(tc["function"]["arguments"] or "{}")
            except Exception:
                targs = {}
            print(f"  → {fn}({json.dumps(targs, ensure_ascii=False)})", flush=True)
            res = an.dispatch(fn, targs)
            if "img" in res:
                content = [{"type": "text", "text": res["note"]},
                           {"type": "image_url", "image_url": {"url": res["img"]}}]
                print(f"     · {res['note']}", flush=True)
            else:
                content = res.get("text", "")
                print(f"     · {content[:180]}", flush=True)
            msgs.append({"role": "tool", "tool_call_id": tc["id"], "content": content})

    print("\n[未收敛：达到最大轮数]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
