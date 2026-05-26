import logging

import requests

from integrations.config import get

logger = logging.getLogger(__name__)


def send_message(text: str) -> dict:
    webhook_url = get("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        logger.info("[DISCORD MOCK] %s", text[:80])
        return {"status": "mocked", "channel": "discord"}

    payload = {"content": text[:2000]}
    try:
        resp = requests.post(webhook_url, json=payload, timeout=15)
        resp.raise_for_status()
        logger.info("[DISCORD] Sent — status=%s", resp.status_code)
        return {"status": "sent", "channel": "discord"}
    except requests.RequestException as e:
        logger.error("[DISCORD] Failed to send: %s", e)
        return {"status": "error", "error": str(e)}
