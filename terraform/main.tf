data "google_project" "project" {
  project_id = var.project_id
}

locals {
  repo_root      = abspath("${path.module}/..")
  backend_dir    = "${local.repo_root}/${var.backend_path}"
  frontend_dir   = "${local.repo_root}/${var.frontend_path}"
  repository_id  = "tic-tac-toe"
  backend_image  = "${var.region}-docker.pkg.dev/${var.project_id}/${local.repository_id}/backend:latest"
  frontend_image = "${var.region}-docker.pkg.dev/${var.project_id}/${local.repository_id}/frontend:latest"
  cloudbuild_sa  = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

# Enable required APIs
resource "google_project_service" "run" {
  project            = var.project_id
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifactregistry" {
  project            = var.project_id
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudbuild" {
  project            = var.project_id
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

# Artifact Registry repository for container images
resource "google_artifact_registry_repository" "repo" {
  project       = var.project_id
  location      = var.region
  repository_id = local.repository_id
  format        = "DOCKER"

  depends_on = [google_project_service.artifactregistry]
}

# Allow Cloud Build to push images to Artifact Registry
resource "google_artifact_registry_repository_iam_member" "cloudbuild_writer" {
  project    = google_artifact_registry_repository.repo.project
  location   = google_artifact_registry_repository.repo.location
  repository = google_artifact_registry_repository.repo.name
  role       = "roles/artifactregistry.writer"
  member     = local.cloudbuild_sa
}

# Build and push backend image (requires gcloud CLI and Cloud Build)
resource "null_resource" "backend_build" {
  triggers = {
    dockerfile = md5(file("${local.backend_dir}/Dockerfile"))
    app        = md5(join("", [for f in fileset("${local.backend_dir}/app", "**") : file("${local.backend_dir}/app/${f}")]))
  }

  provisioner "local-exec" {
    command     = "gcloud builds submit --tag ${local.backend_image} ${local.backend_dir}"
    working_dir = local.repo_root
  }

  depends_on = [
    google_project_service.cloudbuild,
    google_artifact_registry_repository.repo,
  ]
}

# Build and push frontend image (uses Dockerfile.prod)
resource "null_resource" "frontend_build" {
  triggers = {
    dockerfile = md5(file("${local.frontend_dir}/Dockerfile.prod"))
    app        = md5(join("", [for f in fileset("${local.frontend_dir}/src", "**") : file("${local.frontend_dir}/src/${f}")]))
  }

  provisioner "local-exec" {
    command     = "gcloud builds submit ${local.frontend_dir} --config=${local.frontend_dir}/cloudbuild.yaml --substitutions=_IMAGE=${local.frontend_image}"
    working_dir = local.repo_root
  }

  depends_on = [
    google_project_service.cloudbuild,
    google_artifact_registry_repository.repo,
  ]
}

# Backend Cloud Run service
resource "google_cloud_run_v2_service" "backend" {
  name     = "tic-tac-toe-backend"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = local.backend_image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
  }

  depends_on = [
    google_project_service.run,
    null_resource.backend_build,
  ]
}

# Frontend Cloud Run service (needs BACKEND_URL from backend service)
resource "google_cloud_run_v2_service" "frontend" {
  name     = "tic-tac-toe-frontend"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = local.frontend_image

      env {
        name  = "BACKEND_URL"
        value = google_cloud_run_v2_service.backend.uri
      }

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
      }
    }
  }

  depends_on = [
    google_project_service.run,
    null_resource.frontend_build,
  ]
}

# Allow unauthenticated access to both services (public app)
resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  name     = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  name     = google_cloud_run_v2_service.frontend.name
  location = google_cloud_run_v2_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
