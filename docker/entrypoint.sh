#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Starting Personal Finance service"
echo "[entrypoint] Python: $(python --version)"

# If DATABASE_URL is provided, derive POSTGRES_HOST and POSTGRES_PORT so
# older scripts or settings that expect POSTGRES_HOST/POSTGRES_PORT don't fail.
if [ -n "${DATABASE_URL:-}" ]; then
  # DATABASE_URL formats: postgres://user:pass@host:port/db or postgresql+psycopg2://...
  proto_and_rest=${DATABASE_URL#*://}
  host_and_rest=${proto_and_rest#*@}
  HOST_PORT=${host_and_rest%%/*}
  # If HOST_PORT contains a colon, split host and port; otherwise default port to 5432
  if [[ "$HOST_PORT" == *:* ]]; then
    POSTGRES_HOST=${HOST_PORT%%:*}
    POSTGRES_PORT=${HOST_PORT##*:}
  else
    POSTGRES_HOST=$HOST_PORT
    POSTGRES_PORT=5432
  fi
  export POSTGRES_HOST POSTGRES_PORT
  echo "[entrypoint] Derived POSTGRES_HOST=${POSTGRES_HOST} POSTGRES_PORT=${POSTGRES_PORT}"
fi

if [[ "${RUN_MIGRATIONS_ON_START:-0}" == "1" ]]; then
  echo "[entrypoint] Applying Django migrations..."
  python manage.py migrate || echo "[entrypoint][warning] Django migration failed"

  echo "[entrypoint] Collecting static files..."
  python manage.py collectstatic --noinput || echo "[entrypoint][warning] Collectstatic failed"
fi

echo "[entrypoint] Launching: $*"
exec "$@"
