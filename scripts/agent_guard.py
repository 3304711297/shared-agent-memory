#!/usr/bin/env python3
"""Agent Exit Lifecycle Guard (Auto-Cleanup Supervisor for Windows 11).

Runs silently in the background via pythonw (independent virtualenv: ~/.openviking/venv).
Monitors the lifecycle of Hermes Desktop (Hermes.exe) and ZCode GUI (ZCode.exe).

Lifecycle Behavior:
1. When Hermes or ZCode is open, marks state as ACTIVE.
2. When all Agent GUIs are closed:
   - Debounces for 2.5 seconds (preventing spurious triggers during app relaunches).
   - Verifies all Agent GUIs are genuinely closed.
   - Automatically executes full tree-kill on orphaned MCP servers (Node.js, Serena).
   - Reaps hanging backend Python workers.
   - Automatically stops OpenViking gateway, releasing all GPU VRAM and RAM.
3. Consumes ~6MB memory and 0% CPU. Single-instance enforced.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

# Add script directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import psutil
from cleanup_agent_orphans import cleanup_orphans, is_agent_gui_running, log

PID_FILE = Path(r"C:\Users\VOS-User\AppData\Local\hermes\cache\agent_guard.pid")
PYTHONW_EXE = Path(r"C:\Users\VOS-User\.openviking\venv\Scripts\pythonw.exe")
SCRIPT_PATH = SCRIPT_DIR / "agent_guard.py"
CREATE_NO_WINDOW = 0x08000000


def is_guard_running() -> int | None:
    """Check if another agent_guard.py process is alive via PID file."""
    if not PID_FILE.exists():
        return None
    try:
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        if pid == os.getpid():
            return None
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)
            cmd = " ".join(p.cmdline()).lower()
            if "agent_guard.py" in cmd:
                return pid
    except Exception:
        pass
    return None


def run_guard_loop():
    existing_pid = is_guard_running()
    if existing_pid:
        log(f"[Agent Guard] Another instance (PID {existing_pid}) is already running. Exiting.")
        sys.exit(0)

    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")

    log(f"[Agent Guard] Started background listener (PID {os.getpid()}). Monitoring Hermes & ZCode GUIs.")
    was_active = is_agent_gui_running()
    log(f"[Agent Guard] Initial state: Agent GUI active = {was_active}")

    try:
        while True:
            time.sleep(2.5)
            is_active = is_agent_gui_running()

            if is_active:
                if not was_active:
                    log("[Agent Guard] Detected Agent GUI (Hermes/ZCode) launched. Armed for exit cleanup.")
                    was_active = True
            else:
                if was_active:
                    log("[Agent Guard] Agent GUI closed. Debouncing 2.5s before cleanup...")
                    time.sleep(2.5)
                    if not is_agent_gui_running():
                        log("[Agent Guard] Confirmed all Agent GUIs closed. Executing full automated cleanup...")
                        cleanup_orphans(force_all=False, stop_openviking=True)
                        was_active = False
                        log("[Agent Guard] Cleanup complete. Waiting for next Agent launch.")
                    else:
                        log("[Agent Guard] Agent GUI reopened during debounce window. Cleanup aborted.")

    except Exception as e:
        log(f"[Agent Guard] Guard loop encountered exception: {e}")
    finally:
        try:
            if PID_FILE.exists():
                PID_FILE.unlink()
        except Exception:
            pass


def start_daemon():
    """Start guard in background silently via pythonw."""
    pid = is_guard_running()
    if pid:
        print(f"[Agent Guard] Already running in background (PID {pid}).")
        return

    print("[Agent Guard] Starting Agent Guard daemon...")
    cmd = [str(PYTHONW_EXE), str(SCRIPT_PATH), "run"]
    subprocess.Popen(cmd, creationflags=CREATE_NO_WINDOW)
    time.sleep(1)
    new_pid = is_guard_running()
    if new_pid:
        print(f"[Agent Guard] Successfully started and monitoring in background (PID {new_pid}).")
    else:
        print("[Agent Guard] Started.")


def stop_daemon():
    """Stop guard daemon if running."""
    killed = 0
    my_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            pid = proc.info['pid']
            if pid == my_pid:
                continue
            cmd = ' '.join(proc.info['cmdline'] or []).lower()
            if "agent_guard.py" in cmd:
                try:
                    proc.kill()
                except Exception:
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    try:
        if PID_FILE.exists():
            PID_FILE.unlink()
    except Exception:
        pass
    print(f"[Agent Guard] Stopped {killed} guard daemon instance(s).")


def status():
    pid = is_guard_running()
    gui_active = is_agent_gui_running()
    print("\n--- Agent Guard Status ---")
    print(f"  Daemon State : {'RUNNING ✓ (PID ' + str(pid) + ')' if pid else 'STOPPED ✗'}")
    print(f"  Agent GUIs   : {'ACTIVE (Hermes/ZCode open)' if gui_active else 'CLOSED (None open)'}")
    print(f"  Actions      : Automatically cleans Node MCP, Serena, Python, and OpenViking upon GUI exit.\n")


def main():
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    if action == "run":
        run_guard_loop()
    elif action == "start":
        start_daemon()
    elif action == "stop":
        stop_daemon()
    elif action == "restart":
        stop_daemon()
        time.sleep(1)
        start_daemon()
    elif action == "status":
        status()
    else:
        print("Usage: agent_guard.py [start|stop|restart|status|run]")


if __name__ == "__main__":
    main()
