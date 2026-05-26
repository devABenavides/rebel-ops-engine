import logging
import re
import threading
from uuid import uuid4

from agents.base import Agent
from database import Database
from integrations import clickup_client
from models import Message, MessageStatus, Owner, Task
from security import (
    CATEGORY_NEXT_ACTION,
    CATEGORY_OWNER,
    CATEGORY_TEAM,
)

logger = logging.getLogger(__name__)


class RoutingAgent(Agent):
    def __init__(self, db: Database | None = None):
        self._lock = threading.Lock()
        self._db = db or Database(":memory:")
        self._clickup_results: dict[str, dict] = {}

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
        if (re.search(r"\bforce\b", combined) and (re.search(r"\bchild\b", combined) or re.search(r"\bvillage\b", combined))) or \
           (re.search(r"\bsense\b", combined) and re.search(r"\bdanger\b", combined) and re.search(r"\bchild\b", combined)):
            message.owner = Owner.GROGU_CARE
            message.assigned_team = "Jedi Council"
            message.requires_leia = True
            message.security_risk = "high"
            message.error = "[RESTRICTED] Details classified per Grogu Care protocol"
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
            title=f"{cat_val.replace('_', ' ').title()} - {message.sender}",
            description=message.summary or message.content[:200],
            priority=message.priority,
        )
        self._db.insert_task(task, source="router")

        with self._lock:
            self._clickup_results[task.id] = {"status": "initiated"}
        thread = threading.Thread(target=self._sync_clickup, args=(task, message.content, message.suggested_next_action))
        thread.start()

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

    def _sync_clickup(self, task: Task, content: str = "", next_action: str = ""):
        result = clickup_client.create_task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            owner=task.owner,
            team=task.assigned_team,
            content=content,
        )
        with self._lock:
            self._clickup_results[task.id] = result
        if result["status"] == "mocked":
            logger.info("[CLICKUP] Task %s synced (mock)", task.id)
        elif result["status"] == "created":
            logger.info("[CLICKUP] Task %s created - id=%s", task.id, result.get("id"))
            if next_action:
                clickup_client.add_comment(result["id"], next_action)
        else:
            logger.warning("[CLICKUP] Task %s failed: %s", task.id, result.get("error"))

    def get_tasks(self) -> list[Task]:
        return self._db.get_tasks(source="router")

    def get_clickup_results(self) -> dict[str, dict]:
        with self._lock:
            return dict(self._clickup_results)

    def reset(self):
        self._db.reset_all()
        with self._lock:
            self._clickup_results.clear()
