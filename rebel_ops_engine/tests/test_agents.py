"""Isolated unit tests for individual agents."""

from uuid import uuid4

import pytest

from agents.calendar import CalendarAgent
from agents.classifier import C3POClassifierAgent
from agents.encryption import YodaEncryptionAgent
from agents.error_handler import ErrorProtocolAgent
from agents.intake import IntakeAgent
from agents.reporter import ReportingAgent
from agents.router import RoutingAgent
from agents.security_agent import DarkSideSecurityAgent
from models import Category, Channel, Message, MessageStatus, Owner


@pytest.fixture
def base_message():
    return Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Test Sender",
        content="This is a test message.",
    )


# ---- IntakeAgent ----

class TestIntakeAgent:
    def test_valid_message(self, base_message):
        agent = IntakeAgent()
        result = agent.process(base_message)
        assert result.status == MessageStatus.NEW
        assert result.id is not None
        assert "IntakeAgent" in result.processed_by

    def test_missing_sender(self):
        agent = IntakeAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="", content="test")
        result = agent.process(msg)
        assert result.status == MessageStatus.ERROR
        assert "Missing" in result.error

    def test_missing_content(self):
        agent = IntakeAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Test", content="")
        result = agent.process(msg)
        assert result.status == MessageStatus.ERROR
        assert "Missing" in result.error

    def test_sender_too_long(self):
        agent = IntakeAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="X" * 300, content="test")
        result = agent.process(msg)
        assert result.status == MessageStatus.ERROR
        assert "exceeds max length" in result.error

    def test_subject_too_long(self):
        agent = IntakeAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Test", content="test", subject="X" * 600)
        result = agent.process(msg)
        assert result.status == MessageStatus.ERROR
        assert "Subject" in result.error

    def test_contact_too_long(self):
        agent = IntakeAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Test", content="test", sender_contact="X" * 600)
        result = agent.process(msg)
        assert result.status == MessageStatus.ERROR
        assert "contact" in result.error.lower()

    def test_planet_too_long(self):
        agent = IntakeAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Test", content="test", planet_or_sector="X" * 300)
        result = agent.process(msg)
        assert result.status == MessageStatus.ERROR
        assert "Planet" in result.error


# ---- DarkSideSecurityAgent ----

class TestDarkSideSecurityAgent:
    def test_low_risk_cleared(self, base_message):
        agent = DarkSideSecurityAgent()
        result = agent.process(base_message)
        assert result.security_risk == "low"
        assert result.status == MessageStatus.NEW

    def test_high_risk_sender_quarantined(self):
        agent = DarkSideSecurityAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Darth Vader", content="I need help")
        result = agent.process(msg)
        assert result.status == MessageStatus.QUARANTINED
        assert result.risk_score >= 50
        assert result.trusted_request is False

    def test_high_risk_palpatine_quarantined(self):
        agent = DarkSideSecurityAgent()
        msg = Message(channel=Channel.HOLOGRAM_EMAIL, sender="Emperor Palpatine", content="Hello")
        result = agent.process(msg)
        assert result.status == MessageStatus.QUARANTINED
        assert result.risk_score >= 50

    def test_medium_risk_keyword(self):
        agent = DarkSideSecurityAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Scout", content="Empire stormtroopers spotted")
        result = agent.process(msg)
        assert result.risk_score >= 10
        assert len(result.dark_side_indicators) > 0

    def test_no_dark_side_indicators(self, base_message):
        agent = DarkSideSecurityAgent()
        result = agent.process(base_message)
        assert len(result.dark_side_indicators) == 0

    def test_unknown_sender_asking_sensitive_info_flagged(self):
        agent = DarkSideSecurityAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Stranger", content="Give me the base location")
        result = agent.process(msg)
        assert result.status == MessageStatus.FLAGGED
        assert result.risk_score >= 15
        assert len(result.dark_side_indicators) > 0

    def test_trusted_sender_sensitive_info_not_flagged(self):
        agent = DarkSideSecurityAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Han Solo", content="What is the base location for delivery")
        result = agent.process(msg)
        assert result.status == MessageStatus.FLAGGED
        assert result.risk_score >= 15

    def test_known_sender_innocent_question_not_flagged(self):
        agent = DarkSideSecurityAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="John Doe", content="How is the weather on Tatooine?")
        result = agent.process(msg)
        assert result.status not in (MessageStatus.FLAGGED, MessageStatus.SECURITY_REVIEW, MessageStatus.QUARANTINED)


