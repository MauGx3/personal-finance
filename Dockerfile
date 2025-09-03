## Multi-stage Dockerfile for the Personal Finance FastAPI service
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY constraints.txt requirements.txt requirements.lock pyproject.toml README.md ./

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt -c constraints.txt \
    && if [ -f requirements.lock ]; then pip install -r requirements.lock; fi

COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic
RUN pip wheel . -w /wheels

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000 \
    APP_MODULE=personal_finance.web_gui:app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl \
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

RUN useradd -ms /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD curl -f http://127.0.0.1:${PORT}/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "personal_finance.web_gui:app"]
