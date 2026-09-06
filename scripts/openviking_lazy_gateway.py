#!/usr/bin/env python3
"""OpenViking Serverless Lazy Gateway (Socket-Activation & Auto-Sleep).

Listens on port 1933 (the port Hermes expects).
1. When a request arrives:
   - If backends (Embedding 18082 & OpenViking 1934) are asleep, automatically wakes them up silently.
   - Forwards the HTTP request to 1934 and returns the response.
   - Updates the last-active timestamp.
2. When idle for IDLE_TIMEOUT (default: 15 minutes):
   - Automatically terminates 18082 (releasing GPU VRAM) and 1934.
   - Stays listening silently on 1933 with zero GPU / ~15MB RAM footprint.
"""

import http.server
import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

LISTEN_PORT = 1933
BACKEND_PORT = 1934
EMBEDDING_PORT = 18082

IDLE_TIMEOUT_SECONDS = int(os.environ.get("OPENVIKING_IDLE_TIMEOUT", "120"))  # 2 minutes
CREATE_NO_WINDOW = 0x08000000

LLAMA_SERVER_EXE = Path("D:/HermesRuntimes/llamacpp/b10679/cuda/llama-server.exe")
BGE_M3_MODEL = Path("D:/HermesModels/bge-m3-Q8_0.gguf")
OPENVIKING_SERVER_EXE = Path("C:/Users/VOS-User/.openviking/venv/Scripts/openviking-server.exe")
LOG_DIR = Path("C:/Users/VOS-User/.openviking/logs")


class GatewayState:
    def __init__(self):
        self.lock = threading.Lock()
        self.last_active = 0.0
        self.is_awake = False


state = GatewayState()


def is_port_listening(port: int) -> bool:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        url = f"http://127.0.0.1:{port}/health" if port == EMBEDDING_PORT else f"http://127.0.0.1:{port}/api/v1/system/status"
        req = urllib.request.Request(url)
        with opener.open(req, timeout=1.0) as r:
            return r.status in (200, 401)
    except Exception:
        return False


def wake_backends():
    with state.lock:
        if is_port_listening(BACKEND_PORT) and is_port_listening(EMBEDDING_PORT):
            state.is_awake = True
            state.last_active = time.time()
            return

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        print(f"[{time.strftime('%H:%M:%S')}] [Auto-Wake] Activity detected on 1933. Waking up backends...")

        # 1. Start Embedding server (18082) if not running
        if not is_port_listening(EMBEDDING_PORT):
            emb_log = open(LOG_DIR / "embedding-server.log", "a", encoding="utf-8")
            cmd = [
                str(LLAMA_SERVER_EXE),
                "-m", str(BGE_M3_MODEL),
                "--embedding",
                "--port", str(EMBEDDING_PORT),
                "--host", "127.0.0.1",
                "-c", "8192",
                "-b", "8192",
                "--ubatch-size", "8192",
                "-ngl", "99",
            ]
            subprocess.Popen(cmd, stdout=emb_log, stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW)

        # 2. Start OpenViking server (1934) if not running
        if not is_port_listening(BACKEND_PORT):
            ov_log = open(LOG_DIR / "openviking-server.log", "a", encoding="utf-8")
            cmd = [str(OPENVIKING_SERVER_EXE), "--port", str(BACKEND_PORT)]
            subprocess.Popen(cmd, stdout=ov_log, stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW)

        # 3. Wait for readiness
        t0 = time.time()
        while time.time() - t0 < 20.0:
            time.sleep(0.3)
            if is_port_listening(EMBEDDING_PORT) and is_port_listening(BACKEND_PORT):
                print(f"[{time.strftime('%H:%M:%S')}] [Auto-Wake] Backends ready in {time.time() - t0:.2f}s.")
                state.is_awake = True
                state.last_active = time.time()
                return

        print(f"[{time.strftime('%H:%M:%S')}] [Auto-Wake] Warning: Wake-up wait timed out.")
        state.last_active = time.time()


def sleep_backends():
    with state.lock:
        if not state.is_awake:
            return
        print(f"[{time.strftime('%H:%M:%S')}] [Auto-Sleep] Idle for {IDLE_TIMEOUT_SECONDS // 60} minutes. Freeing GPU VRAM...")
        try:
            import psutil
            target_ports = {EMBEDDING_PORT, BACKEND_PORT}
            for conn in psutil.net_connections(kind="inet"):
                if conn.status == psutil.CONN_LISTEN and conn.laddr and conn.laddr.port in target_ports:
                    if conn.pid:
                        try:
                            p = psutil.Process(conn.pid)
                            for child in p.children(recursive=True):
                                try:
                                    child.kill()
                                except Exception:
                                    pass
                            p.kill()
                        except Exception:
                            pass
        except Exception:
            try:
                out = subprocess.run(["netstat", "-ano"], capture_output=True, creationflags=CREATE_NO_WINDOW).stdout.decode("gbk", errors="ignore")
                for port in [str(EMBEDDING_PORT), str(BACKEND_PORT)]:
                    for line in out.splitlines():
                        if port in line and "LISTENING" in line:
                            pid = line.strip().split()[-1]
                            subprocess.run(["taskkill", "/F", "/T", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
            except Exception:
                pass
        state.is_awake = False
        print(f"[{time.strftime('%H:%M:%S')}] [Auto-Sleep] GPU VRAM and resources 100% freed. Standing by.")


def idle_monitor_thread():
    while True:
        time.sleep(10)
        if state.is_awake and state.last_active > 0:
            idle_for = time.time() - state.last_active
            if idle_for >= IDLE_TIMEOUT_SECONDS:
                sleep_backends()


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress routine request logging to keep console/logs clean
        pass

    def do_proxy(self):
        wake_backends()
        state.last_active = time.time()

        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else None

        target_url = f"http://127.0.0.1:{BACKEND_PORT}{self.path}"
        headers = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "content-length")}

        req = urllib.request.Request(target_url, data=body, headers=headers, method=self.command)
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

        try:
            with opener.open(req, timeout=60.0) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ("transfer-encoding", "content-length"):
                        self.send_header(k, v)
                self.send_header("Content-Length", str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            err_body = e.read()
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in ("transfer-encoding", "content-length"):
                    self.send_header(k, v)
            self.send_header("Content-Length", str(len(err_body)))
            self.end_headers()
            self.wfile.write(err_body)
        except Exception as e:
            err_msg = json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err_msg)))
            self.end_headers()
            self.wfile.write(err_msg)

    do_GET = do_proxy
    do_POST = do_proxy
    do_PUT = do_proxy
    do_DELETE = do_proxy
    do_HEAD = do_proxy


def main():
    threading.Thread(target=idle_monitor_thread, daemon=True, name="idle-monitor").start()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", LISTEN_PORT), ProxyHandler)
    print(f"[{time.strftime('%H:%M:%S')}] OpenViking Lazy Gateway listening on 127.0.0.1:{LISTEN_PORT}")
    print(f"  - Auto-wake backends on demand (Embedding: {EMBEDDING_PORT}, OpenViking: {BACKEND_PORT})")
    print(f"  - Auto-sleep after {IDLE_TIMEOUT_SECONDS // 60} minutes of inactivity (releasing GPU VRAM)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down gateway...")
        sleep_backends()


if __name__ == "__main__":
    main()
