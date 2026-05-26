import logging

from agents.base import Agent
from clients import (
    HologramEmailClient,
    NotificationClient,
    WhatsAppClient,
)
from integrations import discord_client as dc
from models import Message, MessageStatus

logger = logging.getLogger(__name__)

whatsapp = WhatsAppClient()
email = HologramEmailClient()
notifier = NotificationClient()


def _proposal_template(summary: str, date: str, slots: list[str], message_id: str) -> str:
    lines = [
        "Rebel Command — Calendar Booking Confirmation",
        "==============================================",
        "",
        f"Request: {summary}",
        f"Date: {date}",
        "",
        "Available 30-minute slots:",
    ]
    for i, slot in enumerate(slots):
        lines.append(f"  [{i + 1}] {slot} — http://localhost:5000/api/calendar/confirm/{message_id}/{i}")
    lines.extend([
        "",
        "Click a link to confirm your preferred time.",
        "May the Force be with you.",
    ])
    return "\n".join(lines)


def _hologram_template(category: str, owner: str, status: str, next_action: str) -> str:
    return (
        "Hologram Transmission Received\n"
        "==============================\n"
        f"Your request has reached Rebel Command.\n"
        f"Category: {category}\n"
        f"Assigned To: {owner}\n"
        f"Current Status: {status}\n"
        f"Next Step: {next_action}\n"
        "May the Force be with you."
    )


def _quarantine_template(sender: str, indicators: list[str]) -> str:
    return (
        "SECURITY ALERT: Possible Dark Side infiltration detected.\n"
        "=====================================================\n"
        f"Sender: {sender}\n"
        f"Indicators: {', '.join(indicators)}\n\n"
        "This request has been quarantined for manual review.\n"
        "No sensitive Rebel information has been shared.\n"
        "Security Team has been notified."
    )


def _bb8_alert(summary: str, priority: str) -> str:
    return (
        "BB-8 ALERT: Critical Security Update\n"
        "=====================================\n"
        f"Summary: {summary}\n"
        f"Priority: {priority}\n\n"
        "Immediate Action: Security Team must verify the threat and begin emergency protocol."
    )


def _ahsoka_template(summary: str, priority: str, security: str, leia: bool, action: str) -> str:
    return (
        "SPECIAL MISSION REVIEW\n"
        "======================\n"
        f"Recipient: Ahsoka Tano\n"
        f"Summary: {summary}\n"
        f"Priority: {priority}\n"
        f"Security Risk: {security}\n\n"
        "Requested Review: Assess whether this contact or situation should be treated "
        "as an opportunity, monitored contact, or risk.\n"
        f"Leia Required: {'Yes' if leia else 'No'}\n"
        f"Recommended Next Step: {action}"
    )


def _din_template(summary: str, priority: str, leia: bool) -> str:
    return (
        "DIN DJARIN PROTECTION PROTOCOL ACTIVATED\n"
        "=========================================\n"
        f"Mission: {summary}\n"
        f"Priority: {priority}\n"
        "Security Level: Restricted\n\n"
        "Recommended Support:\n"
        "- Din Djarin for protection or extraction\n"
        "- BB-8 for instant alerts\n"
        "- R2-D2 for secure coordinates or data\n"
        "- Han Solo for backup transport when needed\n"
        f"Leia Visibility: {'Yes' if leia else 'No'}"
    )


def _luke_template(summary: str, case_type: str, priority: str, action: str) -> str:
    return (
        "JEDI TRAINING & DIPLOMACY ASSIGNMENT\n"
        "====================================\n"
        f"Recipients: Luke Skywalker + Ben Kenobi (Obi-Wan)\n"
        f"Summary: {summary}\n"
        f"Case Type: {case_type}\n"
        f"Priority: {priority}\n"
        f"Recommended Action: {action}"
    )


def _yoda_template(summary: str, risk: str, action: str) -> str:
    return (
        "ENCRYPTED JEDI TRANSMISSION\n"
        "===========================\n"
        "Recipient: Master Yoda\n"
        "Security Level: Restricted\n\n"
        f"Strategic Question: {summary}\n"
        f"Risk: {risk}\n"
        f"Requested Guidance: {action}\n\n"
        "Transmission Method: Encrypted channel only.\n"
        "May the Force be with us."
    )


