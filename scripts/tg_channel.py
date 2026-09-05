"""Telegram Channel Management CLI & Helper for @emoegg.

Uses bot token stored in C:/Users/VOS-User/AppData/Local/hermes/auth/telegram_channel.json
and proxies through 127.0.0.1:3067.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Optional

CONFIG_PATH = Path(os.environ.get("HERMES_HOME", Path.home() / "AppData/Local/hermes")) / "auth" / "telegram_channel.json"


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def call_api(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    cfg = load_config()
    token = cfg["bot_token"]
    proxy = cfg.get("proxy", "http://127.0.0.1:3067")
    url = f"https://api.telegram.org/bot{token}/{method}"

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with opener.open(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_info() -> dict[str, Any]:
    cfg = load_config()
    channel = cfg.get("channel_id", "@emoegg")
    me = call_api("getMe", {})
    chat = call_api("getChat", {"chat_id": channel})
    member = call_api("getChatMember", {"chat_id": channel, "user_id": me["result"]["id"]})
    return {
        "bot": me["result"],
        "chat": chat["result"],
        "permissions": member["result"],
    }


def send_message(text: str, parse_mode: str = "HTML", disable_web_page_preview: bool = False) -> dict[str, Any]:
    cfg = load_config()
    channel = cfg.get("channel_id", "@emoegg")
    payload = {
        "chat_id": channel,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }
    return call_api("sendMessage", payload)


def edit_message(message_id: int, text: str, parse_mode: str = "HTML") -> dict[str, Any]:
    cfg = load_config()
    channel = cfg.get("channel_id", "@emoegg")
    payload = {
        "chat_id": channel,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    return call_api("editMessageText", payload)


def delete_message(message_id: int) -> dict[str, Any]:
    cfg = load_config()
    channel = cfg.get("channel_id", "@emoegg")
    payload = {
        "chat_id": channel,
        "message_id": message_id,
    }
    return call_api("deleteMessage", payload)


def pin_message(message_id: int, notify: bool = False) -> dict[str, Any]:
    cfg = load_config()
    channel = cfg.get("channel_id", "@emoegg")
    payload = {
        "chat_id": channel,
        "message_id": message_id,
        "disable_notification": not notify,
    }
    return call_api("pinChatMessage", payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Telegram Channel Manager for @emoegg")
    sub = parser.add_subparsers(dest="action", required=True)

    sub.add_parser("info", help="Get bot and channel permissions info")

    p_post = sub.add_parser("post", help="Post message to channel")
    p_post.add_argument("text", help="Message text")
    p_post.add_argument("--mode", default="HTML", choices=["HTML", "Markdown", "MarkdownV2"])

    p_edit = sub.add_parser("edit", help="Edit message in channel")
    p_edit.add_argument("id", type=int, help="Message ID")
    p_edit.add_argument("text", help="New message text")
    p_edit.add_argument("--mode", default="HTML", choices=["HTML", "Markdown", "MarkdownV2"])

    p_del = sub.add_parser("delete", help="Delete message in channel")
    p_del.add_argument("id", type=int, help="Message ID")

    p_pin = sub.add_parser("pin", help="Pin message in channel")
    p_pin.add_argument("id", type=int, help="Message ID")

    args = parser.parse_args()

    if args.action == "info":
        res = get_info()
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.action == "post":
        res = send_message(args.text, parse_mode=args.mode)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.action == "edit":
        res = edit_message(args.id, args.text, parse_mode=args.mode)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.action == "delete":
        res = delete_message(args.id)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.action == "pin":
        res = pin_message(args.id)
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
