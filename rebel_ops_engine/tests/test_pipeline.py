"""Tests for pipeline orchestration — error handling, status transitions, and agent ordering."""

from unittest import mock

import pytest

from main import PIPELINE, app, calendar, encryption, error_handler, intake, reporter, router, run_pipeline
from models import Channel, Message, MessageStatus, Owner


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        reporter.reset()
        calendar.reset()
        router.reset()
        encryption.reset()
        error_handler.reset()
        yield c


@pytest.fixture
def base_message():
    return Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Test Sender",
        content="This is a test message.",
    )


class TestPipelineOrder:
    def test_pipeline_has_nine_agents(self):
        assert len(PIPELINE) == 9

    def test_pipeline_agent_names(self):
        names = [a.name for a in PIPELINE]
        expected = [
            "IntakeAgent",
            "DarkSideSecurityAgent",
            "C3POClassifierAgent",
            "RoutingAgent",
            "YodaEncryptionAgent",
            "CalendarAgent",
            "NotificationAgent",
            "ReportingAgent",
            "ErrorProtocolAgent",
        ]
        assert names == expected


class TestPipelineFailure:
    def test_mid_pipeline_agent_failure(self, client):
        orig = intake.process
        intake.process = mock.Mock(side_effect=RuntimeError("intake crash"))
        try:
            resp = client.post("/api/intake", json={
                "channel": "intergalactic_whatsapp",
                "sender": "Test User",
                "content": "This will crash intake",
            })
            data = resp.get_json()
            assert resp.status_code == 400
            assert data["status"] == "error"
            assert "intake crash" in data["error"]
        finally:
            intake.process = orig

    def test_last_agent_failure(self, client):
        orig = reporter.process
        reporter.process = mock.Mock(side_effect=RuntimeError("reporter crash"))
        try:
            resp = client.post("/api/intake", json={
                "channel": "intergalactic_whatsapp",
                "sender": "Test User",
                "content": "This will crash the reporter",
            })
            data = resp.get_json()
            assert data["status"] == "error"
            assert "reporter crash" in data["error"]
        finally:
            reporter.process = orig

    def test_pipeline_stops_on_error_from_agent(self):
        with mock.patch.object(intake, "process") as mock_process:
            error_msg = Message(
                channel=Channel.INTERGALACTIC_WHATSAPP,
                sender="Test",
                content="Test",
                status=MessageStatus.ERROR,
            )
            mock_process.return_value = error_msg

            msg = Message(
                channel=Channel.INTERGALACTIC_WHATSAPP,
                sender="Test",
                content="Test",
            )
            result = run_pipeline(msg)
            assert result.status == MessageStatus.ERROR


class TestPipelineFlags:
    def test_flagged_status_routes_to_security_team(self):
        msg = Message(
            channel=Channel.INTERGALACTIC_WHATSAPP,
            sender="Test",
            content="Test",
        )
        msg.status = MessageStatus.FLAGGED
        result = run_pipeline(msg)
        assert result.status == MessageStatus.FLAGGED
        assert result.owner == Owner.SECURITY_TEAM
        assert result.assigned_team == "Security Team"


class TestPipelineSuccess:
    def test_successful_pipeline_creates_task(self, client):
        client.post("/api/intake", json={
            "channel": "intergalactic_whatsapp",
            "sender": "Davin Felth",
            "content": "I want to join the Rebellion as a pilot.",
        })
        resp = client.get("/tasks")
        tasks = resp.get_json()["data"]
        assert len(tasks) >= 1
        assert any("Recruitment" in t["assigned_team"] for t in tasks)

    def test_completed_message_has_trace(self, client):
        resp = client.post("/api/intake", json={
            "channel": "intergalactic_whatsapp",
            "sender": "Test User",
            "content": "Need supplies on Endor.",
        })
        data = resp.get_json()
        assert data["status"] == "completed"
        assert len(data["trace"]) == 9
        agent_names = [t["agent"] for t in data["trace"]]
        assert agent_names == [
            "IntakeAgent", "DarkSideSecurityAgent", "C3POClassifierAgent",
            "RoutingAgent", "YodaEncryptionAgent", "CalendarAgent",
            "NotificationAgent", "ReportingAgent", "ErrorProtocolAgent",
        ]
