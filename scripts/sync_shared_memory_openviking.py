#!/usr/bin/env python3
"""Sync shared-agent-memory topics to OpenViking incrementally.

Can be called by Git hooks (post-commit, post-merge) or Hermes startup reconciliation.
Runs non-blockingly and fails silently if OpenViking server is offline.
"""

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

OPENVIKING_URL = os.environ.get("OPENVIKING_ENDPOINT", "http://127.0.0.1:1933")
SHARED_TOPICS_DIR = Path("C:/Users/VOS-User/.zcode/cli/memories/projects/default-135ef1b9f66d8a7e/memory")
OV_EXE = Path("C:/Users/VOS-User/.openviking/venv/Scripts/ov.exe")
STATE_FILE = Path("C:/Users/VOS-User/.openviking/last_synced_commit.txt")
GIT_DIR = Path("C:/Users/VOS-User/.zcode/cli/memories")


def is_openviking_online() -> bool:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(f"{OPENVIKING_URL}/api/v1/system/status")
        with opener.open(req, timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False


def get_current_git_head() -> str:
    try:
        res = subprocess.run(
            ["git", "-C", str(GIT_DIR), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        return res.stdout.strip()
    except Exception:
        return ""


def main():
    if not SHARED_TOPICS_DIR.exists():
        return

    if not is_openviking_online():
        return

    current_head = get_current_git_head()
    last_synced = ""
    if STATE_FILE.exists():
        try:
            last_synced = STATE_FILE.read_text(encoding="utf-8").strip()
        except Exception:
            pass

    # If already synced to this commit, skip unless forced via --force
    if current_head and current_head == last_synced and "--force" not in sys.argv:
        print(f"[OpenViking Sync] Already up to date at commit {current_head[:7]}")
        return

    print(f"[OpenViking Sync] Triggering background re-scan for shared memory...")
    try:
        # Trigger background add-resource
        subprocess.Popen(
            [str(OV_EXE), "add-resource", str(SHARED_TOPICS_DIR), "--to", "viking://resources/shared-memory"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if current_head:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            STATE_FILE.write_text(current_head, encoding="utf-8")
        print("[OpenViking Sync] Triggered successfully.")
    except Exception as e:
        print(f"[OpenViking Sync] Failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