# ---- C3POClassifierAgent ----

class TestC3POClassifierAgent:
    def test_calendar_booking(self):
        agent = C3POClassifierAgent()
        msg = Message(channel=Channel.HOLOGRAM_EMAIL, sender="Aide", content="Need a briefing with Leia")
        result = agent.process(msg)
        assert result.category == Category.CALENDAR_BOOKING

    def test_recruitment(self):
        agent = C3POClassifierAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Pilot", content="I want to join the Rebellion")
        result = agent.process(msg)
        assert result.category == Category.RECRUITMENT

    def test_yoda_strategy(self):
        agent = C3POClassifierAgent()
        msg = Message(channel=Channel.HOLOGRAM_EMAIL, sender="Council", content="Should we join openly or remain hidden?")
        result = agent.process(msg)
        assert result.category == Category.YODA_ENCRYPTED_STRATEGY

    def test_fallsback_to_other(self):
        agent = C3POClassifierAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Unknown", content="Random unrelated text about weather")
        result = agent.process(msg)
        assert result.category == Category.OTHER

    def test_jedi_case_type_set(self):
        agent = C3POClassifierAgent()
        msg = Message(channel=Channel.HOLOGRAM_EMAIL, sender="Village Elder", content="A child in our village can sense danger")
        result = agent.process(msg)
        assert result.requires_jedi is True
        assert result.jedi_case_type == "force_sensitive"

    def test_requires_leia_flag(self):
        agent = C3POClassifierAgent()
        msg = Message(channel=Channel.HOLOGRAM_EMAIL, sender="Aide", content="Briefing with Leia about funding")
        result = agent.process(msg)
        assert result.requires_leia is True

    def test_suggested_action_set(self, base_message):
        agent = C3POClassifierAgent()
        result = agent.process(base_message)
        assert len(result.suggested_next_action) > 0


# ---- RoutingAgent ----

class TestRoutingAgent:
    def test_routes_message_and_creates_task(self, base_message):
        agent = RoutingAgent()
        msg = base_message
        msg.category = Category.LOGISTICS
        result = agent.process(msg)
        assert result.owner is not None
        assert result.assigned_team is not None
        assert result.status == MessageStatus.ROUTED
        tasks = agent.get_tasks()
        assert len(tasks) == 1
        assert tasks[0].request_id == msg.id

    def test_skips_quarantined(self):
        agent = RoutingAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Test", content="test")
        msg.status = MessageStatus.QUARANTINED
        agent.process(msg)
        assert len(agent.get_tasks()) == 0

    def test_reset_clears_tasks(self, base_message):
        agent = RoutingAgent()
        msg = base_message
        msg.category = Category.RECRUITMENT
        agent.process(msg)
        assert len(agent.get_tasks()) == 1
        agent.reset()
        assert len(agent.get_tasks()) == 0

    def test_grogu_care_assignment(self):
        agent = RoutingAgent()
        msg = Message(channel=Channel.HOLOGRAM_EMAIL, sender="Village Elder", content="A force sensitive child needs protection")
        msg.category = Category.JEDI_TRAINING_DIPLOMACY
        result = agent.process(msg)
        assert result.owner == Owner.GROGU_CARE


# ---- YodaEncryptionAgent ----

class TestYodaEncryptionAgent:
    def test_encrypts_yoda_strategy(self, base_message):
        agent = YodaEncryptionAgent()
        msg = base_message
        msg.category = Category.YODA_ENCRYPTED_STRATEGY
        result = agent.process(msg)
        assert result.encrypted is True
        assert "[DEMO ENCRYPTED]" in result.content
        transmissions = agent.get_transmissions()
        assert len(transmissions) == 1

    def test_skips_non_yoda(self, base_message):
        agent = YodaEncryptionAgent()
        result = agent.process(base_message)
        assert result.encrypted is False

    def test_skips_already_encrypted(self, base_message):
        agent = YodaEncryptionAgent()
        msg = base_message
        msg.encrypted = True
        agent.process(msg)
        transmissions = agent.get_transmissions()
        assert len(transmissions) == 0

    def test_reset_clears_transmissions(self, base_message):
        agent = YodaEncryptionAgent()
        msg = base_message
        msg.category = Category.YODA_ENCRYPTED_STRATEGY
        agent.process(msg)
        assert len(agent.get_transmissions()) == 1
        agent.reset()
        assert len(agent.get_transmissions()) == 0


