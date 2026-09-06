"""token-stats dashboard plugin — Google/Antigravity quota API, mounted at /api/plugins/token-stats/.

Port of the standalone quota micro-service into a Hermes dashboard-plugin backend router,
so the desktop app's own backend process serves the data — no scheduled task, no separate daemon.
Lifecycle follows the desktop app: app open → service up; app closed → service down.

Auth model: these routes inherit the dashboard's own auth middleware chain
(_plugin_api_runtime_gate in web_server.py + token/session auth). CORS is not needed —
the desktop renderer reaches the backend through the app's namespace-scoped REST door
(host.request / pluginRest / ctx.rest), never cross-origin.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Optional
from concurrent.futures import ThreadPoolExecutor

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
    override = os.environ.get("HERMES_QUOTA_AUTH_DIR")
    if override:
        return Path(override)
    return Path(r"D:\EasyCLIProxyAPI\auth")


def _cache_file() -> Path:
    return _hermes_home() / "desktop-plugins" / "token-stats" / "direct-quota.json"


def _find_usage_db() -> Optional[Path]:
    candidates = [
        Path(r"D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64\usage-records\usage.db"),
        Path(r"D:\EasyCLIProxyAPI\usage-records\usage.db"),
        _auth_dir().parent / "usage-records" / "usage.db",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _get_active_email() -> Optional[str]:
    """Identify the currently active/most recently used account from EasyCLIProxyAPI."""
    db_path = _find_usage_db()
    if db_path and db_path.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
            try:
                row = conn.execute(
                    "SELECT source FROM usage_events WHERE source != '' ORDER BY id DESC LIMIT 1"
                ).fetchone()
                if row and row[0]:
                    return row[0].strip()
            finally:
                conn.close()
        except Exception:
            pass

    log_file = _auth_dir() / "logs" / "main.log"
    if log_file.exists():
        try:
            with open(log_file, "rb") as f:
                f.seek(0, 2)
                size = f.tell()
                f.seek(max(0, size - 8192))
                tail = f.read().decode("utf-8", errors="ignore")
            import re
            matches = re.findall(r"auth=antigravity-([^ \t\r\n]+\.json)", tail)
            if matches:
                last = matches[-1]
                if last.endswith(".json"):
                    return last[:-5]
        except Exception:
            pass

    return None


def get_auth_files() -> list[tuple[Path, dict]]:
    """Return all valid Antigravity auth files and their parsed metadata."""
    auth_dir = _auth_dir()
    if not auth_dir.exists():
        return []
    files: list[tuple[Path, dict]] = []
    for f in sorted(auth_dir.iterdir()):
        if f.name.startswith("antigravity-") and f.name.endswith(".json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if not data.get("disabled", False):
                    files.append((f, data))
            except Exception:
                continue
    return files


def get_auth_file() -> Optional[str]:
    auth_items = get_auth_files()
    if not auth_items:
        return None
    active_email = _get_active_email()
    if active_email:
        for p, d in auth_items:
            if d.get("email") == active_email:
                return str(p)
    auth_items.sort(key=lambda x: (x[1].get("priority", 0), x[1].get("timestamp", 0)), reverse=True)
    return str(auth_items[0][0])


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


def check_workbuddy_status() -> dict[str, Any]:
    """Non-blocking check for local WorkBuddy / codebuddy2openai gateway (port 8787).

    Probes /v1/models for liveness, then fetches /api/usage_summary for
    credits & active account (endpoint added by ZCode, commit 5b4381c).
    """
    import urllib.request

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    endpoint = "http://127.0.0.1:8787/v1"
    try:
        req = urllib.request.Request(f"{endpoint}/models")
        with opener.open(req, timeout=1.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                models = data.get("data", [])
                base: dict[str, Any] = {
                    "id": "workbuddy",
                    "name": "WorkBuddy (codebuddy2openai)",
                    "status": "online",
                    "statusLabel": "运行中",
                    "endpoint": endpoint,
                    "modelsCount": len(models),
                    "note": f"已挂载 {len(models)} 个可用模型",
                }
                # Fetch credits & account summary
                try:
                    req2 = urllib.request.Request("http://127.0.0.1:8787/api/usage_summary")
                    with opener.open(req2, timeout=4) as resp2:
                        usage = json.loads(resp2.read().decode("utf-8"))
                    if "error" not in usage:
                        remain = usage.get("remain", 0.0)
                        total = usage.get("total", 0.0)
                        pct = round(remain / total * 100, 1) if total > 0 else 0.0
                        base.update({
                            "usage": {
                                "nickname": usage.get("nickname", "—"),
                                "total": total,
                                "remain": remain,
                                "used": usage.get("used", 0.0),
                                "remainPercent": pct,
                                "isPaidUser": usage.get("is_paid_user", False),
                                "packages": usage.get("packages", []),
                            },
                            "note": f"账号「{usage.get('nickname', '—')}」· 积分 {remain:.0f}/{total:.0f} ({pct}%)",
                        })
                    else:
                        base["usageError"] = usage.get("error", "unknown")
                except Exception as exc:
                    base["usageError"] = f"积分获取失败: {exc}"
                return base
    except Exception:
        pass

    return {
        "id": "workbuddy",
        "name": "WorkBuddy (codebuddy2openai)",
        "status": "offline",
        "statusLabel": "未启动",
        "endpoint": endpoint,
        "modelsCount": 0,
        "note": "本地反代服务待机中 (端口 8787)",
    }


def _fetch_single_google_quota(auth_path: Path, auth: dict) -> Optional[dict]:
    token = auth.get("access_token", "")
    project_id = auth.get("project_id", "aicode-consumers")
    email = auth.get("email", "")
    priority = auth.get("priority", 0)

    if not token:
        return None

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
                return None
            raw = json.loads(res.read().decode("utf-8"))
    except Exception:
        return None

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

    is_pro = ("qq.com" in email) or (auth.get("plan") == "pro") or (auth.get("is_pro") is True)
    return {
        "account": email,
        "email": email,
        "plan": "Google AI Pro" if is_pro else "Google AI",
        "priority": priority,
        "quota5h": quota_5h if quota_5h is not None else 100,
        "reset5h": reset_5h,
        "quotaWeekly": quota_weekly if quota_weekly is not None else 100,
        "resetWeekly": reset_weekly,
        "claudeQuota5h": third_party_5h if third_party_5h is not None else 100,
        "claudeQuotaWeekly": third_party_weekly if third_party_weekly is not None else 100,
    }


def fetch_google_quota(force: bool = False) -> dict:
    """Fetch quota from Google's official endpoint via the local proxy (30s in-memory cache).

    Supports multi-account pools with concurrent querying and dynamic active-account routing detection.
    """
    global _cache_data, _cache_time

    now = time.time()
    with _cache_lock:
        if not force and _cache_data is not None and (now - _cache_time < CACHE_TTL):
            # Check if active account shifted
            active_email = _get_active_email()
            if active_email and _cache_data.get("account") != active_email:
                accounts = _cache_data.get("accounts", [])
                target = next((a for a in accounts if a.get("account") == active_email), None)
                if target:
                    _cache_data["account"] = target["account"]
                    _cache_data["activeAccount"] = target["account"]
                    _cache_data["plan"] = target["plan"]
                    _cache_data["quota5h"] = target["quota5h"]
                    _cache_data["reset5h"] = target["reset5h"]
                    _cache_data["quotaWeekly"] = target["quotaWeekly"]
                    _cache_data["resetWeekly"] = target["resetWeekly"]
                    _cache_data["claudeQuota5h"] = target["claudeQuota5h"]
                    _cache_data["claudeQuotaWeekly"] = target["claudeQuotaWeekly"]
                    for a in accounts:
                        a["isActive"] = (a.get("account") == active_email)
            return _cache_data

    auth_items = get_auth_files()
    if not auth_items:
        return {"error": f"EasyCLIProxyAPI auth file not found in {_auth_dir()}"}

    active_email = _get_active_email()

    parsed_accounts: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(4, len(auth_items))) as executor:
        futures = [executor.submit(_fetch_single_google_quota, p, a) for p, a in auth_items]
        for f in futures:
            try:
                acc = f.result()
                if acc:
                    parsed_accounts.append(acc)
            except Exception:
                pass

    if not parsed_accounts:
        # Fall back to disk cache
        old = _stale_disk_cache()
        if old is not None:
            return old
        return {"error": "Request to Google failed (network) and no disk cache available"}

    for acc in parsed_accounts:
        acc["isActive"] = (acc.get("account") == active_email)

    primary = next((a for a in parsed_accounts if a.get("isActive")), None)
    if not primary:
        parsed_accounts.sort(key=lambda a: (a.get("priority", 0), a.get("account", "")), reverse=True)
        primary = parsed_accounts[0]
        primary["isActive"] = True

    # Probe WorkBuddy gateway
    wb_status = check_workbuddy_status()

    providers: list[dict[str, Any]] = []
    for acc in parsed_accounts:
        active_label = " (当前活跃)" if acc.get("isActive") else ""
        providers.append({
            "id": f"antigravity_{acc['account']}",
            "name": f"Google AI{active_label}",
            "plan": acc["plan"],
            "account": acc["account"],
            "status": "active" if acc.get("isActive") else "standby",
            "priority": acc["priority"],
            "windows": [
                {"label": "Gemini 5h 滚动额度", "remaining": acc["quota5h"], "reset": acc["reset5h"]},
                {"label": "Gemini 每周总配额", "remaining": acc["quotaWeekly"], "reset": acc["resetWeekly"]},
                {"label": "3P 协同池 (Claude/GPT)", "remaining": acc["claudeQuota5h"], "reset": None},
            ],
        })
    providers.append(wb_status)

    result: dict[str, Any] = {
        "status": "ok",
        "account": primary["account"],
        "activeAccount": primary["account"],
        "plan": primary["plan"],
        "quota5h": primary["quota5h"],
        "reset5h": primary["reset5h"],
        "quotaWeekly": primary["quotaWeekly"],
        "resetWeekly": primary["resetWeekly"],
        "claudeQuota5h": primary["claudeQuota5h"],
        "claudeQuotaWeekly": primary["claudeQuotaWeekly"],
        "accounts": parsed_accounts,
        "accountsCount": len(parsed_accounts),
        "source": "Google 官方直连 (Hermes 内置)",
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "updatedAtLocal": time.strftime("%H:%M:%S"),
        "workbuddy": wb_status,
        "providers": providers,
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


def format_quota_markdown(data: dict) -> str:
    """Render quota and gateway data into crisp, readable markdown for CLI and chat."""
    if "error" in data:
        return f"⚠️ **配额获取异常**: {data.get('error')}"

    sync = data.get("updatedAtLocal", "--")
    wb = data.get("workbuddy", {})
    wb_status = wb.get("statusLabel", "未启动")
    wb_note = wb.get("note", "")

    accounts = data.get("accounts")
    if not accounts:
        accounts = [{
            "account": data.get("account", "未知账号"),
            "plan": data.get("plan", "Google AI Pro"),
            "quota5h": data.get("quota5h", 100),
            "quotaWeekly": data.get("quotaWeekly", 100),
            "reset5h": data.get("reset5h", "--"),
            "resetWeekly": data.get("resetWeekly", "--"),
            "claudeQuota5h": data.get("claudeQuota5h", 100),
            "isActive": True,
        }]

    lines = [f"### 📊 模型配额与本地网关监控 (`{sync}`)\n"]
    lines.append("**Google AI (EasyCLIProxyAPI 官方直连)**")

    for acc in accounts:
        active_badge = " `● 当前活跃`" if acc.get("isActive") else ""
        lines.append(f"- **账号**：`{acc['account']}` ({acc.get('plan', 'Google AI')}){active_badge}")
        lines.append(
            f"  - Gemini 5h: `{acc['quota5h']}%` *(重置: `{acc.get('reset5h') or '--'}`)* | 周配额: `{acc['quotaWeekly']}%` *(重置: `{acc.get('resetWeekly') or '--'}`)*"
        )
        lines.append(f"  - Claude 3p 协同: `{acc.get('claudeQuota5h', 100)}%`")

    lines.append("")
    lines.append("**WorkBuddy (codebuddy2openai)**")
    lines.append(f"- **网关状态**：`{wb_status}` · `{wb_note}`")
    lines.append("- **本地端点**：`http://127.0.0.1:8787/v1`")

    usage = wb.get("usage")
    if wb.get("status") == "online" and usage:
        pct = usage.get("remainPercent", 0)
        paid = "付费版" if usage.get("isPaidUser") else "免费版"
        packages = usage.get("packages", [])
        pkg_lines = "\n".join(
            f"  - 包 `{p.get('code', '')[-8:]}`: `{p.get('remain', 0):.0f}`/`{p.get('total', 0):.0f}` {p.get('unit', 'credits')}"
            for p in packages
        )
        lines.append(f"- **当前账号**：`{usage.get('nickname', '—')}` ({paid})")
        lines.append(f"- **积分余量**：`{usage.get('remain', 0):.1f}` / `{usage.get('total', 0):.0f}` (`{pct}%`)")
        if pkg_lines:
            lines.append(f"- **积分包明细**：\n{pkg_lines}")
    elif wb.get("usageError"):
        lines.append(f"- **积分查询**: ⚠️ {wb.get('usageError')}")

    lines.append("\n*(输入 `/quota refresh` 可强制穿透刷新)*")
    return "\n".join(lines)


@router.get("/quota")
async def quota(force: str = Query("", description="force=1 bypasses the 30s cache")):
    # 顺路做 OpenViking 提炼模型自动跟随（模型没变时是零开销幂等检查）
    _auto_ovlm_follow()
    data = fetch_google_quota(force=force in ("1", "true", "yes"))
    if "error" in data:
        return JSONResponse(status_code=502, content=data)
    return data


# ==================== OpenViking VLM 联动（记忆提炼跟随当前聊天模型） ====================
#
# 机制（为什么改 ov.conf 能“动态”生效）:
#   OpenViking 的 VLM 实例在服务进程启动时按 ov.conf 创建并缓存；
#   本机 1933 懒唤醒网关会在空闲 2 分钟后杀掉真实服务(1934)，
#   下次请求重新拉起并重读 ov.conf —— 因此写入 ov.conf 的改动
#   最迟在“空闲 2 分钟 + 下次唤醒”后生效，无需重启任何常驻进程。

import re as _re  # noqa: E402
import sqlite3 as _sqlite3  # noqa: E402

_HERMES_CONFIG_YAML = _hermes_home() / "config.yaml"
_OV_CONF = Path.home() / ".openviking" / "ov.conf"
_OVLM_STATE_FILE = _hermes_home() / "desktop-plugins" / "token-stats" / "ovlm-state.json"
_OV_BACKEND_PORT = 1934


def _load_ovlm_state() -> dict:
    try:
        return json.loads(_OVLM_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"follow_enabled": True, "last_sync": None}


def _save_ovlm_state(state: dict) -> None:
    try:
        _OVLM_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _OVLM_STATE_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


def _redact_key(key: str) -> str:
    return (key[:4] + "****" + key[-4:]) if key and len(key) > 8 else "****"


def _read_current_chat_route() -> dict[str, Any]:
    """当前聊天模型真源：state.db.sessions 最新活跃一行（只读连接）。

    billing_provider 形如 custom:workbuddy-(127.0.0.1:8787) = "custom:" + provider名小写空格转横线。
    """
    out: dict[str, Any] = {"model": None, "provider": None, "session_id": None, "last_activity": None}
    db_path = _hermes_home() / "state.db"
    if not db_path.exists():
        out["error"] = "state.db not found"
        return out
    try:
        db = _sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
        try:
            row = db.execute(
                "SELECT id, model, billing_provider, last_activity_at FROM sessions "
                "WHERE model IS NOT NULL ORDER BY last_activity_at DESC LIMIT 1"
            ).fetchone()
        finally:
            db.close()
        if row:
            out.update(session_id=row[0], model=row[1], provider=row[2], last_activity=row[3])
    except Exception as exc:
        out["error"] = str(exc)
    return out


def _map_provider(provider_slug: Optional[str]) -> dict[str, Any]:
    """把 billing_provider slug 映射到 config.yaml custom_providers 条目。

    匹配顺序: ①名字 slug 精确匹配 ②括号内 host:port 与 base_url 兜底（兼容改名前的旧 slug）。
    """
    fail = {"resolved": False}
    if not provider_slug or not provider_slug.startswith("custom:"):
        fail["reason"] = f"非 custom 类型 provider（{provider_slug or '空'}），无本地凭据可映射"
        return fail
    try:
        import yaml

        cfg = yaml.safe_load(_HERMES_CONFIG_YAML.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        fail["reason"] = f"config.yaml 读取失败: {exc}"
        return fail
    providers = cfg.get("custom_providers") or []
    want = "custom:" + _re.sub(r"\s+", "-", provider_slug[len("custom:"):].strip().lower())
    port_m = _re.search(r"\(([\d.]+:\d+)\)", provider_slug)
    for p in providers:
        name = str(p.get("name") or "")
        name_slug = "custom:" + _re.sub(r"\s+", "-", name.strip().lower())
        base_url = str(p.get("base_url") or "")
        matched = name_slug == want
        if not matched and port_m and port_m.group(1) in base_url:
            matched = True
        if matched:
            api_key = str(p.get("api_key") or "")
            if not api_key:
                return {"resolved": False, "reason": f"provider「{name}」缺 api_key"}
            return {
                "resolved": True,
                "name": name,
                "base_url": base_url.rstrip("/"),
                "api_key": api_key,
                "models": list((p.get("models") or {}).keys()),
            }
    fail["reason"] = f"custom_providers 中找不到匹配 {provider_slug}"
    return fail


def _ov_backend_awake() -> bool:
    import urllib.request

    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f"http://127.0.0.1:{_OV_BACKEND_PORT}/api/v1/system/status", timeout=1.0) as r:
            return r.status in (200, 401)
    except Exception:
        return False


def _read_ov_conf() -> dict:
    try:
        return json.loads(_OV_CONF.read_text(encoding="utf-8"))
    except Exception:
        return {}


def compute_ovlm_status() -> dict[str, Any]:
    """聚合面板所需状态：ov.conf 当前值 vs 当前聊天模型目标值。"""
    state = _load_ovlm_state()
    chat = _read_current_chat_route()
    conf = _read_ov_conf()
    vlm = conf.get("vlm") or {}
    mapped = _map_provider(chat.get("provider")) if chat.get("provider") else {"resolved": False, "reason": "无活跃会话模型记录"}

    target = None
    if mapped.get("resolved"):
        target = {"api_base": mapped["base_url"], "model": chat.get("model")}

    current = {"api_base": vlm.get("api_base"), "model": vlm.get("model"), "key": _redact_key(str(vlm.get("api_key") or ""))}
    in_sync = bool(target and current["api_base"] == target["api_base"] and current["model"] == target["model"])

    return {
        "current": current,
        "chat": {
            "session_id": chat.get("session_id"),
            "model": chat.get("model"),
            "provider": chat.get("provider"),
            "last_activity": chat.get("last_activity"),
        },
        "mapped": {
            "resolved": mapped.get("resolved", False),
            "name": mapped.get("name"),
            "base_url": mapped.get("base_url"),
            "key_tail": _redact_key(mapped["api_key"]) if mapped.get("resolved") else None,
            "reason": None if mapped.get("resolved") else mapped.get("reason"),
            "model_in_catalog": bool(
                mapped.get("resolved") and (not mapped.get("models") or chat.get("model") in mapped["models"])
            ),
        },
        "target": target,
        "in_sync": in_sync,
        "follow_enabled": bool(state.get("follow_enabled", True)),
        "last_sync": state.get("last_sync"),
        "backend_awake": _ov_backend_awake(),
        "ov_conf_path": str(_OV_CONF),
        "mechanism_note": "写入 ov.conf 后，OpenViking 服务(1934)在空闲 2 分钟自动休眠、下次请求唤醒时按新配置拉起",
    }


def apply_ovlm_sync(force: bool = False) -> dict[str, Any]:
    """把 ov.conf 的 vlm 段改写为当前聊天模型（幂等；目标未变时不落盘）。"""
    status = compute_ovlm_status()
    if not force and not status["follow_enabled"]:
        return {"synced": False, "reason": "联动已暂停（面板开关关闭）", "status": status}
    if not status["mapped"]["resolved"]:
        return {"synced": False, "reason": status["mapped"]["reason"], "status": status}
    if not status["chat"]["model"]:
        return {"synced": False, "reason": "无可用会话模型记录", "status": status}
    if status["in_sync"]:
        return {"synced": True, "changed": False, "reason": "已是目标状态", "status": status}

    conf = _read_ov_conf()
    if not conf:
        return {"synced": False, "reason": f"ov.conf 读取失败 ({_OV_CONF})", "status": status}

    # status 里的 key 已脱敏，这里重新映射拿真实凭据（不回传、不落日志）
    mapped = _map_provider(status["chat"]["provider"])
    if not mapped.get("resolved"):
        return {"synced": False, "reason": mapped.get("reason"), "status": status}
    conf["vlm"] = {
        "provider": "openai",
        "api_base": mapped["base_url"],
        "api_key": mapped["api_key"],
        "model": status["chat"]["model"],
    }

    try:
        tmp = _OV_CONF.with_suffix(".conf.tmp")
        tmp.write_text(json.dumps(conf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(_OV_CONF)
    except Exception as exc:
        return {"synced": False, "reason": f"ov.conf 写入失败: {exc}", "status": status}

    state = _load_ovlm_state()
    state["last_sync"] = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model": status["target"]["model"],
        "api_base": status["target"]["api_base"],
        "session_id": status["chat"]["session_id"],
    }
    _save_ovlm_state(state)

    status2 = compute_ovlm_status()
    return {"synced": True, "changed": True, "backend_awake": status2["backend_awake"], "status": status2}


def _bounce_ov_backend() -> dict[str, Any]:
    """立即生效：杀掉 awake 状态的 1934，下次请求由懒网关按新配置重新拉起。"""
    import subprocess

    out = subprocess.run(["netstat", "-ano"], capture_output=True).stdout.decode("gbk", errors="ignore")
    pids = set()
    for line in out.splitlines():
        if str(_OV_BACKEND_PORT) in line and "LISTENING" in line:
            pids.add(line.strip().split()[-1])
    killed = []
    for pid in pids:
        r = subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
        if r.returncode == 0:
            killed.append(pid)
    return {"killed_pids": killed, "awake_after": _ov_backend_awake()}


_auto_follow_lock = threading.Lock()
_auto_follow_last = 0.0


def _auto_ovlm_follow() -> None:
    """跟随式自动同步：聊天模型变化 → 写 ov.conf + 踢 1934 立即生效。

    每次 /quota 轮询（面板 15s 一次）顺路调用；模型未变化时是零开销检查。
    follow_enabled=false 时完全不动作（手动同步按钮仍可用）。
    """
    global _auto_follow_last
    if not _auto_follow_lock.acquire(blocking=False):
        return
    try:
        if time.time() - _auto_follow_last < 30:  # 冷却：多个轮询源并发时只处理一次
            return
        _auto_follow_last = time.time()
        state = _load_ovlm_state()
        if not state.get("follow_enabled", True):
            return
        status = compute_ovlm_status()
        if status["in_sync"] or not status["mapped"]["resolved"]:
            return
        # 聊天会话刚结束（>90s 无活动）时不自动切换，避免污染下一次会话的目标
        chat = status["chat"]
        last_activity = chat.get("last_activity")
        if isinstance(last_activity, (int, float)) and (time.time() - last_activity) > 90:
            return
        result = apply_ovlm_sync(force=False)
        if result.get("synced") and result.get("changed"):
            bounced = _bounce_ov_backend()
            state["last_auto"] = {
                "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "model": result["status"]["target"]["model"],
                "bounced": bool(bounced.get("killed_pids")),
            }
            _save_ovlm_state(state)
            log.info("OVLM auto-follow: switched to %s, backend bounced=%s",
                     result["status"]["target"]["model"], bool(bounced.get("killed_pids")))
    except Exception:
        log.exception("OVLM auto-follow failed (non-fatal)")
    finally:
        _auto_follow_lock.release()


@router.get("/ovlm")
async def ovlm(
    sync: str = Query("", description="sync=1 执行同步写 ov.conf"),
    force: str = Query("", description="force=1 忽略 follow_enabled 开关强制同步"),
    apply: str = Query("", description="apply=1 同步成功后立即重启 1934 使配置生效"),
    toggle: str = Query("", description="toggle=1 翻转 follow_enabled 开关"),
):
    if toggle in ("1", "true", "yes"):
        state = _load_ovlm_state()
        state["follow_enabled"] = not bool(state.get("follow_enabled", True))
        _save_ovlm_state(state)
    if sync in ("1", "true", "yes"):
        result = apply_ovlm_sync(force=force in ("1", "true", "yes"))
        applied = None
        if result.get("synced") and result.get("changed") and apply in ("1", "true", "yes"):
            applied = _bounce_ov_backend()
        return {**result, "applied": applied}
    return compute_ovlm_status()


@router.get("/health")
async def health():
    return {"status": "ok", "plugin": "token-stats"}
