"""
Integration client interfaces.

All clients auto-detect credentials:
  - If env vars / OAuth tokens are present → real API calls
  - If not → graceful mock fallback with logging

To set up real integrations, see .env.example and credentials/README.md.
"""

import logging

from integrations import calendar_client as cal
from integrations import gmail_client as gmail
from integrations import whatsapp_client as wa

logger = logging.getLogger(__name__)


class WhatsAppClient:
    def send_message(self, to: str, body: str) -> dict:
        return wa.send_message(to, body)


class HologramEmailClient:
    def send_email(self, to: str, subject: str, body: str) -> dict:
        return gmail.send_email(to, subject, body)


class CalendarClient:
    def check_availability(self, date: str = None) -> list[str]:
        slots = cal.check_availability(date)
        return [s["start"] if isinstance(s, dict) else s for s in slots]

    def create_event(self, summary: str, date: str, time: str, description: str = "", attendees: list[str] = None) -> dict:
        return cal.create_event(summary, date, time, description, attendees)

    def find_available_slots(self, date_str: str, duration_min: int = 30, max_slots: int = 3) -> list[str]:
        return cal.find_available_slots(date_str, duration_min, max_slots)


class NotificationClient:
    def notify(self, recipient: str, message: str) -> dict:
        logger.info("[NOTIFICATION] To: %s | %s", recipient, message[:80])
        return {"status": "notified", "recipient": recipient}


class ReportDeliveryClient:
    def deliver_report(self, report_text: str, recipient: str = "") -> dict:
        to = recipient or "alexandra.benavides@paretotalent.com"
        html = _briefing_html(report_text)
        date_part = ""
        for line in report_text.split("\n"):
            stripped = line.strip()
            if stripped.replace("-", "").strip().isdigit() and len(stripped) == 10:
                date_part = f" — {stripped}"
                break
        subject = f"Daily Hologram Briefing{date_part}"
        return gmail.send_email(to, subject, report_text, html=html)


