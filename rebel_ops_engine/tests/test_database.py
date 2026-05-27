"""Isolated unit tests for the Database persistence layer.

Each test uses its own :memory: Database instance to avoid cross-test pollution.
"""

import threading
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from database import Database
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


@pytest.fixture
def db():
    d = Database(path=":memory:")
    yield d
    d.close()


def _make_message(sender="Test Sender", content="Test content") -> Message:
    return Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender=sender,
        content=content,
        id=str(uuid4()),
    )


def _make_task(owner="Han Solo") -> Task:
    return Task(
        id=str(uuid4()),
        request_id=str(uuid4()),
        owner=owner,
        assigned_team="Logistics Team",
        title="Test task",
        description="A test task description",
        priority="medium",
    )


def _make_booking(message_id="", requestor="Test Requestor") -> CalendarBooking:
    return CalendarBooking(
        message_id=message_id or str(uuid4()),
        requestor=requestor,
        date="2025-05-26",
        time="10:00",
        duration="30 minutes",
        subject="Test meeting",
    )


# ---- Messages ----

class TestMessages:
    def test_insert_and_get(self, db):
        msg = _make_message()
        db.insert_message(msg)
        retrieved = db.get_message(msg.id)
        assert retrieved is not None
        assert retrieved.id == msg.id
        assert retrieved.sender == "Test Sender"
        assert retrieved.channel == Channel.INTERGALACTIC_WHATSAPP
        assert retrieved.status == MessageStatus.NEW

    def test_insert_and_get_all(self, db):
        msgs = [_make_message(sender=f"User{i}") for i in range(5)]
        for m in msgs:
            db.insert_message(m)
        all_msgs = db.get_all_messages()
        assert len(all_msgs) == 5

    def test_get_message_not_found(self, db):
        retrieved = db.get_message("nonexistent-id")
        assert retrieved is None

    def test_get_all_empty(self, db):
        assert db.get_all_messages() == []

    def test_insert_replace_same_id(self, db):
        msg_id = str(uuid4())
        msg1 = _make_message(sender="First")
        msg1.id = msg_id
        db.insert_message(msg1)

        msg2 = _make_message(sender="Second")
        msg2.id = msg_id
        db.insert_message(msg2)

        retrieved = db.get_message(msg_id)
        assert retrieved.sender == "Second"

    def test_message_all_fields_round_trip(self, db):
        msg = Message(
            channel=Channel.HOLOGRAM_EMAIL,
            sender="Round Trip Sender",
            content="Round trip test content with special chars: ñ, é, 中文",
            id=str(uuid4()),
            category=Category.LOGISTICS,
            owner=Owner.HAN_SOLO,
            status=MessageStatus.COMPLETED,
            risk_score=42,
            encrypted=True,
            error=None,
            processed_by=["IntakeAgent", "RoutingAgent"],
            priority="high",
            security_risk="medium",
            jedi_case_type="none",
            requires_leia=True,
            requires_jedi=False,
            trusted_request=False,
            dark_side_indicators=["sith", "infiltration"],
            summary="Test summary",
            suggested_next_action="Route to Han Solo",
            assigned_team="Logistics Team",
            sender_contact="contact@rebel.com",
            subject="Test subject",
            planet_or_sector="Tatooine",
            proposals=["10:00", "14:00", "16:00"],
            trace=[{"agent": "IntakeAgent", "action": "validated"}],
        )
        db.insert_message(msg)
        retrieved = db.get_message(msg.id)

        assert retrieved.id == msg.id
        assert retrieved.channel == msg.channel
        assert retrieved.sender == msg.sender
        assert retrieved.content == msg.content
        assert retrieved.category == msg.category
        assert retrieved.owner == msg.owner
        assert retrieved.status == msg.status
        assert retrieved.risk_score == msg.risk_score
        assert retrieved.encrypted == msg.encrypted
        assert retrieved.error == msg.error
        assert retrieved.processed_by == msg.processed_by
        assert retrieved.priority == msg.priority
        assert retrieved.security_risk == msg.security_risk
        assert retrieved.jedi_case_type == msg.jedi_case_type
        assert retrieved.requires_leia == msg.requires_leia
        assert retrieved.requires_jedi == msg.requires_jedi
        assert retrieved.trusted_request == msg.trusted_request
        assert retrieved.dark_side_indicators == msg.dark_side_indicators
        assert retrieved.summary == msg.summary
        assert retrieved.suggested_next_action == msg.suggested_next_action
        assert retrieved.assigned_team == msg.assigned_team
        assert retrieved.sender_contact == msg.sender_contact
        assert retrieved.subject == msg.subject
        assert retrieved.planet_or_sector == msg.planet_or_sector
        assert retrieved.proposals == msg.proposals
        assert retrieved.trace == msg.trace

    def test_null_fields_round_trip(self, db):
        msg = _make_message()
        msg.category = None
        msg.owner = None
        msg.error = None
        db.insert_message(msg)
        retrieved = db.get_message(msg.id)
        assert retrieved.category is None
        assert retrieved.owner is None
        assert retrieved.error is None

    def test_empty_lists_round_trip(self, db):
        msg = _make_message()
        msg.dark_side_indicators = []
        msg.proposals = []
        msg.trace = []
        msg.processed_by = []
        db.insert_message(msg)
        retrieved = db.get_message(msg.id)
        assert retrieved.dark_side_indicators == []
        assert retrieved.proposals == []
        assert retrieved.trace == []
        assert retrieved.processed_by == []

    def test_long_content_stored(self, db):
        msg = _make_message(content="X" * 10000)
        db.insert_message(msg)
        retrieved = db.get_message(msg.id)
        assert len(retrieved.content) == 10000


