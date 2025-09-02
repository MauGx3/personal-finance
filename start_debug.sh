#!/usr/bin/env bash
set -euo pipefail
echo "=== Debug start script ==="
echo "User: $(whoami)"
echo "PWD: $(pwd)"
echo "Python candidates:"
if [ -x ./.venv/bin/python ]; then
  echo "./.venv/bin/python ->"
  ./.venv/bin/python -V || true
  ./.venv/bin/python -m pip --version || true
  ./.venv/bin/python -m pip list || true
fi
echo "system python ->"
python -V || true
python -m pip --version || true
python -m pip list || true
echo "=== End python info ==="

# Run the normal start command
if [ -x ./.venv/bin/python ]; then
  exec ./.venv/bin/python -m gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:$PORT personal_finance.web_gui:app
else
  exec python -m gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:$PORT personal_finance.web_gui:app
fi
