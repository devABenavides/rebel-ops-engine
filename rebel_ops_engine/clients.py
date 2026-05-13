"""
Integration client interfaces.

Replace each mock implementation with a real API client:
- WhatsAppClient  -> twilio-rest-api / WhatsApp Business Cloud API
- HologramEmailClient -> smtplib / SendGrid / Mailgun
- CalendarClient  -> google-calendar-api / CalDAV
- NotificationClient  -> slack-sdk / smtplib / twilio
- ReportDeliveryClient -> smtplib / slack-sdk / SendGrid
"""

import logging

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """Send messages via Intergalactic WhatsApp.

    To replace with real WhatsApp Business API:
        from twilio.rest import Client
        self.client = Client(account_sid, auth_token)
        self.client.messages.create(body=body, from_=from_, to=to)
    """
    def send_message(self, to: str, body: str) -> dict:
        logger.info("[WHATSAPP] To: %s | Body: %s", to, body[:80])
        return {"status": "sent", "channel": "whatsapp", "to": to}


class HologramEmailClient:
    """Send transmissions via Hologram Email.

    To replace with real email (SMTP/SendGrid):
        import smtplib
        server.sendmail(from_addr, to_addrs, msg.as_string())
    """
    def send_email(self, to: str, subject: str, body: str) -> dict:
        logger.info("[EMAIL] To: %s | Subject: %s", to, subject)
        return {"status": "sent", "channel": "email", "to": to}


class CalendarClient:
    """Manage calendar availability and events.

    To replace with real Google Calendar API:
        from googleapiclient.discovery import build
        service = build('calendar', 'v3', credentials=creds)
        service.events().list(calendarId='primary', ...)
    """
    def check_availability(self, date: str) -> list[str]:
        slots = ["09:00", "10:00", "11:00", "14:00", "15:00"]
        logger.info("[CALENDAR] Available slots for %s: %s", date, slots)
        return slots

    def create_event(self, summary: str, date: str, time: str,
                     attendees: list[str] = None) -> dict:
        logger.info("[CALENDAR] Event created: %s on %s at %s", summary, date, time)
        return {"status": "created", "summary": summary, "date": date, "time": time}


class NotificationClient:
    """Send internal team notifications.

    To replace with real Slack webhook:
        import requests
        requests.post(webhook_url, json={"text": message})
    """
    def notify(self, recipient: str, message: str) -> dict:
        logger.info("[NOTIFICATION] To: %s | %s", recipient, message[:80])
        return {"status": "notified", "recipient": recipient}


class ReportDeliveryClient:
    """Deliver the daily Hologram Briefing.

    To replace with real email/Slack:
        send_email(to=leia_email, subject=briefing_subject, body=report_text)
    """
    def deliver_report(self, report_text: str, recipient: str = "General Leia") -> dict:
        logger.info("[REPORT] Delivered daily briefing to %s", recipient)
        return {"status": "delivered", "recipient": recipient}
