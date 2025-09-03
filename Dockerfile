## Clean hardened multi-stage Dockerfile for Personal Finance FastAPI service
## Hardened multi-stage Dockerfile for Personal Finance service
## Security goals:
##  - Minimal base (python:3.11-slim-bookworm with explicit patch)
##  - No build toolchain in final image
##  - Non-root runtime user
##  - Stdlib-only healthcheck (no curl)
##  - Deterministic dependency install using constraints if present

ARG PYTHON_VERSION=3.11.9

#############################
# Builder
#############################
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY constraints.txt requirements.txt requirements.lock pyproject.toml README.md ./
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel --no-cache-dir \
    && pip install --no-cache-dir -r requirements.txt -c constraints.txt \
    && if [ -f requirements.lock ]; then pip install --no-cache-dir -r requirements.lock; fi

COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic
RUN pip wheel . -w /wheels

#############################
# Runtime
#############################
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000 APP_MODULE=personal_finance.web_gui:app PATH="/opt/venv/bin:$PATH"
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/personal_finance-*.whl || true

COPY alembic.ini ./
COPY alembic ./alembic
COPY src ./src
COPY requirements.txt constraints.txt requirements.lock* ./
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN adduser --system --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Simple healthcheck: return 0 if /health responds 200, else 1
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,sys,urllib.request;u=f'http://127.0.0.1:{os.environ.get('PORT','8000')}/health';\nimport urllib.error;\ntry: sys.exit(0 if urllib.request.urlopen(u, timeout=4).status==200 else 1)\nexcept Exception: sys.exit(1)"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "personal_finance.web_gui:app"]

