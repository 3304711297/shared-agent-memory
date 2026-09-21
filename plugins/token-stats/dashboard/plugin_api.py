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
import datetime
from pathlib import Path
from typing import Any, Optional
from concurrent.futures import ThreadPoolExecutor

import sqlite3 as _sqlite3

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


_rl_cache: Optional[dict] = None
_rl_cache_time = 0.0
RL_CACHE_TTL = 20  # seconds — log scanning is cheap but not free; panel polls every 15s


def _fmt_credits_exact(value: Any) -> str:
    """积分的精确呈现（保留 2 位小数、去尾零，不约数、不显示浮点噪声）。

    上游 `CycleRemainCapacity` 是量化到 2 位小数的字符串，经 float64 呈现会带二进制
    尾数（实测 `"833.33000192"` 真值即 833.33 —— `833.33000192 + 3316.66999808 == 4150`
    精确闭合，证明尾数是浮点噪声而非真实额度）。故此处按 2 位小数量化后再去尾零：
    既保住真值精度，也不把噪声当有效数字展示。
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        return "—"
    if num != num or num in (float("inf"), float("-inf")):  # NaN / inf
        return "—"
    text = f"{num:.2f}".rstrip("0").rstrip(".")
    return text or "0"


def _workbuddy_rate_limit() -> dict[str, Any]:
    """WorkBuddy(8787) 上游频率限制状态与滚动用量观测（只读，不发起任何探测请求）。

    数据来源与优先级：
      ① 反代自曝端点 http://127.0.0.1:8787/api/rate_limit（新版 converter.py 提供，
         由真实上游 6004 报文落盘，最准）；
      ② 回退：扫描 Hermes 自身 logs/errors.log(+.1) 中的 6004 报文
         （老版构建没有 ① 时仍可用，纯被动解析，不消耗任何配额）。
    滚动用量一律来自反代 usage.jsonl 的本地统计（近 5h / 24h）。

    注意：腾讯侧并未公开固定阈值，实测「触发时的 5h 请求数」在 46~212 之间、
    「5h token 量」在 9.3M~20.3M 之间均出现过，且与未触发区间存在重叠，
    因此这里**只报实测值，不伪造百分比/阈值**。
    """
    global _rl_cache, _rl_cache_time
    if _rl_cache is not None and (time.time() - _rl_cache_time) < RL_CACHE_TTL:
        return dict(_rl_cache)

    import re as _rl_re
    import urllib.request as _u

    chat = _read_current_chat_route()
    model = chat.get("model") or ""
    out: dict[str, Any] = {
        "model": model,
        "state": "unknown",
        "resetAt": None,
        "resetLocal": None,
        "remainingSec": None,
        "message": None,
        "observed": {},
        "source": None,
    }

    # ---------- ① 优先：反代自曝端点 ----------
    try:
        opener = _u.build_opener(_u.ProxyHandler({}))
        with opener.open("http://127.0.0.1:8787/api/rate_limit", timeout=1.5) as r:
            rl = json.loads(r.read().decode("utf-8"))
        models = (rl or {}).get("models") or {}
        entry = models.get(model) if model else None
        if not entry and not model and models:
            entry = next(iter(models.values()))
        if entry:
            out.update(
                state=entry.get("state") or "unknown",
                resetAt=entry.get("resetAt"),
                resetLocal=entry.get("resetLocal"),
                remainingSec=entry.get("remainingSec"),
                message=entry.get("message"),
                source="workbuddy2api /api/rate_limit",
                limitedUid=entry.get("limitedUid"),
                limitedNickname=entry.get("limitedNickname"),
                isActiveAccountLimited=entry.get("isActiveAccountLimited"),
            )
            # 反代自 a404e80 起把「冷却已结束」从 ok 细化为 expired，三态语义：
            #   limited=正在冷却 / expired=曾限过已恢复 / ok=从未被限（无条目）
            # 这里原样透传给展示层，不做折叠——否则已恢复会被误报成「正常」或「未知」。
        elif rl is not None:
            out.update(
                state="ok",
                source="workbuddy2api /api/rate_limit",
            )
        if rl:
            if "rotation" in rl:
                out["rotation"] = rl.get("rotation")
            if "server" in rl:
                out["server"] = rl.get("server")
            if "nickname" in rl:
                out["nickname"] = rl.get("nickname")
            if "models" in rl:
                out["allModels"] = rl.get("models")
            if "accountCooldowns" in rl:
                out["accountCooldowns"] = rl.get("accountCooldowns")
            if "nightFree" in rl:
                out["nightFree"] = bool(rl.get("nightFree"))
            if "nightWindow" in rl:
                out["nightWindow"] = rl.get("nightWindow")
            # 降级感知透传（converter d311129+）：/api/rate_limit.fallbacks =
            # {requested: {actual, reason, count, lastLocal}}。当前会话模型命中时
            # 提升为顶层 fallback 字段，展示层据此渲染「你以为在用 ≠ 实际在用」。
            fbs = rl.get("fallbacks") or {}
            if fbs:
                out["allFallbacks"] = fbs
                hit = fbs.get(model)
                if hit:
                    out["fallback"] = {"requested": model, **hit}
            ru = rl.get("rollingUsage") or {}
            u_entry = ru.get(model) if model else None
            if not u_entry and not model and ru:
                u_entry = next(iter(ru.values()))
            if u_entry:
                out.setdefault("observed", {}).update(u_entry)
    except Exception:
        pass

    # ---------- ② 回退：解析 Hermes errors.log 的 6004 报文 ----------
    if not out.get("resetAt"):
        found: dict[str, Any] = {}
        for name in ("errors.log.1", "errors.log"):
            p = _hermes_home() / "logs" / name
            if not p.exists():
                continue
            try:
                size = p.stat().st_size
                with open(p, "rb") as f:
                    f.seek(max(0, size - 4 * 1024 * 1024))
                    tail = f.read().decode("utf-8", errors="ignore")
            except Exception:
                continue
            for m in _rl_re.finditer(
                r"model=([\w.\-]+).*?\"code\":6004,\"msg\":\"([^\"]*?将在\s*"
                r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*UTC\+8\s*重置[^\"]*?)\"",
                tail,
            ):
                try:
                    ts = datetime.datetime.strptime(m.group(3), "%Y-%m-%d %H:%M:%S").replace(
                        tzinfo=datetime.timezone(datetime.timedelta(hours=8))
                    )
                except Exception:
                    continue
                sec = ts.timestamp() - time.time()
                if sec <= 0:
                    continue  # 已过期，冷却结束
                cand = {
                    "model": m.group(1),
                    "state": "limited",
                    "resetAt": ts.isoformat(),
                    "resetLocal": m.group(3)[11:],
                    "remainingSec": int(sec),
                    "message": m.group(2),
                }
                # 命中当前聊天模型的优先；否则取最近一次
                if model and cand["model"] == model:
                    found = cand
                    break
                if not found:
                    found = cand
        if found:
            out.update(found)
            out["source"] = "Hermes errors.log (6004 报文)"
        elif out.get("source") is None:
            out["state"] = "ok"
            out["source"] = "Hermes errors.log (无 6004)"

    # ---------- 滚动用量观测（usage.jsonl） ----------
    try:
        now_ms = time.time() * 1000
        tz8 = datetime.timezone(datetime.timedelta(hours=8))
        now_dt = datetime.datetime.now(tz8)
        today_start_ms = now_dt.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000
        reqs_today = tok_today = err_today = 0
        reqs5 = reqs24 = err5 = 0
        tok5 = tok24 = 0
        last429: Optional[float] = None
        p = Path(os.environ.get("LOCALAPPDATA", "")) / "workbuddy2api" / "usage" / "usage.jsonl"
        if not p.exists():
            p = Path(os.environ.get("LOCALAPPDATA", "")) / "codebuddy2openai" / "usage" / "usage.jsonl"
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    ts = rec.get("ts")
                    if not ts or (now_ms - ts) > 24 * 3600 * 1000:
                        continue
                    if model and rec.get("model") != model:
                        continue
                    age5 = (now_ms - ts) <= 5 * 3600 * 1000
                    tokens = (rec.get("input_tokens") or 0) + (rec.get("output_tokens") or 0)
                    if rec.get("ok"):
                        reqs24 += 1
                        tok24 += tokens
                        if age5:
                            reqs5 += 1
                            tok5 += tokens
                        if ts >= today_start_ms:
                            reqs_today += 1
                            tok_today += tokens
                    elif rec.get("error") == "HTTP 429":
                        if age5:
                            err5 += 1
                        if ts >= today_start_ms:
                            err_today += 1
                        if last429 is None or ts > last429:
                            last429 = ts
        observed_local = {
            "reqsToday": reqs_today,
            "tokensToday": tok_today,
            "err429_today": err_today,
            "reqs5h": reqs5,
            "reqs24h": reqs24,
            "tokens5h": tok5,
            "tokens24h": tok24,
            "err429_5h": err5,
            "last429Local": (
                time.strftime("%m-%d %H:%M:%S", time.localtime(last429 / 1000)) if last429 else None
            ),
        }
        if "observed" not in out or not out["observed"]:
            out["observed"] = observed_local
        else:
            # 补齐可能缺失的字段
            for k, v in observed_local.items():
                out["observed"].setdefault(k, v)
        if "nightFree" not in out:
            out["nightFree"] = (now_dt.hour >= 23 or now_dt.hour < 8)
    except Exception:
        pass

    if out.get("state") == "unknown" and out.get("observed"):
        out["state"] = "limited" if out["observed"].get("err429_5h") else "ok"
    try:
        out["observedAt"] = time.strftime("%H:%M:%S")
    except Exception:
        pass
    with _cache_lock:
        _rl_cache = out
        _rl_cache_time = time.time()
    return out


def check_workbuddy_status() -> dict[str, Any]:
    """Non-blocking check for local WorkBuddy / workbuddy2api gateway (port 8787).

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
                    "name": "WorkBuddy (workbuddy2api)",
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
                            "note": f"账号「{usage.get('nickname', '—')}」· 积分 {_fmt_credits_exact(remain)}/{_fmt_credits_exact(total)} ({pct}%)",
                        })
                    else:
                        base["usageError"] = usage.get("error", "unknown")
                except Exception as exc:
                    base["usageError"] = f"积分获取失败: {exc}"
                # 上游频率限制状态（只读，不消耗配额）
                try:
                    base["rateLimit"] = _workbuddy_rate_limit()
                except Exception as exc:
                    base["rateLimit"] = {"state": "unknown", "error": str(exc)}
                return base
    except Exception:
        pass

    return {
        "id": "workbuddy",
        "name": "WorkBuddy (workbuddy2api)",
        "status": "offline",
        "statusLabel": "未启动",
        "endpoint": endpoint,
        "modelsCount": 0,
        "note": "本地反代服务待机中 (端口 8787)",
        "rateLimit": {"state": "offline"},
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
        # Google 拉取全失败（网络不可达 / token 过期 401 等）：降级而非整体失败。
        # WorkBuddy 积分是独立数据源，必须保持实时 —— 旧实现整端点退回磁盘缓存，
        # 导致 force 刷新后 WorkBuddy 积分永远钉在缓存快照（用户可见 bug）。
        wb_status = check_workbuddy_status()
        degraded: dict[str, Any] = {
            "status": "degraded",
            "degraded": True,
            "degradedReason": "Google 官方配额接口拉取失败（token 过期或网络不可达，可检查 EasyCLIProxyAPI 网关是否运行）；Google 额度为磁盘缓存快照，WorkBuddy 积分为实时探测",
            "workbuddy": wb_status,
            "providers": [wb_status],
            "source": f"⚠️ 降级模式：Google 配额不可用 · WorkBuddy 实时 · {time.strftime('%H:%M:%S')}",
            "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "updatedAtLocal": time.strftime("%H:%M:%S"),
        }
        old = _stale_disk_cache()
        if old is not None:
            for k in ("account", "activeAccount", "plan", "quota5h", "reset5h", "quotaWeekly",
                      "resetWeekly", "claudeQuota5h", "claudeQuotaWeekly", "accounts", "accountsCount"):
                if k in old:
                    degraded[k] = old[k]
        # 清掉内存缓存：降级期间每次轮询都重新实时探测，恢复后无缝回到正常路径
        with _cache_lock:
            _cache_data = None
            _cache_time = 0.0
        return degraded

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

    if data.get("degraded"):
        lines.append(f"> ⚠️ **降级模式**：{data.get('degradedReason', 'Google 配额不可用')}\n")
    lines.append("**Google AI (EasyCLIProxyAPI 官方直连)**")

    for acc in accounts:
        active_badge = " `● 当前活跃`" if acc.get("isActive") else ""
        lines.append(f"- **账号**：`{acc['account']}` ({acc.get('plan', 'Google AI')}){active_badge}")
        lines.append(
            f"  - Gemini 5h: `{acc['quota5h']}%` *(重置: `{acc.get('reset5h') or '--'}`)* | 周配额: `{acc['quotaWeekly']}%` *(重置: `{acc.get('resetWeekly') or '--'}`)*"
        )
        lines.append(f"  - Claude 3p 协同: `{acc.get('claudeQuota5h', 100)}%`")

    lines.append("")
    lines.append("**WorkBuddy (workbuddy2api)**")
    lines.append(f"- **网关状态**：`{wb_status}` · `{wb_note}`")
    lines.append("- **本地端点**：`http://127.0.0.1:8787/v1`")

    rl = wb.get("rateLimit") or {}
    if rl:
        st = rl.get("state", "unknown")
        icon = {"limited": "🔴", "ok": "🟢", "expired": "🟡", "offline": "⚪"}.get(st, "⚪")
        obs = rl.get("observed") or {}
        rot = rl.get("rotation") or {}
        if rot:
            mode_label = {
                "failover": "故障自动避让 (failover)",
                "roundrobin": f"按请求轮询 (每 {rot.get('rotate_count', 1)} 次)",
                "off": "单账号固定 (off)",
            }.get(rot.get("mode"), rot.get("mode", "off"))
            acc_cnt = rot.get("accounts_count", 1)
            src_tag = "已热加载" if rot.get("config_source") == "hot" else "默认"
            soonest_tag = f" · `临期优先: {rot.get('soonest_expire_day')}`" if rot.get("soonest_expire_day") else ""
            lines.append(f"- **账号调度**：`{mode_label}` · `{acc_cnt} 个可用账号`{soonest_tag} *({src_tag})*")
        if st == "limited":
            bits = [f"{icon} **频率限制**：已触发（上游 code 6004）"]
            if rl.get("resetLocal"):
                bits.append(f"重置于 `{rl['resetLocal']}`")
            if rl.get("remainingSec") is not None:
                h, m2 = divmod(int(rl["remainingSec"]) // 60, 60)
                bits.append(f"剩余 `{h}h{m2}m`")
            lines.append("- " + " · ".join(bits))
        elif st == "expired":
            # 曾触发过 6004 且冷却时刻已过：服务可用，但额度刚被消耗过，值得提示
            bits = [f"{icon} **频率限制**：已恢复（冷却结束）"]
            if rl.get("resetLocal"):
                bits.append(f"重置于 `{rl['resetLocal']}`")
            lines.append("- " + " · ".join(bits))
        else:
            label = "正常" if st == "ok" else ("网关离线" if st == "offline" else "未知")
            lines.append(f"- {icon} **频率限制**：{label}")
        if rl.get("model"):
            lines.append(f"- **监控模型**：`{rl['model']}`")
        all_models = rl.get("allModels") or {}
        limited_others = [
            f"`{m}` (重置于 `{info.get('resetLocal')}`)"
            for m, info in all_models.items()
            if info.get("state") == "limited" and m != rl.get("model")
        ]
        if limited_others:
            lines.append(f"- ⚠️ **其他冷却中模型**：{', '.join(limited_others)}")
        if rl.get("nightFree"):
            lines.append("- 🌙 **夜间限免**：`限免中 (23:00–08:00)` · 调用不扣积分")
        elif rl.get("nightWindow"):
            lines.append("- ☀️ **时段计费**：`白天按量计费` (夜间 23:00–08:00 免积分)")
        srv = rl.get("server") or {}
        if srv.get("protocols"):
            proto_str = "/".join(p.capitalize() for p in srv["protocols"])
            lines.append(f"- **协议网关**：`{proto_str}` (413保护: {srv.get('maxBodyMb', 16)}MB)")
        if obs:
            reqs_today = obs.get("reqsToday")
            tok_today = obs.get("tokensToday")
            if reqs_today is not None:
                lines.append(
                    f"- **今日用量**：`{reqs_today}` 次 / `{(tok_today or 0)/1e6:.2f}M` tokens"
                    + (f" · 429 次数 `{obs.get('err429_today', 0)}`" if obs.get("err429_today") else "")
                )
            lines.append(
                f"- **近 5h 用量**：`{obs.get('reqs5h', 0)}` 次 / `{(obs.get('tokens5h') or 0)/1e6:.2f}M` tokens"
                + (f" · 429 次数 `{obs.get('err429_5h', 0)}`" if obs.get("err429_5h") else "")
            )
            if obs.get("last429Local"):
                lines.append(f"- **最近一次 429**：`{obs['last429Local']}`")
        if rl.get("source"):
            lines.append(f"- *限制状态数据源：{rl['source']}*")

    usage = wb.get("usage")
    if wb.get("status") == "online" and usage:
        pct = usage.get("remainPercent", 0)
        paid = "付费版" if usage.get("isPaidUser") else "免费版"
        packages = usage.get("packages", [])
        pkg_lines = "\n".join(
            f"  - 包 `{p.get('code', '')[-8:]}`: `{_fmt_credits_exact(p.get('remain', 0))}`/`{_fmt_credits_exact(p.get('total', 0))}` {p.get('unit', 'credits')}"
            for p in packages
        )
        lines.append(f"- **当前账号**：`{usage.get('nickname', '—')}` ({paid})")
        lines.append(f"- **积分余量**：`{_fmt_credits_exact(usage.get('remain', 0))}` / `{_fmt_credits_exact(usage.get('total', 0))}` (`{pct}%`)")
        if pkg_lines:
            lines.append(f"- **积分包明细**：\n{pkg_lines}")
    elif wb.get("usageError"):
        lines.append(f"- **积分查询**: ⚠️ {wb.get('usageError')}")

    lines.append("\n*(输入 `/quota refresh` 可强制穿透刷新)*")
    return "\n".join(lines)


@router.get("/rate_limit")
async def rate_limit():
    """WorkBuddy(8787) 上游频率限制状态与滚动用量观测（只读，不消耗配额）。"""
    return _workbuddy_rate_limit()


@router.get("/quota")
async def quota(force: str = Query("", description="force=1 bypasses the 30s cache")):
    data = fetch_google_quota(force=force in ("1", "true", "yes"))
    if "error" in data:
        return JSONResponse(status_code=502, content=data)
    return data



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


@router.get("/health")
async def health():
    return {"status": "ok", "plugin": "token-stats"}
