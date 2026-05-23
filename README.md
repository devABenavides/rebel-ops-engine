# Star Wars Agents — Rebel Operations Engine
### AI-Powered Request Management System for Founders & Remote Teams

General Leia is a busy executive managing the Rebellion. Requests arrive through Intergalactic WhatsApp and Hologram Email. Instead of reviewing everything manually, this multi-agent system automates the entire workflow — classifying, routing, and responding to operational requests from across the galaxy.

**Automation does not replace the entrepreneur. It protects the entrepreneur's time.** The entrepreneur should only handle high-value decisions, VIP meetings, and final escalations.

Built as an MVP with Flask and React. Every external integration (Gmail, Google Calendar, Meta WhatsApp, ClickUp) works for real when configured and falls back to a logged mock when it isn't.

## What this does

- **Automatic request classification** — C3POClassifierAgent categorizes incoming messages into 15 operational categories and routes to the right owner or team
- **Dark Side security scanning** — DarkSideSecurityAgent scores risk from message content and sender identity, quarantines high-threat requests (≥50 risk), flags medium-risk for security review
- **Encrypted strategic routing** — YodaEncryptionAgent encrypts sensitive transmissions with a swappable cipher (demo default: reverse-string). Production deployment would replace this with AES-256 or equivalent enterprise encryption.
- **Calendar management** — CalendarAgent books events via Google Calendar API, enforces Leia's private calendar protection, sends confirmation links
- **Multi-channel notifications** — NotificationAgent sends channel-specific templates (WhatsApp via Meta Cloud API, Hologram Email via Gmail API, BB-8 alerts, quarantine alerts)
- **Automated task creation** — RoutingAgent + ErrorProtocolAgent create prioritized tasks synced to ClickUp API
- **Daily Hologram Briefing** — ReportingAgent generates a full operational summary by category, owner, and urgency, delivered via Gmail
- **Real-time dashboard** — React + Vite frontend with command center, workflow graph, inbox, calendar, and task views
- **Webhook integration** — Accepts incoming messages via WhatsApp and Gmail webhooks, syncs tasks to ClickUp
- **Full audit trail** — Every request carries a pipeline trace; all in-memory state is resettable via API

## Why I built this

I built this to demonstrate how an executive assistant — powered by AI agents — can help a busy entrepreneur manage the chaos of incoming requests.

General Leia is the model for every modern founder or CEO. Requests flood in through multiple channels (WhatsApp, email). Each one needs to be read, understood, classified, secured, and routed to the right person. Some contain sensitive information that must be encrypted. Some are threats that must be blocked. Some need calendar coordination. Others need operational follow-up.

Without automation, this is a full-time job just to triage. The entrepreneur gets buried in noise instead of focusing on high-value decisions, VIP relationships, and strategic direction.

This system shows what happens when you give an executive a team of AI agents that handle the full lifecycle — from intake to security scanning to classification to routing to notification to calendar booking to daily reporting. The entrepreneur only steps in for what truly needs their judgment.

**Automation does not replace the entrepreneur. It protects the entrepreneur's time.**

## Impact

Without this system, a founder managing 50+ daily requests spends:
→ 2-3 hours/day on manual triage and routing
→ 30-45 min/day creating tasks manually in ClickUp
→ 20-30 min/day scheduling meetings and sending confirmations
→ High risk of missed follow-ups and lost requests

With this system:
→ 100% of requests classified automatically in <2 seconds
→ 0 manual task creation in ClickUp
→ 0 manual calendar coordination for standard requests
→ Full audit trail for every request
→ Daily briefing delivered automatically every morning
→ Founder only handles: VIP decisions, escalations, strategy

## Architecture

```
→ Agent 1: IntakeAgent — normalize incoming requests from WhatsApp / Hologram Email
→ Agent 2: DarkSideSecurityAgent — risk scoring, threat quarantine
→ Agent 3: C3POClassifierAgent — category + owner assignment (15 categories)
→ Agent 4: RoutingAgent — creates Task records, holds SECURITY_REVIEW items
→ Agent 5: YodaEncryptionAgent — encrypted transmission for Yoda strategy
→ Agent 6: CalendarAgent — Google Calendar booking, private calendar enforcement
→ Agent 7: NotificationAgent — multi-channel acknowledgment templates
→ Agent 8: ReportingAgent — daily Hologram Briefing generation + delivery
→ Agent 9: ErrorProtocolAgent — error handling, ClickUp task sync
→ Dashboard: React + Vite frontend (CommandCenter, WorkflowGraph, Briefing, Calendar, Tasks)
```

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.14, Flask 3.1 |
| Frontend | React 19, Vite 6, JavaScript (JSX), plain CSS |
| Integrations | Gmail API, Google Calendar API, Meta WhatsApp Cloud API, ClickUp API |
| Testing | pytest 8.3, pytest-cov |
| Linting | ruff |
| Auth (integrations) | OAuth 2.0 (Google), Bearer token (Meta, ClickUp) |
| Config | python-dotenv, .env.example |

## Demo

[Screenshot / video link]

## Getting Started

The project lives in the `rebel_ops_engine/` directory.

```bash
cd rebel_ops_engine
pip install -r requirements.txt
python main.py
```

The server starts at `http://localhost:5000`.

See [`rebel_ops_engine/README.md`](rebel_ops_engine/README.md) for full documentation including setup, demo script, API endpoints, architecture, and security notes.

## Frontend

```bash
cd rebel_ops_engine/frontend
npm install
npm run dev
```

Opens at `http://localhost:3000`.

## Tests

```bash
cd rebel_ops_engine
python -m pytest tests/ -v
```

## Lint

```bash
cd rebel_ops_engine
python -m ruff check .
```

## Environment

```bash
cd rebel_ops_engine
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/macOS
```

No environment variables are needed for the demo — all integrations fall back to mocks. Add real credentials to connect with live APIs.

## Built-in Project Automation

This repository includes OpenCode skills and agents to automate maintenance, quality, and security tasks:

| Skill / Agent | What it does |
|---|---|
| **documentation-maintainer** | Reviews and improves project documentation (README, AGENTS.md, setup, architecture). Run with `update-docs` command. |
| **repo-audit** | Read-only technical audit covering architecture, correctness, security, performance, testing, and developer experience. Produces prioritized findings (P0–P3). |
| **test-strategist** | Reviews the testing setup and produces a practical improvement plan focused on high-value, safety-critical tests. |
| **security-auditor** | Inspects code for secrets, auth, input validation, API boundaries, dependency risks, and sensitive data exposure. Returns findings with severity levels. |
| **implement-audit-plan** | Applies only explicitly approved findings from a repo audit — focused, validated changes with security checks. |
| **workflow-evaluator** | Evaluates OpenCode session quality, scoring workflow order, rule compliance, and implementation quality with a PASS / REWORK verdict. |

## AI / Maintainer Context

See [`AGENTS.md`](AGENTS.md) for the full agent pipeline, routing rules, security rules, API endpoints, and key file reference.

## Built by

**Alexandra Benavides**  
Bilingual Executive Assistant & Operations Coordinator  
Founder Support | AI Systems | Agile Delivery | Remote US/LATAM

I build operational AI systems for founders and remote teams —
and I run the operations they support.

→ https://www.linkedin.com/in/alexandrabenavidesc/ 
→ alexandra.benavides@gmail.com
