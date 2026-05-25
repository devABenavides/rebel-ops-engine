import base64
import logging
import os
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from integrations.config import get

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.readonly"]

GMAIL_CREDENTIALS_PATH = "credentials/gmail_oauth.json"
GMAIL_TOKEN_PATH = "credentials/gmail_token.json"


def _get_service():
    import os as _os
    if _os.environ.get("PYTEST_CURRENT_TEST") or _os.environ.get("REBEL_SKIP_OAUTH"):
        return None
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), "..", GMAIL_TOKEN_PATH)
    creds_path = os.path.join(os.path.dirname(__file__), "..", GMAIL_CREDENTIALS_PATH)

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                logger.warning("No Gmail OAuth credentials file at %s — Gmail client unavailable", creds_path)
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0, timeout_seconds=30)
            except Exception as e:
                logger.warning("Gmail OAuth flow failed: %s", e)
                return None
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    try:
        return build("gmail", "v1", credentials=creds)
    except Exception as e:
        logger.error("Failed to build Gmail service: %s", e)
        return None


def send_email(to: str, subject: str, body: str, html: str = "") -> dict:
    service = _get_service()
    if service is None:
        logger.info("[GMAIL MOCK] To: %s | Subject: %s", to, subject)
        return {"status": "mocked", "channel": "gmail", "to": to}

    msg = EmailMessage()
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")
    msg["To"] = to
    msg["Subject"] = subject
    msg["From"] = get("EMAIL_FROM", "rebel-command@example.com")

    encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    try:
        result = service.users().messages().send(userId="me", body={"raw": encoded}).execute()
        logger.info("[GMAIL] Sent to %s — id=%s", to, result.get("id"))
        return {"status": "sent", "channel": "gmail", "to": to, "id": result.get("id")}
    except HttpError as e:
        logger.error("[GMAIL] Failed to send: %s", e)
        return {"status": "error", "error": str(e)}


def list_unread() -> list[dict]:
    service = _get_service()
    if service is None:
        logger.info("[GMAIL MOCK] list_unread() — empty")
        return []

    try:
        result = service.users().messages().list(userId="me", q="is:unread", maxResults=20).execute()
        messages = result.get("messages", [])
        parsed = []
        for msg in messages:
            detail = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
            parsed.append({
                "id": msg["id"],
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "snippet": detail.get("snippet", ""),
                "thread_id": detail.get("threadId", ""),
            })
        return parsed
    except HttpError as e:
        logger.error("[GMAIL] Failed to list unread: %s", e)
        return []


def mark_read(message_id: str) -> bool:
    service = _get_service()
    if service is None:
        return True
    try:
        service.users().messages().modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}).execute()
        return True
    except HttpError as e:
        logger.error("[GMAIL] Failed to mark read %s: %s", message_id, e)
        return False
