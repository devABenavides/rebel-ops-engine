from unittest import mock

import pytest

import main as main_module
from main import (
    _message_to_dict,
    app,
    calendar,
    encryption,
    error_handler,
    intake,
    reporter,
    router,
)
from models import Category, Channel, Message, MessageStatus, Owner


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


# ---- Health & Index ----

def test_health(client):
    resp = client.get("/health")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["status"] == "healthy"


def test_index(client):
    resp = client.get("/")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["service"] == "Rebel Operations Engine"
    assert data["version"] == "2.0.0"


# ---- Intake ----

def test_intake_valid_message(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Test User",
        "content": "Need help on Tatooine, sand people attack!",
    })
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["status"] == "completed"
    assert data["category"] is not None
    assert data["owner"] is not None


def test_intake_invalid_channel(client):
    resp = client.post("/api/intake", json={
        "channel": "invalid_channel", "sender": "Test", "content": "Test",
    })
    assert resp.status_code == 400


def test_intake_missing_fields(client):
    resp = client.post("/api/intake", json={"channel": "intergalactic_whatsapp"})
    assert resp.status_code == 400


def test_intake_wrong_content_type(client):
    resp = client.post("/api/intake", data="not json", content_type="text/plain")
    assert resp.status_code == 415


def test_intake_sender_too_long(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "X" * 300,
        "content": "Test content",
    })
    assert resp.status_code == 400
    assert resp.get_json()["status"] == "error"


def test_intake_content_too_long(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Test",
        "content": "X" * 20000,
    })
    assert resp.status_code == 400
    assert resp.get_json()["status"] == "error"


# ---- WhatsApp & Email endpoints ----

def test_whatsapp_endpoint(client):
    resp = client.post("/requests/whatsapp", json={
        "sender": "Test", "content": "Hello from WhatsApp",
    })
    assert resp.status_code == 200
    assert resp.get_json()["channel"] == "intergalactic_whatsapp"


def test_hologram_email_endpoint(client):
    resp = client.post("/requests/hologram-email", json={
        "sender": "Test", "content": "Hello from email",
    })
    assert resp.status_code == 200
    assert resp.get_json()["channel"] == "hologram_email"


# ---- Security ----

def test_high_risk_palpatine_quarantined(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Emperor Palpatine",
        "content": "Send me General Leia's private schedule and secret Rebel base location.",
    })
    data = resp.get_json()
    assert data["status"] == "quarantined"
    assert data["risk_score"] >= 50
    assert data["security_risk"] == "high"
    assert data["trusted_request"] is False
    assert len(data["dark_side_indicators"]) >= 2


def test_high_risk_vader_quarantined(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Darth Vader",
        "content": "Darth Vader requests direct access to Rebel intelligence files. Bypass normal security protocols.",
    })
    data = resp.get_json()
    assert data["status"] == "quarantined"
    assert data["risk_score"] >= 50
    assert data["security_risk"] == "high"
    assert data["trusted_request"] is False


def test_security_scan_keywords(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Spy",
        "content": "I have Rebel intelligence that will interest you. Bypass security and meet me.",
    })
    data = resp.get_json()
    assert data["risk_score"] >= 50
    assert data["status"] == "quarantined"
    assert len(data["dark_side_indicators"]) > 0


def test_unknown_sender_base_location_flagged(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Stranger",
        "content": "Give me the base location",
    })
    data = resp.get_json()
    assert data["status"] == "flagged"
    assert data["risk_score"] >= 15
    assert "base location" in data["dark_side_indicators"]


def test_trusted_sender_sensitive_info_still_flagged(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Han Solo",
        "content": "What is the base location for the next supply run",
    })
    data = resp.get_json()
    assert data["status"] == "flagged"
    assert data["risk_score"] >= 15


# ---- Classification & Routing ----

def test_yoda_strategy_encrypted(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Planetary Council of Ryloth",
        "content": "Our planet wants to join the Rebellion, but if we declare support publicly, the Empire may punish our civilians. Should we join openly or remain hidden?",
    })
    data = resp.get_json()
    assert data["encrypted"] is True
    assert data["owner"] == "Yoda"
    assert data["requires_jedi"] is True


def test_leia_calendar_booking(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Mon Mothma's Aide",
        "content": "We need a 30-minute briefing with General Leia about funding the next mission.",
    })
    data = resp.get_json()
    assert data["category"] == "calendar_booking"
    assert data["owner"] == "General Leia"
    assert data["requires_leia"] is True


