"""降级感知验证：plugin_api 对 /api/rate_limit.fallbacks 的透传与当前模型命中提升。

三场景：
1. 当前会话模型命中 fallbacks -> out.fallback = {requested, actual, reason, count, lastLocal}
2. 未命中 -> 只带 allFallbacks，无顶层 fallback
3. 旧版反代无 fallbacks 字段 -> 两个降级字段都不出现（向后兼容）
"""

import json
import sys
from pathlib import Path

import pytest

PLUGIN_DIR = Path(__file__).resolve().parents[1] / "plugins" / "token-stats" / "dashboard"
sys.path.insert(0, str(PLUGIN_DIR))

import plugin_api  # noqa: E402


class FakeResp:
    status = 200

    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeOpener:
    def __init__(self, payload):
        self._payload = payload

    def open(self, url, timeout=None):
        return FakeResp(self._payload)


def _patch_env(monkeypatch, fake_rl, current_model):
    monkeypatch.setattr(plugin_api, "_rl_cache", None)
    monkeypatch.setattr(plugin_api, "_rl_cache_time", 0)
    monkeypatch.setattr(plugin_api, "_read_current_chat_route", lambda: {"model": current_model, "provider": "custom:workbuddy"})
    monkeypatch.setattr("urllib.request.build_opener", lambda *a, **k: FakeOpener(fake_rl))


def test_fallback_promoted_when_current_model_hits(monkeypatch):
    fake_rl = {
        "models": {},
        "fallbacks": {
            "gpt-6-astra": {
                "actual": "deepseek-v4-pro",
                "reason": "11102 unauthorized",
                "count": 3,
                "lastLocal": "09-12 13:03:42",
            }
        },
    }
    _patch_env(monkeypatch, fake_rl, "gpt-6-astra")
    out = plugin_api._workbuddy_rate_limit()
    assert out.get("fallback") == {
        "requested": "gpt-6-astra",
        "actual": "deepseek-v4-pro",
        "reason": "11102 unauthorized",
        "count": 3,
        "lastLocal": "09-12 13:03:42",
    }
    assert out.get("allFallbacks") == fake_rl["fallbacks"]


def test_no_fallback_promotion_when_model_not_hit(monkeypatch):
    fake_rl = {
        "models": {},
        "fallbacks": {
            "gpt-5.6-luna": {"actual": "fast-model", "reason": "11102 unauthorized", "count": 1, "lastLocal": "09-12 12:00:00"}
        },
    }
    _patch_env(monkeypatch, fake_rl, "glm-5.3-flash")
    out = plugin_api._workbuddy_rate_limit()
    assert "fallback" not in out
    assert out.get("allFallbacks") == fake_rl["fallbacks"]


def test_old_proxy_without_fallbacks_field(monkeypatch):
    _patch_env(monkeypatch, {"models": {}}, "glm-5.3-flash")
    out = plugin_api._workbuddy_rate_limit()
    assert "fallback" not in out
    assert "allFallbacks" not in out


def test_rotation_soonest_expiry_and_server_metadata_passed(monkeypatch):
    """验证 rotation.soonest_expire_day 与 server 诊断元数据被完整透传。"""
    fake_rl = {
        "models": {},
        "rotation": {
            "mode": "failover",
            "rotate_count": 1,
            "accounts_count": 2,
            "soonest_expire_day": "2026-09-15",
            "config_source": "hot",
        },
        "server": {
            "maxBodyMb": 16.0,
            "userAgent": "CLI/2.63.2 CodeBuddy/2.63.2",
            "protocols": ["chat", "messages", "responses"],
        },
    }
    _patch_env(monkeypatch, fake_rl, "glm-5.3-flash")
    out = plugin_api._workbuddy_rate_limit()
    assert out.get("rotation", {}).get("soonest_expire_day") == "2026-09-15"
    assert out.get("server", {}).get("protocols") == ["chat", "messages", "responses"]
    assert out.get("server", {}).get("maxBodyMb") == 16.0
