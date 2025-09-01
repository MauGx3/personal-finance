#!/usr/bin/env bash
set -euo pipefail

# Install project dependencies
pip install -e .

# Wait for postgres service inside the compose network
./.devcontainer/wait-for-postgres.sh db 5432

# Initialize database if not already initialized
python setup_database.py || true
