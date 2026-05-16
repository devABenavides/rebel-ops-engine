# Rebel Operations Engine — AI Guide

## Project root
`rebel_ops_engine/`

## Server

Before starting, kill any stale Flask process still bound to port 5000:
```bash
netstat -ano | findstr :5000
taskkill /f /pid <PID>
```

Then start fresh:
```bash
cd rebel_ops_engine && python main.py
```

The server auto-detects if port 5000 is already in use and exits with a clear error message.

## Tests
```bash
cd rebel_ops_engine && python -m pytest tests/ -v
```

## Lint
```bash
cd rebel_ops_engine && python -m ruff check .
```

## Frontend
```bash
cd rebel_ops_engine/frontend && npm run dev
```

## Key files
- `main.py` — Flask app, 20+ routes, pipeline orchestrator
- `models.py` — Message, Task, EncryptedTransmission, CalendarBooking, DailyBriefing dataclasses + enums (Channel, MessageStatus, Priority, SecurityRisk, JediCaseType, Category, Owner)
- `security.py` — Risk scoring, category→owner/team mapping, routing tables, keyword detection
- `clients.py` — Integration client interfaces (WhatsAppClient, HologramEmailClient, CalendarClient, NotificationClient, ReportDeliveryClient)
- `agents/` — 9 agents in pipeline order (NotificationAgent uses channel-specific templates: WhatsApp, hologram, quarantine, BB-8 alert, etc.)
- `demo.py` — 16 spec-aligned demo messages
- `briefing.py` — Daily Hologram Briefing generator with full category/owner breakdown
- `.env.example` — Environment variable template for replacing mocked integrations
- `tests/test_engine.py` — 51 integration tests
- `tests/test_agents.py` — 70 isolated unit tests
- `tests/test_security.py` — 54 pure unit tests for security functions
- `tests/test_briefing.py` — 15 unit tests for briefings
- `tests/conftest.py` — Shared fixtures (base_message, fresh_router, etc.)
- `frontend/src/` — React app with 8 page-level components + MorningBriefing CSS
- `pyproject.toml` — Ruff linter config

## Agent pipeline order
IntakeAgent → DarkSideSecurityAgent → C3POClassifierAgent → RoutingAgent → YodaEncryptionAgent → NotificationAgent → CalendarAgent → ReportingAgent → ErrorProtocolAgent

Pipeline built from `AGENT_REGISTRY` dict in `main.py`. Add new agents to the registry to include them in the pipeline.

## Categories & owners (v2 routing rules)
| Category | Owner | Team |
|---|---|---|
| calendar_booking | General Leia | Executive Office |
| planet_help | Rebel Defense Team | Defense Team |
| recruitment | Rebel Recruitment Team | Recruitment Team |
| soldier_support | Operations Team | Operations |
| population_training | Luke Skywalker + Ben Kenobi | Jedi Training & Diplomacy Team |
| logistics | Han Solo | Logistics Team |
| investor_partner | Partnerships Team | Partnerships |
| urgent_security | Security Team | Security Team |
| jedi_training_diplomacy | Luke Skywalker + Ben Kenobi | Jedi Training & Diplomacy Team |
| ahsoka_special_mission | Ahsoka Tano | Special Mission Review |
| yoda_encrypted_strategy | Yoda | Jedi Council |
| field_operations | Chewbacca | Field Operations |
| special_protection | Din Djarin | Protection Team |
| data_support | R2-D2 | Operations Analytics |
| other | Operations Team | Intake Review |

## Security rules
- High-risk keywords (≥50 risk): emperor palpatine, darth vader, secret rebel base, private leia schedule, bypass security, rebel intelligence, sith, imperial surveillance, sabotage, spying, infiltration
- Medium-risk keywords (+10 each): empire, imperial forces, stormtroopers, imperial patrol
- Sender names "emperor palpatine" and "darth vader" guarantee risk ≥50 regardless of content
- Yoda strategy → encrypted with demo reverse-string cipher, creates EncryptedTransmission record
- Leia's private calendar → stored but never exposed via public API
- Security output includes: security_risk (low/medium/high), dark_side_indicators list, trusted_request boolean
- Every routed request creates a Task record
- SECURITY_REVIEW messages are classified and notified but held at router (no task created)

## API endpoints
- `GET /health` — Health check
- `POST /requests/whatsapp` — Submit via Intergalactic WhatsApp
- `POST /requests/hologram-email` — Submit via Hologram Email
- `GET /requests` — List all requests
- `GET /requests/<id>` — Get single request
- `GET /tasks` — List all generated tasks
- `POST /demo/seed` — Load 16 demo messages
- `POST /demo/run-all` — Load demo + return routing summary
- `GET /briefings/daily` — Get daily Hologram Briefing
- `POST /briefings/generate` — Generate briefing
- `GET /api/briefing/inbox` — Morning Briefing inbox data (messages, tasks, delegation, schedule)
- `GET /api/integrations` — Integration status (which services are configured)
- `GET /api/requests/<id>/trace` — Get pipeline trace for a request
- `GET /webhooks/whatsapp` — WhatsApp webhook verification
- `POST /webhooks/whatsapp` — WhatsApp webhook incoming message
- `POST /webhooks/gmail` — Gmail webhook notification
- `POST /api/intake` — Submit a message (legacy, specify channel)
- `GET /api/agents` — List all 9 agents in the pipeline
- `GET /api/calendar` — List public calendar bookings
- `POST /api/reset` — Reset all in-memory state
- `POST /webhooks/clickup` — ClickUp webhook event