# ---- Tasks ----

class TestTasks:
    def test_insert_and_get(self, db):
        task = _make_task()
        db.insert_task(task)
        tasks = db.get_tasks()
        assert len(tasks) == 1
        assert tasks[0].id == task.id
        assert tasks[0].owner == "Han Solo"
        assert tasks[0].title == "Test task"

    def test_get_by_source(self, db):
        t1 = _make_task()
        t2 = _make_task()
        db.insert_task(t1, source="router")
        db.insert_task(t2, source="error_handler")

        router_tasks = db.get_tasks(source="router")
        assert len(router_tasks) == 1
        assert router_tasks[0].id == t1.id

        error_tasks = db.get_tasks(source="error_handler")
        assert len(error_tasks) == 1
        assert error_tasks[0].id == t2.id

    def test_get_all_tasks(self, db):
        tasks = [_make_task(owner=f"Owner{i}") for i in range(3)]
        for t in tasks:
            db.insert_task(t)
        all_tasks = db.get_tasks()
        assert len(all_tasks) == 3

    def test_empty_tasks(self, db):
        assert db.get_tasks() == []
        assert db.get_tasks(source="router") == []

    def test_task_fields_round_trip(self, db):
        now = datetime.now(timezone.utc)
        task = Task(
            id=str(uuid4()),
            request_id=str(uuid4()),
            owner="General Leia",
            assigned_team="Executive Office",
            title="Strategy meeting",
            description="Quarterly strategy review with command staff",
            priority="high",
            status="in_progress",
            created_at=now,
        )
        db.insert_task(task)
        retrieved = db.get_tasks()[0]
        assert retrieved.id == task.id
        assert retrieved.request_id == task.request_id
        assert retrieved.owner == task.owner
        assert retrieved.assigned_team == task.assigned_team
        assert retrieved.title == task.title
        assert retrieved.description == task.description
        assert retrieved.priority == task.priority
        assert retrieved.status == task.status
        assert retrieved.created_at == task.created_at


# ---- Calendar Bookings ----

class TestCalendarBookings:
    def test_insert_and_get_all(self, db):
        booking = _make_booking()
        db.insert_booking(booking)
        all_bookings = db.get_all_bookings()
        assert len(all_bookings) == 1
        assert all_bookings[0].message_id == booking.message_id

    def test_get_public_bookings(self, db):
        b1 = _make_booking(requestor="Public Requestor")
        b1.is_private = False
        b2 = _make_booking(requestor="Private Requestor")
        b2.is_private = True
        db.insert_booking(b1)
        db.insert_booking(b2)

        all_bookings = db.get_all_bookings()
        assert len(all_bookings) == 2

        public = db.get_public_bookings()
        assert len(public) == 1
        assert public[0].requestor == "Public Requestor"

    def test_booking_fields_round_trip(self, db):
        booking = CalendarBooking(
            message_id=str(uuid4()),
            requestor="Mon Mothma",
            date="2025-06-01",
            time="14:00",
            duration="60 minutes",
            subject="Alliance strategy",
            is_private=True,
            attendees=["Leia", "Mon Mothma", "Ackbar"],
        )
        db.insert_booking(booking)
        retrieved = db.get_all_bookings()[0]
        assert retrieved.message_id == booking.message_id
        assert retrieved.requestor == booking.requestor
        assert retrieved.date == booking.date
        assert retrieved.time == booking.time
        assert retrieved.duration == booking.duration
        assert retrieved.subject == booking.subject
        assert retrieved.is_private == booking.is_private
        assert retrieved.attendees == booking.attendees

    def test_empty_public_bookings(self, db):
        assert db.get_public_bookings() == []