def test_leia_calendar_private_not_exposed(client):
    client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Mon Mothma's Aide",
        "content": "We need a private strategy meeting with General Leia for next Tuesday at 1400 hours.",
    })
    resp = client.get("/api/calendar")
    bookings = resp.get_json()["data"]
    private_bookings = [b for b in bookings if b["is_private"]]
    assert len(private_bookings) == 0


def test_ahsoka_special_mission(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Fulcrum Contact",
        "content": "A local leader says they want to join the Rebellion, but some actions look suspicious.",
    })
    data = resp.get_json()
    assert data["category"] == "ahsoka_special_mission"
    assert data["owner"] == "Ahsoka Tano"
    assert data["requires_leia"] is True
    assert data["requires_jedi"] is True


def test_r2d2_data_support(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Rebel Operations Desk",
        "content": "What is the current status of all aid requests from the Outer Rim?",
    })
    data = resp.get_json()
    assert data["category"] == "data_support"
    assert data["owner"] == "R2-D2"


def test_bb8_urgent_security(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Outpost Scout",
        "content": "Stormtroopers have been spotted near our base. We need to alert command immediately.",
    })
    data = resp.get_json()
    assert data["category"] == "urgent_security"
    assert data["owner"] == "Security Team"


def test_han_solo_logistics(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Medical Corps",
        "content": "We need medical supplies delivered to Hoth within 24 hours.",
    })
    data = resp.get_json()
    assert data["category"] == "logistics"
    assert data["owner"] == "Han Solo"


def test_chewbacca_field_operations(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Wookiee Chieftain",
        "content": "Imperial forces are damaging our forests. We need field support and defense coordination.",
    })
    data = resp.get_json()
    assert data["category"] == "field_operations"
    assert data["owner"] == "Chewbacca"


def test_grogu_sensitive_case(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Village Elder",
        "content": "A child in our village can sense danger before it happens. The Empire is searching for them.",
    })
    data = resp.get_json()
    assert data["category"] == "jedi_training_diplomacy"
    assert data["owner"] == "Grogu Care Team"
    assert data["requires_jedi"] is True
    assert data["requires_leia"] is True
    assert data["security_risk"] == "high"
    assert data["jedi_case_type"] == "force_sensitive"


def test_din_djarin_protection(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Rebel Intelligence",
        "content": "A Rebel informant has been discovered. They need extraction before the Empire arrives.",
    })
    data = resp.get_json()
    assert data["category"] == "special_protection"
    assert data["owner"] == "Din Djarin"


def test_jarjar_planet_help(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Jar Jar Binks",
        "content": "Mesa Jar Jar Binks. Mesa people need help! Big trouble coming from da Empire.",
    })
    data = resp.get_json()
    assert data["category"] == "planet_help"
    assert data["owner"] == "Rebel Defense Team"
    assert data["assigned_team"] == "Defense Team"


def test_recruitment(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Davin Felth",
        "content": "I am a pilot from Corellia and I want to join the Rebellion.",
    })
    data = resp.get_json()
    assert data["category"] == "recruitment"
    assert data["owner"] == "Rebel Recruitment Team"
    assert data["assigned_team"] == "Recruitment Team"


def test_partnerships(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Senator Treen",
        "content": "Our senator can provide funding, ships, and diplomatic support to the Rebellion.",
    })
    data = resp.get_json()
    assert data["category"] == "investor_partner"
    assert data["owner"] == "Partnerships Team"
    assert data["assigned_team"] == "Partnerships"


def test_ewok_training(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Ewok Elder",
        "content": "The Ewoks have seen Imperial scouts. We need training and warning systems.",
    })
    data = resp.get_json()
    assert data["category"] == "population_training"
    assert data["owner"] == "Luke Skywalker + Ben Kenobi"
    assert data["jedi_case_type"] == "training"


def test_mediation(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Ambassador of Bothawui",
        "content": "Two planetary leaders refuse to work together. We need someone neutral to mediate.",
    })
    data = resp.get_json()
    assert data["category"] == "jedi_training_diplomacy"
    assert data["owner"] == "Luke Skywalker + Ben Kenobi"
    assert data["jedi_case_type"] == "mediation"
    assert data["requires_jedi"] is True


# ---- Demo ----

def test_demo_load_all(client):
    resp = client.post("/api/demo/load")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["loaded"] == 16

    palpatine = [r for r in data["results"] if r["sender"] == "Emperor Palpatine"][0]
    assert palpatine["risk_score"] >= 50
    assert palpatine["status"] == "quarantined"
    assert palpatine["security_risk"] == "high"

    yoda_result = [r for r in data["results"] if r["sender"] == "Planetary Council of Ryloth"][0]
    assert yoda_result["encrypted"] is True
    assert yoda_result["owner"] == "Yoda"

    jarjar = [r for r in data["results"] if r["sender"] == "Jar Jar Binks"][0]
    assert jarjar["category"] == "planet_help"
    assert jarjar["owner"] == "Rebel Defense Team"


