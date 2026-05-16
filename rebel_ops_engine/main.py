import json
import logging
import os
import socket
import sys

from flask import Flask, jsonify, request

from agents.calendar import CalendarAgent
from agents.classifier import C3POClassifierAgent
from agents.encryption import YodaEncryptionAgent
from agents.error_handler import ErrorProtocolAgent
from agents.intake import IntakeAgent
from agents.notifier import NotificationAgent
from agents.reporter import ReportingAgent
from agents.router import RoutingAgent
from agents.security_agent import DarkSideSecurityAgent
from briefing import generate_hologram_briefing
from demo import DEMO_MESSAGES
from integrations import clickup_client
from integrations import gmail_client as gmail
from integrations import whatsapp_client as wa
from integrations.config import ensure_env_loaded
from models import Channel, Message, MessageStatus

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or os.urandom(24).hex()
ensure_env_loaded()

intake = IntakeAgent()
security = DarkSideSecurityAgent()
classifier = C3POClassifierAgent()
router = RoutingAgent()
encryption = YodaEncryptionAgent()
notifier = NotificationAgent()
calendar = CalendarAgent()
reporter = ReportingAgent()
error_handler = ErrorProtocolAgent()

AGENT_REGISTRY = {
    "IntakeAgent": (intake, "Receives and normalizes incoming requests from WhatsApp and Hologram Email"),
    "DarkSideSecurityAgent": (security, "Scans for Dark Side threats — Palpatine, Vader, Sith, infiltration — and quarantines high-risk messages"),
    "C3POClassifierAgent": (classifier, "Classifies requests into operational categories and recommends the best owner and team"),
    "RoutingAgent": (router, "Routes classified requests to the correct owner, assigns team, and creates tasks"),
    "YodaEncryptionAgent": (encryption, "Handles encrypted strategic transmissions for Master Yoda"),
    "NotificationAgent": (notifier, "Sends channel-specific acknowledgments and templates (WhatsApp, Email, BB-8 alerts, etc.)"),
    "CalendarAgent": (calendar, "Manages calendar bookings and enforces Leia's private calendar protection"),
    "ReportingAgent": (reporter, "Stores processed requests and generates the Daily Hologram Briefing"),
    "ErrorProtocolAgent": (error_handler, "Handles quarantined messages and processing errors, creates ops tasks"),
}

PIPELINE = [entry[0] for entry in AGENT_REGISTRY.values()]


def run_pipeline(message: Message) -> Message:
    message.status = MessageStatus.NEW
    message.trace = []
    for agent in PIPELINE:
        if message.status in (MessageStatus.ERROR, MessageStatus.FLAGGED):
            break
        try:
            message = agent.process(message)
        except Exception as e:
            message.status = MessageStatus.ERROR
            message.error = str(e)
            logger.exception("Pipeline exception at %s: %s", agent.name, e)
            error_handler.process(message)
            break
    if message.status not in (MessageStatus.ERROR, MessageStatus.QUARANTINED,
                               MessageStatus.SECURITY_REVIEW, MessageStatus.FLAGGED,
                               MessageStatus.AWAITING_CONFIRMATION):
        message.status = MessageStatus.COMPLETED
    return message


def _message_to_dict(m: Message) -> dict:
    return {
        "id": m.id,
        "channel": m.channel.value,
        "sender": m.sender,
        "content": m.content[:1000],
        "category": m.category.value if m.category else None,
        "owner": m.owner.value if m.owner else None,
        "status": m.status.value,
        "risk_score": m.risk_score,
        "encrypted": m.encrypted,
        "error": m.error,
        "processed_by": m.processed_by,
        "priority": m.priority,
        "security_risk": m.security_risk,
        "jedi_case_type": m.jedi_case_type,
        "requires_leia": m.requires_leia,
        "requires_jedi": m.requires_jedi,
        "trusted_request": m.trusted_request,
        "dark_side_indicators": m.dark_side_indicators,
        "summary": m.summary,
        "suggested_next_action": m.suggested_next_action,
        "assigned_team": m.assigned_team,
        "subject": m.subject,
        "planet_or_sector": m.planet_or_sector,
        "proposals": m.proposals,
        "trace": m.trace,
    }


