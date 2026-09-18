"""token-stats 积分精确显示契约（2026-09-18）。

背景：用户要求状态栏积分**精确显示数值、不要约数**。原实现有两类失真：
① 状态栏 chip 用 `fmtCredits()` 把积分压缩成 `1.8k` 这种约数（完全丢失明细）；
② 大看板/后端 markdown 用 `toFixed(1)` / `:.0f` / `:.1f`，与上游真值不一致。

上游真值口径（实测腾讯计费接口）：`CycleRemainCapacity` 是**字符串**且量化到 2 位小数，
但经 float64 呈现会带二进制尾数 —— 实测 `"833.33000192"` 真值即 833.33
（`833.33000192 + 3316.66999808 == 4150` 精确闭合，证明尾数是 float64 噪声而非真实额度）。
故「精确」= 保留 2 位小数，既不截断真值也不显示浮点噪声。

本文件锁定：
1. 后端 `_fmt_credits_exact()` 的格式化口径（2 位小数、去尾零、不约数）；
2. plugin_api 各消费点改用精确格式（markdown 明细不再 .0f/.1f 丢精度）；
3. 前端不再存在 `fmtCredits` 这类缩约函数。
"""

import re
from pathlib import Path

HOME = Path(__file__).resolve().parents[1]
PLUGIN_API = HOME / "plugins" / "token-stats" / "dashboard" / "plugin_api.py"
PLUGIN_JS = HOME / "desktop-plugins" / "token-stats" / "plugin.js"


def _load_plugin_api():
    import importlib.util

    spec = importlib.util.spec_from_file_location("token_stats_plugin_api_exact", PLUGIN_API)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_fmt_credits_exact_keeps_two_decimals_without_noise():
    """精确格式：2 位小数、去尾零；浮点噪声必须被吸收（不显示 833.33000192 这种尾巴）。"""
    mod = _load_plugin_api()
    f = mod._fmt_credits_exact

    # 上游真值（float64 噪声形态）→ 干净 2 位小数
    assert f(833.33000192) == "833.33"
    assert f(1833.33000192) == "1833.33"
    assert f(3816.66999808) == "3816.67"
    # 整数不拖 ".00" 尾巴
    assert f(1000.0) == "1000"
    assert f(4150) == "4150"
    assert f(0.0) == "0"
    # 半整数只留 1 位
    assert f(0.5) == "0.5"
    # None / 非数 → '—'（不臆造 0）
    assert f(None) == "—"
    assert f("abc") == "—"


def test_backend_markdown_uses_exact_credits_not_rounded():
    """后端 markdown 明细必须打印精确值：不得再用 .0f / .1f 抹掉小数。"""
    src = PLUGIN_API.read_text(encoding="utf-8")

    assert "_fmt_credits_exact" in src, "后端缺少精确格式化函数"

    bad = []
    for i, line in enumerate(src.splitlines(), 1):
        if re.search(r"(remain|total|used|积分)", line) and re.search(r":\.[01]f\}", line):
            bad.append((i, line.strip()[:120]))
    assert not bad, f"仍存在抹掉精度的积分格式化：{bad}"


def test_frontend_chip_shows_exact_value_not_abbreviated():
    """状态栏 chip 必须渲染精确积分（原 fmtCredits 把 1833.33 压成 1.8k）。"""
    js = PLUGIN_JS.read_text(encoding="utf-8")

    assert "fmtCredits" not in js, "plugin.js 仍存在约数函数 fmtCredits"
    assert "fmtExactCredits" in js, "plugin.js 缺少精确格式化函数 fmtExactCredits"
    chip_idx = js.find("workbuddy.usage?.remain")
    assert chip_idx > -1, "chip 积分渲染点丢失"
    around = js[max(0, chip_idx - 400):chip_idx + 400]
    assert "fmtExactCredits" in around, "chip 积分点未改用精确格式"


def test_frontend_board_and_packages_not_rounded_away():
    """看板大卡与积分包明细不得把小数抹掉（原 .toFixed(1) / .toFixed(0)）。"""
    js = PLUGIN_JS.read_text(encoding="utf-8")

    for pat, why in (
        (r"usage\.remain\.toFixed\(1\)", "看板积分余量仍用 toFixed(1)"),
        (r"Math\.round\(data\.workbuddy\.usage\.total", "看板积分总量仍用 Math.round 截断"),
        (r"Math\.round\(quotaData\.workbuddy\.usage\.remain\)", "Popover 积分余量仍用 Math.round 截断"),
        (r"Math\.round\(quotaData\.workbuddy\.usage\.total\)", "Popover 积分总量仍用 Math.round 截断"),
    ):
        assert not re.search(pat, js), why

    assert not re.search(r"\(p\.remain \|\| 0\)\.toFixed\(0\)", js), "积分包余量仍用 toFixed(0)"
    assert not re.search(r"\(p\.total \|\| 0\)\.toFixed\(0\)", js), "积分包总量仍用 toFixed(0)"
