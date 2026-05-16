# Star Wars Agents — Rebel Operations Engine

This repository contains the **Rebel Operations Engine**, a local agentic application for the Rebel Alliance to process, classify, route, and respond to operational requests from across the galaxy. Built as an MVP with Flask, React, and replaceable mock integrations.

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
