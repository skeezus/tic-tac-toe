.PHONY: install run run-backend run-frontend test docker-up docker-down docker-build clean-pyc tf-init tf-plan tf-apply tf-destroy

# Remove Python bytecode cache (avoids Terraform file() issues, keeps tree clean)
clean-pyc:
	@find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Install backend and frontend dependencies
install:
	cd backend && poetry install
	cd frontend && npm install

# Run backend and frontend together (Ctrl+C stops both)
run: clean-pyc
	@trap 'kill 0' INT; \
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & \
	cd frontend && npm run dev & \
	wait

# Run backend only
run-backend: clean-pyc
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend only
run-frontend:
	cd frontend && npm run dev

# Run backend tests
test: clean-pyc
	cd backend && poetry run pytest tests/ -v

# Run with Docker (no local Node/Python needed)
docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down

# Terraform (GCP Cloud Run). Set PROJECT_ID=your-gcp-project for plan/apply.
PROJECT_ID ?= mangetakk

tf-init:
	terraform -chdir=terraform init

tf-plan: tf-init clean-pyc
	@if [ -z "$(PROJECT_ID)" ]; then echo "Usage: make tf-plan PROJECT_ID=your-gcp-project"; exit 1; fi
	terraform -chdir=terraform plan -var="project_id=$(PROJECT_ID)"

tf-apply: tf-init clean-pyc
	@if [ -z "$(PROJECT_ID)" ]; then echo "Usage: make tf-apply PROJECT_ID=your-gcp-project"; exit 1; fi
	terraform -chdir=terraform apply -var="project_id=$(PROJECT_ID)"

tf-destroy: tf-init
	@if [ -z "$(PROJECT_ID)" ]; then echo "Usage: make tf-destroy PROJECT_ID=your-gcp-project"; exit 1; fi
	terraform -chdir=terraform destroy -var="project_id=$(PROJECT_ID)"
