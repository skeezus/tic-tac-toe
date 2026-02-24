# Tic-Tac-Toe

Multiplayer browser Tic-Tac-Toe: React frontend, FastAPI backend, WebSockets. See [CLAUDE.md](./CLAUDE.md) for requirements and architecture.

## Run locally

**Prerequisites:** Node.js 18+ (frontend). Use `nvm use` if you have [nvm](https://github.com/nvm-sh/nvm); the repo includes an `.nvmrc` for Node 20.

**One command** (from project root):

```bash
make install   # first time only
make run       # backend + frontend together; Ctrl+C stops both
```

Open http://localhost:5173.

**With Docker** (no Node/Python installed):

```bash
make docker-up    # or: docker compose up --build
```

Then open http://localhost:5173. Stop with `Ctrl+C` or `make docker-down`.

**Or run separately (without Docker):**

```bash
# Backend
cd backend && poetry install && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (another terminal)
cd frontend && npm install && npm run dev
```

Connect → Create game (or paste game ID and Join). Use a second browser/device to join the same game and play.

## Deploy to GCP Cloud Run

From the repo root, with [Terraform](https://www.terraform.io/) and [gcloud](https://cloud.google.com/sdk) configured:

```bash
terraform -chdir=terraform init
terraform -chdir=terraform apply -var="project_id=YOUR_GCP_PROJECT_ID"
```

Then open the frontend URL from the output (`terraform -chdir=terraform output frontend_url`). See [terraform/README.md](terraform/README.md) for details.

## Project layout

- `backend/` — FastAPI app, WebSocket handler, in-memory game store, server-side rules
- `frontend/` — Vite + React, minimal UI, renders server state only
- `terraform/` — GCP Cloud Run deploy (Artifact Registry, Cloud Build, two Cloud Run services)
