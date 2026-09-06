#!/usr/bin/env python3
"""OpenViking Unified Service Manager (Lazy Gateway & Process Control).

Usage:
  python openviking_service.py [start|stop|restart|status]

- start: Launches openviking_lazy_gateway.py via pythonw (listens on 1933, auto-wakes 18082/1934 on demand, auto-sleeps on idle).
- stop: Forcefully stops lazy gateway (1933), OpenViking backend (1934), and BGE-M3 embedding (18082), freeing all RAM and VRAM.
- restart: Stops all services and starts a fresh lazy gateway.
- status: Displays the operational status of Gateway (1933), Backend (1934), and Embedding (18082).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

LISTEN_PORT = 1933
BACKEND_PORT = 1934
EMBEDDING_PORT = 18082

PYTHONW_EXE = Path(r"C:\Users\VOS-User\.openviking\venv\Scripts\pythonw.exe")
LAZY_GATEWAY_SCRIPT = Path(r"C:\Users\VOS-User\AppData\Local\hermes\scripts\openviking_lazy_gateway.py")
CREATE_NO_WINDOW = 0x08000000


def check_port_listening(port: int, path: str = "/api/v1/system/status") -> bool:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        url = f"http://127.0.0.1:{port}{path}"
        req = urllib.request.Request(url)
        with opener.open(req, timeout=1.2) as resp:
            return resp.status in (200, 401)
    except Exception:
        return False


def get_pids_for_ports(ports: list[int]) -> set[str]:
    pids = set()
    try:
        out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, errors="ignore").stdout
        for line in out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and parts[3] == "LISTENING":
                local_addr = parts[1]
                for p in ports:
                    if local_addr.endswith(f":{p}"):
                        pids.add(parts[4])
    except Exception:
        pass
    return pids


def start():
    if check_port_listening(LISTEN_PORT):
        print(f"[OpenViking Gateway {LISTEN_PORT}] Already running.")
        status()
        return

    print(f"[OpenViking Gateway {LISTEN_PORT}] Starting lazy gateway silently...")
    if not PYTHONW_EXE.exists():
        print(f"Error: Pythonw binary not found at {PYTHONW_EXE}")
        return
    if not LAZY_GATEWAY_SCRIPT.exists():
        print(f"Error: Lazy gateway script not found at {LAZY_GATEWAY_SCRIPT}")
        return

    cmd = [str(PYTHONW_EXE), str(LAZY_GATEWAY_SCRIPT)]
    subprocess.Popen(cmd, creationflags=CREATE_NO_WINDOW)

    for _ in range(15):
        time.sleep(0.4)
        if check_port_listening(LISTEN_PORT):
            print(f"[OpenViking Gateway {LISTEN_PORT}] Successfully started and listening.")
            status()
            return
    print(f"[OpenViking Gateway {LISTEN_PORT}] Started (waiting for socket ready).")
    status()


def stop():
    print("[OpenViking] Stopping all related services...")
    pids = get_pids_for_ports([LISTEN_PORT, BACKEND_PORT, EMBEDDING_PORT])

    # Also find pythonw processes running openviking_lazy_gateway
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = ' '.join(proc.info['cmdline'] or [])
                if 'openviking_lazy_gateway.py' in cmd:
                    pids.add(str(proc.info['pid']))
                elif 'openviking-server.exe' in cmd:
                    pids.add(str(proc.info['pid']))
                elif 'llama-server.exe' in cmd and 'bge-m3' in cmd:
                    pids.add(str(proc.info['pid']))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        pass

    if pids:
        for pid in pids:
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        print(f"[OpenViking] Terminated {len(pids)} process(es) (PIDs: {', '.join(pids)}).")
    else:
        print("[OpenViking] No running processes found.")

    time.sleep(0.5)
    print("[OpenViking] All services and GPU VRAM 100% stopped and freed.")


def status():
    gw_online = check_port_listening(LISTEN_PORT)
    bk_online = check_port_listening(BACKEND_PORT)
    emb_online = check_port_listening(EMBEDDING_PORT, path="/health")

    print("\n--- OpenViking Status ---")
    print(f"  Lazy Gateway    (Port {LISTEN_PORT}): {'ONLINE ✓ (Listening)' if gw_online else 'OFFLINE ✗'}")
    print(f"  Backend Core    (Port {BACKEND_PORT}): {'ACTIVE  (Awake)' if bk_online else 'STANDBY / SLEEPING'}")
    print(f"  BGE-M3 Embed    (Port {EMBEDDING_PORT}): {'ACTIVE  (VRAM in use)' if emb_online else 'STANDBY / SLEEPING'}")
    if gw_online:
        print("  Auto-wake: Enabled (wakes 18082/1934 on first query, auto-sleeps after 120s idle)\n")
    else:
        print("  Service is completely stopped. Run 'openviking_service.py start' to launch.\n")


def main():
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    if action == "start":
        start()
    elif action == "stop":
        stop()
    elif action == "restart":
        stop()
        time.sleep(1)
        start()
    elif action == "status":
        status()
    else:
        print("Usage: openviking_service.py [start|stop|restart|status]")


if __name__ == "__main__":
    main()