class NotificationAgent(Agent):
    @property
    def name(self) -> str:
        return "NotificationAgent"

    def process(self, message: Message) -> Message:
        if message.status in (MessageStatus.QUARANTINED, MessageStatus.ERROR):
            if message.status == MessageStatus.QUARANTINED:
                alert = _quarantine_template(message.sender, message.dark_side_indicators)
                notifier.notify("Security Team", alert)
                inds = ', '.join(message.dark_side_indicators[:3])
                dc.send_message(
                    f"**Security Alert — Quarantined**\n"
                    f"Sender: {message.sender}\nIndicators: {inds}\nRisk: {message.security_risk}"
                )
            message.trace.append({"agent": self.name, "action": "notified", "details": {"recipient": "Security Team", "template": "quarantine_alert"}})
            if self.name not in message.processed_by:
                message.processed_by.append(self.name)
            return message

        if message.status == MessageStatus.AWAITING_CONFIRMATION and message.proposals:
            from agents.calendar import _extract_date as _cal_date
            summary = message.summary or message.content[:100]
            raw_date = _cal_date(message.content)
            body = _proposal_template(summary, raw_date, message.proposals, message.id)
            DEMO_EMAIL = "alexandra.benavides@paretotalent.com"
            email.send_email(DEMO_EMAIL, "Rebel Command: Confirm Your Calendar Slot", body)
            message.trace.append({
                "agent": self.name, "action": "notified",
                "details": {"recipients": [DEMO_EMAIL], "template": "calendar_proposal"},
            })
            if self.name not in message.processed_by:
                message.processed_by.append(self.name)
            return message

        category = message.category.value if message.category else "unknown"
        owner = message.owner.value if message.owner else "Unassigned"
        summary = message.summary or message.content[:100]
        action = message.suggested_next_action or "Review and respond"

        recipients = []
        if message.channel.value == "intergalactic_whatsapp":
            whatsapp.send_message(
                message.sender,
                f"[{category.upper()}] {summary[:200]}\nAssigned: {owner}\nNext: {action}",
            )
            recipients.append(message.sender)
        else:
            DEMO_EMAIL = "alexandra.benavides@paretotalent.com"
            email.send_email(
                DEMO_EMAIL,
                f"Rebel Command: {category.replace('_', ' ').title()}",
                _hologram_template(category, owner, message.status.value, action),
            )
            recipients.append(message.sender)

        if category == "urgent_security":
            notifier.notify("Security Team", _bb8_alert(summary, message.priority))
            dc.send_message(f"**🚨 BB-8 Alert — Urgent Security**\n{summary}\nPriority: {message.priority}")
            recipients.append("Security Team")

        if category == "ahsoka_special_mission":
            notifier.notify("Ahsoka Tano", _ahsoka_template(
                summary, message.priority, message.security_risk,
                message.requires_leia, action,
            ))
            recipients.append("Ahsoka Tano")

        if category == "special_protection":
            notifier.notify("Din Djarin", _din_template(summary, message.priority, message.requires_leia))
            recipients.append("Din Djarin")

        if category in ("jedi_training_diplomacy", "population_training"):
            notifier.notify("Luke Skywalker + Ben Kenobi", _luke_template(summary, message.jedi_case_type, message.priority, action))
            recipients.append("Luke Skywalker + Ben Kenobi")

        if category == "yoda_encrypted_strategy":
            notifier.notify("Yoda", _yoda_template(summary, message.security_risk, action))
            recipients.append("Yoda")

        message.trace.append({
            "agent": self.name, "action": "notified",
            "details": {"recipients": recipients, "template": category},
        })

        logger.info(
            "Notification sent for %s: %s -> %s (%s)",
            category, message.sender, owner, message.status.value,
        )
        if self.name not in message.processed_by:
            message.processed_by.append(self.name)
        return message