def test_demo_run_all(client):
    resp = client.post("/demo/run-all")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["summary"]["total"] == 16
    assert data["summary"]["quarantined"] >= 2
    assert data["summary"]["encrypted"] >= 1
    assert data["summary"]["tasks_created"] >= 13


def test_list_messages(client):
    client.post("/api/demo/load")
    resp = client.get("/api/messages")
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data["data"]) == 16


def test_get_single_message(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Jar Jar Binks",
        "content": "Mesa need help!",
    })
    msg_id = resp.get_json()["id"]
    resp2 = client.get(f"/api/messages/{msg_id}")
    data = resp2.get_json()
    assert resp2.status_code == 200
    assert data["id"] == msg_id
    assert data["sender"] == "Jar Jar Binks"


def test_get_single_message_not_found(client):
    resp = client.get("/api/messages/nonexistent-id")
    assert resp.status_code == 404


def test_agents_list(client):
    resp = client.get("/api/agents")
    data = resp.get_json()["data"]
    assert resp.status_code == 200
    names = [a["name"] for a in data]
    assert "IntakeAgent" in names
    assert "DarkSideSecurityAgent" in names
    assert "C3POClassifierAgent" in names
    assert "RoutingAgent" in names
    assert "YodaEncryptionAgent" in names
    assert "NotificationAgent" in names
    assert "CalendarAgent" in names
    assert "ReportingAgent" in names
    assert "ErrorProtocolAgent" in names
    assert len(data) == 9


# ---- Tasks ----

def test_tasks_created_after_demo(client):
    client.post("/api/demo/load")
    resp = client.get("/tasks")
    tasks = resp.get_json()["data"]
    assert resp.status_code == 200
    assert len(tasks) >= 14
    for t in tasks:
        assert "owner" in t
        assert "assigned_team" in t
        assert "title" in t


def test_recruitment_creates_task(client):
    client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Davin Felth",
        "content": "I am a pilot and I want to join the Rebellion.",
    })
    resp = client.get("/tasks")
    tasks = resp.get_json()["data"]
    recruitment_tasks = [t for t in tasks if "Recruitment" in t.get("assigned_team", "")]
    assert len(recruitment_tasks) >= 1


# ---- Briefing ----

def test_briefing_generated(client):
    client.post("/api/demo/load")
    resp = client.get("/api/briefing")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "DAILY HOLOGRAM BRIEFING" in text
    assert "General Leia" in text
    assert "Total Requests:" in text
    assert "Quarantined" in text
    assert "Encrypted" in text
    assert "Security Risks Detected" in text
    assert "Recommended Focus" in text


def test_briefing_generate_endpoint(client):
    resp = client.post("/briefings/generate")
    assert resp.status_code == 200


# ---- Calendar ----

def test_calendar_no_private_exposure(client):
    client.post("/api/demo/load")
    resp = client.get("/api/calendar")
    data = resp.get_json()["data"]
    for b in data:
        assert not b["is_private"], f"Private booking exposed: {b}"


# ---- Reset ----

def test_reset(client):
    client.post("/api/demo/load")
    resp = client.get("/api/messages")
    assert len(resp.get_json()["data"]) == 16
    client.post("/api/reset")
    resp = client.get("/api/messages")
    assert len(resp.get_json()["data"]) == 0
    resp = client.get("/tasks")
    assert len(resp.get_json()["data"]) == 0

# ---- Webhooks ----
def test_whatsapp_webhook_verify_valid(client):
    import os
    os.environ["WHATSAPP_VERIFY_TOKEN"] = "rebel_ops_verify"
    resp = client.get("/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=rebel_ops_verify&hub.challenge=12345")
    assert resp.status_code == 200
    assert resp.get_data(as_text=True) == "12345"




def test_whatsapp_webhook_verify_invalid(client):
    resp = client.get("/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=wrong_token&hub.challenge=12345")
    assert resp.status_code == 403


def test_whatsapp_webhook_post(client):
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "15551234567",
                        "text": {"body": "Hello from WhatsApp webhook"},
                    }],
                },
            }],
        }],
    }
    resp = client.post("/webhooks/whatsapp", json=payload, content_type="application/json")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_gmail_webhook_post(client):
    payload = {"message": {"data": "test"}}
    resp = client.post("/webhooks/gmail", json=payload, content_type="application/json")
    assert resp.status_code == 200


