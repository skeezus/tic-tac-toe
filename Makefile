.PHONY: install run run-backend run-frontend docker-up docker-down docker-build

# Install backend and frontend dependencies
install:
	cd backend && poetry install
	cd frontend && npm install

# Run backend and frontend together (Ctrl+C stops both)
run:
	@trap 'kill 0' INT; \
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & \
	cd frontend && npm run dev & \
	wait

# Run backend only
run-backend:
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend only
run-frontend:
	cd frontend && npm run dev

# Run with Docker (no local Node/Python needed)
docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down
