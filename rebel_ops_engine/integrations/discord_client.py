import logging

import requests

from database import Database
from integrations.config import get

logger = logging.getLogger(__name__)

_db = Database()


def send_message(text: str) -> dict:
    webhook_url = get("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        logger.info("[DISCORD MOCK] %s", text[:80])
        return {"status": "mocked", "channel": "discord"}

    payload = {"content": text[:2000]}
    try:
        resp = requests.post(webhook_url, json=payload, timeout=15)
        resp.raise_for_status()
        msg_id = resp.json().get("id")
        if msg_id:
            _db.insert_discord_message(str(msg_id))
        logger.info("[DISCORD] Sent — status=%s", resp.status_code)
        return {"status": "sent", "channel": "discord"}
    except requests.RequestException as e:
        logger.error("[DISCORD] Failed to send: %s", e)
        return {"status": "error", "error": str(e)}


def clear_messages() -> int:
    webhook_url = get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return 0

    msg_ids = _db.get_all_discord_message_ids()
    if not msg_ids:
        logger.info("[DISCORD] No stored messages to clear")
        return 0

    deleted = 0
    for msg_id in msg_ids:
        try:
            resp = requests.delete(f"{webhook_url}/messages/{msg_id}", timeout=15)
            if resp.status_code == 404:
                logger.warning("[DISCORD] Message %s not found (already deleted)", msg_id)
            else:
                resp.raise_for_status()
                deleted += 1
            _db.delete_discord_message(msg_id)
        except requests.RequestException as e:
            logger.error("[DISCORD] Failed to delete message %s: %s", msg_id, e)

    logger.info("[DISCORD] Cleared %d messages from Discord, %d from DB", deleted, len(msg_ids))
    return deleted
