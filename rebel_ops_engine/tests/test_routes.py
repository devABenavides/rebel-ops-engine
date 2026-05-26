"""Route contract tests — error paths, edge cases, and auth not covered in test_engine.py."""

from unittest import mock

import pytest

from main import app, calendar, encryption, error_handler, reporter, router


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


class TestWhatsAppEndpoint:
    def test_wrong_content_type(self, client):
        resp = client.post("/requests/whatsapp", data="not json", content_type="text/plain")
        assert resp.status_code == 415
        assert resp.get_json()["error"] == "Content-Type must be application/json"

    def test_empty_json_body(self, client):
        resp = client.post("/requests/whatsapp", json={})
        assert resp.status_code == 400

    def test_invalid_json_body(self, client):
        resp = client.post("/requests/whatsapp", data="not valid json", content_type="application/json")
        assert resp.status_code == 400


class TestHologramEmailEndpoint:
    def test_wrong_content_type(self, client):
        resp = client.post("/requests/hologram-email", data="not json", content_type="text/plain")
        assert resp.status_code == 415
        assert resp.get_json()["error"] == "Content-Type must be application/json"

    def test_empty_json_body(self, client):
        resp = client.post("/requests/hologram-email", json={})
        assert resp.status_code == 400

    def test_invalid_json_body(self, client):
        resp = client.post("/requests/hologram-email", data="not valid json", content_type="application/json")
        assert resp.status_code == 400


class TestIntakeEndpoint:
    def test_empty_json_body(self, client):
        resp = client.post("/api/intake", json={})
        assert resp.status_code == 400

    def test_invalid_json_body(self, client):
        resp = client.post("/api/intake", data="not valid json", content_type="application/json")
        assert resp.status_code == 400


class TestPagination:
    def test_messages_pagination_defaults(self, client):
        for i in range(5):
            client.post("/api/intake", json={"channel": "intergalactic_whatsapp", "sender": f"User{i}", "content": f"Message {i}"})
        resp = client.get("/api/messages")
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["page"] == 1
        assert data["limit"] == 100
        assert data["total"] == 5
        assert data["total_pages"] == 1

    def test_messages_pagination_custom_page(self, client):
        for i in range(10):
            client.post("/api/intake", json={"channel": "intergalactic_whatsapp", "sender": f"User{i}", "content": f"Message {i}"})
        resp = client.get("/api/messages?page=1&limit=3")
        data = resp.get_json()
        assert resp.status_code == 200
        assert len(data["data"]) == 3
        assert data["page"] == 1
        assert data["limit"] == 3
        assert data["total"] == 10
        assert data["total_pages"] == 4

    def test_messages_pagination_out_of_range(self, client):
        for i in range(3):
            client.post("/api/intake", json={"channel": "intergalactic_whatsapp", "sender": f"User{i}", "content": f"Message {i}"})
        resp = client.get("/api/messages?page=999")
        data = resp.get_json()
        assert resp.status_code == 200
        assert len(data["data"]) == 0

    def test_tasks_pagination(self, client):
        client.post("/api/demo/load")
        resp = client.get("/tasks")
        data = resp.get_json()
        assert resp.status_code == 200
        assert "page" in data
        assert "limit" in data
        assert "total" in data
        assert "total_pages" in data

    def test_calendar_pagination(self, client):
        client.post("/api/demo/load")
        resp = client.get("/api/calendar")
        data = resp.get_json()
        assert resp.status_code == 200
        assert "page" in data
        assert "limit" in data


class TestWebhookAuth:
    def test_whatsapp_requires_auth_when_secret_set(self, client):
        with mock.patch("main._WEBHOOK_SECRET", "s3cr3t"):
            resp = client.post("/webhooks/whatsapp", json={"entry": [{"changes": [{"value": {"messages": [{"from": "123", "text": {"body": "hi"}}]}}]}]})
            assert resp.status_code == 401
            assert resp.get_json()["error"] == "unauthorized"

    def test_whatsapp_auth_with_correct_secret(self, client):
        with mock.patch("main._WEBHOOK_SECRET", "s3cr3t"):
            resp = client.post("/webhooks/whatsapp", json={"entry": [{"changes": [{"value": {"messages": [{"from": "123", "text": {"body": "hi"}}]}}]}]},
                               headers={"X-Webhook-Secret": "s3cr3t"})
            assert resp.status_code == 200

    def test_gmail_requires_auth_when_secret_set(self, client):
        with mock.patch("main._WEBHOOK_SECRET", "s3cr3t"):
            resp = client.post("/webhooks/gmail", json={"message": {"data": "test"}})
            assert resp.status_code == 401
            assert resp.get_json()["error"] == "unauthorized"

    def test_clickup_requires_auth_when_secret_set(self, client):
        with mock.patch("main._WEBHOOK_SECRET", "s3cr3t"):
            resp = client.post("/webhooks/clickup", json={"event": "test"})
            assert resp.status_code == 401
            assert resp.get_json()["error"] == "unauthorized"


