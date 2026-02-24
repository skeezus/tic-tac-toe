# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Install Poetry
ENV POETRY_VERSION=1.8.5
ENV POETRY_HOME=/opt/poetry
ENV PATH="${POETRY_HOME}/bin:${PATH}"
RUN pip install --no-cache-dir poetry=="${POETRY_VERSION}"

# Install dependencies (no dev deps)
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-root

# Application
COPY app ./app

# Cloud Run sets PORT=8080; default 8000 for local runs
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
