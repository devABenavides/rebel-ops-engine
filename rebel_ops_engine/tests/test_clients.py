"""Tests for integration client interfaces in clients.py.

All tests mock the underlying integration modules to avoid network calls.
"""

from unittest import mock

import pytest

from clients import (
    CalendarClient,
    HologramEmailClient,
    NotificationClient,
    ReportDeliveryClient,
    WhatsAppClient,
    _briefing_html,
    _html_escape,
)


@pytest.fixture(autouse=True)
def mock_integrations():
    """Mock all integration modules to prevent any real API calls."""
    patchers = [
        mock.patch("clients.wa"),
        mock.patch("clients.gmail"),
        mock.patch("clients.cal"),
    ]
    mocks = [p.start() for p in patchers]
    yield mocks
    for p in patchers:
        p.stop()


class TestWhatsAppClient:
    def test_send_message(self, mock_integrations):
        mock_wa = mock_integrations[0]
        mock_wa.send_message.return_value = {"status": "mocked", "channel": "whatsapp", "to": "15551234567"}

        client = WhatsAppClient()
        result = client.send_message("15551234567", "Hello from the Rebellion!")

        mock_wa.send_message.assert_called_once_with("15551234567", "Hello from the Rebellion!")
        assert result["status"] == "mocked"

    def test_send_message_empty_body(self, mock_integrations):
        mock_wa = mock_integrations[0]

        client = WhatsAppClient()
        client.send_message("15551234567", "")

        mock_wa.send_message.assert_called_once_with("15551234567", "")


class TestHologramEmailClient:
    def test_send_email(self, mock_integrations):
        mock_gmail = mock_integrations[1]
        mock_gmail.send_email.return_value = {"status": "mocked"}

        client = HologramEmailClient()
        result = client.send_email("test@rebel.com", "Subject", "Body text")

        mock_gmail.send_email.assert_called_once_with("test@rebel.com", "Subject", "Body text")
        assert result["status"] == "mocked"

    def test_send_email_no_subject(self, mock_integrations):
        mock_gmail = mock_integrations[1]

        client = HologramEmailClient()
        client.send_email("test@rebel.com", "", "Body text")

        mock_gmail.send_email.assert_called_once_with("test@rebel.com", "", "Body text")


class TestCalendarClient:
    def test_check_availability(self, mock_integrations):
        mock_cal = mock_integrations[2]
        mock_cal.check_availability.return_value = [{"start": "10:00"}, {"start": "11:00"}]

        client = CalendarClient()
        slots = client.check_availability("2025-06-01")

        mock_cal.check_availability.assert_called_once_with("2025-06-01")
        assert slots == ["10:00", "11:00"]

    def test_check_availability_no_date(self, mock_integrations):
        mock_cal = mock_integrations[2]
        mock_cal.check_availability.return_value = []

        client = CalendarClient()
        slots = client.check_availability()
        assert slots == []

    def test_create_event(self, mock_integrations):
        mock_cal = mock_integrations[2]
        mock_cal.create_event.return_value = {"status": "mocked", "event_id": "evt_123"}

        client = CalendarClient()
        result = client.create_event("Meeting", "2025-06-01", "10:00")

        mock_cal.create_event.assert_called_once_with("Meeting", "2025-06-01", "10:00", "", None)
        assert result["event_id"] == "evt_123"

    def test_find_available_slots(self, mock_integrations):
        mock_cal = mock_integrations[2]
        mock_cal.find_available_slots.return_value = ["10:00", "11:00", "14:00"]

        client = CalendarClient()
        slots = client.find_available_slots("2025-06-01", 30, 3)

        mock_cal.find_available_slots.assert_called_once_with("2025-06-01", 30, 3)
        assert slots == ["10:00", "11:00", "14:00"]


class TestNotificationClient:
    def test_notify(self):
        client = NotificationClient()
        result = client.notify("recipient@rebel.com", "Your mission briefing is ready")

        assert result["status"] == "notified"
        assert result["recipient"] == "recipient@rebel.com"

    def test_notify_empty_message(self):
        client = NotificationClient()
        result = client.notify("recipient@rebel.com", "")

        assert result["status"] == "notified"