# ---- Encrypted Transmissions ----

class TestEncryptedTransmissions:
    def test_insert_and_get(self, db):
        t = EncryptedTransmission(
            id=str(uuid4()),
            request_id=str(uuid4()),
            recipient="Yoda",
            ciphertext="gnirtS esreveR",
            encryption_method="demo_reverse_string",
        )
        db.insert_transmission(t)
        transmissions = db.get_transmissions()
        assert len(transmissions) == 1
        assert transmissions[0].id == t.id
        assert transmissions[0].recipient == "Yoda"
        assert transmissions[0].ciphertext == "gnirtS esreveR"

    def test_multiple_transmissions(self, db):
        for i in range(3):
            t = EncryptedTransmission(
                id=str(uuid4()),
                request_id=str(uuid4()),
                recipient=f"Recipient{i}",
                ciphertext=f"ciphertext{i}",
            )
            db.insert_transmission(t)
        assert len(db.get_transmissions()) == 3

    def test_empty_transmissions(self, db):
        assert db.get_transmissions() == []


# ---- Discord Messages ----

class TestDiscordMessages:
    def test_insert_and_get(self, db):
        msg_id = "discord-msg-123"
        db.insert_discord_message(msg_id)
        ids = db.get_all_discord_message_ids()
        assert msg_id in ids

    def test_insert_ignore_duplicate(self, db):
        msg_id = "discord-msg-dup"
        db.insert_discord_message(msg_id)
        db.insert_discord_message(msg_id)
        ids = db.get_all_discord_message_ids()
        assert len([i for i in ids if i == msg_id]) == 1

    def test_delete_discord_message(self, db):
        msg_id = "discord-msg-to-delete"
        db.insert_discord_message(msg_id)
        db.delete_discord_message(msg_id)
        ids = db.get_all_discord_message_ids()
        assert msg_id not in ids

    def test_empty_discord(self, db):
        assert db.get_all_discord_message_ids() == []


# ---- Reset ----

class TestReset:
    def test_reset_all_clears_all_tables(self, db):
        db.insert_message(_make_message())
        db.insert_task(_make_task())
        db.insert_booking(_make_booking())
        t = EncryptedTransmission(id=str(uuid4()), request_id=str(uuid4()), recipient="Yoda", ciphertext="test")
        db.insert_transmission(t)
        db.insert_discord_message("discord-1")

        db.reset_all()
        assert db.get_all_messages() == []
        assert db.get_tasks() == []
        assert db.get_all_bookings() == []
        assert db.get_transmissions() == []
        assert db.get_all_discord_message_ids() == []

    def test_reset_all_empty_db(self, db):
        db.reset_all()
        assert db.get_all_messages() == []


# ---- Concurrency ----

class TestConcurrency:
    def test_threading_lock_safety(self, db):
        errors = []

        def insert_msg(i):
            try:
                msg = _make_message(sender=f"Thread{i}", content=f"Content from thread {i}")
                db.insert_message(msg)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=insert_msg, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(db.get_all_messages()) == 20


# ---- Serialization helpers ----

class TestSerialization:
    def test_boolean_serialization(self):
        assert Database._b(True) == 1
        assert Database._b(False) == 0
        assert Database._to_b(1) is True
        assert Database._to_b(0) is False

    def test_json_serialization(self):
        data = ["a", "b", "c"]
        serialized = Database._js(data)
        assert serialized == '["a", "b", "c"]'
        deserialized = Database._from_json(serialized)
        assert deserialized == data

    def test_json_serialization_empty_list(self):
        assert Database._js([]) == "[]"
        assert Database._from_json("[]") == []

    def test_from_json_empty_string(self):
        assert Database._from_json("") == []

    def test_from_json_invalid(self):
        assert Database._from_json("{{{invalid}}") == []

    def test_enum_null(self):
        assert Database._enum(Category, None) is None

    def test_enum_valid(self):
        assert Database._enum(Category, "logistics") == Category.LOGISTICS

    def test_enum_invalid(self):
        assert Database._enum(Category, "invalid_category") is None
