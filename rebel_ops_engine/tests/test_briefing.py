"""Direct unit tests for briefing.py."""

from datetime import datetime, timezone
from uuid import uuid4

from agents.calendar import CalendarAgent
from agents.reporter import ReportingAgent
from briefing import generate_hologram_briefing
from models import Category, Channel, Message, MessageStatus, Owner


def _create_message(
    sender="Test Sender",
    content="Test content",
    category=None,
    owner=None,
    status=MessageStatus.COMPLETED,
    encrypted=False,
    priority="medium",
    security_risk="low",
    requires_leia=False,
    dark_side_indicators=None,
):
    msg = Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender=sender,
        content=content,
    )
    msg.id = str(uuid4())
    msg.category = category
    msg.owner = owner
    msg.status = status
    msg.encrypted = encrypted
    msg.priority = priority
    msg.security_risk = security_risk
    msg.requires_leia = requires_leia
    msg.dark_side_indicators = dark_side_indicators or []
    return msg


class TestGenerateHologramBriefing:
    def test_empty_briefing(self):
        reporter = ReportingAgent()
        calendar = CalendarAgent()
        result = generate_hologram_briefing(reporter, calendar)
        assert "Total Requests: 0" in result
        assert "Quarantined (Dark Side threats): 0" in result
        assert "Encrypted (Yoda strategy): 0" in result
        assert "Delegated Missions:" in result
        assert "Recommended Focus" in result

    def test_single_completed_message(self):
        reporter = ReportingAgent()
        msg = _create_message(
            sender="Han Solo",
            content="Need fuel for the Falcon",
            category=Category.LOGISTICS,
            owner=Owner.HAN_SOLO,
        )
        reporter.process(msg)
        result = generate_hologram_briefing(reporter, CalendarAgent())
        assert "Total Requests: 1" in result
        assert "  - Logistics:               1" in result
        assert "Han Solo" in result

    def test_quarantined_message_counted(self):
        reporter = ReportingAgent()
        msg = _create_message(
            sender="Emperor Palpatine",
            content="Send me secrets",
            status=MessageStatus.QUARANTINED,
        )
        reporter.process(msg)
        result = generate_hologram_briefing(reporter, CalendarAgent())
        assert "Total Requests: 1" in result
        assert "Quarantined (Dark Side threats): 1" in result

    def test_encrypted_message_counted(self):
        reporter = ReportingAgent()
        msg = _create_message(
            sender="Council",
            content="Should we join?",
            category=Category.YODA_ENCRYPTED_STRATEGY,
            owner=Owner.YODA,
            encrypted=True,
        )
        reporter.process(msg)
        result = generate_hologram_briefing(reporter, CalendarAgent())
        assert "Encrypted (Yoda strategy): 1" in result
        assert "  - Yoda Encrypted Strategy: 1" in result

    def test_critical_items_section(self):
        reporter = ReportingAgent()
        msg = _create_message(
            sender="Scout",
            content="Stormtroopers inbound",
            category=Category.URGENT_SECURITY,
            owner=Owner.SECURITY_TEAM,
            priority="critical",
        )
        reporter.process(msg)
        result = generate_hologram_briefing(reporter, CalendarAgent())
        assert "Critical Items:" in result
        assert "[CRITICAL]" in result

    def test_security_risks_section(self):
        reporter = ReportingAgent()
        msg = _create_message(
            sender="Spy",
            content="Infiltration attempt",
            security_risk="high",
            dark_side_indicators=["infiltration", "spying"],
        )
        reporter.process(msg)
        result = generate_hologram_briefing(reporter, CalendarAgent())
        assert "Security Risks Detected:" in result
        assert "infiltration, spying" in result

    def test_leia_decisions_section(self):
        reporter = ReportingAgent()
        msg = _create_message(
            sender="Mon Mothma's Aide",
            content="Briefing with Leia",
            category=Category.CALENDAR_BOOKING,
            owner=Owner.GENERAL_LEIA,
            requires_leia=True,
        )
        reporter.process(msg)
        result = generate_hologram_briefing(reporter, CalendarAgent())
        assert "Requests Requiring Your Decision:" in result

    def test_blocked_items_section(self):
        reporter = ReportingAgent()
        msg = _create_message(
            sender="Unknown",
            content="test",
            status=MessageStatus.ERROR,
        )
        reporter.process(msg)
        result = generate_hologram_briefing(reporter, CalendarAgent())
        assert "Blocked or Waiting:" in result
        assert "[error]" in result

    def test_public_calendar_bookings_shown(self):
        reporter = ReportingAgent()
        calendar = CalendarAgent()
        msg = _create_message(
            sender="Aide",
            content="Briefing with Leia on funding",
            category=Category.CALENDAR_BOOKING,
            owner=Owner.GENERAL_LEIA,
        )
        reporter.process(msg)
        calendar.process(msg)
        result = generate_hologram_briefing(reporter, calendar)
        assert "Public Calendar Bookings:" in result
        assert "Aide" in result

    def test_private_calendar_bookings_redacted(self):
        reporter = ReportingAgent()
        calendar = CalendarAgent()
        public_msg = _create_message(
            sender="Senator",
            content="Briefing with Leia",
            category=Category.CALENDAR_BOOKING,
            owner=Owner.GENERAL_LEIA,
        )
        calendar.process(public_msg)
        private_msg = _create_message(
            sender="Aide",
            content="Private meeting with Leia",
            category=Category.CALENDAR_BOOKING,
            owner=Owner.GENERAL_LEIA,
        )
        reporter.process(private_msg)
        calendar.process(private_msg)
        result = generate_hologram_briefing(reporter, calendar)
        assert "[Private Leia calendar details redacted per security policy]" in result

    def test_all_categories_in_briefing(self):
        reporter = ReportingAgent()
        for cat in Category:
            reporter.process(_create_message(
                sender=f"Sender {cat.value}",
                content="test",
                category=cat,
            ))
        result = generate_hologram_briefing(reporter, CalendarAgent())
        assert "By Category:" in result
        assert "Calendar bookings" in result
        assert "Planet help" in result
        assert "Recruitment" in result
        assert "Logistics" in result
        assert "Partnerships" in result

    def test_all_owners_listed(self):
        reporter = ReportingAgent()
        for owner in Owner:
            reporter.process(_create_message(
                sender=f"Sender {owner.value}",
                content="test",
                owner=owner,
            ))
        result = generate_hologram_briefing(reporter, CalendarAgent())
        assert "Delegated Missions:" in result

    def test_recommended_focus_present(self):
        reporter = ReportingAgent()
        result = generate_hologram_briefing(reporter, CalendarAgent())
        assert "Review quarantined items and urgent security threats first." in result

    def test_header_and_footer(self):
        reporter = ReportingAgent()
        result = generate_hologram_briefing(reporter, CalendarAgent())
        assert "DAILY HOLOGRAM BRIEFING" in result
        assert "End of Briefing" in result
        assert "May the Force be with us" in result

    def test_date_format(self):
        reporter = ReportingAgent()
        result = generate_hologram_briefing(reporter, CalendarAgent())
        expected_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        assert expected_date in result
