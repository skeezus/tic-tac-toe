# Tic-Tac-Toe

Multiplayer browser Tic-Tac-Toe: React frontend, FastAPI backend, WebSockets. See [CLAUDE.md](./CLAUDE.md) for requirements and architecture.

## Run locally

**Backend** (from project root):

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (in another terminal):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Connect → Create game (or paste game ID and Join). Use a second browser/device to join the same game and play.

## Project layout

- `backend/` — FastAPI app, WebSocket handler, in-memory game store, server-side rules
- `frontend/` — Vite + React, minimal UI, renders server state only
