#!/usr/bin/env bash
# Usage: wait-for-postgres.sh host port
set -euo pipefail

HOST="$1"
PORT="$2"

echo "Waiting for PostgreSQL at ${HOST}:${PORT}..."

until pg_isready -h "${HOST}" -p "${PORT}" >/dev/null 2>&1; do
  sleep 1
done

echo "Postgres is ready"
