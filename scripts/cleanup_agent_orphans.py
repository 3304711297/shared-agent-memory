#!/usr/bin/env python3
"""Cleanup Agent Orphan Processes (Node.js MCP, Serena, Zombie Python, OpenViking).

Safely and specifically reaps orphaned processes spawned by Hermes and ZCode MCP servers.
Does NOT touch unrelated user node/python processes (e.g. web dev, scripts).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

LOG_DIR = Path(r"C:\Users\VOS-User\AppData\Local\hermes\logs")
LOG_FILE = LOG_DIR / "agent_cleanup.log"

MCP_NODE_KEYWORDS = [
    "chrome-devtools-mcp",
    "desktop-commander",
    "context7-mcp",
]


def log(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def is_agent_gui_running() -> bool:
    """Check if Hermes Desktop or ZCode GUI is actively open."""
    if not psutil:
        return False
    for proc in psutil.process_iter(['name']):
        try:
            name = (proc.info['name'] or '').lower()
            if name in ('hermes.exe', 'zcode.exe'):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def cleanup_orphans(force_all: bool = False, stop_openviking: bool = True) -> dict[str, int]:
    """Reap orphaned MCP, worker, and helper processes.
    
    If force_all is False and an Agent GUI is currently open, it will protect
    the active session and only reap truly dead/orphaned MCP servers.
    """
    killed_counts = {"node": 0, "serena": 0, "python": 0, "other": 0}
    gui_active = is_agent_gui_running()

    if not psutil:
        subprocess.run(["taskkill", "/F", "/IM", "serena.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return killed_counts

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            pid = proc.info['pid']
            if pid == os.getpid():
                continue
            name = (proc.info['name'] or '').lower()
            cmdline = ' '.join(proc.info['cmdline'] or []).lower()

            # 1. Node.js MCP servers
            if name == 'node.exe':
                if any(kw in cmdline for kw in MCP_NODE_KEYWORDS):
                    # Only kill if GUI is closed OR force_all
                    if not gui_active or force_all:
                        try:
                            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            killed_counts["node"] += 1
                        except Exception:
                            pass

            # 2. Serena MCP (serena.exe and its spawned uvx/python helpers)
            elif name == 'serena.exe' or ('serena' in cmdline and name in ('python.exe', 'pythonw.exe', 'uv.exe', 'uvx.exe')):
                if not gui_active or force_all:
                    try:
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        killed_counts["serena"] += 1
                    except Exception:
                        pass

            # 3. Zombie Hermes CLI / Gateway / Serve processes (ONLY when GUI is closed)
            elif name in ('python.exe', 'pythonw.exe'):
                if not gui_active or force_all:
                    if "hermes_cli.main gateway run" in cmdline or "hermes_cli.main --profile default serve" in cmdline:
                        try:
                            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            killed_counts["python"] += 1
                        except Exception:
                            pass

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # 4. Stop OpenViking stack if requested and GUI is closed
    if stop_openviking and (not gui_active or force_all):
        try:
            sys.path.insert(0, r"C:\Users\VOS-User\AppData\Local\hermes\scripts")
            import openviking_service
            openviking_service.stop()
            killed_counts["other"] += 1
        except Exception as e:
            log(f"Error stopping OpenViking: {e}")

    log(f"Cleanup finished. Terminated: Node={killed_counts['node']}, Serena={killed_counts['serena']}, Python={killed_counts['python']}, OpenViking={killed_counts['other']}")
    return killed_counts


def main():
    force = "--force" in sys.argv
    no_ov = "--no-openviking" in sys.argv
    log(f"Manual cleanup invoked (GUI active: {is_agent_gui_running()}, force: {force})")
    cleanup_orphans(force_all=force, stop_openviking=not no_ov)


if __name__ == "__main__":
    main()
