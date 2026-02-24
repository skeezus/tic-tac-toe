variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "mangetakk"
}

variable "region" {
  description = "GCP region for Artifact Registry and Cloud Run"
  type        = string
  default     = "us-central1"
}

variable "backend_path" {
  description = "Path to backend directory (relative to repo root)"
  type        = string
  default     = "backend"
}

variable "frontend_path" {
  description = "Path to frontend directory (relative to repo root)"
  type        = string
  default     = "frontend"
}
