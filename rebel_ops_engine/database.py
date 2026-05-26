import json
import logging
import os
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Optional

from models import (
    CalendarBooking,
    Category,
    Channel,
    EncryptedTransmission,
    Message,
    MessageStatus,
    Owner,
    Task,
)

logger = logging.getLogger(__name__)


def _db_path() -> str:
    return os.getenv("DATABASE_PATH", "rebel_ops.db")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path: str | None = None):
        self._path = path or _db_path()
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self._path, check_same_thread=False, timeout=10)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_tables()

    # ---- Schema ----

    def _init_tables(self):
        with self._lock:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    channel TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    category TEXT,
                    owner TEXT,
                    status TEXT NOT NULL DEFAULT 'new',
                    risk_score INTEGER DEFAULT 0,
                    encrypted INTEGER DEFAULT 0,
                    error TEXT,
                    processed_by TEXT DEFAULT '[]',
                    priority TEXT DEFAULT 'medium',
                    security_risk TEXT DEFAULT 'low',
                    jedi_case_type TEXT DEFAULT 'none',
                    requires_leia INTEGER DEFAULT 0,
                    requires_jedi INTEGER DEFAULT 0,
                    trusted_request INTEGER DEFAULT 1,
                    dark_side_indicators TEXT DEFAULT '[]',
                    summary TEXT DEFAULT '',
                    suggested_next_action TEXT DEFAULT '',
                    assigned_team TEXT DEFAULT '',
                    sender_contact TEXT DEFAULT '',
                    subject TEXT DEFAULT '',
                    planet_or_sector TEXT DEFAULT '',
                    proposals TEXT DEFAULT '[]',
                    trace TEXT DEFAULT '[]'
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    request_id TEXT,
                    owner TEXT NOT NULL,
                    assigned_team TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'open',
                    source TEXT DEFAULT 'router',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS calendar_bookings (
                    message_id TEXT PRIMARY KEY,
                    requestor TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    duration TEXT DEFAULT '30 minutes',
                    subject TEXT,
                    is_private INTEGER DEFAULT 0,
                    attendees TEXT DEFAULT '[]'
                );

                CREATE TABLE IF NOT EXISTS encrypted_transmissions (
                    id TEXT PRIMARY KEY,
                    request_id TEXT,
                    recipient TEXT NOT NULL,
                    ciphertext TEXT NOT NULL,
                    encryption_method TEXT DEFAULT 'demo_reverse_string',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS discord_messages (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
                CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks(owner);
                CREATE INDEX IF NOT EXISTS idx_tasks_source ON tasks(source);
            """)
            self._conn.commit()

    # ---- Serialization helpers ----

    @staticmethod
    def _b(v: bool) -> int:
        return 1 if v else 0

    @staticmethod
    def _to_b(v: int) -> bool:
        return bool(v)

    @staticmethod
    def _js(v: list | dict) -> str:
        return json.dumps(v, default=str)

    @staticmethod
    def _from_json(s: str) -> list:
        if not s:
            return []
        try:
            return json.loads(s)
        except (json.JSONDecodeError, TypeError):
            return []

    @staticmethod
    def _enum(enum_cls, val: str | None):
        if val is None:
            return None
        try:
            return enum_cls(val)
        except (ValueError, TypeError):
            return None

    # ---- Messages ----

    def insert_message(self, msg: Message):
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO messages (
                    id, channel, sender, content, timestamp, category, owner, status,
                    risk_score, encrypted, error, processed_by, priority, security_risk,
                    jedi_case_type, requires_leia, requires_jedi, trusted_request,
                    dark_side_indicators, summary, suggested_next_action, assigned_team,
                    sender_contact, subject, planet_or_sector, proposals, trace
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    msg.id,
                    msg.channel.value,
                    msg.sender,
                    msg.content,
                    msg.timestamp.isoformat(),
                    msg.category.value if msg.category else None,
                    msg.owner.value if msg.owner else None,
                    msg.status.value,
                    msg.risk_score,
                    self._b(msg.encrypted),
                    msg.error,
                    self._js(msg.processed_by),
                    msg.priority,
                    msg.security_risk,
                    msg.jedi_case_type,
                    self._b(msg.requires_leia),
                    self._b(msg.requires_jedi),
                    self._b(msg.trusted_request),
                    self._js(msg.dark_side_indicators),
                    msg.summary,
                    msg.suggested_next_action,
                    msg.assigned_team,
                    msg.sender_contact,
                    msg.subject,
                    msg.planet_or_sector,
                    self._js(msg.proposals),
                    self._js(msg.trace),
                ),
            )
            self._conn.commit()

    def get_message(self, message_id: str) -> Optional[Message]:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM messages WHERE id = ?", (message_id,)
            ).fetchone()
            if row is None:
                return None
            return self._row_to_message(row)

    def get_all_messages(self) -> list[Message]:
        with self._lock:
            rows = self._conn.execute("SELECT * FROM messages").fetchall()
            return [self._row_to_message(r) for r in rows]

    def _row_to_message(self, row: sqlite3.Row) -> Message:
        msg = Message(
            channel=Channel(row["channel"]),
            sender=row["sender"],
            content=row["content"],
            id=row["id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            category=self._enum(Category, row["category"]),
            owner=self._enum(Owner, row["owner"]),
            status=self._enum(MessageStatus, row["status"]),
            risk_score=row["risk_score"],
            encrypted=self._to_b(row["encrypted"]),
            error=row["error"],
            processed_by=self._from_json(row["processed_by"]),
            priority=row["priority"],
            security_risk=row["security_risk"],
            jedi_case_type=row["jedi_case_type"],
            requires_leia=self._to_b(row["requires_leia"]),
            requires_jedi=self._to_b(row["requires_jedi"]),
            trusted_request=self._to_b(row["trusted_request"]),
            dark_side_indicators=self._from_json(row["dark_side_indicators"]),
            summary=row["summary"],
            suggested_next_action=row["suggested_next_action"],
            assigned_team=row["assigned_team"],
            sender_contact=row["sender_contact"],
            subject=row["subject"],
            planet_or_sector=row["planet_or_sector"],
            proposals=self._from_json(row["proposals"]),
            trace=self._from_json(row["trace"]),
        )
        return msg

    # ---- Tasks ----

    def insert_task(self, task: Task, source: str = "router"):
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO tasks
                   (id, request_id, owner, assigned_team, title, description,
                    priority, status, source, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    task.id,
                    task.request_id,
                    task.owner,
                    task.assigned_team,
                    task.title,
                    task.description,
                    task.priority,
                    task.status,
                    source,
                    task.created_at.isoformat(),
                ),
            )
            self._conn.commit()

    def get_tasks(self, source: str | None = None) -> list[Task]:
        with self._lock:
            if source:
                rows = self._conn.execute(
                    "SELECT * FROM tasks WHERE source = ?", (source,)
                ).fetchall()
            else:
                rows = self._conn.execute("SELECT * FROM tasks").fetchall()
            return [self._row_to_task(r) for r in rows]

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            request_id=row["request_id"],
            owner=row["owner"],
            assigned_team=row["assigned_team"],
            title=row["title"],
            description=row["description"],
            priority=row["priority"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    # ---- Calendar Bookings ----

    def insert_booking(self, booking: CalendarBooking):
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO calendar_bookings
                   (message_id, requestor, date, time, duration, subject,
                    is_private, attendees)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    booking.message_id,
                    booking.requestor,
                    booking.date,
                    booking.time,
                    booking.duration,
                    booking.subject,
                    self._b(booking.is_private),
                    self._js(booking.attendees),
                ),
            )
            self._conn.commit()

    def get_all_bookings(self) -> list[CalendarBooking]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM calendar_bookings"
            ).fetchall()
            return [self._row_to_booking(r) for r in rows]

    def get_public_bookings(self) -> list[CalendarBooking]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM calendar_bookings WHERE is_private = 0"
            ).fetchall()
            return [self._row_to_booking(r) for r in rows]

    def _row_to_booking(self, row: sqlite3.Row) -> CalendarBooking:
        return CalendarBooking(
            message_id=row["message_id"],
            requestor=row["requestor"],
            date=row["date"],
            time=row["time"],
            duration=row["duration"],
            subject=row["subject"],
            is_private=self._to_b(row["is_private"]),
            attendees=self._from_json(row["attendees"]),
        )

    # ---- Encrypted Transmissions ----

    def insert_transmission(self, t: EncryptedTransmission):
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO encrypted_transmissions
                   (id, request_id, recipient, ciphertext, encryption_method, created_at)
                   VALUES (?,?,?,?,?,?)""",
                (
                    t.id,
                    t.request_id,
                    t.recipient,
                    t.ciphertext,
                    t.encryption_method,
                    t.created_at.isoformat(),
                ),
            )
            self._conn.commit()

    def get_transmissions(self) -> list[EncryptedTransmission]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM encrypted_transmissions"
            ).fetchall()
            return [self._row_to_transmission(r) for r in rows]

    def _row_to_transmission(self, row: sqlite3.Row) -> EncryptedTransmission:
        return EncryptedTransmission(
            id=row["id"],
            request_id=row["request_id"],
            recipient=row["recipient"],
            ciphertext=row["ciphertext"],
            encryption_method=row["encryption_method"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    # ---- Discord Messages ----

    def insert_discord_message(self, message_id: str):
        with self._lock:
            self._conn.execute(
                "INSERT OR IGNORE INTO discord_messages (id, created_at) VALUES (?, ?)",
                (message_id, _now()),
            )
            self._conn.commit()

    def get_all_discord_message_ids(self) -> list[str]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT id FROM discord_messages ORDER BY created_at"
            ).fetchall()
            return [r["id"] for r in rows]

    def delete_discord_message(self, message_id: str):
        with self._lock:
            self._conn.execute(
                "DELETE FROM discord_messages WHERE id = ?", (message_id,)
            )
            self._conn.commit()

    # ---- Reset ----

    def reset_all(self):
        with self._lock:
            self._conn.executescript("""
                DELETE FROM messages;
                DELETE FROM tasks;
                DELETE FROM calendar_bookings;
                DELETE FROM encrypted_transmissions;
                DELETE FROM discord_messages;
            """)
            self._conn.commit()

    def close(self):
        self._conn.close()
