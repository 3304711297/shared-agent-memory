"""
Google / Antigravity Quota Monitor & Local Micro-Service
专为 Hermes Desktop Plugin (token-stats) 提供实时配额服务：
1. 自动定位 EasyCLIProxyAPI 官方凭据 (D:\\EasyCLIProxyAPI\\auth\\antigravity-*.json)；
2. 提取 Google OAuth 凭据，经本地代理直连 Google 官方 retrieveUserQuotaSummary 接口；
3. 解析 5h 重置窗口、周重置窗口、剩余百分比与精确重置时间戳；
4. 内存缓存 30s，磁盘持久化 direct-quota.json；
5. 内置高性能本地 HTTP 服务 (http://127.0.0.1:18088/quota)，开启 CORS 供前端无阻直读。
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread, Lock

PORT = 18088
PROXY_URL = "http://127.0.0.1:3067"
CACHE_TTL = 30  # 秒

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(SCRIPT_DIR, "direct-quota.json")
AUTH_DIR = r"D:\EasyCLIProxyAPI\auth"

_cache_data = None
_cache_time = 0
_lock = Lock()


def get_auth_file():
    if not os.path.exists(AUTH_DIR):
        return None
    for f in os.listdir(AUTH_DIR):
        if f.startswith("antigravity-") and f.endswith(".json"):
            return os.path.join(AUTH_DIR, f)
    return None


def fetch_google_quota(force=False):
    global _cache_data, _cache_time
    now = time.time()

    with _lock:
        if not force and _cache_data and (now - _cache_time < CACHE_TTL):
            return _cache_data

    auth_path = get_auth_file()
    if not auth_path:
        return {"error": "EasyCLIProxyAPI auth file not found in D:\\EasyCLIProxyAPI\\auth"}

    try:
        with open(auth_path, "r", encoding="utf-8") as f:
            auth = json.load(f)
    except Exception as e:
        return {"error": f"Failed to read auth file: {e}"}

    token = auth.get("access_token", "")
    project_id = auth.get("project_id", "aicode-consumers")
    email = auth.get("email", "")

    if not token:
        return {"error": "No access_token found in auth file"}

    # Antigravity 实际使用的是 daily-cloudcode-pa 端点，而非通用 cloudcode-pa
    url = "https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary"
    payload = json.dumps({"project": project_id}).encode("utf-8")

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

    try:
        with opener.open(req, timeout=8) as res:
            if res.status != 200:
                return {"error": f"Google returned HTTP {res.status}"}
            raw = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        # 网络异常时，尝试读取磁盘旧缓存
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    old = json.load(f)
                    old["stale"] = True
                    return old
            except Exception:
                pass
        return {"error": f"Request to Google failed: {e}"}

    quota_5h = None
    reset_5h = None
    quota_weekly = None
    reset_weekly = None
    third_party_5h = None
    third_party_weekly = None

    groups = raw.get("groups", [])
    for g in groups:
        dname = g.get("displayName", "")
        buckets = g.get("buckets", [])
        for b in buckets:
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

    result = {
        "status": "ok",
        "account": email,
        "plan": "Google AI Pro",
        "quota5h": quota_5h if quota_5h is not None else 100,
        "reset5h": reset_5h,
        "quotaWeekly": quota_weekly if quota_weekly is not None else 100,
        "resetWeekly": reset_weekly,
        "claudeQuota5h": third_party_5h,
        "claudeQuotaWeekly": third_party_weekly,
        "source": "Google 官方直连 (EasyCLIProxyAPI)",
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "updatedAtLocal": time.strftime("%H:%M:%S"),
    }

    with _lock:
        _cache_data = result
        _cache_time = now

    # 异步或同步写回文件
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return result


class QuotaHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        clean_path = self.path.split("?")[0]
        query = self.path.split("?")[1] if "?" in self.path else ""
        force = ("force=1" in query) or ("refresh=1" in query)

        if clean_path in ("/quota", "/api/quota", "/"):
            data = fetch_google_quota(force=force)
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/health":
            body = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # 静默运行，不打扰控制台
        return


def run_server(port=PORT):
    server = HTTPServer(("127.0.0.1", port), QuotaHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes Google Quota Service")
    parser.add_argument("--serve", action="store_true", help="Run HTTP server daemon")
    parser.add_argument("--port", type=int, default=PORT, help="Port to listen on")
    args = parser.parse_args()

    if args.serve:
        # 预热首次抓取
        fetch_google_quota()
        run_server(args.port)
    else:
        res = fetch_google_quota()
        print(json.dumps(res, ensure_ascii=False, indent=2))