def _handle_intake(channel: Channel, sender: str, content: str,
                   subject: str = "", contact: str = "",
                   planet: str = "") -> tuple[dict, int]:
    message = Message(
        channel=channel,
        sender=sender,
        content=content,
        subject=subject,
        sender_contact=contact,
        planet_or_sector=planet,
    )
    message = run_pipeline(message)
    status_code = 400 if message.status in (MessageStatus.ERROR, MessageStatus.QUARANTINED) else 200
    return _message_to_dict(message), status_code


# ---- Health ----

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "Rebel Operations Engine"})


# ---- Legacy endpoints (backward compatible) ----

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "Rebel Operations Engine",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "GET /": "This help",
            "GET /health": "Health check",
            "POST /api/intake": "Submit a message (channel, sender, content)",
            "POST /requests/whatsapp": "Submit via Intergalactic WhatsApp",
            "POST /requests/hologram-email": "Submit via Hologram Email",
            "GET /api/messages": "List all processed messages",
            "GET /requests": "Alias for /api/messages",
            "GET /api/messages/<id>": "Get single message",
            "GET /requests/<id>": "Alias for /api/messages/<id>",
            "GET /tasks": "List all generated tasks",
            "GET /api/agents": "List all agents",
            "POST /api/demo/load": "Load all demo messages",
            "POST /demo/seed": "Alias for /api/demo/load",
            "POST /demo/run-all": "Load demo + return routing summary",
            "GET /api/briefing": "Generate daily Hologram Briefing",
            "GET /briefings/daily": "Alias for /api/briefing",
            "POST /briefings/generate": "Generate briefing explicitly",
            "POST /api/reset": "Reset all in-memory state",
            "GET /api/calendar": "List public calendar bookings",
        },
    })


@app.route("/api/intake", methods=["POST"])
def api_intake():
    if request.content_type != "application/json":
        return jsonify({"error": "Content-Type must be application/json"}), 415
    data = request.get_json(force=False)
    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400
    channel_str = data.get("channel", "intergalactic_whatsapp")
    try:
        channel = Channel(channel_str)
    except ValueError:
        return jsonify({"error": f"Invalid channel: {channel_str}"}), 400
    result, code = _handle_intake(
        channel=channel,
        sender=data.get("sender", ""),
        content=data.get("content", ""),
        subject=data.get("subject", ""),
        contact=data.get("sender_contact", ""),
        planet=data.get("planet_or_sector", ""),
    )
    return jsonify(result), code


# ---- New spec-aligned endpoints ----

@app.route("/requests/whatsapp", methods=["POST"])
def requests_whatsapp():
    if request.content_type != "application/json":
        return jsonify({"error": "Content-Type must be application/json"}), 415
    data = request.get_json(force=False)
    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400
    result, code = _handle_intake(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender=data.get("sender", ""),
        content=data.get("content", ""),
        subject=data.get("subject", ""),
        contact=data.get("sender_contact", ""),
        planet=data.get("planet_or_sector", ""),
    )
    return jsonify(result), code


@app.route("/requests/hologram-email", methods=["POST"])
def requests_hologram_email():
    if request.content_type != "application/json":
        return jsonify({"error": "Content-Type must be application/json"}), 415
    data = request.get_json(force=False)
    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400
    result, code = _handle_intake(
        channel=Channel.HOLOGRAM_EMAIL,
        sender=data.get("sender", ""),
        content=data.get("content", ""),
        subject=data.get("subject", ""),
        contact=data.get("sender_contact", ""),
        planet=data.get("planet_or_sector", ""),
    )
    return jsonify(result), code


@app.route("/requests", methods=["GET"])
@app.route("/api/messages", methods=["GET"])
def list_requests():
    msgs = reporter.get_all_messages()
    return jsonify([_message_to_dict(m) for m in msgs])


@app.route("/requests/<message_id>", methods=["GET"])
@app.route("/api/messages/<message_id>", methods=["GET"])
def get_request(message_id):
    m = reporter.get_message(message_id)
    if m is not None:
        d = _message_to_dict(m)
        if m.encrypted:
            d["content"] = "[ENCRYPTED CONTENT]"
        return jsonify(d)
    return jsonify({"error": "Message not found"}), 404


