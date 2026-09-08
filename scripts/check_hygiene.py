#!/usr/bin/env python3
"""Public repository hygiene scan.

Scans all git-tracked files for machine-specific hardcoded usernames and private credentials.
Exits with code 1 if violations are found.
"""
import os
import re
import subprocess
import sys

# High-risk patterns
SENSITIVE_PATTERNS = [
    (r"C:[/\\]Users[/\\]VOS-User\b", "Hardcoded machine username path (VOS-User)"),
    (r"D:[/\\]Users[/\\]VOS-User\b", "Hardcoded machine username path (VOS-User)"),
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub Personal Access Token"),
    (r"github_pat_[A-Za-z0-9_]{30,}", "GitHub Fine-Grained Token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "Private key block"),
]


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    res = subprocess.run(
        ["git", "-C", repo_root, "ls-files"],
        capture_output=True,
        text=True,
        check=True
    )
    files = [f.strip() for f in res.stdout.splitlines() if f.strip()]

    violations = []
    for rel_path in files:
        full_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(full_path):
            continue
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            continue

        for pattern, desc in SENSITIVE_PATTERNS:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                for m in matches:
                    line_no = content[:m.start()].count("\n") + 1
                    violations.append(f"{rel_path}:{line_no} - {desc}: '{m.group(0)}'")

    if violations:
        print(f"❌ Hygiene scan failed! Found {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)

    print(f"✅ Hygiene scan passed: scanned {len(files)} tracked files, 0 violations found.")


if __name__ == "__main__":
    main()
