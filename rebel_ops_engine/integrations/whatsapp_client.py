import logging

import requests

from integrations.config import get

logger = logging.getLogger(__name__)

API_VERSION = "v22.0"


def send_message(to: str, body: str) -> dict:
    phone_number_id = get("WHATSAPP_PHONE_NUMBER_ID")
    access_token = get("WHATSAPP_ACCESS_TOKEN")

    if not phone_number_id or not access_token:
        logger.info("[WHATSAPP MOCK] To: %s | Body: %s", to, body[:80])
        return {"status": "mocked", "channel": "whatsapp", "to": to}

    url = f"https://graph.facebook.com/{API_VERSION}/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body[:4096]},
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        logger.info("[WHATSAPP] Sent to %s — id=%s", to, data.get("messages", [{}])[0].get("id"))
        return {"status": "sent", "channel": "whatsapp", "to": to, "id": data.get("messages", [{}])[0].get("id")}
    except requests.RequestException as e:
        logger.error("[WHATSAPP] Failed to send: %s", e)
        return {"status": "error", "error": str(e)}


def verify_webhook(mode: str, token: str, challenge: str) -> tuple[str, int]:
    verify_token = get("WHATSAPP_VERIFY_TOKEN")
    if not verify_token:
        logger.error("WHATSAPP_VERIFY_TOKEN not configured")
        return "Forbidden", 403
    if mode == "subscribe" and token == verify_token:
        return challenge, 200
    return "Forbidden", 403

