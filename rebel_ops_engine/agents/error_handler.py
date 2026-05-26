import logging
import threading
from uuid import uuid4

from agents.base import Agent
from database import Database
from integrations import clickup_client
from models import Message, MessageStatus, Task

logger = logging.getLogger(__name__)


class ErrorProtocolAgent(Agent):
    def __init__(self, db: Database | None = None):
        self._lock = threading.Lock()
        self._db = db or Database(":memory:")
        self._clickup_results: dict[str, dict] = {}

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
            self._db.insert_task(task, source="error")
            self._sync_clickup_async(task, message.content, message.error or "Review quarantined message")
            message.trace.append({"agent": self.name, "action": "quarantine_logged", "details": {"task_id": task.id}})

        elif message.status == MessageStatus.ERROR:
            logger.error("Error processing message %s: %s", message.id, message.error)

            task = Task(
                id=str(uuid4()),
                request_id=message.id,
                owner="Operations Team",
                assigned_team="Operations",
                title=f"Automation Error - {message.sender}",
                description=message.error or "Unknown error",
                priority="medium",
                status="open",
            )
            self._db.insert_task(task, source="error")
            self._sync_clickup_async(task, message.content, message.error or "Investigate processing error")
            message.trace.append({"agent": self.name, "action": "error_logged", "details": {"task_id": task.id}})

        else:
            message.trace.append({"agent": self.name, "action": "passed", "details": {"status": message.status.value}})

        if self.name not in message.processed_by:
            message.processed_by.append(self.name)
        return message

    def _sync_clickup_async(self, task: Task, content: str = "", comment_text: str = ""):
        with self._lock:
            self._clickup_results[task.id] = {"status": "initiated"}
        thread = threading.Thread(target=self._sync_clickup, args=(task, content, comment_text))
        thread.start()

    def _sync_clickup(self, task: Task, content: str = "", comment_text: str = ""):
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
            logger.info("[CLICKUP] Error task %s synced (mock)", task.id)
        elif result["status"] == "created":
            logger.info("[CLICKUP] Error task %s created - id=%s", task.id, result.get("id"))
            if comment_text:
                clickup_client.add_comment(result["id"], comment_text)
        else:
            logger.warning("[CLICKUP] Error task %s failed: %s", task.id, result.get("error"))

    def get_error_tasks(self) -> list[Task]:
        return self._db.get_tasks(source="error")

    def get_clickup_results(self) -> dict[str, dict]:
        with self._lock:
            return dict(self._clickup_results)

    def reset(self):
        self._db.reset_all()
        with self._lock:
            self._clickup_results.clear()
