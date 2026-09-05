---
name: telegram-channel-ops
description: Use when managing or posting to Telegram channels. Administer, publish, and automate channel operations.
---

# Telegram Channel Operations & Management

Standard operating procedure for administering, publishing to, and maintaining Telegram channels programmatically via the Telegram Bot API.

## 1. Authentication & Network Architecture

Telegram API endpoints are blocked in certain regions. All HTTP calls must route through an explicit local HTTP/HTTPS proxy.

### Configuration Schema

Store credentials in an untracked JSON file (e.g. `auth/telegram_channel.json`) or environment variables:

```json
{
  "bot_token": "<TOKEN>",
  "bot_username": "<BOT_USERNAME>",
  "channel_id": "@<CHANNEL_SLUG_OR_CHAT_ID>",
  "proxy": "http://127.0.0.1:3067"
}
```

### Base API Invocation Pattern

Always configure `urllib.request` or `requests` with the local proxy:

```python
import json
import urllib.request

def call_tg_api(method: str, payload: dict, token: str, proxy: str = "http://127.0.0.1:3067") -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with opener.open(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))
```

---

## 2. Channel Operations Workflow

### Step 1: Preflight Permission Verification
Before publishing, verify the bot's existence and administrative rights in the channel:
1. `getMe` -> Confirm bot identity and status.
2. `getChatMember(chat_id, user_id=bot_id)` -> Verify the status is `administrator` and `can_post_messages: true`.

### Step 2: Content Formatting & Publishing
- **Parse Mode**: Prefer `HTML` over `MarkdownV2`. `MarkdownV2` requires rigorous escaping of 18 reserved punctuation characters (`_`, `*`, `[`, `]`, `(`, `)`, `~`, `` ` ``, `>`, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`), leading to frequent HTTP 400 parse errors.
- **Length Constraint**: Telegram text messages are strictly capped at 4,096 UTF-8 characters. Split long articles across paragraph (`\n\n`) boundaries before dispatch.
- **Web Preview**: Set `"disable_web_page_preview": true` unless a hero link card is explicitly desired.

```python
def post_channel_message(chat_id: str, text: str, token: str, proxy: str) -> int:
    res = call_tg_api("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }, token, proxy)
    return res["result"]["message_id"]
```

### Step 3: Hot-Editing & Takedowns
- **Editing**: `editMessageText(chat_id, message_id, text, parse_mode="HTML")`.
- **Takedown**: `deleteMessage(chat_id, message_id)`.
- **Pinning**: `pinChatMessage(chat_id, message_id, disable_notification=True)`.

---

## 3. Account-Restriction Bypass Architecture

When the channel owner's personal account is subject to Telegram anti-spam restrictions (e.g. Spambot mute, unable to initiate chats, unable to contact `@BotFather`):

### What NEVER to do
- **Never attempt Userbot / MTProto client logins (Telethon / Pyrogram) using a flagged account**: Telegram account restrictions are enforced on the server-side MTProto RPC layer, so client scripts fail with `UserRestrictedError` or `ChatWriteForbiddenError`. Logging into third-party MTProto sessions with heavily flagged accounts frequently triggers automated fraud heuristics and results in immediate permanent account termination (`PHONE_NUMBER_BANNED`), which permanently destroys channel ownership.

### Reliable Workarounds
1. **Secondary Unrestricted Account**:
   - Create the administrative bot on an unflagged secondary account via `@BotFather`.
   - Administrative operations inside channel settings do not require private chat capabilities. The restricted owner account can open Channel Settings -> Administrators -> Add Administrator and promote the newly created Bot with posting/editing rights.
2. **Mutual Contacts Exemption**:
   - Telegram Spambot restrictions primarily filter interactions with strangers. When two accounts mutually save each other's phone numbers in their address books, Telegram classifies them as Mutual Contacts. Mutual contacts can send direct messages and invite each other to channels despite active Spambot restrictions.
3. **Channel Asset Overhaul (Ownership Transfer)**:
   - If an account has repeated spam penalties, transfer channel ownership to a clean account to eliminate single-point-of-failure risks. Requires 2FA active for >7 days and current session age >24 hours:
     `Channel Settings -> Administrators -> [Select Clean Account] -> Transfer Channel Ownership -> Enter 2FA Password`.

---

## 4. Key Pitfalls & Invariants

- **Bot Message Edit Boundary**: A Telegram Bot can only edit messages sent by that bot itself. A bot cannot edit messages posted by human administrators via `editMessageText`; if a human-authored message must be modified, the bot must delete the original message and re-post the corrected text.
- **Proxy Requirement**: Local scripts calling `api.telegram.org` must explicitly pass the proxy handler; standard environment variables (`HTTP_PROXY` / `HTTPS_PROXY`) are ignored by default in some Python `urllib` Windows setups without `ProxyHandler`.
- **Channel ID Prefix**: Public channels use `@slug`; private channels require numeric chat IDs beginning with `-100` (e.g. `-1002070574431`). Passing a raw integer without `-100` returns `Chat not found`.
