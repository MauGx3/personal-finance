#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Starting Personal Finance service"
echo "[entrypoint] Python: $(python --version)"

if [[ "${RUN_MIGRATIONS_ON_START:-0}" == "1" ]]; then
  echo "[entrypoint] Applying Alembic migrations..."
  alembic upgrade head || echo "[entrypoint][warning] Alembic migration failed"
fi

echo "[entrypoint] Launching: $*"
exec "$@"
