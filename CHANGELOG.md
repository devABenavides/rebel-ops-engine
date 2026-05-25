# Changelog

## [2.1.0] — 2026-05-25

### Added
- **SQLite persistence** — new `database.py` module with 4 tables (messages, tasks, calendar_bookings, encrypted_transmissions), WAL journaling, JSON serialization for complex fields
- **Shared Database instance** — all storage-backed agents (ReportingAgent, RoutingAgent, ErrorProtocolAgent, CalendarAgent, YodaEncryptionAgent) accept a shared `Database` instance; defaults to `:memory:` for test isolation
- **Team Directory frontend page** — `Owners.jsx` with 19-character owner reference table including workflow role and business meaning
- **Missing status values** — `SCHEDULED`, `IN_PROGRESS`, `ESCALATED_TO_LEIA` added to `MessageStatus` enum
- **Grogu Care protocol enhancement** — `requires_leia=True`, `security_risk="high"`, and restriction details set on Grogu Care route

### Changed
- **Pipeline finalization** — `run_pipeline()` now persists final message status via `db.insert_message()` after pipeline completes (agents only add trace entries)
- **`.env.example`** — added `DATABASE_PATH` environment variable for SQLite file location

### Fixed
- Documentation updated to reflect SQLite-backed storage instead of in-memory dicts/lists

## [2.0.0] — 2026-05-15

### Added
- **Calendar confirmation flow** — interactive HTML confirmation endpoint (`GET /api/calendar/confirm/<id>/<slot>`) with slot selection, Google Calendar event creation, and confirmation email
- **Webhook integrations** — WhatsApp webhook verification + incoming message parsing, Gmail webhook notification, ClickUp webhook endpoint
- **ClickUp task sync** — background thread syncs both routing tasks and error protocol tasks to ClickUp API
- **Channel-specific notification templates** — Ahsoka Tano special mission, Din Djarin protection protocol, Luke Skywalker + Ben Kenobi Jedi assignment, Yoda encrypted transmission, BB-8 security alerts, calendar proposal confirmations
- **`_proposal_template`** — calendar slot proposal notification template with per-slot confirmation links
- **Integration status endpoint** (`GET /api/integrations`) — reports which external services are configured
- **Morning Briefing inbox endpoint** (`GET /api/briefing/inbox`) — structured data for frontend dashboard including messages, tasks, delegation breakdown, schedule
- **Frontend light theme redesign** — new CommandCenter, WorkflowGraph, Briefing, Calendar, Tasks, MorningBriefing page components
- **ErrorBoundary component** — React error boundary wrapper
- **Inline thread execution** — `threading.Thread.start` patched to run synchronously in tests, removing `time.sleep` race conditions

### Changed
- **Pipeline order** — CalendarAgent moved after YodaEncryptionAgent (encrypt before booking)
- **CalendarAgent** — added proposal-based booking flow with `AWAITING_CONFIRMATION` status + private calendar enforcement using `contains_private_leia_info`
- **RoutingAgent** — Grogu Care protocol triggers on force-sensitive child detection; SECURITY_REVIEW items held without task creation
- **ErrorProtocolAgent** — async ClickUp sync; separate task templates for quarantined vs error messages
- **NotificationAgent** — full channel dispatch logic with category-specific templates for urgent_security, ahsoka_special_mission, special_protection, jedi_training_diplomacy, yoda_encrypted_strategy
- **ReportingAgent** — `generate_daily_briefing` method returning structured `DailyBriefing` dataclass
- **`clients.py`** — refactored into full integration client classes (WhatsAppClient, HologramEmailClient, CalendarClient, NotificationClient, ReportDeliveryClient) with HTML briefing template (`_briefing_html`)
- **Test count** — agent tests grew from ~18 to 70, engine tests from ~32 to 52 (previously)

### Fixed
- Pipeline `AGENT_REGISTRY` order now matches documented pipeline order
- Test counts in documentation updated to reflect actual collected tests

## [1.0.0] — 2026-05-13

### Added
- **Initial release** — Rebel Operations Engine MVP
- **9-agent pipeline**: IntakeAgent → DarkSideSecurityAgent → C3POClassifierAgent → RoutingAgent → YodaEncryptionAgent → CalendarAgent → NotificationAgent → ReportingAgent → ErrorProtocolAgent
- **Dual-channel intake**: Intergalactic WhatsApp + Hologram Email
- **Dark Side security scanning**: keyword scoring (high-risk, medium-risk, sensitive keywords), sender-based risk (Palpatine/Vader guarantee ≥50), FLAGGED / SECURITY_REVIEW / QUARANTINED thresholds
- **15-category classifier**: rule-based C3PO classifier with Jedi case type detection
- **Routing engine**: category-to-owner/team mapping, Task record creation
- **Yoda encrypted strategy**: reverse-string demo cipher, EncryptedTransmission records
- **Calendar booking**: Google Calendar API integration with private calendar enforcement
- **Notification templates**: hologram acknowledgment, quarantine alert
- **Daily Hologram Briefing**: text report with category/owner breakdown, critical items, security risks, Leia decisions, blocked items, public calendar
- **16 demo messages** covering every category and edge case
- **In-memory state**: all agents resettable via API
- **Flask API**: health, intake, messages, tasks, agents, demo, briefing, reset, calendar endpoints
- **React + Vite frontend**: CommandCenter dashboard, WorkflowGraph, Briefing, Calendar, Tasks, MessageForm
- **OpenCode automation**: repo-audit, test-strategist, documentation-maintainer, security-auditor skills
- **CI pipeline**: GitHub Actions with ruff lint + pytest on push/PR
- **Mock integrations**: all external APIs (Gmail, Google Calendar, Meta WhatsApp, ClickUp) auto-mock when credentials absent
