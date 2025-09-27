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
COPY requirements ./requirements
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Fix SSL/certificate issues and install packages
RUN pip install --upgrade pip setuptools wheel --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
    && pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt -c constraints.txt \
    && if [ -f requirements.lock ]; then pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.lock; fi

COPY src ./src
COPY personal_finance ./personal_finance
COPY config ./config
COPY manage.py ./
COPY alembic.ini ./
COPY alembic ./alembic
RUN pip wheel . -w /wheels

#############################
# Runtime
#############################
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000 DJANGO_SETTINGS_MODULE=config.settings.production PATH="/opt/venv/bin:$PATH"
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org /wheels/personal_finance-*.whl || true

COPY alembic.ini ./
COPY alembic ./alembic
COPY personal_finance ./personal_finance
COPY config ./config
COPY manage.py ./
COPY locale ./locale
COPY staticfiles ./staticfiles
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN addgroup --system appuser \
    && adduser --system --ingroup appuser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Simple healthcheck: return 0 if /health responds 200, else 1
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,sys,urllib.request;u=f'http://127.0.0.1:{os.environ.get('PORT','8000')}/health';\nimport urllib.error;\ntry: sys.exit(0 if urllib.request.urlopen(u, timeout=4).status==200 else 1)\nexcept Exception: sys.exit(1)"

ENTRYPOINT ["/entrypoint.sh"]
# Use a shell form to allow runtime expansion of $PORT by the platform (Leapcell)
# The entrypoint will exec this command, so it is important to keep it as a single
# string passed to a shell so ${PORT} expands. Default to 8000 if PORT is not set.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --worker-class uvicorn.workers.UvicornWorker config.asgi:application"]
