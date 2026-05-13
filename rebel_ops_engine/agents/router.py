import logging
from uuid import uuid4

from agents.base import Agent
from models import Message, MessageStatus, Owner, Task
from security import (
    CATEGORY_NEXT_ACTION,
    CATEGORY_OWNER,
    CATEGORY_TEAM,
)

logger = logging.getLogger(__name__)


class RoutingAgent(Agent):
    def __init__(self):
        self._tasks: list[Task] = []

    @property
    def name(self) -> str:
        return "RoutingAgent"

    def process(self, message: Message) -> Message:
        if message.status not in (MessageStatus.NEW, MessageStatus.ROUTED, MessageStatus.SECURITY_REVIEW):
            message.trace.append({"agent": self.name, "action": "skipped", "details": {"reason": f"status={message.status.value}"}})
            if self.name not in message.processed_by:
                message.processed_by.append(self.name)
            return message

        cat_val = message.category.value if message.category else "other"

        combined = (message.sender + " " + message.content).lower()
        if ("force" in combined and ("child" in combined or "village" in combined)) or \
           ("sense" in combined and "danger" in combined and "child" in combined):
            message.owner = Owner.GROGU_CARE
            message.assigned_team = "Jedi Council"
        else:
            message.owner = CATEGORY_OWNER.get(cat_val, Owner.GENERAL_LEIA)
            message.assigned_team = CATEGORY_TEAM.get(cat_val, "Intake Review")
        message.suggested_next_action = CATEGORY_NEXT_ACTION.get(cat_val, "")

        if message.status == MessageStatus.SECURITY_REVIEW:
            message.trace.append({"agent": self.name, "action": "held", "details": {"reason": "awaiting security review", "owner": message.owner.value if message.owner else None}})
            if self.name not in message.processed_by:
                message.processed_by.append(self.name)
            return message

        task = Task(
            id=str(uuid4()),
            request_id=message.id,
            owner=message.owner.value,
            assigned_team=message.assigned_team,
            title=f"{cat_val.replace('_', ' ').title()} — {message.sender}",
            description=message.summary or message.content[:200],
            priority=message.priority,
        )
        self._tasks.append(task)
        logger.debug(
            "Routed %s to %s (team: %s, task: %s)",
            message.sender, message.owner.value, message.assigned_team, task.id,
        )

        message.trace.append({
            "agent": self.name, "action": "routed",
            "details": {
                "owner": message.owner.value if message.owner else None,
                "team": message.assigned_team,
                "task_id": task.id,
            },
        })

        if message.status == MessageStatus.NEW:
            message.status = MessageStatus.ROUTED

        if self.name not in message.processed_by:
            message.processed_by.append(self.name)
        return message

    def get_tasks(self) -> list[Task]:
        return list(self._tasks)

    def reset(self):
        self._tasks.clear()
