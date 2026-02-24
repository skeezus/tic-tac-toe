# Deploy Tic-Tac-Toe to GCP Cloud Run

This Terraform config builds the backend and frontend containers, pushes them to Artifact Registry, and deploys two Cloud Run services (backend + frontend). The frontend is configured with the backend URL at deploy time so the app works end-to-end.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.5
- [gcloud](https://cloud.google.com/sdk/docs/install) CLI, authenticated and set to your project
- GCP project with billing enabled

## Setup

1. Authenticate and set project:

   ```bash
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. From the **repository root** (not inside `terraform/`), run:

   ```bash
   terraform -chdir=terraform init
   terraform -chdir=terraform plan -var="project_id=YOUR_PROJECT_ID"
   terraform -chdir=terraform apply -var="project_id=YOUR_PROJECT_ID"
   ```

   Or use a `terraform.tfvars` file:

   ```hcl
   project_id = "your-gcp-project-id"
   region     = "us-central1"
   ```

   Then:

   ```bash
   terraform -chdir=terraform init
   terraform -chdir=terraform apply
   ```

3. After apply, open the frontend URL:

   ```bash
   terraform -chdir=terraform output frontend_url
   ```

## What gets created

- **APIs enabled:** Cloud Run, Artifact Registry, Cloud Build
- **Artifact Registry** repo: `tic-tac-toe` in your region
- **Images:** Built via Cloud Build from `backend/` and `frontend/` (frontend uses `Dockerfile.prod`)
- **Cloud Run services:** `tic-tac-toe-backend` and `tic-tac-toe-frontend`, both public (`allUsers` can invoke)

## CORS

The backend allows all origins (`allow_origins=["*"]`). For a production lock-down, restrict to your frontend URL in `backend/app/main.py`.