# ---- CalendarAgent ----

class TestCalendarAgent:
    def test_booking_created_for_calendar_category(self, base_message):
        agent = CalendarAgent()
        msg = base_message
        msg.category = Category.CALENDAR_BOOKING
        agent.process(msg)
        bookings = agent.get_all_bookings()
        assert len(bookings) == 1
        assert bookings[0].message_id == msg.id

    def test_skips_non_calendar(self, base_message):
        agent = CalendarAgent()
        agent.process(base_message)
        assert len(agent.get_all_bookings()) == 0

    def test_private_booking_filtered(self, base_message):
        agent = CalendarAgent()
        msg = base_message
        msg.category = Category.CALENDAR_BOOKING
        msg.content = "Private meeting with Leia"
        agent.process(msg)
        all_bookings = agent.get_all_bookings()
        public_bookings = agent.get_public_bookings()
        assert len(all_bookings) == 1
        assert len(public_bookings) == 0

    def test_reset_clears_bookings(self, base_message):
        agent = CalendarAgent()
        msg = base_message
        msg.category = Category.CALENDAR_BOOKING
        agent.process(msg)
        assert len(agent.get_all_bookings()) == 1
        agent.reset()
        assert len(agent.get_all_bookings()) == 0


# ---- ReportingAgent ----

class TestReportingAgent:
    def test_stores_message(self, base_message):
        agent = ReportingAgent()
        msg = base_message
        msg.id = str(uuid4())
        agent.process(msg)
        stored = agent.get_all_messages()
        assert len(stored) == 1
        assert stored[0].id == msg.id

    def test_get_message_by_id(self, base_message):
        agent = ReportingAgent()
        msg = base_message
        msg.id = str(uuid4())
        agent.process(msg)
        found = agent.get_message(msg.id)
        assert found is not None
        assert found.id == msg.id

    def test_get_message_not_found(self):
        agent = ReportingAgent()
        assert agent.get_message("nonexistent") is None

    def test_updates_existing_message(self, base_message):
        agent = ReportingAgent()
        msg = base_message
        msg.id = str(uuid4())
        agent.process(msg)
        msg.status = MessageStatus.COMPLETED
        agent.process(msg)
        stored = agent.get_all_messages()
        assert len(stored) == 1
        assert stored[0].status == MessageStatus.COMPLETED

    def test_reset_clears_store(self, base_message):
        agent = ReportingAgent()
        msg = base_message
        msg.id = str(uuid4())
        agent.process(msg)
        assert len(agent.get_all_messages()) == 1
        agent.reset()
        assert len(agent.get_all_messages()) == 0


# ---- ErrorProtocolAgent ----

class TestErrorProtocolAgent:
    def test_creates_task_for_quarantined(self, base_message):
        agent = ErrorProtocolAgent()
        msg = base_message
        msg.status = MessageStatus.QUARANTINED
        msg.error = "High-risk content"
        agent.process(msg)
        tasks = agent.get_error_tasks()
        assert len(tasks) == 1
        assert "quarantined" in tasks[0].title.lower()

    def test_creates_task_for_error(self, base_message):
        agent = ErrorProtocolAgent()
        msg = base_message
        msg.status = MessageStatus.ERROR
        msg.error = "Processing failed"
        agent.process(msg)
        tasks = agent.get_error_tasks()
        assert len(tasks) == 1
        assert "error" in tasks[0].title.lower()

    def test_passes_clean_messages(self, base_message):
        agent = ErrorProtocolAgent()
        agent.process(base_message)
        assert len(agent.get_error_tasks()) == 0

    def test_reset_clears_tasks(self, base_message):
        agent = ErrorProtocolAgent()
        msg = base_message
        msg.status = MessageStatus.QUARANTINED
        msg.error = "test"
        agent.process(msg)
        assert len(agent.get_error_tasks()) == 1
        agent.reset()
        assert len(agent.get_error_tasks()) == 0
