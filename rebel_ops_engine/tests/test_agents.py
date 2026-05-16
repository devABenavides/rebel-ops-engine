"""Isolated unit tests for individual agents."""

from uuid import uuid4

import pytest

from agents.calendar import CalendarAgent, _extract_date, _extract_time
from agents.classifier import C3POClassifierAgent
from agents.encryption import YodaEncryptionAgent
from agents.error_handler import ErrorProtocolAgent
from agents.intake import IntakeAgent
from agents.notifier import (
    NotificationAgent,
    _ahsoka_template,
    _bb8_alert,
    _din_template,
    _hologram_template,
    _luke_template,
    _quarantine_template,
    _yoda_template,
)
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

    def test_security_review_threshold(self):
        agent = DarkSideSecurityAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Scout Leader", content="infiltration attempt detected")
        result = agent.process(msg)
        assert result.status == MessageStatus.SECURITY_REVIEW
        assert result.security_risk == "medium"
        assert result.risk_score == 25
        assert "infiltration" in result.dark_side_indicators


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

    def test_soldier_support_classification(self):
        agent = C3POClassifierAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Trooper", content="soldier needs medical aid")
        result = agent.process(msg)
        assert result.category == Category.SOLDIER_SUPPORT

    def test_jedi_case_type_fallback(self):
        agent = C3POClassifierAgent()
        msg = Message(channel=Channel.HOLOGRAM_EMAIL, sender="Jedi Council", content="We need guidance for the young")
        result = agent.process(msg)
        assert result.category == Category.JEDI_TRAINING_DIPLOMACY
        assert result.requires_jedi is True
        assert result.jedi_case_type == "none"


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

    def test_security_review_hold(self):
        agent = RoutingAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Test", content="test")
        msg.category = Category.OTHER
        msg.status = MessageStatus.SECURITY_REVIEW
        result = agent.process(msg)
        assert len(agent.get_tasks()) == 0
        assert any(t["action"] == "held" for t in result.trace)

    def test_clickup_sync(self):
        agent = RoutingAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Test", content="test")
        msg.category = Category.LOGISTICS
        agent.process(msg)
        import time
        time.sleep(0.5)
        results = agent.get_clickup_results()
        assert len(results) == 1
        task_id = list(results.keys())[0]
        assert results[task_id]["status"] in ("mocked", "initiated")


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

    def test_extract_date_found(self):
        assert _extract_date("Let's meet next Tuesday") != "unknown"
        assert _extract_date("Schedule for tomorrow") != "unknown"
        assert _extract_date("Event on 2024-05-15") != "unknown"

    def test_extract_date_not_found(self):
        assert _extract_date("No date mentioned here") == "unknown"

    def test_extract_time_found(self):
        assert _extract_time("Meet at 14:00") != "unknown"
        assert _extract_time("At 3pm we start") != "unknown"

    def test_extract_time_not_found(self):
        assert _extract_time("No time mentioned here") == "unknown"


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

    def test_clickup_sync(self):
        agent = ErrorProtocolAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Test", content="test")
        msg.status = MessageStatus.QUARANTINED
        msg.error = "test"
        agent.process(msg)
        import time
        time.sleep(0.5)
        results = agent.get_clickup_results()
        assert len(results) == 1
        task_id = list(results.keys())[0]
        assert results[task_id]["status"] in ("mocked", "initiated")


# ---- NotificationAgent ----

