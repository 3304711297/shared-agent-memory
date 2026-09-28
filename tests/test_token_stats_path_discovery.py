"""token-stats 插件 EasyCLIProxyAPI 路径动态探测契约测试。

验证内容：
1. 能够自适应发现版本化目录（如 EasyCLIProxyAPI-v0.3.8-Windows-amd64）与 oauth/auth 子目录；
2. _auth_dir() 优先发现包含 antigravity-*.json 的有效凭据目录；
3. _find_usage_db() 能够正确定位 usage-records/usage.db；
4. 支持环境变量 HERMES_QUOTA_AUTH_DIR 覆盖；
5. 在多账号存在时 get_auth_files() 能正常解析。
"""

import os
import sys
from pathlib import Path
import pytest

PLUGIN_DIR = Path(__file__).resolve().parents[1] / "plugins" / "token-stats" / "dashboard"
sys.path.insert(0, str(PLUGIN_DIR))

import plugin_api  # noqa: E402


def test_auth_dir_detects_real_or_fallback():
    """在当前环境下应能正确探测到 EasyCLIProxyAPI 的凭据目录。"""
    auth_dir = plugin_api._auth_dir()
    assert isinstance(auth_dir, Path)
    # 若本机存在 EasyCLIProxyAPI-v0.3.8-Windows-amd64，应定位到其 oauth 目录
    expected = Path(r"D:\EasyCLIProxyAPI-v0.3.8-Windows-amd64\oauth")
    if expected.exists():
        assert auth_dir == expected
        assert auth_dir.name in ("oauth", "auth")


def test_auth_dir_honors_env_override(monkeypatch, tmp_path):
    """验证 HERMES_QUOTA_AUTH_DIR 环境变量优先。"""
    custom_dir = tmp_path / "custom_auth"
    custom_dir.mkdir()
    monkeypatch.setenv("HERMES_QUOTA_AUTH_DIR", str(custom_dir))
    assert plugin_api._auth_dir() == custom_dir


def test_find_usage_db_locates_valid_db():
    """验证 usage.db 能够被自适应发现。"""
    db_path = plugin_api._find_usage_db()
    expected = Path(r"D:\EasyCLIProxyAPI-v0.3.8-Windows-amd64\usage-records\usage.db")
    if expected.exists():
        assert db_path is not None
        assert db_path.exists()
        assert db_path.name == "usage.db"


def test_get_auth_files_returns_antigravity_accounts():
    """验证能正确载入有效账号凭据。"""
    files = plugin_api.get_auth_files()
    expected_dir = Path(r"D:\EasyCLIProxyAPI-v0.3.8-Windows-amd64\oauth")
    if expected_dir.exists() and any(expected_dir.glob("antigravity-*.json")):
        assert len(files) > 0
        for path, data in files:
            assert path.name.startswith("antigravity-")
            assert "access_token" in data
            assert not data.get("disabled", False)


def test_mock_discovery_logic(monkeypatch, tmp_path):
    """使用模拟目录结构测试版本升级时对 oauth 与 auth 目录的自动选择。"""
    root1 = tmp_path / "EasyCLIProxyAPI-v0.3.9-Windows-amd64"
    oauth_dir = root1 / "oauth"
    oauth_dir.mkdir(parents=True)
    # 模拟放置一个凭据
    (oauth_dir / "antigravity-test@gmail.com.json").write_text('{"access_token": "abc", "email": "test@gmail.com"}', encoding="utf-8")

    monkeypatch.setattr(plugin_api, "_candidate_base_dirs", lambda: [root1])
    monkeypatch.delenv("HERMES_QUOTA_AUTH_DIR", raising=False)

    assert plugin_api._auth_dir() == oauth_dir
    items = plugin_api.get_auth_files()
    assert len(items) == 1
    assert items[0][1]["email"] == "test@gmail.com"