def test_clickup_webhook_post(client):
    payload = {"event": "task_created", "task_id": "abc123"}
    resp = client.post("/webhooks/clickup", json=payload, content_type="application/json")
    assert resp.status_code == 200


# ---- Trace ----

def test_request_trace(client):
    resp = client.post("/api/intake", json={
        "channel": "intergalactic_whatsapp",
        "sender": "Test User",
        "content": "Need help on Tatooine",
    })
    msg_id = resp.get_json()["id"]
    trace_resp = client.get(f"/api/requests/{msg_id}/trace")
    data = trace_resp.get_json()
    assert trace_resp.status_code == 200
    assert data["id"] == msg_id
    assert len(data["trace"]) > 0
    assert any(t["agent"] == "IntakeAgent" for t in data["trace"])


def test_request_trace_not_found(client):
    resp = client.get("/api/requests/nonexistent/trace")
    assert resp.status_code == 404


# ---- Integration Status (removed — was gated for security) ----

def test_integration_status_removed(client):
    resp = client.get("/api/integrations")
    assert resp.status_code == 404


# ---- Briefing Inbox ----

def test_briefing_inbox_empty(client):
    resp = client.get("/api/briefing/inbox")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["total_messages"] == 0
    assert data["needs_attention"] == []
    assert data["open_tasks"] == []


def test_briefing_inbox_after_demo(client):
    client.post("/api/demo/load")
    resp = client.get("/api/briefing/inbox")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["total_messages"] == 16
    assert data["completed"] >= 10
    assert data["quarantined"] >= 2
    assert data["encrypted"] >= 1
    assert len(data["messages"]) == 16
    assert isinstance(data["delegation"], dict)
    assert len(data["delegation"]) > 0


# ---- T1: Pipeline exception handling ----

def test_pipeline_exception_handling(client):
    with mock.patch.object(intake, "process", side_effect=ValueError("intake exploded")):
        resp = client.post("/api/intake", json={
            "channel": "intergalactic_whatsapp",
            "sender": "Test User",
            "content": "This will trigger an exception",
        })
    data = resp.get_json()
    assert resp.status_code == 400
    assert data["status"] == "error"
    assert "intake exploded" in data["error"]

    resp2 = client.get("/tasks")
    tasks = resp2.get_json()["data"]
    error_tasks = [t for t in tasks if "Automation Error" in t.get("title", "")]
    assert len(error_tasks) >= 1


# ---- T2: Calendar confirmation endpoint ----

def test_calendar_confirm_endpoint(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Mon Mothma's Aide",
        "content": "We need a briefing with General Leia next Tuesday at 10:00 about funding.",
    })
    data = resp.get_json()
    assert data["category"] == "calendar_booking"
    assert data["status"] == "awaiting_confirmation"
    assert len(data.get("proposals", [])) > 0
    msg_id = data["id"]

    confirm_resp = client.get(f"/api/calendar/confirm/{msg_id}/0")
    assert confirm_resp.status_code == 200
    assert b"Confirmed" in confirm_resp.data
    assert b"General Leia" in confirm_resp.data

    msg_resp = client.get(f"/api/messages/{msg_id}")
    msg_data = msg_resp.get_json()
    assert len(msg_data.get("proposals", [])) == 0
    assert msg_data["status"] == "completed"


def test_calendar_confirm_not_found(client):
    resp = client.get("/api/calendar/confirm/nonexistent-id/0")
    assert resp.status_code == 404
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "Booking not found"

def test_calendar_confirm_invalid_slot(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Mon Mothma's Aide",
        "content": "Briefing with General Leia next Wednesday at 14:00",
    })
    data = resp.get_json()
    assert data["status"] == "awaiting_confirmation", f"Expected awaiting_confirmation, got {data['status']}"
    msg_id = data["id"]
    num_slots = len(data.get("proposals", []))

    resp = client.get(f"/api/calendar/confirm/{msg_id}/{num_slots + 1}")
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Invalid slot - please choose a valid option"


# ---- T3: Gmail webhook parsing ----

def test_gmail_webhook_parsing(client):
    fake_emails = [
        {
            "id": "msg_abc123",
            "from": "Outer Rim Scout",
            "subject": "Stormtroopers spotted near base",
            "snippet": "We have spotted stormtroopers near our outpost on Lothal",
        },
    ]
    with mock.patch.object(main_module.gmail, "list_unread", return_value=fake_emails), \
         mock.patch.object(main_module.gmail, "mark_read") as mock_mark:
        resp = client.post("/webhooks/gmail", json={"message": {"data": "test"}})
        assert resp.status_code == 200

        msgs_resp = client.get("/api/messages")
        msgs = msgs_resp.get_json()["data"]
        match = [m for m in msgs if "Outer Rim Scout" in m["sender"]]
        assert len(match) >= 1
        assert "Stormtroopers" in match[0]["content"]

        mock_mark.assert_called_once_with("msg_abc123")


