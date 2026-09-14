#!/usr/bin/env python3
"""Public repository hygiene scan.

Scans all git-tracked files for machine-specific hardcoded usernames and private credentials.
Exits with code 1 if violations are found.

Usage:
    python scripts/check_hygiene.py            # scan tracked files, exit 1 on violation
    python scripts/check_hygiene.py --verbose  # also list allowlisted placeholders
"""
import os
import re
import subprocess
import sys

# Secret patterns (kept in sync with the main branch scanner)
SENSITIVE_PATTERNS = [
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub Personal Access Token"),
    (r"github_pat_[A-Za-z0-9_]{30,}", "GitHub Fine-Grained Token"),
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API Key"),
    (r"\bsk-(?:ant-|proj-)?[a-zA-Z0-9_-]{32,}\b", "OpenAI/Anthropic API Key"),
    (r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b", "Telegram Bot Token"),
    (r"\bxox[baprs]-[0-9a-zA-Z]{10,48}\b", "Slack Token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "Private key block"),
]

# Machine-absolute home paths: <drive>:\Users\<name> / <drive>:/Users/<name>.
# A generic rule is used instead of enumerating known usernames so that any machine
# identity is caught, including paths copied in from someone else's computer.
# Matching is case-insensitive so a lower-cased drive letter cannot slip past.
MACHINE_PATH_PATTERN = re.compile(
    r"[A-Za-z]:[\\/]{1,2}Users[\\/]{1,2}([^\\/\"'`\s,;)\]}]*)",
    re.IGNORECASE,
)

# Tokens that are documentation placeholders rather than a real account name.
PLACEHOLDER_TOKENS = {
    "<user>", "<username>", "<user-name>", "<your-user>", "<your-username>",
    "username", "user", "name", "yourname", "public", "default",
    "%username%", "%userprofile%", "$user", "wdagutilityaccount",
}

# The scanner itself necessarily describes the patterns it hunts for; skip it.
SELF_EXCLUDED = {"scripts/check_hygiene.py"}

TRAILING_JUNK = "`'\".)>,;:]"


def scan_text(rel_path, content, verbose):
    """Return (violations, allowlisted) for one file's text."""
    violations, allowlisted = [], []
    for pattern, desc in SENSITIVE_PATTERNS:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            line_no = content[:m.start()].count("\n") + 1
            violations.append(f"{rel_path}:{line_no} - {desc}: '{m.group(0)}'")

    for m in MACHINE_PATH_PATTERN.finditer(content):
        token = m.group(1).strip()
        line_no = content[:m.start()].count("\n") + 1
        shown = m.group(0).rstrip(TRAILING_JUNK)
        # Normalise away bracket/quote decoration so '<user>' and '`name`' count as
        # placeholders while a real account name does not.
        name = token.strip("<>{}[]()`'\"").strip().lower()
        if name in PLACEHOLDER_TOKENS:
            allowlisted.append(f"{rel_path}:{line_no} - placeholder: '{shown}'")
        else:
            violations.append(
                f"{rel_path}:{line_no} - Hardcoded machine home path: '{shown}'"
            )
    return violations, allowlisted


def main():
    verbose = "--verbose" in sys.argv
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    res = subprocess.run(
        ["git", "-C", repo_root, "ls-files"],
        capture_output=True,
        text=True,
        check=True
    )
    files = [f.strip() for f in res.stdout.splitlines() if f.strip()]

    violations = []
    allowlisted = []
    scanned = 0
    for rel_path in files:
        full_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(full_path):
            continue
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            continue
        scanned += 1
        if rel_path.replace(os.sep, "/") in SELF_EXCLUDED:
            continue
        v, a = scan_text(rel_path, content, verbose)
        violations.extend(v)
        allowlisted.extend(a)

    if verbose and allowlisted:
        print(f"ℹ️  {len(allowlisted)} allowlisted placeholder(s):")
        for a in allowlisted:
            print(f"  - {a}")

    if violations:
        print(f"❌ Hygiene scan failed! Found {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)

    print(f"✅ Hygiene scan passed: scanned {scanned} tracked files, 0 violations found.")


if __name__ == "__main__":
    main()
