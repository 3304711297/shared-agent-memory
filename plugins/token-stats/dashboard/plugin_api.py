"""token-stats dashboard plugin — Google/Antigravity quota API, mounted at /api/plugins/token-stats/.

Port of the standalone quota micro-service (desktop-plugins/token-stats/fetch_quota.py, port
18088) into a Hermes dashboard-plugin backend router, so the desktop app's own backend
process serves the data — no scheduled task, no separate daemon. Lifecycle follows the
desktop app: app open → service up; app closed → service down.

Auth model: these routes inherit the dashboard's own auth middleware chain
(_plugin_api_runtime_gate in web_server.py + token/session auth). CORS is not needed —
the desktop renderer reaches the backend through the app's namespace-scoped REST door
(host.request / pluginRest), never cross-origin.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

log = logging.getLogger(__name__)

router = APIRouter()

CACHE_TTL = 30  # seconds — matches the standalone service's behaviour
PROXY_URL = os.environ.get("HERMES_QUOTA_PROXY", "http://127.0.0.1:3067")

_cache_lock = threading.Lock()
_cache_data: Optional[dict] = None
_cache_time = 0.0


def _hermes_home() -> Path:
    home = os.environ.get("HERMES_HOME")
    return Path(home) if home else Path.home() / ".hermes"


def _auth_dir() -> Path:
    # EasyCLIProxyAPI official credential store (local gateway bridge).
    override = os.environ.get("HERMES_QUOTA_AUTH_DIR")
    if override:
        return Path(override)
    return Path(r"D:\EasyCLIProxyAPI\auth")


def _cache_file() -> Path:
    # Keep the cache file next to the desktop plugin that reads it, so the old
    # frontend keeps its disk fallback even while the backend moves here.
    return _hermes_home() / "desktop-plugins" / "token-stats" / "direct-quota.json"


def get_auth_file() -> Optional[str]:
    auth_dir = _auth_dir()
    if not auth_dir.exists():
        return None
    for f in sorted(auth_dir.iterdir()):
        if f.name.startswith("antigravity-") and f.name.endswith(".json"):
            return str(f)
    return None


def _stale_disk_cache() -> Optional[dict]:
    cache = _cache_file()
    if not cache.exists():
        return None
    try:
        old = json.loads(cache.read_text(encoding="utf-8"))
        old["stale"] = True
        return old
    except Exception:
        return None


def fetch_google_quota(force: bool = False) -> dict:
    """Fetch quota from Google's official endpoint via the local proxy (30s in-memory cache)."""
    global _cache_data, _cache_time

    now = time.time()
    with _cache_lock:
        if not force and _cache_data is not None and (now - _cache_time < CACHE_TTL):
            return _cache_data

    auth_path = get_auth_file()
    if not auth_path:
        return {"error": f"EasyCLIProxyAPI auth file not found in {_auth_dir()}"}

    try:
        auth = json.loads(Path(auth_path).read_text(encoding="utf-8"))
    except Exception as exc:
        return {"error": f"Failed to read auth file: {exc}"}

    token = auth.get("access_token", "")
    project_id = auth.get("project_id", "aicode-consumers")
    email = auth.get("email", "")

    if not token:
        return {"error": "No access_token found in auth file"}

    # Antigravity uses the daily-cloudcode-pa endpoint (not generic cloudcode-pa).
    url = "https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary"
    payload = json.dumps({"project": project_id}).encode("utf-8")

    try:
        import urllib.request

        proxy_handler = urllib.request.ProxyHandler({"http": PROXY_URL, "https": PROXY_URL})
        opener = urllib.request.build_opener(proxy_handler)
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "antigravity/hub/2.8.1 windows/amd64",
            },
        )
        with opener.open(req, timeout=8) as res:
            if res.status != 200:
                return {"error": f"Google returned HTTP {res.status}"}
            raw = json.loads(res.read().decode("utf-8"))
    except Exception:
        # Network failure → fall back to the on-disk cache, flagged stale.
        old = _stale_disk_cache()
        if old is not None:
            return old
        return {"error": "Request to Google failed (network) and no disk cache available"}

    quota_5h: Optional[float] = None
    reset_5h: Optional[str] = None
    quota_weekly: Optional[float] = None
    reset_weekly: Optional[str] = None
    third_party_5h: Optional[float] = None
    third_party_weekly: Optional[float] = None

    for g in raw.get("groups", []):
        dname = g.get("displayName", "")
        for b in g.get("buckets", []):
            bid = b.get("bucketId", "")
            frac = b.get("remainingFraction", 1.0)
            pct = round(frac * 100, 1)
            reset_time = b.get("resetTime")

            if "Gemini" in dname or "gemini" in bid:
                if "5h" in bid and quota_5h is None:
                    quota_5h = pct
                    reset_5h = reset_time
                elif ("week" in bid or "weekly" in bid) and quota_weekly is None:
                    quota_weekly = pct
                    reset_weekly = reset_time
            elif "Claude" in dname or "3p" in bid:
                if "5h" in bid and third_party_5h is None:
                    third_party_5h = pct
                elif ("week" in bid or "weekly" in bid) and third_party_weekly is None:
                    third_party_weekly = pct

    result: dict[str, Any] = {
        "status": "ok",
        "account": email,
        "plan": "Google AI Pro",
        "quota5h": quota_5h if quota_5h is not None else 100,
        "reset5h": reset_5h,
        "quotaWeekly": quota_weekly if quota_weekly is not None else 100,
        "resetWeekly": reset_weekly,
        "claudeQuota5h": third_party_5h,
        "claudeQuotaWeekly": third_party_weekly,
        "source": "Google 官方直连 (Hermes 内置)",
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "updatedAtLocal": time.strftime("%H:%M:%S"),
    }

    with _cache_lock:
        _cache_data = result
        _cache_time = now

    try:
        cache = _cache_file()
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

    return result


@router.get("/quota")
async def quota(force: str = Query("", description="force=1 bypasses the 30s cache")):
    data = fetch_google_quota(force=force in ("1", "true", "yes"))
    if "error" in data:
        return JSONResponse(status_code=502, content=data)
    return data


@router.get("/health")
async def health():
    return {"status": "ok", "plugin": "token-stats"}
