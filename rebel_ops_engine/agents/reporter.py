import logging
from collections import Counter

from agents.base import Agent
from models import DailyBriefing, Message, MessageStatus

logger = logging.getLogger(__name__)


class ReportingAgent(Agent):
    def __init__(self):
        self._store: dict[str, Message] = {}

    @property
    def name(self) -> str:
        return "ReportingAgent"

    def process(self, message: Message) -> Message:
        self._store[message.id] = message
        message.trace.append({
            "agent": self.name, "action": "stored",
            "details": {"status": message.status.value, "owner": message.owner.value if message.owner else None},
        })
        if self.name not in message.processed_by:
            message.processed_by.append(self.name)
        return message

    def get_all_messages(self) -> list[Message]:
        return list(self._store.values())

    def get_message(self, message_id: str) -> Message | None:
        return self._store.get(message_id)

    def reset(self):
        self._store.clear()

    def generate_daily_briefing(self, date_str: str) -> DailyBriefing:
        msgs = [m for m in self._store.values() if m.timestamp.strftime("%Y-%m-%d") <= date_str]
        quarantined = [m for m in msgs if m.status == MessageStatus.QUARANTINED]
        encrypted = [m for m in msgs if m.encrypted]
        by_category = Counter(m.category.value if m.category else "unknown" for m in msgs)
        by_owner = Counter(m.owner.value if m.owner else "Unassigned" for m in msgs)
        urgent = [
            {
                "id": m.id, "sender": m.sender,
                "category": m.category.value if m.category else "unknown",
                "status": m.status.value,
            }
            for m in msgs
            if m.category and m.category.value == "urgent_security"
        ]
        critical = [
            {
                "id": m.id, "sender": m.sender,
                "category": m.category.value if m.category else "unknown",
                "priority": m.priority,
            }
            for m in msgs
            if m.priority in ("high", "critical")
        ]
        security_items = [
            {
                "id": m.id, "sender": m.sender,
                "risk": m.security_risk,
                "indicators": m.dark_side_indicators[:5],
            }
            for m in msgs
            if m.security_risk in ("medium", "high")
        ]
        leia_decisions = [
            {
                "id": m.id, "sender": m.sender,
                "category": m.category.value if m.category else "unknown",
            }
            for m in msgs if m.requires_leia
        ]
        blocked = [
            {"id": m.id, "sender": m.sender, "status": m.status.value}
            for m in msgs if m.status in (MessageStatus.QUARANTINED, MessageStatus.ERROR, MessageStatus.FLAGGED)
        ]

        return DailyBriefing(
            date=date_str,
            total_messages=len(msgs),
            quarantined=len(quarantined),
            encrypted=len(encrypted),
            by_category=dict(by_category),
            by_owner=dict(by_owner),
            urgent_items=urgent,
            calendar_bookings=[],
            critical_items=critical,
            security_items=security_items,
            leia_decisions=leia_decisions,
            blocked_items=blocked,
            recommended_focus="Review quarantined items and urgent security threats first.",
        )
