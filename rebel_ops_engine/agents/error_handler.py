import logging
from uuid import uuid4

from agents.base import Agent
from models import Message, MessageStatus, Task

logger = logging.getLogger(__name__)


class ErrorProtocolAgent(Agent):
    def __init__(self):
        self._error_tasks: list[Task] = []

    @property
    def name(self) -> str:
        return "ErrorProtocolAgent"

    def process(self, message: Message) -> Message:
        if message.status == MessageStatus.QUARANTINED:
            logger.warning(
                "High-risk message quarantined. Sender: %s | Indicators: %s",
                message.sender, message.dark_side_indicators,
            )
            logger.warning("Reason: %s", message.error)

            task = Task(
                id=str(uuid4()),
                request_id=message.id,
                owner="Security Team",
                assigned_team="Security",
                title=f"Review quarantined message from {message.sender}",
                description=message.error or "No details",
                priority="high",
                status="open",
            )
            self._error_tasks.append(task)
            message.trace.append({"agent": self.name, "action": "quarantine_logged", "details": {"task_id": task.id}})

        elif message.status == MessageStatus.ERROR:
            logger.error("Error processing message %s: %s", message.id, message.error)

            task = Task(
                id=str(uuid4()),
                request_id=message.id,
                owner="Operations Team",
                assigned_team="Operations",
                title=f"Automation Error — {message.sender}",
                description=message.error or "Unknown error",
                priority="medium",
                status="open",
            )
            self._error_tasks.append(task)
            message.trace.append({"agent": self.name, "action": "error_logged", "details": {"task_id": task.id}})

        else:
            message.trace.append({"agent": self.name, "action": "passed", "details": {"status": message.status.value}})

        if self.name not in message.processed_by:
            message.processed_by.append(self.name)
        return message

    def get_error_tasks(self) -> list[Task]:
        return list(self._error_tasks)

    def reset(self):
        self._error_tasks.clear()
