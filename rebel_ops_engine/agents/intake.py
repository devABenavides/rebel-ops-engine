import logging
from datetime import datetime, timezone
from uuid import uuid4

from agents.base import Agent
from models import Message, MessageStatus

logger = logging.getLogger(__name__)

MAX_SENDER_LENGTH = 200
MAX_CONTENT_LENGTH = 10000
MAX_SUBJECT_LENGTH = 500
MAX_CONTACT_LENGTH = 500
MAX_PLANET_LENGTH = 200


class IntakeAgent(Agent):
    @property
    def name(self) -> str:
        return "IntakeAgent"

    def process(self, message: Message) -> Message:
        message.status = MessageStatus.NEW
        if not message.sender or not message.content:
            message.status = MessageStatus.ERROR
            message.error = "Missing sender or content"
            message.trace.append({"agent": self.name, "action": "rejected", "details": {"reason": "Missing sender or content"}})
            logger.warning("IntakeAgent: missing sender or content")
            return message
        if len(message.sender) > MAX_SENDER_LENGTH:
            message.status = MessageStatus.ERROR
            message.error = f"Sender exceeds max length of {MAX_SENDER_LENGTH}"
            message.trace.append({"agent": self.name, "action": "rejected", "details": {"reason": "Sender too long"}})
            return message
        if len(message.content) > MAX_CONTENT_LENGTH:
            message.status = MessageStatus.ERROR
            message.error = f"Content exceeds max length of {MAX_CONTENT_LENGTH}"
            message.trace.append({"agent": self.name, "action": "rejected", "details": {"reason": "Content too long"}})
            return message
        if message.subject and len(message.subject) > MAX_SUBJECT_LENGTH:
            message.status = MessageStatus.ERROR
            message.error = f"Subject exceeds max length of {MAX_SUBJECT_LENGTH}"
            message.trace.append({"agent": self.name, "action": "rejected", "details": {"reason": "Subject too long"}})
            return message
        if message.sender_contact and len(message.sender_contact) > MAX_CONTACT_LENGTH:
            message.status = MessageStatus.ERROR
            message.error = f"Sender contact exceeds max length of {MAX_CONTACT_LENGTH}"
            message.trace.append({"agent": self.name, "action": "rejected", "details": {"reason": "Contact too long"}})
            return message
        if message.planet_or_sector and len(message.planet_or_sector) > MAX_PLANET_LENGTH:
            message.status = MessageStatus.ERROR
            message.error = f"Planet/sector exceeds max length of {MAX_PLANET_LENGTH}"
            message.trace.append({"agent": self.name, "action": "rejected", "details": {"reason": "Planet too long"}})
            return message
        if message.id is None:
            message.id = str(uuid4())
        if message.timestamp is None:
            message.timestamp = datetime.now(timezone.utc)
        message.trace.append({
            "agent": self.name, "action": "validated",
            "details": {"id": message.id, "channel": message.channel.value},
        })
        if self.name not in message.processed_by:
            message.processed_by.append(self.name)
        return message