def test_gmail_webhook_empty_list(client):
    with mock.patch.object(main_module.gmail, "list_unread", return_value=[]):
        resp = client.post("/webhooks/gmail", json={"message": {"data": "test"}})
        assert resp.status_code == 200

        msgs_resp = client.get("/api/messages")
        assert len(msgs_resp.get_json()["data"]) == 0


# ---- T4: WhatsApp webhook full parsing ----

def test_whatsapp_webhook_intake_created(client):
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "Scout Leader",
                        "text": {"body": "Need supplies on Hoth"},
                    }],
                },
            }],
        }],
    }
    resp = client.post("/webhooks/whatsapp", json=payload)
    assert resp.status_code == 200

    msgs_resp = client.get("/api/messages")
    msgs = msgs_resp.get_json()["data"]
    match = [m for m in msgs if "Scout Leader" in m["sender"]]
    assert len(match) >= 1
    assert "Need supplies on Hoth" in match[0]["content"]


def test_whatsapp_webhook_malformed_payload(client):
    resp = client.post("/webhooks/whatsapp", json={})
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}

    resp = client.post("/webhooks/whatsapp", json={
        "entry": [{"changes": [{"value": {"messages": [{}]}}]}],
    })
    assert resp.status_code == 200

    resp = client.post("/webhooks/whatsapp", json={
        "entry": [{"changes": [{"value": {"messages": [{"from": "123"}]}}]}],
    })
    assert resp.status_code == 200


# ---- T6: _message_to_dict serialization ----

def test_message_to_dict_all_keys():
    msg = Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Test Sender",
        content="Test content",
    )
    msg.id = "test-id-abc"
    msg.category = Category.LOGISTICS
    msg.owner = Owner.HAN_SOLO
    msg.status = MessageStatus.COMPLETED
    msg.encrypted = False
    msg.risk_score = 0
    msg.error = None
    msg.processed_by = ["IntakeAgent"]
    msg.priority = "medium"
    msg.security_risk = "low"
    msg.jedi_case_type = "none"
    msg.requires_leia = False
    msg.requires_jedi = False
    msg.trusted_request = True
    msg.dark_side_indicators = []
    msg.summary = "Test summary"
    msg.suggested_next_action = "Test action"
    msg.assigned_team = "Logistics Team"
    msg.subject = ""
    msg.planet_or_sector = ""
    msg.proposals = []
    msg.trace = [{"agent": "IntakeAgent", "action": "validated"}]

    d = _message_to_dict(msg)
    assert d["id"] == "test-id-abc"
    assert d["channel"] == "intergalactic_whatsapp"
    assert d["sender"] == "Test Sender"
    assert d["content"] == "Test content"
    assert d["category"] == "logistics"
    assert d["owner"] == "Han Solo"
    assert d["status"] == "completed"
    assert d["risk_score"] == 0
    assert d["encrypted"] is False
    assert d["error"] is None
    assert d["processed_by"] == ["IntakeAgent"]
    assert d["trace"] == [{"agent": "IntakeAgent", "action": "validated"}]
    assert d["proposals"] == []


def test_message_to_dict_content_truncation():
    long_content = "X" * 5000
    msg = Message(
        channel=Channel.HOLOGRAM_EMAIL,
        sender="Long Content Sender",
        content=long_content,
    )
    msg.id = "test-id-trunc"
    msg.category = Category.OTHER
    msg.owner = Owner.OPERATIONS_TEAM
    msg.status = MessageStatus.COMPLETED

    d = _message_to_dict(msg)
    assert len(d["content"]) == 1000
    assert d["content"] == "X" * 1000


def test_message_to_dict_null_fields():
    msg = Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Null Fields",
        content="Test",
    )
    msg.id = "test-null-fields"
    msg.category = None
    msg.owner = None

    d = _message_to_dict(msg)
    assert d["category"] is None
    assert d["owner"] is None
    assert d["error"] is None


def test_message_to_dict_encrypted_content(client):
    resp = client.post("/api/intake", json={
        "channel": "hologram_email",
        "sender": "Council of Ryloth",
        "content": "Should we join openly or remain hidden? This is a strategic question.",
    })
    data = resp.get_json()
    assert data["encrypted"] is True

    get_resp = client.get(f"/api/messages/{data['id']}")
    msg_data = get_resp.get_json()
    assert "[DEMO ENCRYPTED]" in data["content"]
    assert msg_data["encrypted"] is True