@app.route("/api/tasks", methods=["GET"])
@app.route("/tasks", methods=["GET"])
def list_tasks():
    all_tasks = router.get_tasks() + error_handler.get_error_tasks()
    clickup_results = {}
    for k, v in router.get_clickup_results().items():
        clickup_results[k] = v
    for k, v in error_handler.get_clickup_results().items():
        clickup_results[k] = v
    return jsonify([
        {
            "id": t.id,
            "request_id": t.request_id,
            "owner": t.owner,
            "assigned_team": t.assigned_team,
            "title": t.title,
            "description": t.description[:200],
            "priority": t.priority,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
            "clickup": clickup_results.get(t.id, {"status": "initiated"}),
        }
        for t in all_tasks
    ])

@app.route("/api/agents", methods=["GET"])
def api_agents():
    return jsonify([
        {"name": name, "description": desc}
        for name, (_, desc) in AGENT_REGISTRY.items()
    ])


# ---- Demo ----

@app.route("/api/demo/load", methods=["POST"])
@app.route("/demo/seed", methods=["POST"])
def api_demo_load():
    router.reset()
    error_handler.reset()
    clickup_client.clear_list()
    results = []
    for msg in DEMO_MESSAGES:
        result = run_pipeline(msg)
        results.append({
            "sender": result.sender,
            "status": result.status.value,
            "category": result.category.value if result.category else None,
            "owner": result.owner.value if result.owner else None,
            "risk_score": result.risk_score,
            "encrypted": result.encrypted,
            "error": result.error,
            "priority": result.priority,
            "security_risk": result.security_risk,
            "requires_leia": result.requires_leia,
            "requires_jedi": result.requires_jedi,
            "assigned_team": result.assigned_team,
            "suggested_next_action": result.suggested_next_action[:100],
        })
    return jsonify({"loaded": len(results), "results": results})


@app.route("/demo/run-all", methods=["POST"])
def demo_run_all():
    reporter.reset()
    calendar.reset()
    router.reset()
    encryption.reset()
    error_handler.reset()

    results = []
    for msg in DEMO_MESSAGES:
        result = run_pipeline(msg)
        results.append({
            "sender": result.sender,
            "status": result.status.value,
            "category": result.category.value if result.category else None,
            "owner": result.owner.value if result.owner else None,
            "assigned_team": result.assigned_team,
            "priority": result.priority,
            "security_risk": result.security_risk,
            "encrypted": result.encrypted,
            "requires_leia": result.requires_leia,
            "requires_jedi": result.requires_jedi,
            "error": result.error,
        })

    tasks = [
        {"owner": t.owner, "team": t.assigned_team, "title": t.title, "priority": t.priority}
        for t in router.get_tasks()
    ]

    return jsonify({
        "summary": {
            "total": len(results),
            "quarantined": sum(1 for r in results if r["status"] == "quarantined"),
            "encrypted": sum(1 for r in results if r["encrypted"]),
            "tasks_created": len(tasks),
        },
        "results": results,
        "tasks": tasks,
    })


# ---- Briefing ----

@app.route("/api/briefing", methods=["GET"])
@app.route("/briefings/daily", methods=["GET"])
def api_briefing():
    report = generate_hologram_briefing(reporter, calendar)
    return jsonify({"briefing": report})


@app.route("/briefings/generate", methods=["POST"])
@app.route("/api/briefings/generate", methods=["POST"])
def briefing_generate():
    report = generate_hologram_briefing(reporter, calendar)
    try:
        from clients import ReportDeliveryClient
        ReportDeliveryClient().deliver_report(report)
    except Exception:
        pass
    return jsonify({"briefing": report})


# ---- Reset ----

@app.route("/api/requests/<message_id>/trace", methods=["GET"])
@app.route("/requests/<message_id>/trace", methods=["GET"])
def request_trace(message_id):
    m = reporter.get_message(message_id)
    if m is not None:
        return jsonify({"id": m.id, "sender": m.sender, "trace": m.trace})
    return jsonify({"error": "Message not found"}), 404


@app.route("/api/reset", methods=["POST"])
def api_reset():
    reporter.reset()
    calendar.reset()
    router.reset()
    encryption.reset()
    error_handler.reset()
    clickup_client.clear_list()
    return jsonify({"status": "reset"}), 200


