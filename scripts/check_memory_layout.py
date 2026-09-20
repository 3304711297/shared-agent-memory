#!/usr/bin/env python3
"""Guard the shared-memory junction layout (the link that silently breaks).

Why this exists
---------------
The real store is `D:/ai coding/GitRepos/shared-agent-memory` (branch `main`),
and `%LOCALAPPDATA%/hermes/memories/topics` is an NTFS junction pointing at its
`projects/<project>/memory/` directory. That target only exists on `main`:

  * checking out `hermes` (or any branch) inside the REAL STORE removes
    `projects/` from the working tree, so the junction's target vanishes and
    every read of `memories/topics/MEMORY.md` fails with "No such file or
    directory" — while git itself reports a perfectly clean tree;
  * `projects/` is `.gitignore`d on the `hermes` branch, so nothing in git
    status hints that anything is wrong.

This happened once (2026-09-20): the real store sat on `hermes` for ~1.5h, the
junction was dead the whole time, and six skill commits landed on `hermes`
instead of `main`. The failure is silent and easy to misread as "the file was
deleted" or "the junction was never created" — it is neither, and the junction
must NOT be recreated (its target just needs the right branch back).

What it checks
--------------
  1. the real store is on `main` (the single-store invariant);
  2. `memories/topics` resolves and actually contains the memory files;
  3. the memory file count on disk matches the count tracked on `main`;
  4. every junction under the Hermes home resolves to an existing target.

Exit 1 on any violation, 0 when clean. Read-only: never repairs, never writes.

Usage:
    python scripts/check_memory_layout.py            # scan, exit 1 on violation
    python scripts/check_memory_layout.py --verbose  # also list every junction
"""
import argparse
import os
import subprocess
import sys

# A junction/symlink carries FILE_ATTRIBUTE_REPARSE_POINT (0x400) in
# st_file_attributes; os.path.islink() is False for junctions, so it cannot be
# used here. This is the same predicate the layout is created with.
FILE_ATTRIBUTE_REPARSE_POINT = 0x400

DEFAULT_REAL_STORE = r"D:\ai coding\GitRepos\shared-agent-memory"


def _git(repo, *args):
    out = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    return out.returncode, (out.stdout or "").strip()


def _is_reparse_point(path):
    try:
        attrs = os.lstat(path).st_file_attributes
    except (OSError, AttributeError):
        return False
    return bool(attrs & FILE_ATTRIBUTE_REPARSE_POINT)


def _walk_junctions(root, max_depth=3):
    """Yield (path, target, target_exists) for every junction under root.

    Does not descend INTO a junction: its contents belong to another tree, and
    following them would both double-report and risk cycles.
    """
    found = []
    root = os.path.abspath(root)

    def walk(node, depth):
        if depth > max_depth:
            return
        try:
            entries = list(os.scandir(node))
        except (PermissionError, FileNotFoundError, OSError):
            return
        for entry in entries:
            if _is_reparse_point(entry.path):
                target = os.path.realpath(entry.path)
                found.append((entry.path, target, os.path.exists(target)))
                continue
            try:
                if entry.is_dir(follow_symlinks=False):
                    walk(entry.path, depth + 1)
            except OSError:
                continue

    walk(root, 0)
    return found


def check_real_store_branch(store, violations, notes):
    if not os.path.isdir(os.path.join(store, ".git")):
        violations.append(f"real store is not a git repository: {store}")
        return None
    code, branch = _git(store, "rev-parse", "--abbrev-ref", "HEAD")
    if code != 0:
        violations.append(f"cannot read branch of real store: {store}")
        return None
    if branch != "main":
        violations.append(
            f"real store is on '{branch}', not 'main' — this removes projects/ from the "
            f"working tree and kills the memories/topics junction. "
            f"Fix: cd \"{store}\" && git checkout main"
        )
    else:
        notes.append(f"real store branch: {branch}")
    return branch


def find_junction_target(home):
    """The junction whose TARGET must exist — reported explicitly, not by name."""
    topics = os.path.join(home, "memories", "topics")
    return topics


def check_topics_resolves(home, store, violations, notes):
    topics = find_junction_target(home)
    if not os.path.exists(topics):
        violations.append(
            f"{topics} does not resolve — either the junction is missing or its target "
            f"(the real store's projects/<project>/memory/) is gone"
        )
        return
    if not _is_reparse_point(topics):
        violations.append(
            f"{topics} is a real directory, not a junction — memories would be stored in a "
            f"second location instead of the single real store"
        )
        return
    target = os.path.realpath(topics)
    notes.append(f"memories/topics -> {target}")

    index = os.path.join(topics, "MEMORY.md")
    if not os.path.exists(index):
        violations.append(f"{topics}/MEMORY.md is missing — shared memory index unavailable")
        return
    notes.append(f"MEMORY.md present ({os.path.getsize(index)} bytes)")

    if store and os.path.isdir(os.path.join(store, ".git")):
        rel = os.path.relpath(target, store).replace("\\", "/")
        code, listing = _git(store, "ls-tree", "-r", "main", "--name-only", rel + "/")
        if code == 0:
            tracked = [x for x in listing.splitlines() if x.strip()]
            on_disk = [n for n in os.listdir(target) if os.path.isfile(os.path.join(target, n))]
            notes.append(f"memory files: {len(on_disk)} on disk, {len(tracked)} tracked on main")
            if len(on_disk) != len(tracked):
                violations.append(
                    f"memory file count differs: {len(on_disk)} on disk vs {len(tracked)} "
                    f"tracked on main/{rel} — the working tree and main disagree"
                )


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verbose", action="store_true", help="list every junction checked")
    ap.add_argument("--real-store", default=os.environ.get("SAM_REAL_STORE", DEFAULT_REAL_STORE))
    ap.add_argument(
        "--home",
        default=os.environ.get("HERMES_HOME") or os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes"),
    )
    args = ap.parse_args()

    if not args.home or not os.path.isdir(args.home):
        print(f"❌ cannot locate Hermes home (got: {args.home!r}); pass --home", file=sys.stderr)
        return 1

    violations, notes = [], []
    check_real_store_branch(args.real_store, violations, notes)
    check_topics_resolves(args.home, args.real_store, violations, notes)

    junctions = _walk_junctions(args.home)
    broken = [(p, t) for p, t, ok in junctions if not ok]
    notes.append(f"junctions under home: {len(junctions)} (broken: {len(broken)})")
    for path, target in broken:
        violations.append(f"broken junction: {path} -> {target} (target missing)")
    if args.verbose:
        for path, target, ok in junctions:
            print(f"  {'✅' if ok else '❌'} {os.path.relpath(path, args.home)} -> {target}")

    for note in notes:
        print(f"  · {note}")
    if violations:
        print(f"\n❌ Memory layout check FAILED ({len(violations)} violation(s)):")
        for v in violations:
            print(f"   - {v}")
        return 1
    print("\n✅ Memory layout OK: real store on main, topics junction resolves, all junctions live.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
