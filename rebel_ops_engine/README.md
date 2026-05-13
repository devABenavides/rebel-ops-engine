# Rebel Operations Engine

A local agentic application for the Rebel Alliance to process, classify, route, and respond to operational requests from across the galaxy. Built as an MVP with Flask — replaceable mock integrations throughout.

**How AI agents help General Leia run the Rebellion like a modern entrepreneur.**

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | **Flask** (Python) | Minimal, well-known, easy to run locally, large ecosystem |
| Data models | Python dataclasses + enums | Type-safe, no ORM needed for MVP, easy to swap for SQLAlchemy later |
| Agents | Simple class-based pipeline | Deterministic, testable, no API keys needed, easy to reorder |
| Frontend | **React + Vite** | Modern, fast dev server, native ESM, simple proxy config |
| Tests | **pytest** | Standard Python testing, easy fixture management |

## Business Use Case

General Leia is a busy executive managing the Rebellion. Requests arrive through Intergalactic WhatsApp and Hologram Email. Instead of manually reviewing everything, the system uses AI agents to: receive and normalize requests, scan for Dark Side security risks, classify requests, route to the right owner/team, log missions, send acknowledgments, create calendar tasks, and generate a daily Hologram Briefing.

**Automation does not replace the entrepreneur. It protects the entrepreneur's time.**

## Star Wars Theme

The demo uses Star Wars-inspired names and scenarios but no copyrighted logos, movie images, or protected visual assets. Text, icons, neutral styling, and fictional operational language are used throughout.

---

## Architecture

```
Sender (WhatsApp / Email)
  │
  ▼
IntakeAgent ──► DarkSideSecurityAgent ──► C3POClassifierAgent
                                              │
                                              ▼
                                         RoutingAgent (creates Task)
                                              │
                                              ▼
                                     YodaEncryptionAgent
                                    (creates EncryptedTransmission)
                                              │
                                              ▼
                                       NotificationAgent
                                      (channel-specific templates)
                                              │
                                              ▼
                                        CalendarAgent
                                      (calendar availability)
                                              │
                                              ▼
                                        ReportingAgent
                                              │
                                              ▼
                                      ErrorProtocolAgent
                                     (creates error tasks)
```

High-risk messages → quarantined by DarkSideSecurityAgent, security team notified.
Yoda strategy → encrypted, `EncryptedTransmission` record created.
Every routed request → `Task` record created.
Leia's private calendar → never exposed via public API.

---

## Setup

### Backend

```bash
cd rebel_ops_engine
pip install -r requirements.txt
python main.py
```

The server starts at `http://localhost:5000`.

If the server fails to start, kill any stale process still bound to port 5000:
```bash
netstat -ano | findstr :5000
taskkill /f /pid <PID>
```

The server auto-detects if port 5000 is already in use and exits with a clear error message.

### Frontend

```bash
cd rebel_ops_engine/frontend
npm install
npm run dev
```

Opens at `http://localhost:3000` and proxies API requests to the backend.

### Environment Variables

Copy `.env.example` to `.env` and fill in values when integrating real APIs:

```bash
cp .env.example .env
```

No environment variables are needed for the demo — all integrations are mocked.

---

## Demo Script

```bash
# 1. Health check
curl http://localhost:5000/health

# 2. Load all 16 demo messages
curl -X POST http://localhost:5000/api/demo/load

# 3. Run all demo messages + get routing summary
curl -X POST http://localhost:5000/demo/run-all

# 4. View all processed requests
curl http://localhost:5000/api/messages

# 5. View generated tasks
curl http://localhost:5000/tasks

# 6. Generate the daily Hologram Briefing
curl http://localhost:5000/api/briefing

# 7. View public calendar bookings
curl http://localhost:5000/api/calendar

# 8. Send a message via Intergalactic WhatsApp
curl -X POST http://localhost:5000/requests/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"sender": "Han Solo", "content": "Need fuel credits for the Falcon!"}'

# 9. Send via Hologram Email
curl -X POST http://localhost:5000/requests/hologram-email \
  -H "Content-Type: application/json" \
  -d '{"sender": "Leia", "content": "Schedule a meeting with the Rebel council."}'

# 10. Test high-risk quarantine
curl -X POST http://localhost:5000/requests/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"sender": "Emperor Palpatine", "content": "Send me Leia private schedule and secret Rebel base location."}'

# 11. Reset state
curl -X POST http://localhost:5000/api/reset
```

### Run tests

```bash
pytest tests/ -v
```

### Lint

