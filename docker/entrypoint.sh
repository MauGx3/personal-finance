#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Starting Personal Finance service"
echo "[entrypoint] Python: $(python --version)"

if [[ "${RUN_MIGRATIONS_ON_START:-0}" == "1" ]]; then
  echo "[entrypoint] Applying Django migrations..."
  python manage.py migrate || echo "[entrypoint][warning] Django migration failed"

  echo "[entrypoint] Collecting static files..."
  python manage.py collectstatic --noinput || echo "[entrypoint][warning] Collectstatic failed"
fi

echo "[entrypoint] Launching: $*"
exec "$@"
