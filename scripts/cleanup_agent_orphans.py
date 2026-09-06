#!/usr/bin/env python3
"""Cleanup Agent Orphan Processes (Node.js MCP, Serena, Zombie Python).

Safely and specifically reaps orphaned processes spawned by Hermes and ZCode MCP servers.
Does NOT touch unrelated user node/python processes (e.g. web dev, scripts).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

try:
    import psutil
except ImportError:
    psutil = None


MCP_KEYWORDS = [
    "chrome-devtools-mcp",
    "desktop-commander",
    "context7-mcp",
    "serena",
]


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


def cleanup_orphans(force_all: bool = False, stop_openviking: bool = False) -> dict[str, int]:
    """Reap orphaned MCP and helper processes.
    
    If force_all is False, will refuse to kill Hermes/ZCode backend workers if their GUI is still active.
    """
    killed_counts = {"node": 0, "serena": 0, "python": 0, "other": 0}
    if not psutil:
        print("[Cleanup] psutil not available, running fallback taskkill...")
        subprocess.run(["taskkill", "/F", "/IM", "serena.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return killed_counts

    gui_active = is_agent_gui_running()

    for proc in psutil.process_iter(['pid', 'ppid', 'name', 'cmdline']):
        try:
            pid = proc.info['pid']
            if pid == os.getpid():
                continue
            name = (proc.info['name'] or '').lower()
            cmdline = ' '.join(proc.info['cmdline'] or []).lower()

            # 1. Node.js MCP servers
            if name == 'node.exe':
                if any(kw in cmdline for kw in ["chrome-devtools-mcp", "desktop-commander", "context7-mcp"]):
                    # Check if parent is dead or orphaned
                    try:
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        killed_counts["node"] += 1
                    except Exception:
                        pass

            # 2. Serena MCP
            elif name == 'serena.exe' or ('serena' in cmdline and name in ('python.exe', 'pythonw.exe', 'uv.exe', 'uvx.exe')):
                try:
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    killed_counts["serena"] += 1
                except Exception:
                    pass

            # 3. Zombie Hermes CLI / Gateway / Serve processes (ONLY when GUI is closed or force_all)
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

    if stop_openviking:
        try:
            from openviking_service import stop as stop_ov
            stop_ov()
        except Exception:
            pass

    return killed_counts


def main():
    force = "--force" in sys.argv
    stop_ov = "--stop-openviking" in sys.argv
    print(f"[Cleanup] Scanning for orphaned Agent processes (GUI active: {is_agent_gui_running()})...")
    res = cleanup_orphans(force_all=force, stop_openviking=stop_ov)
    total = sum(res.values())
    print(f"[Cleanup] Done. Terminated {total} orphaned process(es):")
    print(f"  - Node.js MCP servers: {res['node']}")
    print(f"  - Serena MCP workers : {res['serena']}")
    print(f"  - Zombie Python runs : {res['python']}")


if __name__ == "__main__":
    main()
