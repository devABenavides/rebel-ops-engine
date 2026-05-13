import logging
import re

from agents.base import Agent
from clients import CalendarClient
from models import CalendarBooking, Message
from security import contains_private_leia_info

logger = logging.getLogger(__name__)

cal_client = CalendarClient()

DATE_PATTERNS = [
    (r'(next\s+\w+day)', lambda m: m.group(1)),
    (r'(tomorrow)', lambda m: 'tomorrow'),
    (r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', lambda m: m.group(1)),
    (r'(\w+day)', lambda m: m.group(1)),
]

TIME_PATTERNS = [
    (r'(\d{1,2}:\d{2}\s*(?:am|pm)?)', lambda m: m.group(1)),
    (r'(\d{1,4}\s*hours)', lambda m: m.group(1)),
    (r'at\s+(\d{1,2})\s*(?:am|pm)', lambda m: m.group(1)),
]


def _extract_date(content: str) -> str:
    lower = content.lower()
    for pattern, extract in DATE_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            return extract(m)
    return "unknown"


def _extract_time(content: str) -> str:
    lower = content.lower()
    for pattern, extract in TIME_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            return extract(m)
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
                duration="1 hour",
                subject=message.content[:100],
                is_private=is_private,
            )
            self._bookings.append(booking)

            if not is_private:
                slots = cal_client.check_availability(date_val)
                logger.info("Available slots for %s: %s", date_val, slots)

            status = "PRIVATE" if is_private else "CONFIRMED"
            logger.info("Calendar booking %s from %s (%s at %s)", status, message.sender, date_val, time_val)
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
