#!/usr/bin/env python3
"""Sync youshouldknow docs to OpenViking incrementally.

Triggered by Git hooks (post-commit, post-merge) or manual run.
Runs non-blockingly and fails silently if OpenViking server is offline.
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path

OPENVIKING_URL = os.environ.get("OPENVIKING_ENDPOINT", "http://127.0.0.1:1933")
YSK_DOCS_DIR = Path("D:/ai coding/GitRepos/youshouldknow/docs")
GIT_DIR = Path("D:/ai coding/GitRepos/youshouldknow")
OV_EXE = Path.home() / ".openviking/venv/Scripts/ov.exe"
STATE_FILE = Path.home() / ".openviking/last_synced_ysk_commit.txt"


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
    if not YSK_DOCS_DIR.exists():
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

    if current_head and current_head == last_synced and "--force" not in sys.argv:
        print(f"[OpenViking YSK Sync] Already up to date at commit {current_head[:7]}")
        return

    print("[OpenViking YSK Sync] Triggering background incremental scan for youshouldknow...")
    try:
        subprocess.Popen(
            [str(OV_EXE), "add-resource", str(YSK_DOCS_DIR), "--to", "viking://resources/ysk"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if current_head:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            STATE_FILE.write_text(current_head, encoding="utf-8")
        print("[OpenViking YSK Sync] Triggered successfully.")
    except Exception as e:
        print(f"[OpenViking YSK Sync] Failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
