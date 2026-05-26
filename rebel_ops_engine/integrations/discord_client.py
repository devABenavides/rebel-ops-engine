import logging

import requests

from integrations.config import get

logger = logging.getLogger(__name__)

_sent_message_ids: list[str] = []


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
            _sent_message_ids.append(str(msg_id))
        logger.info("[DISCORD] Sent — status=%s", resp.status_code)
        return {"status": "sent", "channel": "discord"}
    except requests.RequestException as e:
        logger.error("[DISCORD] Failed to send: %s", e)
        return {"status": "error", "error": str(e)}


def clear_messages() -> int:
    webhook_url = get("DISCORD_WEBHOOK_URL")
    if not webhook_url or not _sent_message_ids:
        return 0

    deleted = 0
    for msg_id in list(_sent_message_ids):
        try:
            resp = requests.delete(f"{webhook_url}/messages/{msg_id}", timeout=15)
            resp.raise_for_status()
            _sent_message_ids.remove(msg_id)
            deleted += 1
        except requests.RequestException:
            pass
    if deleted:
        logger.info("[DISCORD] Cleared %d messages", deleted)
    return deleted