# ---- Calendar ----

@app.route("/api/calendar", methods=["GET"])
def api_calendar():
    bookings = calendar.get_public_bookings()
    return jsonify([
        {
            "message_id": b.message_id,
            "requestor": b.requestor,
            "date": b.date,
            "time": b.time,
            "subject": b.subject[:60],
            "is_private": b.is_private,
        }
        for b in bookings
    ])


# ---- Webhooks ----

@app.route("/webhooks/whatsapp", methods=["GET"])
def whatsapp_webhook_verify():
    mode = request.args.get("hub.mode", "")
    token = request.args.get("hub.verify_token", "")
    challenge = request.args.get("hub.challenge", "")
    body, code = wa.verify_webhook(mode, token, challenge)
    return body, code


@app.route("/webhooks/whatsapp", methods=["POST"])
def whatsapp_webhook():
    data = request.get_json(force=True)
    logger.info("[WEBHOOK] WhatsApp incoming: %s", json.dumps(data, indent=2)[:500])
    try:
        entry = data.get("entry", [{}])[0]
        change = entry.get("changes", [{}])[0]
        msg = change.get("value", {}).get("messages", [{}])[0]
        from_number = msg.get("from", "unknown")
        text = msg.get("text", {}).get("body", "")
        if text:
            _handle_intake(Channel.INTERGALACTIC_WHATSAPP, from_number, text)
    except Exception as e:
        logger.warning("[WEBHOOK] Failed to parse WhatsApp message: %s", e)
    return jsonify({"status": "ok"}), 200


@app.route("/webhooks/gmail", methods=["POST"])
def gmail_webhook():
    data = request.get_json(force=True)
    logger.info("[WEBHOOK] Gmail notification: %s", json.dumps(data, indent=2)[:500])
    try:
        unread = gmail.list_unread()
        for msg in unread:
            content = f"From: {msg['from']}\nSubject: {msg['subject']}\n{msg['snippet']}"
            result, code = _handle_intake(Channel.HOLOGRAM_EMAIL, msg["from"], content, subject=msg["subject"])
            if code == 200:
                gmail.mark_read(msg["id"])
    except Exception as e:
        logger.warning("[WEBHOOK] Failed to process Gmail notifications: %s", e)
    return jsonify({"status": "ok"}), 200


@app.route("/webhooks/clickup", methods=["POST"])
def clickup_webhook():
    data = request.get_json(force=True)
    logger.info("[WEBHOOK] ClickUp event: %s", json.dumps(data, indent=2)[:500])
    return jsonify({"status": "ok"}), 200


# ---- Integration status ----

