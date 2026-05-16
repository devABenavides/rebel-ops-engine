import logging
import re
from datetime import datetime, timedelta

from agents.base import Agent
from clients import CalendarClient
from models import CalendarBooking, Message, MessageStatus
from security import contains_private_leia_info

logger = logging.getLogger(__name__)

cal_client = CalendarClient()

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _extract_date(content: str) -> str:
    lower = content.lower()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    m = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', lower)
    if m:
        parts = m.groups()
        return f"{parts[2].zfill(4) if len(parts[2]) == 4 else '20' + parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"

    if re.search(r'\btomorrow\b', lower):
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    m = re.search(r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', lower)
    if m:
        target = m.group(1)
        today_weekday = today.weekday()
        target_weekday = WEEKDAYS.index(target)
        days_ahead = (target_weekday - today_weekday + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    m = re.search(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', lower)
    if m:
        target = m.group(1)
        today_weekday = today.weekday()
        target_weekday = WEEKDAYS.index(target)
        days_ahead = (target_weekday - today_weekday + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    return "unknown"


def _extract_time(content: str) -> str:
    lower = content.lower()
    m = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', lower)
    if m:
        hour = int(m.group(1))
        minute = m.group(2)
        period = m.group(3)
        if period == "pm" and hour < 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        return f"{hour:02d}:{minute}"

    m = re.search(r'at\s+(\d{1,2})\s*(am|pm)', lower)
    if m:
        hour = int(m.group(1))
        period = m.group(2)
        if period == "pm" and hour < 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        return f"{hour:02d}:00"

    return "unknown"


class CalendarAgent(Agent):
    def __init__(self):
        self._bookings: list[CalendarBooking] = []

    @property
    def name(self) -> str:
        return "CalendarAgent"

    def process(self, message: Message) -> Message:
        if message.category and message.category.value == "calendar_booking":
            is_private = contains_private_leia_info(message.content)
            date_val = _extract_date(message.content)
            time_val = _extract_time(message.content)

            booking = CalendarBooking(
                message_id=message.id,
                requestor=message.sender,
                date=date_val,
                time=time_val,
                duration="30 minutes",
                subject=message.content[:100],
                is_private=is_private,
            )
            self._bookings.append(booking)

            if not is_private and date_val != "unknown":
                slots = cal_client.find_available_slots(date_val)
                if slots:
                    message.proposals = slots
                    message.status = MessageStatus.AWAITING_CONFIRMATION
                    message.suggested_next_action = (
                        f"Choose a slot: {', '.join(slots)}. "
                        f"Confirm at: http://localhost:5000/api/calendar/confirm/{message.id}/0"
                    )
                    message.trace.append({
                        "agent": self.name, "action": "proposed_slots",
                        "details": {"date": date_val, "slots": slots},
                    })
                    logger.info("Proposed slots for %s: %s", message.sender, slots)
                    message.processed_by.append(self.name)
                    return message

            if not is_private and date_val != "unknown" and time_val != "unknown":
                try:
                    result = cal_client.create_event(booking.subject[:100], booking.date, booking.time)
                    logger.info("Calendar event: %s", result.get("status", "unknown"))
                except Exception as e:
                    logger.warning("Failed to create calendar event: %s", e)

            logger.info("Calendar booking from %s (%s at %s)", message.sender, date_val, time_val)
            if is_private:
                message.error = "Private Leia calendar details redacted from reports"
            message.trace.append({
                "agent": self.name, "action": "booked",
                "details": {"date": date_val, "time": time_val, "private": is_private},
            })
        else:
            message.trace.append({"agent": self.name, "action": "skipped", "details": {"reason": "not calendar_booking"}})

        if self.name not in message.processed_by:
            message.processed_by.append(self.name)
        return message

    def get_public_bookings(self) -> list[CalendarBooking]:
        return [b for b in self._bookings if not b.is_private]

    def get_all_bookings(self) -> list[CalendarBooking]:
        return list(self._bookings)

    def reset(self):
        self._bookings.clear()
