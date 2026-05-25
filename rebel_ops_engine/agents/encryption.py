import logging
from uuid import uuid4

from agents.base import Agent
from database import Database
from models import EncryptedTransmission, Message, MessageStatus
from security import is_yoda_strategy

logger = logging.getLogger(__name__)


class YodaEncryptionAgent(Agent):
    def __init__(self, db: Database | None = None):
        self._db = db or Database(":memory:")

    @property
    def name(self) -> str:
        return "YodaEncryptionAgent"

    def process(self, message: Message) -> Message:
        if message.encrypted:
            message.trace.append({"agent": self.name, "action": "skipped", "details": {"reason": "already encrypted"}})
            if self.name not in message.processed_by:
                message.processed_by.append(self.name)
            return message

        category_val = message.category.value if message.category else None
        if is_yoda_strategy(message.content, category_val, message.sender):
            original = message.content
            ciphertext = original[::-1]
            message.content = f"[DEMO ENCRYPTED] {ciphertext}"
            message.encrypted = True
            if message.status == MessageStatus.NEW:
                message.status = MessageStatus.ROUTED

            transmission = EncryptedTransmission(
                id=str(uuid4()),
                request_id=message.id,
                recipient="Yoda",
                ciphertext=ciphertext,
                encryption_method="demo_reverse_string",
            )
            self._db.insert_transmission(transmission)
            message.trace.append({
                "agent": self.name, "action": "encrypted",
                "details": {"transmission_id": transmission.id, "method": "demo_reverse_string"},
            })
            logger.info(
                "Encrypted Yoda strategy transmission %s from %s",
                transmission.id, message.sender,
            )
        else:
            message.trace.append({"agent": self.name, "action": "skipped", "details": {"reason": "not yoda strategy"}})
        if self.name not in message.processed_by:
            message.processed_by.append(self.name)
        return message

    def get_transmissions(self) -> list[EncryptedTransmission]:
        return self._db.get_transmissions()

    def reset(self):
        self._db.reset_all()
