# Minimal, modern multi-stage Dockerfile for the personal-finance Django app
# Goals:
#  - small runtime image (no build toolchain)
#  - deterministic install of pinned production deps
#  - non-root runtime user
#  - simple python stdlib healthcheck

ARG PYTHON_VERSION=3.11.9

#############################
# Builder: install build deps and create a virtualenv with production deps
#############################
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /build

# Install build dependencies needed for wheels (psycopg, cryptography, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements to leverage Docker cache
COPY requirements/ ./requirements/
COPY pyproject.toml setup.cfg* ./

# Create isolated venv and install pinned production dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy the project sources and install the project package into the venv
COPY . .
RUN pip install --no-cache-dir .

#############################
# Runtime: small image with only the venv and app files
#############################
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app

# Only bring runtime OS deps (libpq for postgres drivers)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy venv from builder and application files
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build /app

# Make sure the repo entrypoint is executable and create a non-root user
RUN if [ -f /app/docker/entrypoint.sh ]; then chmod +x /app/docker/entrypoint.sh; fi \
    && addgroup --system appuser \
    && adduser --system --ingroup appuser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthcheck: use stdlib to probe /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,sys,urllib.request;u=f'http://127.0.0.1:{os.environ.get('PORT','8000')}/health';\n+try:\n+  sys.exit(0 if urllib.request.urlopen(u, timeout=4).status==200 else 1)\n+except Exception:\n  sys.exit(1)"

# Entrypoint should exist in repo at docker/entrypoint.sh; keep it executable
ENTRYPOINT ["/app/docker/entrypoint.sh"]
# Default: run Gunicorn with Uvicorn worker for ASGI (scales for websockets)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "config.asgi:application"]
