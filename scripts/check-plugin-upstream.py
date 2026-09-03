#!/usr/bin/env python3
"""
插件上游更新检测脚本 (Plugin Upstream Watcher)

检测 4 大核心插件 (superpowers, desktop-commander, serena, context7) 的上游 GitHub 仓库是否有新 Commit 或新 Release，并在 CI 环境中自动生成 Issue。
"""

import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM_CONFIG_PATH = os.path.join(ROOT_DIR, "plugins", "upstream.json")


def get_github_headers():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {
        "User-Agent": "Hermes-Plugin-Watcher/1.0",
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def api_get(url):
    headers = get_github_headers()
    # 如果有 token，优先用 urllib
    if "Authorization" in headers:
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            pass

    # 回退到 gh api CLI（本地已认证）
    try:
        endpoint = url.replace("https://api.github.com/", "")
        res = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True)
        if res.returncode == 0:
            return json.loads(res.stdout)
    except Exception:
        pass

    return None


def check_plugin(name, config):
    repo = config["repo"]
    branch = config.get("branch", "main")
    last_commit = config.get("last_synced_commit", "")
    last_release = config.get("last_synced_release", "")

    # 1. 查最新 Commit
    commit_data = api_get(f"https://api.github.com/repos/{repo}/commits/{branch}")
    latest_sha = commit_data.get("sha", "") if commit_data else ""
    latest_sha_short = latest_sha[:7] if latest_sha else ""
    commit_msg = (
        commit_data.get("commit", {}).get("message", "").splitlines()[0]
        if commit_data
        else ""
    )
    commit_date = (
        commit_data.get("commit", {}).get("author", {}).get("date", "")
        if commit_data
        else ""
    )

    # 2. 查最新 Release / Tag
    release_data = api_get(f"https://api.github.com/repos/{repo}/releases/latest")
    latest_release = release_data.get("tag_name", "") if release_data else ""
    release_url = release_data.get("html_url", "") if release_data else ""

    has_commit_update = bool(
        latest_sha_short and last_commit and latest_sha_short != last_commit
    )
    has_release_update = bool(
        latest_release and last_release and latest_release != last_release
    )

    return {
        "name": name,
        "repo": repo,
        "description": config.get("description", ""),
        "last_commit": last_commit,
        "latest_commit": latest_sha_short,
        "latest_commit_full": latest_sha,
        "commit_msg": commit_msg,
        "commit_date": commit_date,
        "last_release": last_release,
        "latest_release": latest_release or "无",
        "release_url": release_url,
        "has_update": has_commit_update or has_release_update,
        "has_commit_update": has_commit_update,
        "has_release_update": has_release_update,
    }


def main():
    if not os.path.exists(UPSTREAM_CONFIG_PATH):
        print(f"Config not found: {UPSTREAM_CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(UPSTREAM_CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    plugins = data.get("plugins", {})
    updates = []

    print(f"=== 开始检测 {len(plugins)} 个核心插件的上游更新状态 ===")
    for name, cfg in plugins.items():
        res = check_plugin(name, cfg)
        status_sym = "🚀 发现更新" if res["has_update"] else "✅ 最新状态"
        print(
            f"{status_sym} [{name}] ({res['repo']}): 本地 Commit {res['last_commit']} -> 上游 {res['latest_commit']} | Release {res['last_release']} -> {res['latest_release']}"
        )
        if res["has_update"]:
            updates.append(res)

    # 输出 Summary
    print(f"\n检测完成：共发现 {len(updates)} 个插件存在上游更新。")

    # 如果在 GitHub Actions 中，写入 GITHUB_OUTPUT
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"has_updates={'true' if updates else 'false'}\n")
            f.write(f"update_count={len(updates)}\n")

    if "--report" in sys.argv and updates:
        report_lines = [
            "# 🔔 插件上游更新通知 (Plugin Upstream Updates Detected)\n",
            f"检测时间：`{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}`\n",
            "| 插件名称 | 上游仓库 | 本地同步基线 | 上游最新状态 | 变更摘要 |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for u in updates:
            diff_url = (
                f"https://github.com/{u['repo']}/compare/{u['last_commit']}...{u['latest_commit']}"
                if u["last_commit"] and u["latest_commit"]
                else f"https://github.com/{u['repo']}"
            )
            report_lines.append(
                f"| **`{u['name']}`** | [{u['repo']}](https://github.com/{u['repo']}) | Commit `{u['last_commit']}`<br>Tag `{u['last_release']}` | Commit [`{u['latest_commit']}`]({diff_url})<br>Tag `{u['latest_release']}` | {u['commit_msg']} |"
            )

        report_lines.extend(
            [
                "\n### 🛠️ 处理建议",
                "1. 点击上方 Compare 链接查看具体代码变更与 Release Notes；",
                "2. 评估是否存在破坏性变动（Breaking Changes）或新功能；",
                "3. 如需同步更新，使用 `git pull` / 同步对应 `plugins/<name>` 目录，并更新 `plugins/upstream.json` 基线；",
                "4. 评估确认无须改动或同步完成后，可直接留言关闭本 Issue。",
            ]
        )
        report_text = "\n".join(report_lines)
        print("\n=== Markdown Report ===\n")
        print(report_text)

        report_file = os.path.join(ROOT_DIR, "upstream-report.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_text)


if __name__ == "__main__":
    main()
