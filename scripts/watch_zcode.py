"""ZCode Session Watcher — robust background listener for Hermes-ZCode collaboration.

Polls C:/Users/VOS-User/.zcode/cli/db/db.sqlite every 3 seconds.
Accurately detects when the target session has completed its turn/work by checking:
1. Main session has settled (last part is assistant text / completion, no pending/running tools).
2. No recent activity (time_updated within last 15 seconds on main session or active subagents).
3. Ignores stale historical subagents from earlier completed batches.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

DB_PATH = Path(r"C:\Users\VOS-User\.zcode\cli\db\db.sqlite")


def is_active_working(conn: sqlite3.Connection, session_id: str, active_window_s: float = 15.0) -> bool:
    cur = conn.cursor()
    now_ms = time.time() * 1000
    cutoff_ms = now_ms - (active_window_s * 1000)

    # 1. Any currently running/pending tool in the main session?
    running_tool = cur.execute(
        f"SELECT 1 FROM part WHERE session_id = '{session_id}' AND json_extract(data, '$.type') = 'tool' AND json_extract(data, '$.state.status') IN ('running', 'pending') LIMIT 1"
    ).fetchone()
    if running_tool:
        return True

    # 2. Any subagent actively updated in the last 15 seconds?
    recent_subagents = cur.execute(
        f"SELECT id FROM session WHERE parent_id = '{session_id}' AND time_updated >= {cutoff_ms}"
    ).fetchall()

    for (sa_id,) in recent_subagents:
        sa_running = cur.execute(
            f"SELECT 1 FROM part WHERE session_id = '{sa_id}' AND json_extract(data, '$.type') = 'tool' AND json_extract(data, '$.state.status') IN ('running', 'pending') LIMIT 1"
        ).fetchone()
        if sa_running:
            return True

        # Check if recent subagent is mid-step
        last_part = cur.execute(
            f"SELECT data FROM part WHERE session_id = '{sa_id}' ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        if last_part:
            pd = json.loads(last_part[0])
            if pd.get("type") == "step-start":
                return True

    # 3. Check main session's latest event
    last_main_part = cur.execute(
        f"SELECT data, time_created FROM part WHERE session_id = '{session_id}' ORDER BY rowid DESC LIMIT 1"
    ).fetchone()
    if not last_main_part:
        return False

    mpd = json.loads(last_main_part[0])
    mtype = mpd.get("type")

    # If the main session just started a step or is executing a tool
    if mtype == "step-start":
        return True
    if mtype == "tool" and mpd.get("state", {}).get("status") in ("running", "pending"):
        return True

    # If the last event was a step-finish triggered by tool calls within 8s, it's still thinking/chaining
    if mtype == "step-finish" and mpd.get("reason") == "tool-calls":
        if now_ms - last_main_part[1] < 8000:
            return True

    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch ZCode session until complete")
    parser.add_argument("--session", default="sess_656a8367-2a67-4b01-be2c-f06bb80ecba5", help="Session ID to watch")
    parser.add_argument("--timeout", type=int, default=1800, help="Max wait seconds")
    parser.add_argument("--interval", type=int, default=3, help="Poll interval")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"Error: Database {DB_PATH} does not exist", file=sys.stderr)
        sys.exit(2)

    start_time = time.time()
    session_id = args.session
    consecutive_idle = 0

    while time.time() - start_time < args.timeout:
        try:
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
            working = is_active_working(conn, session_id)
            conn.close()

            if not working:
                consecutive_idle += 1
                if consecutive_idle >= 2:  # 2 checks idle (~6s)
                    print(f"ZCode session {session_id} has settled!")
                    sys.exit(0)
            else:
                consecutive_idle = 0
        except Exception:
            pass

        time.sleep(args.interval)

    print(f"Timeout after {args.timeout}s watching {session_id}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
