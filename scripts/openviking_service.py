#!/usr/bin/env python3
"""OpenViking + Local Embedding Daemon Supervisor for Windows 11.

Manages:
  1. llama-server.exe on port 18082 (CUDA BGE-M3 1024-dim embedding)
  2. openviking-server.exe on port 1933 (Context Database)

All processes are launched silently without pop-up terminal windows.
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

LLAMA_SERVER_EXE = Path("D:/HermesRuntimes/llamacpp/b10679/cuda/llama-server.exe")
BGE_M3_MODEL = Path("D:/HermesModels/bge-m3-Q8_0.gguf")
OPENVIKING_SERVER_EXE = Path("C:/Users/VOS-User/.openviking/venv/Scripts/openviking-server.exe")
LOG_DIR = Path("C:/Users/VOS-User/.openviking/logs")

CREATE_NO_WINDOW = 0x08000000


def check_port_alive(url: str) -> bool:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(url)
        with opener.open(req, timeout=1.5) as r:
            return r.status in (200, 401)
    except Exception:
        return False


def start_embedding_server():
    if check_port_alive("http://127.0.0.1:18082/health"):
        print("[Embedding Server 18082] Already running.")
        return

    print("[Embedding Server 18082] Starting llama-server with bge-m3...")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = open(LOG_DIR / "embedding-server.log", "a", encoding="utf-8")
    cmd = [
        str(LLAMA_SERVER_EXE),
        "-m", str(BGE_M3_MODEL),
        "--embedding",
        "--port", "18082",
        "--host", "127.0.0.1",
        "-c", "8192",
        "-b", "8192",
        "--ubatch-size", "8192",
        "-ngl", "99",
    ]
    subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        creationflags=CREATE_NO_WINDOW,
    )
    for _ in range(10):
        time.sleep(0.5)
        if check_port_alive("http://127.0.0.1:18082/health"):
            print("[Embedding Server 18082] Ready.")
            return
    print("[Embedding Server 18082] Started (waiting for initialization).")


def start_openviking_server():
    if check_port_alive("http://127.0.0.1:1933/api/v1/system/status"):
        print("[OpenViking Server 1933] Already running.")
        return

    print("[OpenViking Server 1933] Starting openviking-server...")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = open(LOG_DIR / "openviking-server.log", "a", encoding="utf-8")
    cmd = [str(OPENVIKING_SERVER_EXE)]
    subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        creationflags=CREATE_NO_WINDOW,
    )
    for _ in range(15):
        time.sleep(0.5)
        if check_port_alive("http://127.0.0.1:1933/api/v1/system/status"):
            print("[OpenViking Server 1933] Ready.")
            return
    print("[OpenViking Server 1933] Started (waiting for initialization).")


def status():
    emb_ok = check_port_alive("http://127.0.0.1:18082/health")
    ov_ok = check_port_alive("http://127.0.0.1:1933/api/v1/system/status")
    print(f"Embedding Server (18082): {'ONLINE ✓' if emb_ok else 'OFFLINE ✗'}")
    print(f"OpenViking Server (1933): {'ONLINE ✓' if ov_ok else 'OFFLINE ✗'}")


def stop():
    print("Stopping services...")
    out = subprocess.run(["netstat", "-ano"], capture_output=True).stdout.decode("gbk", errors="ignore")
    for port in ["18082", "1933"]:
        for line in out.splitlines():
            if port in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                print(f"Killing PID {pid} on port {port}...")
                subprocess.run(["taskkill", "/F", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Services stopped.")


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "start"
    if action == "start":
        start_embedding_server()
        start_openviking_server()
        status()
    elif action == "stop":
        stop()
    elif action == "restart":
        stop()
        time.sleep(1)
        start_embedding_server()
        start_openviking_server()
        status()
    elif action == "status":
        status()
    else:
        print("Usage: openviking_service.py [start|stop|restart|status]")


if __name__ == "__main__":
    main()
