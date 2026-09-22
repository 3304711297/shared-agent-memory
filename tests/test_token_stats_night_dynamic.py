"""TDD 契约测试：token-stats 插件动态感知夜间限免范围，避免误导用户「所有模型全免费」。

验证内容：
1. plugin_api.py 当 nightFree=True 时：
   - 当前模型属于夜间限免模型（如 hy4-preview）时，明确指出「当前模型限免中」；
   - 当前模型不属于夜间限免模型时，明确标注「指定模型限免中 / 仅部分模型」，避免用户误以为全场免费。
2. desktop/plugin.js 与 desktop-plugins/token-stats/desktop/plugin.js 保持一致：
   - RateLimitRow 与看板标题包含「指定模型」或明确指向模型页标签，消除全场免积分误导。
"""

import json
import sys
from pathlib import Path
import pytest

PLUGIN_DIR = Path(__file__).resolve().parents[1] / "plugins" / "token-stats" / "dashboard"
sys.path.insert(0, str(PLUGIN_DIR))

import plugin_api  # noqa: E402


def test_markdown_quota_differentiates_current_model_when_night_free():
    """当当前模型在夜间限免名单中时，提示当前模型限免。"""
    data = {
        "updatedAtLocal": "2026-09-22 23:30:00",
        "workbuddy": {
            "status": "online",
            "statusLabel": "在线 (8787)",
            "rateLimit": {
                "model": "hy4-preview",
                "state": "ok",
                "nightFree": True,
                "nightWindow": {
                    "active": True,
                    "start": "23:00",
                    "end": "08:00",
                    "desc": "指定模型 23:00–次日08:00 免积分",
                    "scope": "specific_models",
                    "nightFreeModels": ["hy4-preview"],
                },
            },
        },
    }
    md = plugin_api.format_quota_markdown(data)
    assert "当前模型 `hy4-preview`" in md
    assert "限免中" in md


def test_markdown_quota_clarifies_specific_models_when_current_not_free():
    """当当前模型不在夜间限免名单时，明确注明仅指定模型限免，避免误解全场免费。"""
    data = {
        "updatedAtLocal": "2026-09-22 23:30:00",
        "workbuddy": {
            "status": "online",
            "statusLabel": "在线 (8787)",
            "rateLimit": {
                "model": "claude-3-7-sonnet",
                "state": "ok",
                "nightFree": True,
                "nightWindow": {
                    "active": True,
                    "start": "23:00",
                    "end": "08:00",
                    "desc": "指定模型 23:00–次日08:00 免积分",
                    "scope": "specific_models",
                    "nightFreeModels": ["hy4-preview"],
                },
            },
        },
    }
    md = plugin_api.format_quota_markdown(data)
    # 不能简单粗暴说「夜间限免：限免中 · 调用不扣积分」
    assert "指定模型" in md or "部分模型" in md
    assert "全免费" not in md
    assert "当前模型 `hy4-preview`" not in md


def test_plugin_js_clarifies_night_free_scope():
    """desktop/plugin.js 必须明确指定模型限免，禁止给用户造成全场免费的假象。"""
    p = Path(__file__).resolve().parents[1] / "plugins" / "token-stats" / "desktop" / "plugin.js"
    code = p.read_text(encoding="utf-8")
    # RateLimitRow 或看板中的夜间文案必须包含「指定模型」或类似精准限定
    assert "指定模型" in code or "部分模型" in code
