# Rebel Operations Engine — Frontend

React + Vite UI for the Rebel Operations Engine backend.

## Stack

| Layer | Choice |
|---|---|
| Framework | React 19 |
| Bundler | Vite 6 |
| Language | JavaScript (JSX) |
| Styling | Plain CSS |
| API client | Custom `fetch` wrapper (`api.js`) |
| State | React hooks (`useState`, `useEffect`) |

## How to Run

```bash
# Install dependencies (first time only)
npm install

# Start dev server (port 3000)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

The dev server at `http://localhost:3000` proxies API calls to `http://localhost:5000` (Flask backend). Both must be running simultaneously.

## Proxy Configuration

Defined in `vite.config.js`. Every request to these paths is forwarded to Flask:

| Frontend path | Proxied to |
|---|---|
| `/api/*` | `http://localhost:5000/api/*` |
| `/requests/*` | `http://localhost:5000/requests/*` |
| `/tasks*` | `http://localhost:5000/tasks*` |
| `/demo*` | `http://localhost:5000/demo*` |
| `/briefings*` | `http://localhost:5000/briefings*` |
| `/health` | `http://localhost:5000/health` |

## Component Structure

```
src/
  main.jsx               — ReactDOM entry point
  App.jsx                — Root layout, sidebar nav, page routing
  App.css                — All styles (light theme)
  api.js                 — API client (BASE = '/api')
  components/
    CommandCenter.jsx    — Dashboard with message list, stats, delegation overview
    WorkflowGraph.jsx    — Interactive SVG pipeline architecture diagram
    Briefing.jsx         — Daily Hologram Briefing display
    Owners.jsx           — Team Directory (19-character owner reference)
    MessageForm.jsx      — Send a message via WhatsApp or Email
    Calendar.jsx         — Public calendar bookings
    Tasks.jsx            — Generated task list
    MorningBriefing.jsx  — Enhanced morning briefing dashboard with stats, delegation, calendar
    MorningBriefing.css  — Styles for the morning briefing component
    Architecture.css     — Styles for the WorkflowGraph component
    ErrorBoundary.jsx    — React error boundary wrapper
```

Components are page-level — each mapped to a sidebar tab in `App.jsx`.

## API Client (`api.js`)

All API calls go through the `api` object. Every method returns a Promise.

```javascript
import { api } from './api.js'

// Read endpoints
const messages = await api.messages()
const briefing = await api.briefing()     // { briefing: "..." }
const tasks = await api.tasks()
const calendar = await api.calendar()
const agents = await api.agents()
const status  = await api.status()
const inbox   = await api.inbox()        // Morning Briefing data
const integrations = await api.integrations()  // Service status

// Write endpoints
const result = await api.intake("intergalactic_whatsapp", "Han Solo", "Need fuel")
await api.demoLoad()
await api.reset()
```

The client automatically parses JSON responses and throws on HTTP errors. All requests time out after 15 seconds.

## Building for Production

```bash
npm run build
```

Output goes to `dist/`. Serve the `dist/` folder behind the Flask backend or a static file server. The proxy config is for development only — in production, either serve the frontend from Flask or configure your reverse proxy manually.
