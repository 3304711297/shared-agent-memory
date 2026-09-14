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
    # 机器绝对路径：<盘符>:\Users\<名字> / <盘符>:/Users/<名字>。
    # 用通用规则而非枚举已知用户名——枚举写法本身就是把真实用户名写进公开仓库
    # （本文件曾因此自泄漏），且换机/换用户名即失效。
    (r"[A-Za-z]:[\\/]{1,2}Users[\\/]{1,2}([^\\/\"'`\s,;)\]}]+)", "Hardcoded machine username path"),
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub Personal Access Token"),
    (r"github_pat_[A-Za-z0-9_]{30,}", "GitHub Fine-Grained Token"),
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API Key"),
    (r"\bsk-(?:ant-|proj-)?[a-zA-Z0-9_-]{32,}\b", "OpenAI/Anthropic API Key"),
    (r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b", "Telegram Bot Token"),
    (r"\bxox[baprs]-[0-9a-zA-Z]{10,48}\b", "Slack Token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "Private key block"),
]

# 机器路径命中里的“名字”若为文档约定占位符或系统内置目录，不算违规。
# 维护说明：只允许真正通用的占位词；不要把某个真实用户名加进来（那正是本规则要拦的东西）。
PATH_NAME_ALLOWLIST = {
    "name", "username", "user", "yourname", "your-name", "account", "xxx",
    "<username>", "<user>", "<用户名>", "用户名", "your_user", "myuser",
    "public",  # C:\Users\Public —— Windows 内置共享目录
    "...",     # C:\Users\... —— 文档里表示“此处省略”的写法
}
# 机器路径规则的描述串，用于在下面的判定里识别“这条是路径规则”
_PATH_RULE_DESC = "Hardcoded machine username path"


def _is_allowlisted_path(match: "re.Match[str]") -> bool:
    """路径规则命中时，判断捕获到的用户名是否为允许的占位符。"""
    if match.lastindex is None:
        return False
    name = match.group(match.lastindex)
    return bool(name) and name.strip().lower() in PATH_NAME_ALLOWLIST


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
                    if desc == _PATH_RULE_DESC and _is_allowlisted_path(m):
                        continue
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