class TestReportDeliveryClient:
    def test_deliver_report(self, mock_integrations):
        mock_gmail = mock_integrations[1]
        mock_gmail.send_email.return_value = {"status": "mocked"}

        report = "DAILY HOLOGRAM BRIEFING\n2025-05-26\nGeneral Leia\nTotal Requests: 10"
        client = ReportDeliveryClient()
        result = client.deliver_report(report)

        mock_gmail.send_email.assert_called_once()
        args, _ = mock_gmail.send_email.call_args
        to, subject = args[0], args[1]
        assert subject.startswith("Daily Hologram Briefing")
        assert to == "alexandra.benavides@paretotalent.com"
        assert result["status"] == "mocked"

    def test_deliver_report_no_date(self, mock_integrations):
        mock_gmail = mock_integrations[1]
        mock_gmail.send_email.return_value = {"status": "mocked"}

        report = "DAILY HOLOGRAM BRIEFING\nGeneral Leia\nTotal Requests: 5"
        client = ReportDeliveryClient()
        client.deliver_report(report)

        args, _ = mock_gmail.send_email.call_args
        subject = args[1]
        assert subject == "Daily Hologram Briefing"

    def test_deliver_report_custom_recipient(self, mock_integrations):
        mock_gmail = mock_integrations[1]

        report = "DAILY HOLOGRAM BRIEFING\n2025-05-26\nTest"
        client = ReportDeliveryClient()
        client.deliver_report(report, recipient="custom@rebel.com")

        args, _ = mock_gmail.send_email.call_args
        to = args[0]
        assert to == "custom@rebel.com"


class TestBriefingHtml:
    def test_generates_valid_html(self):
        text = "DAILY HOLOGRAM BRIEFING\n2025-05-26\nGeneral Leia\nTotal Requests: 10"
        html = _briefing_html(text)
        assert "<!DOCTYPE html>" in html
        assert "DAILY HOLOGRAM BRIEFING" in html
        assert "General Leia" in html
        assert "May the Force be with you" in html

    def test_security_risk_lines_rendered(self):
        text = "DAILY HOLOGRAM BRIEFING\n  Risk: high | Sith detected"
        html = _briefing_html(text)
        assert "Risk: high | Sith detected" in html

    def test_bracketed_items_rendered(self):
        text = "DAILY HOLOGRAM BRIEFING\n  [quarantined] Palpatine blocked"
        html = _briefing_html(text)
        assert "[quarantined] Palpatine blocked" in html

    def test_section_headers(self):
        text = (
            "DAILY HOLOGRAM BRIEFING\n"
            "By Category:\n"
            "Delegated Missions:\n"
            "Critical Items:\n"
            "Security Risks Detected:\n"
            "Recommended Focus for Tomorrow:\n"
            "End of Briefing"
        )
        html = _briefing_html(text)
        assert "By Category" in html
        assert "Delegated Missions" in html
        assert "Critical Items" in html
        assert "Security Risks Detected" in html
        assert "Recommended Focus for Tomorrow" in html
        assert "End of Briefing" in html

    def test_stat_row_colors(self):
        text = "DAILY HOLOGRAM BRIEFING\nTotal Requests: 10\nQuarantined: 2\nEncrypted: 1"
        html = _briefing_html(text)
        assert "Total Requests:" in html
        assert "Quarantined" in html
        assert "Encrypted" in html

    def test_line_items(self):
        text = "DAILY HOLOGRAM BRIEFING\n  - Item one\n  - Item two\n  [Private Leia meeting at 1400]"
        html = _briefing_html(text)
        assert "Item one" in html
        assert "Private Leia" in html

    def test_empty_text(self):
        html = _briefing_html("")
        assert "<!DOCTYPE html>" in html

    def test_html_special_chars_escaped(self):
        text = "DAILY HOLOGRAM BRIEFING\nMalicious <script>alert('xss')</script>"
        html = _briefing_html(text)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


class TestHtmlEscape:
    def test_escapes_ampersand(self):
        assert _html_escape("A & B") == "A &amp; B"

    def test_escapes_lt(self):
        assert _html_escape("<tag>") == "&lt;tag&gt;"

    def test_escapes_gt(self):
        assert _html_escape("a > b") == "a &gt; b"

    def test_escapes_all(self):
        assert _html_escape("<a & b>") == "&lt;a &amp; b&gt;"

    def test_no_special_chars(self):
        assert _html_escape("simple text") == "simple text"

    def test_empty_string(self):
        assert _html_escape("") == ""
