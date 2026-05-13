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
    bookings = resp.get_json()
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
    assert len(data) == 16


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
    data = resp.get_json()
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
    tasks = resp.get_json()
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
    tasks = resp.get_json()
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
    data = resp.get_json()
    for b in data:
        assert not b["is_private"], f"Private booking exposed: {b}"


# ---- Reset ----

def test_reset(client):
    client.post("/api/demo/load")
    resp = client.get("/api/messages")
    assert len(resp.get_json()) == 16
    client.post("/api/reset")
    resp = client.get("/api/messages")
    assert len(resp.get_json()) == 0
    resp = client.get("/tasks")
    assert len(resp.get_json()) == 0