def _briefing_html(text: str) -> str:
    lines = text.split("\n")
    sections = []
    date_str = ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("=" * 10):
            continue
        if stripped.startswith("DAILY HOLOGRAM BRIEFING"):
            sections.append(
                f"<h1 style=\"font-family:'Instrument Serif',Georgia,serif;"
                f"font-size:28px;color:#d4872a;margin:0 0 4px;font-weight:400;\">"
                f"{_html_escape(stripped)}</h1>"
            )
        elif date_str == "" and stripped.replace("-", "").isdigit():
            date_str = stripped
            sections.append(
                f"<div style=\"font-size:14px;color:#6b6b66;margin-bottom:16px;\">"
                f"{_html_escape(stripped)}</div>"
            )
        elif stripped.startswith("General Leia"):
            sections.append(f"<p style=\"font-size:16px;color:#1c1c1f;margin:0 0 4px;\">{_html_escape(stripped)}</p>")
        elif stripped.startswith("Here is today"):
            sections.append(f"<p style=\"font-size:14px;color:#3b3b3f;margin:0 0 20px;\">{_html_escape(stripped)}</p>")
        elif stripped.startswith("Total Requests:"):
            sections.append(_stat_row(stripped, "#1c1c1f"))
        elif stripped.startswith("Quarantined"):
            sections.append(_stat_row(stripped, "#ef5350"))
        elif stripped.startswith("Encrypted"):
            sections.append(_stat_row(stripped, "#d4872a"))
        elif stripped == "By Category:":
            sections.append(_section_header("By Category"))
        elif stripped == "Delegated Missions:":
            sections.append(_section_header("Delegated Missions"))
        elif stripped.startswith("Critical Items:"):
            sections.append(_section_header("Critical Items"))
        elif stripped.startswith("Security Risks"):
            sections.append(_section_header("Security Risks Detected"))
        elif stripped.startswith("Requests Requiring"):
            sections.append(_section_header("Requests Requiring Your Decision"))
        elif stripped.startswith("Blocked or Waiting"):
            sections.append(_section_header("Blocked or Waiting"))
        elif stripped.startswith("Recommended Focus"):
            sections.append(_section_header("Recommended Focus for Tomorrow"))
        elif stripped.startswith("Public Calendar"):
            sections.append(_section_header("Public Calendar Bookings"))
        elif stripped.startswith("End of Briefing"):
            sections.append(
                f"<div style=\"font-style:italic;color:#d4872a;font-size:14px;"
                f"text-align:center;margin-top:24px;\">{_html_escape(stripped)}</div>"
            )
        elif stripped.startswith("  - "):
            sections.append(f"<div style=\"padding:3px 0 3px 16px;color:#3b3b3f;font-size:13px;\">{_html_escape(stripped)}</div>")
        elif stripped.startswith("  ["):
            badge_color = "#ef5350"
            if "[MEDIUM]" in stripped:
                badge_color = "#d4872a"
            stripped_esc = _html_escape(stripped)
            sections.append(
                f"<div style=\"padding:4px 0 4px 16px;font-size:13px;\">"
                f"<span style=\"display:inline-block;padding:1px 8px;border-radius:4px;"
                f"font-weight:600;font-size:11px;background:{badge_color}20;color:{badge_color};\">"
                f"{stripped_esc.split(']')[0].lstrip('[')}</span>"
                f"<span style=\"color:#3b3b3f;margin-left:6px;\">{stripped_esc.split(']', 1)[1] if ']' in stripped_esc else stripped_esc}</span>"
                f"</div>"
            )
        elif stripped.startswith("  Risk:"):
            parts = stripped.split("|")
            risk_badge = "low"
            for p in parts:
                p = p.strip()
                if p.startswith("Risk:"):
                    risk_badge = p.split(":", 1)[1].strip()
            badge_colors = {"high": "#ef5350", "medium": "#d4872a", "low": "#4caf7d"}
            bc = badge_colors.get(risk_badge, "#6b6b66")
            sections.append(
                f"<div style=\"padding:4px 0 4px 16px;font-size:13px;color:#3b3b3f;\">"
                f"<span style=\"display:inline-block;padding:1px 8px;border-radius:4px;"
                f"font-weight:600;font-size:11px;background:{bc}20;color:{bc};\">{_html_escape(risk_badge.upper())}</span>"
                f"<span style=\"margin-left:6px;\">{_html_escape(stripped)}</span>"
                f"</div>"
            )
        elif stripped.startswith("  [") and "]" in stripped:
            status_text = stripped.split("[")[1].split("]")[0]
            sc = {"quarantined": "#ef5350", "error": "#ef5350", "flagged": "#d4872a", "completed": "#4caf7d"}.get(status_text, "#6b6b66")
            rest = stripped.split("]", 1)[1].strip() if "]" in stripped else stripped
            sections.append(
                f"<div style=\"padding:4px 0 4px 16px;font-size:13px;color:#3b3b3f;\">"
                f"<span style=\"display:inline-block;padding:1px 8px;border-radius:4px;"
                f"font-weight:600;font-size:11px;background:{sc}20;color:{sc};\">{_html_escape(status_text.upper())}</span>"
                f"<span style=\"margin-left:6px;\">{_html_escape(rest)}</span>"
                f"</div>"
            )
        elif "[Private Leia" in stripped:
            sections.append(f"<div style=\"padding:3px 0 3px 16px;font-size:12px;font-style:italic;color:#6b6b66;\">{_html_escape(stripped)}</div>")
        else:
            sections.append(f"<div style=\"padding:2px 0;color:#3b3b3f;font-size:13px;\">{_html_escape(stripped)}</div>")

    body = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f1ea;font-family:'Inter',-apple-system,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f1ea;">
<tr><td align="center" style="padding:32px 16px;">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fdfcf9;border:1px solid #e3ddd0;border-radius:12px;">
<tr><td style="padding:32px;">
{body}
</td></tr>
<tr><td style="padding:16px 32px;border-top:1px solid #e3ddd0;font-size:12px;color:#6b6b66;text-align:center;">
May the Force be with you — Rebel Command
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""


def _stat_row(text: str, color: str) -> str:
    esc = _html_escape(text)
    return f"<div style=\"padding:4px 0;font-size:14px;color:{color};\">{esc}</div>"


def _section_header(text: str) -> str:
    style = "font-weight:600;color:#1c1c1f;font-size:15px;"
    style += "margin-top:20px;margin-bottom:6px;"
    style += "border-bottom:1px solid #e3ddd0;padding-bottom:4px;"
    return f"<div style=\"{style}\">{_html_escape(text)}</div>"


def _html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
