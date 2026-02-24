# syntax=docker/dockerfile:1
# Use Debian-based image so Rollup's optional native bindings (linux-x64-gnu) install correctly.
# Alpine (musl) can hit npm optional-deps bugs with @rollup/rollup-linux-x64-musl.
FROM node:20-slim

WORKDIR /app

# Install dependencies (npm ci can skip optional deps; explicit install works around npm#4828)
COPY package.json package-lock.json* ./
RUN npm ci && npm install @rollup/rollup-linux-x64-gnu --no-save

# Copy source (vite.config uses BACKEND_URL at runtime)
COPY . .

# Backend URL for proxy when running in Docker (override at runtime if needed)
ENV BACKEND_URL=http://backend:8000

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