class TestWebhookIdempotency:
    def test_whatsapp_duplicate_message_id(self, client):
        import main as main_module
        main_module._processed_webhook_ids.clear()

        msg_id = "dup-msg-123"
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": msg_id,
                            "from": "15551234567",
                            "text": {"body": "First message"},
                        }],
                    },
                }],
            }],
        }
        resp1 = client.post("/webhooks/whatsapp", json=payload)
        assert resp1.status_code == 200
        assert resp1.get_json() == {"status": "ok"}

        resp2 = client.post("/webhooks/whatsapp", json=payload)
        assert resp2.status_code == 200
        assert resp2.get_json()["duplicate"] is True

        msgs_resp = client.get("/api/messages")
        msgs = msgs_resp.get_json()["data"]
        related = [m for m in msgs if "15551234567" in m["sender"]]
        assert len(related) == 1


class TestAgentsEndpoint:
    def test_agents_list_structure(self, client):
        resp = client.get("/api/agents")
        data = resp.get_json()
        assert resp.status_code == 200
        assert len(data["data"]) == 9
        for agent in data["data"]:
            assert "name" in agent
            assert "description" in agent
        assert data["page"] == 1
        assert data["total"] == 9

    def test_agents_list_names(self, client):
        resp = client.get("/api/agents")
        names = [a["name"] for a in resp.get_json()["data"]]
        expected = [
            "IntakeAgent", "DarkSideSecurityAgent", "C3POClassifierAgent",
            "RoutingAgent", "YodaEncryptionAgent", "CalendarAgent",
            "NotificationAgent", "ReportingAgent", "ErrorProtocolAgent",
        ]
        assert names == expected


class TestReset:
    def test_reset_multiple_times(self, client):
        client.post("/api/demo/load")
        resp1 = client.post("/api/reset")
        assert resp1.status_code == 200
        assert resp1.get_json() == {"status": "reset"}

        resp2 = client.post("/api/reset")
        assert resp2.status_code == 200
        assert resp2.get_json() == {"status": "reset"}

    def test_reset_then_load_again(self, client):
        client.post("/api/demo/load")
        client.post("/api/reset")
        resp = client.post("/api/demo/load")
        assert resp.status_code == 200
        assert resp.get_json()["loaded"] == 16


class TestFrontendStaticFiles:
    def test_frontend_index_served(self, client):
        resp = client.get("/index.html")
        assert resp.status_code == 200
        assert resp.content_type and "text/html" in resp.content_type


class TestIntegrationsEndpoint:
    def test_integrations_all_boolean(self, client):
        resp = client.get("/api/integrations")
        data = resp.get_json()
        assert resp.status_code == 200
        for key in ("gmail", "calendar", "clickup", "whatsapp", "discord"):
            assert isinstance(data[key], bool)


class TestBriefingInboxCounts:
    def test_briefing_inbox_counts_after_demo(self, client):
        client.post("/api/demo/load")
        resp = client.get("/api/briefing/inbox")
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["total_messages"] == 16
        assert data["completed"] + data["quarantined"] + data["encrypted"] > 0
        assert isinstance(data["delegation"], dict)
        assert len(data["delegation"]) > 0


class TestCalendarConfirmEdgeCases:
    def test_calendar_confirm_already_confirmed(self, client):
        resp = client.post("/api/intake", json={
            "channel": "hologram_email",
            "sender": "Mon Mothma's Aide",
            "content": "Briefing with General Leia next Thursday at 10:00 about supplies.",
        })
        data = resp.get_json()
        assert data["status"] == "awaiting_confirmation"
        msg_id = data["id"]

        client.get(f"/api/calendar/confirm/{msg_id}/0")
        confirm2 = client.get(f"/api/calendar/confirm/{msg_id}/0")
        assert confirm2.status_code == 400
        assert confirm2.get_json()["error"] == "This booking has already been confirmed"