@app.route("/api/integrations", methods=["GET"])
def integration_status():
    return jsonify({
        "gmail": bool(os.getenv("GMAIL_CREDENTIALS_PATH")),
        "calendar": bool(os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH")),
        "clickup": bool(os.getenv("CLICKUP_API_TOKEN")),
        "whatsapp": bool(os.getenv("WHATSAPP_PHONE_NUMBER_ID")),
        "slack": bool(os.getenv("SLACK_WEBHOOK_URL")),
    })


# ---- Morning Briefing data ----

@app.route("/api/briefing/inbox", methods=["GET"])
def briefing_inbox():
    msgs = reporter.get_all_messages()
    all_tasks = router.get_tasks() + error_handler.get_error_tasks()
    bookings = calendar.get_public_bookings()

    needs_attention = [
        {
            "id": m.id, "sender": m.sender,
            "category": m.category.value if m.category else "unknown",
            "priority": m.priority,
            "subject": m.subject or m.content[:80],
            "timestamp": m.timestamp.isoformat(),
            "channel": m.channel.value,
            "status": m.status.value,
            "encrypted": m.encrypted,
            "risk_score": m.risk_score,
        }
        for m in msgs if m.requires_leia
    ]

    open_tasks = [
        {
            "id": t.id, "title": t.title, "owner": t.owner,
            "team": t.assigned_team, "priority": t.priority,
            "status": t.status,
        }
        for t in all_tasks if t.status == "open"
    ]

    completed_count = sum(1 for m in msgs if m.status == MessageStatus.COMPLETED)
    quarantined_count = sum(1 for m in msgs if m.status == MessageStatus.QUARANTINED)
    encrypted_count = sum(1 for m in msgs if m.encrypted)

    delegation = {}
    for m in msgs:
        owner = m.owner.value if m.owner else "Unassigned"
        delegation[owner] = delegation.get(owner, 0) + 1

    messages_list = [
        {
            "id": m.id, "channel": m.channel.value,
            "sender": m.sender, "category": m.category.value if m.category else "unknown",
            "status": m.status.value, "priority": m.priority,
            "encrypted": m.encrypted, "owner": m.owner.value if m.owner else None,
            "assigned_team": m.assigned_team,
            "subject": m.subject or m.content[:80],
            "content": m.content[:200],
            "risk_score": m.risk_score,
            "timestamp": m.timestamp.isoformat(),
        }
        for m in sorted(msgs, key=lambda x: x.timestamp, reverse=True)
    ]

    return jsonify({
        "total_messages": len(msgs),
        "completed": completed_count,
        "quarantined": quarantined_count,
        "encrypted": encrypted_count,
        "needs_attention": needs_attention,
        "open_tasks": open_tasks,
        "delegation": delegation,
        "messages": messages_list,
        "schedule": [
            {
                "requestor": b.requestor,
                "subject": b.subject[:60],
                "date": b.date,
                "time": b.time,
            }
            for b in bookings
        ],
    })


# ---- Calendar confirmation ----

@app.route("/api/calendar/confirm/<message_id>/<int:slot>", methods=["GET"])
def calendar_confirm(message_id, slot):
    from agents.calendar import _extract_date as _cal_date
    from clients import CalendarClient as _CalClient

    msg = reporter.get_message(message_id)
    if msg is None:
        return "<h1>404</h1><p>Booking not found.</p>", 404

    if not msg.proposals:
        return "<h1>Already Confirmed</h1><p>This booking has already been confirmed.</p>"

    if slot < 0 or slot >= len(msg.proposals):
        return "<h1>Invalid Slot</h1><p>Please choose a valid option.</p>", 400

    chosen_time = msg.proposals[slot]
    date_str = _cal_date(msg.content)
    summary = msg.summary or msg.content[:100]

    cal = _CalClient()
    result = cal.create_event(summary, date_str, chosen_time)

    confirmed_slot = msg.proposals[slot]
    msg.proposals = []
    msg.status = MessageStatus.COMPLETED
    msg.trace.append({
        "agent": "CalendarConfirm",
        "action": "confirmed",
        "details": {"date": date_str, "time": confirmed_slot},
    })

    email_body = (
        f"Your briefing with General Leia has been confirmed.\n\n"
        f"Date: {date_str}\n"
        f"Time: {confirmed_slot}\n"
        f"Duration: 30 minutes\n\n"
        f"May the Force be with you."
    )
    try:
        recipient = msg.sender_contact or msg.sender
        gmail.send_email(recipient, "Rebel Command: Booking Confirmed", email_body)
    except Exception:
        pass

    status_text = result.get("status", "error")
    if status_text == "mocked":
        status_text = "simulated (mock mode)"

    return f"""
    <html><body style="font-family:sans-serif;background:#f5f1ea;padding:40px;color:#1c1c1f">
    <h1>✅ Confirmed</h1>
    <p>Your 30-minute briefing with <strong>General Leia</strong> has been scheduled.</p>
    <p><strong>Date:</strong> {date_str}<br>
    <strong>Time:</strong> {confirmed_slot} (America/Bogota)<br>
    <strong>Event:</strong> {status_text}</p>
    <p><a href="http://localhost:5000/" style="color:#d4872a;">Back to Command Center</a></p>
    </body></html>
    """


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if sock.connect_ex(("127.0.0.1", 5000)) == 0:
        logger.error("Port 5000 already in use — old process still running!")
        logger.error("Kill it:  netstat -ano | findstr :5000  then  taskkill /f /pid <PID>")
        sys.exit(1)
    sock.close()

    logger.info("=" * 50)
    logger.info("  Rebel Operations Engine v2.0")
    logger.info("  Running at http://127.0.0.1:5000")
    logger.info("=" * 50)
    app.run(host="127.0.0.1", port=5000, debug=False)