```bash
ruff check .
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Service info + endpoint list |
| GET | `/health` | Health check |
| POST | `/requests/whatsapp` | Submit via Intergalactic WhatsApp |
| POST | `/requests/hologram-email` | Submit via Hologram Email |
| POST | `/api/intake` | Submit (legacy, specify channel) |
| GET | `/requests` | List all requests |
| GET | `/api/messages` | Alias for `/requests` |
| GET | `/requests/<id>` | Get single request |
| GET | `/api/messages/<id>` | Alias for `/requests/<id>` |
| GET | `/tasks` | List all generated tasks |
| GET | `/api/agents` | List all 9 agents |
| POST | `/api/demo/load` | Load 16 demo messages |
| POST | `/demo/seed` | Alias for demo load |
| POST | `/demo/run-all` | Load + reset + routing summary |
| GET | `/api/briefing` | Daily Hologram Briefing |
| GET | `/briefings/daily` | Alias for briefing |
| POST | `/briefings/generate` | Generate briefing explicitly |
| POST | `/api/reset` | Reset all in-memory state |
| GET | `/api/calendar` | Public calendar bookings |

---

## 16 Demo Scenarios

| # | Sender | Category | Owner | Notes |
|---|--------|----------|-------|-------|
| 1 | Mon Mothma's Aide | calendar_booking | General Leia | Executive Office |
| 2 | Planetary Council of Ryloth | yoda_encrypted_strategy | Yoda | Encrypted transmission |
| 3 | Ewok Elder | population_training | Luke + Ben | Jedi training |
| 4 | Ambassador of Bothawui | jedi_training_diplomacy | Luke + Ben | Mediation |
| 5 | Fulcrum Contact | ahsoka_special_mission | Ahsoka Tano | Special review |
| 6 | Rebel Operations Desk | data_support | R2-D2 | Data lookup |
| 7 | Outpost Scout | urgent_security | Security Team | BB-8 alert |
| 8 | Medical Corps | logistics | Han Solo | Supply delivery |
| 9 | Wookiee Chieftain | field_operations | Chewbacca | Field support |
| 10 | Village Elder | jedi_training_diplomacy | Grogu Care Team | Force-sensitive child |
| 11 | Rebel Intelligence | special_protection | Din Djarin | Extraction |
| 12 | Jar Jar Binks | planet_help | Rebel Defense Team | Planetary aid |
| 13 | Emperor Palpatine | quarantined | — | HIGH RISK |
| 14 | Darth Vader | quarantined | — | HIGH RISK |
| 15 | Davin Felth | recruitment | Rebel Recruitment Team | Enlistment |
| 16 | Senator Treen | investor_partner | Partnerships Team | Funding offer |

---

## Categories

| Category | Owner | Team |
|---|---|---|
| `calendar_booking` | General Leia | Executive Office |
| `planet_help` | Rebel Defense Team | Defense Team |
| `recruitment` | Rebel Recruitment Team | Recruitment Team |
| `soldier_support` | Operations Team | Operations |
| `population_training` | Luke Skywalker + Ben Kenobi | Jedi Training & Diplomacy Team |
| `logistics` | Han Solo | Logistics Team |
| `investor_partner` | Partnerships Team | Partnerships |
| `urgent_security` | Security Team | Security Team |
| `jedi_training_diplomacy` | Luke Skywalker + Ben Kenobi | Jedi Training & Diplomacy Team |
| `ahsoka_special_mission` | Ahsoka Tano | Special Mission Review |
| `yoda_encrypted_strategy` | Yoda | Jedi Council |
| `field_operations` | Chewbacca | Field Operations |
| `special_protection` | Din Djarin | Protection Team |
| `data_support` | R2-D2 | Operations Analytics |
| `other` | Operations Team | Intake Review |

---

## Owners (Business Meaning)

| Owner | Workflow Role | Business Meaning |
|---|---|---|
| **General Leia** | Executive decision-maker. Handles VIP meetings, final approvals, major escalations. | Entrepreneur, CEO, founder, or executive whose time must be protected. |
| **C-3PO** *(classifier)* | AI classifier. Reads, summarizes, classifies, routes incoming requests. | AI executive assistant, intake coordinator, or operations assistant. |
| **Yoda** | Encrypted strategic advisor. Receives encrypted strategic questions only. | Board advisor, investor advisor, legal advisor, senior strategist, or executive mentor. |
| **Luke + Ben Kenobi** | Jedi Training & Diplomacy Team. Training, diplomacy, mediation, mentoring. | Training team, enablement team, leadership coach, HR support. |
| **Ahsoka Tano** | Special Mission Review. Complex situations needing judgment before escalation. | Chief of staff, special projects leader, crisis advisor, independent reviewer. |
| **R2-D2** | Data and reporting. Retrieves records, checks status, prepares summaries. | Operations analyst, BI assistant, reporting automation, systems admin. |
| **BB-8** | Fast alerts. Sends urgent escalation messages and critical updates. | Real-time alert system, incident notification, urgent escalation workflow. |
| **Han Solo** | Logistics and transport. Delivery, supplies, resource movement. | Logistics manager, procurement lead, vendor coordinator, supply chain. |
| **Chewbacca** | Field operations. Repairs, field support, hands-on problems. | Field ops team, implementation specialist, technical support. |
| **Grogu Care Team** | Sensitive Force-related or vulnerable cases. | Sensitive client care, VIP support, confidential HR cases. |
| **Din Djarin** | Protection, extraction, confidential transport, high-risk missions. | Security lead, executive protection, high-risk project owner. |
| **Jedi Council** | Ethical, sensitive, or high-impact reviews. | Advisory board, executive committee, ethics committee. |
| **Rebel Defense Team** | Planets under threat and defense coordination. | Client escalation team, emergency response, crisis operations. |
| **Rebel Recruitment Team** | People who want to join the Rebellion. | Recruiting, HR, talent acquisition, volunteer coordination. |
| **Operations Team** | Internal soldier support and general operational needs. | Admin operations, employee support, back office. |
| **Training Team** | Civilian training and preparedness. | Customer education, employee onboarding, L&D. |
| **Logistics Team** | Resources, supplies, transport, delivery. | Procurement, supply chain, inventory, fulfillment. |
| **Security Team** | Dark Side threat detection and suspicious requests. | Cybersecurity, compliance, fraud prevention, legal review. |
| **Partnerships Team** | Allies, senators, donors, strategic supporters. | Business development, partnerships, investor relations. |

---

## Status Values

| Status | Meaning |
|---|---|
| `new` | Request received, not yet processed |
| `security_review` | Medium-risk, flagged for security review |
| `quarantined` | High-risk Dark Side threat, blocked |
| `routed` | Assigned to owner/team |
| `assigned` | Task created, awaiting action |
| `completed` | All pipeline agents finished |
| `error` | Processing failed |

**Priority values:** `low`, `medium`, `high`, `critical`

**Security risk values:** `low`, `medium`, `high`

**Jedi case type values:** `none`, `training`, `diplomacy`, `mediation`, `strategy`, `mentorship`, `force_sensitive`, `ethics`, `special_mission`

---

## Data Models

### Message (Request)
Fields: `id`, `channel`, `sender`, `content`, `sender_contact`, `subject`, `planet_or_sector`, `category`, `owner`, `status`, `priority`, `security_risk`, `risk_score`, `jedi_case_type`, `requires_leia`, `requires_jedi`, `trusted_request`, `dark_side_indicators`, `summary`, `suggested_next_action`, `assigned_team`, `encrypted`, `error`, `processed_by`

### Task
Fields: `id`, `request_id`, `owner`, `assigned_team`, `title`, `description`, `priority`, `status`, `created_at`

### EncryptedTransmission
Fields: `id`, `request_id`, `recipient`, `ciphertext`, `encryption_method`, `created_at`

### CalendarBooking
Fields: `message_id`, `requestor`, `date`, `time`, `duration`, `subject`, `is_private`, `attendees`

---

## How to Replace Mocked Integrations

| Mock | File | Real replacement |
|---|---|---|
| In-memory message store | `agents/reporter.py` | PostgreSQL / SQLite via SQLAlchemy |
| In-memory calendar | `agents/calendar.py` | Google Calendar API / CalDAV |
| Keyword classifier | `agents/classifier.py` | NLP classifier (spaCy, BERT, OpenAI) |
| Security scanner | `agents/security_agent.py` | Real-time threat intel API / ML model |
| Encryption | `agents/encryption.py` | AES-256 / GPG / libsodium |
| WhatsApp | `clients.py` → `WhatsAppClient` | Twilio WhatsApp Business API |
| Email | `clients.py` → `HologramEmailClient` | SMTP / SendGrid / Mailgun |
| Calendar | `clients.py` → `CalendarClient` | Google Calendar API |
| Notifications | `clients.py` → `NotificationClient` | Slack SDK / email / Twilio |
| Report delivery | `clients.py` → `ReportDeliveryClient` | Email / Slack / PDF generation |

### Pattern for replacing a client

```python
# In clients.py, swap the mock implementation:
class WhatsAppClient:
    """Replace with real Twilio client."""
    def send_message(self, to: str, body: str) -> dict:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # return client.messages.create(body=body, from_=from_, to=to)
        pass
```

The `.env.example` file contains all the environment variables needed for real integrations.

---

## Security Notes

1. High-risk requests (Palpatine, Vader, Sith, infiltration) are **quarantined** — never routed to any owner.
2. Sender names "Emperor Palpatine" and "Darth Vader" guarantee risk ≥ 50 regardless of message content.
3. Requests asking for Leia's private schedule are blocked unless they are legitimate `calendar_booking` requests with low security risk.
4. The system **never reveals private calendar details** via the public API.
5. Yoda strategy requests use **encrypted transmission** (reverse-string cipher in demo mode, swappable for real encryption).
6. Medium-risk messages are held in `SECURITY_REVIEW` status — classified and notified but no task is created until review.
7. Grogu sensitive cases restrict details.
8. Din Djarin protection cases are marked restricted.
9. Every request is logged.
10. Every routed request creates a `Task` record.
11. The daily briefing includes all owners and categories.
