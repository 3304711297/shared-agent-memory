#!/usr/bin/env python3
"""Public repository hygiene scan.

Scans all git-tracked files for machine-specific hardcoded usernames and private credentials.
Exits with code 1 if violations are found.

This file is duplicated byte-identical in two places and must stay that way:
shared-agent-memory (main + hermes branches) and the hermes home repo
(hermes branch). Edit one copy, then copy it over the other and compare
sha256 — divergence is real risk, not cosmetics: the two copies once grew
different secret-placeholder rules, so identical content passed in one repo
and failed CI in the other.

Usage:
    python scripts/check_hygiene.py            # scan tracked files, exit 1 on violation
    python scripts/check_hygiene.py --verbose  # also list allowlisted placeholders
"""
import os
import re
import subprocess
import sys

# High-risk secret patterns.
SECRET_PATTERNS = [
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
# A generic rule is used instead of enumerating known usernames so that any
# machine identity is caught, including paths copied in from someone else's
# computer; enumerating real names would leak them into this public file.
# The trailing `+` (not `*`) is deliberate: a bare "C:/Users/" carries no
# identity and must not be matched, or the empty capture becomes a false
# positive. Matching is case-insensitive so a lower-cased drive letter cannot
# slip past.
MACHINE_PATH_PATTERN = re.compile(
    r"[A-Za-z]:[\\/]{1,2}Users[\\/]{1,2}([^\\/\"'`\s,;)\]}]+)",
    re.IGNORECASE,
)

# Tokens that are documentation placeholders rather than a real account name.
# Maintenance rule: only genuinely generic placeholders belong here; adding a
# real account name would defeat the rule this file exists to enforce.
PLACEHOLDER_TOKENS = {
    "name", "username", "user", "yourname", "your-name", "your_user", "myuser",
    "account", "default", "public", "xxx", "xxxx",
    "%username%", "%userprofile%", "$user", "wdagutilityaccount",
    "<user>", "<username>", "<user-name>", "<your-user>", "<your-username>",
    # CJK / localized placeholders (docs are Chinese in these repos)
    "<当前用户>", "<用户名>", "<使用者>", "<你的用户名>", "当前用户", "用户名",
    # ellipsis / redaction forms
    "...", "…", "<...>", "***",
}

TRAILING_JUNK = "`'\".)>,;:]"

# Secret-shaped strings that are documentation placeholders, not credentials.
# A real key is high-entropy; docs write marked or repeated-character forms
# (e.g. a GitHub PAT example = the ghp_ prefix plus a run of x's).
SECRET_PLACEHOLDER_MARKERS = ("...", "…", "redacted", "placeholder", "example", "your", "<", ">")


def _is_secret_placeholder(token):
    """True when a secret-pattern match is clearly a doc placeholder.

    Two independent signals, both cheap and both safe against real keys:
      1. a marker word/bracket that only appears in documentation;
      2. a run of 8+ identical characters — a real key never repeats one
         character that many times in a row (covers AKIAxxxx… as well as
         ghp_xxxx…, without needing to know each vendor's prefix shape).
    """
    low = token.lower()
    if any(m in low for m in SECRET_PLACEHOLDER_MARKERS):
        return True
    return re.search(r"(.)\1{7,}", low) is not None


def scan_text(rel_path, content):
    """Return (violations, allowlisted) for one file's text."""
    violations, allowlisted = [], []
    for pattern, desc in SECRET_PATTERNS:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            line_no = content[:m.start()].count("\n") + 1
            token = m.group(0)
            if _is_secret_placeholder(token):
                allowlisted.append(f"{rel_path}:{line_no} - placeholder secret: '{token}'")
                continue
            violations.append(f"{rel_path}:{line_no} - {desc}: '{token}'")

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
        v, a = scan_text(rel_path, content)
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
