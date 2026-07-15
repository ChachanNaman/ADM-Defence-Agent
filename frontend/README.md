# adm-defender — Frontend

React 19 + Tailwind 4 + Vite UI for the ADM Defense Agent.

## What it does

A three-panel interface that lets a user review inbound ADMs and run the agent against them:

- **AdmSidebar** — list of all ADMs with status badges
- **AdmNoticePanel** — raw ADM detail + joined PNR record
- **AgentPanel** — "Run Agent" button, live decision badge (DISPUTE / PAY / ESCALATE), and the output artifact with copy-to-clipboard

## Tech

- React 19 with TypeScript
- Tailwind 4 for styling
- Vite for dev server and build
- Plain `fetch` for API calls via `lib/api.ts`
- No state library — component-local state is sufficient at this scale
- No auth/login — not in scope for the demo

## Available Scripts

```bash
npm install       # install dependencies
npm run dev       # start dev server (default :5173)
npm run build     # production build
npm run preview   # preview production build
npm run lint      # run oxlint
```

## Backend connection

The dev server proxies `/api` requests to `http://localhost:8000` (configured in `vite.config.ts`). The backend must be running locally for the UI to function.

## What's wired vs. not

The synchronous `POST /agent/run/{adm_id}` endpoint is wired into the UI. A WebSocket endpoint (`WS /ws/agent/{adm_id}`) exists on the backend for live step-by-step streaming but is not yet connected in the frontend — that's the natural next enhancement.
