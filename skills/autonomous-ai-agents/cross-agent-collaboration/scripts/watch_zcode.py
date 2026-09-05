"""ZCode Session Watcher — background listener for Hermes-ZCode collaboration.

Polls C:/Users/VOS-User/.zcode/cli/db/db.sqlite every 3 seconds.
When all active subagents in the target session (or the latest session) reach
status='completed' or main session tool calls finish, exits 0.
Used with Hermes terminal(command="...", background=True, notify=True)
to wake up Hermes automatically without blocking the chat window.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

DB_PATH = Path(r"C:\Users\VOS-User\.zcode\cli\db\db.sqlite")


def get_latest_session(conn: sqlite3.Connection) -> str:
    cur = conn.cursor()
    row = cur.execute(
        "SELECT id FROM session WHERE task_type != 'subagent_child' ORDER BY time_updated DESC LIMIT 1"
    ).fetchone()
    if not row:
        raise RuntimeError("No session found in db.sqlite")
    return row[0]


def check_session_done(conn: sqlite3.Connection, session_id: str) -> bool:
    cur = conn.cursor()
    subagents = cur.execute(
        f"SELECT id FROM session WHERE parent_id = '{session_id}'"
    ).fetchall()

    if subagents:
        for sa in subagents:
            sa_id = sa[0]
            part = cur.execute(
                f"SELECT data FROM part WHERE session_id = '{sa_id}' ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            if not part:
                return False
            pd = json.loads(part[0])
            ptype = pd.get("type")
            if ptype == "tool" and pd.get("state", {}).get("status") in ("running", "pending"):
                return False
            if ptype == "step-start":
                return False

    main_part = cur.execute(
        f"SELECT data FROM part WHERE session_id = '{session_id}' ORDER BY rowid DESC LIMIT 1"
    ).fetchone()
    if not main_part:
        return False
    mpd = json.loads(main_part[0])
    mtype = mpd.get("type")
    if mtype == "tool" and mpd.get("state", {}).get("status") in ("running", "pending"):
        return False
    if mtype == "step-start":
        return False

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch ZCode session until complete")
    parser.add_argument("--session", default="", help="Session ID to watch (empty for latest)")
    parser.add_argument("--timeout", type=int, default=1800, help="Max wait seconds (default: 30min)")
    parser.add_argument("--interval", type=int, default=3, help="Poll interval in seconds")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"Error: Database {DB_PATH} does not exist", file=sys.stderr)
        sys.exit(2)

    start_time = time.time()
    session_id = args.session

    while time.time() - start_time < args.timeout:
        try:
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
            if not session_id:
                session_id = get_latest_session(conn)

            done = check_session_done(conn, session_id)
            conn.close()

            if done:
                print(f"ZCode session {session_id} has completed!")
                sys.exit(0)
        except Exception:
            pass

        time.sleep(args.interval)

    print(f"Timeout after {args.timeout}s watching {session_id}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
