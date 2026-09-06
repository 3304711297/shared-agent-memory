#!/usr/bin/env python3
"""Shim: `openviking-server` on PATH for Hermes plugin auto-start.

When Hermes' OpenViking memory plugin finds the configured endpoint unreachable
(http://127.0.0.1:1933), it spawns `openviking-server --host <h> --port <p>` from PATH.
This shim intercepts that spawn and starts the FULL lazy-gateway stack instead
(gateway on 1933 + on-demand openviking-server 1934 + BGE-M3 embedding 18082,
with 2-minute idle auto-sleep), preserving the intended server topology.

Any --host/--port args are ignored: the gateway always binds 127.0.0.1:1933.
Exit 0 immediately; the gateway daemonizes via pythonw.
"""
import os
import subprocess
import sys
import time
import urllib.request

GATEWAY_SCRIPT = r"C:\Users\VOS-User\AppData\Local\hermes\scripts\openviking_lazy_gateway.py"
SERVICE_SCRIPT = r"C:\Users\VOS-User\AppData\Local\hermes\scripts\openviking_service.py"
PYTHONW = r"C:\Users\VOS-User\.openviking\venv\Scripts\pythonw.exe"
CREATE_NO_WINDOW = 0x08000000


def _alive(port: int, path: str) -> bool:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}")
        with opener.open(req, timeout=1.2) as r:
            return r.status in (200, 401)
    except Exception:
        return False


def main() -> int:
    if _alive(1933, "/api/v1/system/status"):
        return 0  # someone already listens (gateway or real server): nothing to do

    if os.path.exists(PYTHONW) and os.path.exists(GATEWAY_SCRIPT):
        # Full stack: lazy gateway (1933) + on-demand backends (1934/18082)
        subprocess.Popen([PYTHONW, GATEWAY_SCRIPT], creationflags=CREATE_NO_WINDOW)
    elif os.path.exists(PYTHONW):
        # Fallback: unified service manager (starts gateway as well)
        subprocess.Popen([PYTHONW, SERVICE_SCRIPT, "start"], creationflags=CREATE_NO_WINDOW)
    else:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