class TestNotificationAgent:
    def test_name(self):
        agent = NotificationAgent()
        assert agent.name == "NotificationAgent"

    def test_hologram_template(self):
        result = _hologram_template("logistics", "Han Solo", "routed", "Deliver supplies")
        assert "Hologram Transmission Received" in result
        assert "logistics" in result
        assert "Han Solo" in result
        assert "Deliver supplies" in result

    def test_quarantine_template(self):
        result = _quarantine_template("Darth Vader", ["infiltration", "spying"])
        assert "SECURITY ALERT" in result
        assert "Darth Vader" in result
        assert "infiltration, spying" in result
        assert "quarantined" in result

    def test_bb8_alert(self):
        result = _bb8_alert("Stormtroopers inbound", "critical")
        assert "BB-8 ALERT" in result
        assert "Stormtroopers inbound" in result
        assert "critical" in result

    def test_ahsoka_template(self):
        result = _ahsoka_template("Suspicious contact", "high", "low", True, "Review dossier")
        assert "SPECIAL MISSION REVIEW" in result
        assert "Ahsoka Tano" in result
        assert "Suspicious contact" in result
        assert "high" in result
        assert "Leia Required: Yes" in result

    def test_din_template(self):
        result = _din_template("Extract informant", "high", False)
        assert "DIN DJARIN PROTECTION PROTOCOL ACTIVATED" in result
        assert "Extract informant" in result
        assert "Leia Visibility: No" in result

    def test_luke_template(self):
        result = _luke_template("Mediation on Bothawui", "mediation", "high", "Send Luke")
        assert "JEDI TRAINING & DIPLOMACY ASSIGNMENT" in result
        assert "Luke Skywalker + Ben Kenobi" in result
        assert "mediation" in result
        assert "Send Luke" in result

    def test_yoda_template(self):
        result = _yoda_template("Should we join openly?", "low", "Encrypt and transmit")
        assert "ENCRYPTED JEDI TRANSMISSION" in result
        assert "Master Yoda" in result
        assert "Should we join openly?" in result
        assert "Encrypt and transmit" in result

    def test_process_quarantined(self, base_message):
        agent = NotificationAgent()
        msg = base_message
        msg.status = MessageStatus.QUARANTINED
        msg.dark_side_indicators = ["infiltration"]
        msg.error = "High-risk content"
        result = agent.process(msg)
        assert "NotificationAgent" in result.processed_by
        traces = [t for t in result.trace if t["agent"] == "NotificationAgent"]
        assert len(traces) == 1

    def test_process_error(self, base_message):
        agent = NotificationAgent()
        msg = base_message
        msg.status = MessageStatus.ERROR
        result = agent.process(msg)
        assert "NotificationAgent" in result.processed_by

    def test_process_whatsapp_channel(self):
        agent = NotificationAgent()
        msg = Message(
            channel=Channel.INTERGALACTIC_WHATSAPP,
            sender="Test User",
            content="Need supplies",
        )
        msg.category = Category.LOGISTICS
        msg.owner = Owner.HAN_SOLO
        msg.status = MessageStatus.ROUTED
        msg.summary = "Need supplies for the mission"
        msg.suggested_next_action = "Coordinate delivery"
        result = agent.process(msg)
        assert "NotificationAgent" in result.processed_by

    def test_process_email_channel(self):
        agent = NotificationAgent()
        msg = Message(
            channel=Channel.HOLOGRAM_EMAIL,
            sender="test@rebel.com",
            content="Need supplies",
        )
        msg.category = Category.LOGISTICS
        msg.owner = Owner.HAN_SOLO
        msg.status = MessageStatus.ROUTED
        msg.summary = "Need supplies"
        msg.suggested_next_action = "Coordinate delivery"
        result = agent.process(msg)
        assert "NotificationAgent" in result.processed_by

    def test_process_urgent_security(self):
        agent = NotificationAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Scout", content="Stormtroopers spotted")
        msg.category = Category.URGENT_SECURITY
        msg.owner = Owner.SECURITY_TEAM
        msg.status = MessageStatus.ROUTED
        msg.summary = "Stormtroopers spotted near base"
        msg.priority = "high"
        result = agent.process(msg)
        assert "NotificationAgent" in result.processed_by

    def test_process_ahsoka_mission(self):
        agent = NotificationAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Fulcrum", content="Suspicious contact")
        msg.category = Category.AHSOKA_SPECIAL_MISSION
        msg.owner = Owner.AHSOKA_TANO
        msg.status = MessageStatus.ROUTED
        msg.summary = "Suspicious contact needs review"
        msg.priority = "medium"
        msg.security_risk = "low"
        msg.requires_leia = True
        result = agent.process(msg)
        assert "NotificationAgent" in result.processed_by

    def test_process_special_protection(self):
        agent = NotificationAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Intel", content="Informant needs extraction")
        msg.category = Category.SPECIAL_PROTECTION
        msg.owner = Owner.DIN_DJARIN
        msg.status = MessageStatus.ROUTED
        msg.summary = "Informant extraction required"
        msg.priority = "high"
        result = agent.process(msg)
        assert "NotificationAgent" in result.processed_by

    def test_process_jedi_training(self):
        agent = NotificationAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Council", content="Mediation needed")
        msg.category = Category.JEDI_TRAINING_DIPLOMACY
        msg.owner = Owner.LUKE_BEN
        msg.status = MessageStatus.ROUTED
        msg.summary = "Mediation between two systems"
        msg.priority = "medium"
        msg.jedi_case_type = "mediation"
        result = agent.process(msg)
        assert "NotificationAgent" in result.processed_by

    def test_process_yoda_strategy(self):
        agent = NotificationAgent()
        msg = Message(channel=Channel.INTERGALACTIC_WHATSAPP, sender="Council", content="Should we join?")
        msg.category = Category.YODA_ENCRYPTED_STRATEGY
        msg.owner = Owner.YODA
        msg.status = MessageStatus.ROUTED
        msg.summary = "Strategic question about joining"
        msg.security_risk = "low"
        result = agent.process(msg)
        assert "NotificationAgent" in result.processed_by
