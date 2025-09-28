# Logging in personal-finance

This document describes logging-related environment variables and recommendations
for running in development and containerized environments.

## Environment variables

- `PORTFOLIO_LOG_LEVEL` — controls the global log level for the package.
  Allowed values: `TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
  If unset or invalid, the default is `INFO`. When an invalid value is set a
  concise warning will be emitted to stderr explaining the fallback.

- `PORTFOLIO_CONTAINERIZED` — when set to `1` (or `true`) the application will
  emit structured JSON logs to stdout (via `loguru`'s `serialize=True`). This
  is recommended in container environments where logs are collected by a
  central agent (Filebeat, Fluentd, Promtail, etc.). When not set a human-
  readable, colorized log format is used for developer-friendly output.

## Recommendations

- In container images, set `PORTFOLIO_CONTAINERIZED=1` and ensure `PORTFOLIO_LOG_LEVEL`
  is set appropriately (usually `INFO` or `WARNING` for production).

- For local development, prefer `PORTFOLIO_CONTAINERIZED` unset and use `DEBUG`
  or `TRACE` when deep debugging is required. Avoid enabling `TRACE` in
  production.

- Structured logs emitted in container mode include fields such as timestamp,
  logger name, level, module, function, line, and message. Use your log
  pipeline to map and index those fields.

## Example docker-compose snippet

services:
  web:
    image: myapp:latest
    environment:
      - PORTFOLIO_CONTAINERIZED=1
      - PORTFOLIO_LOG_LEVEL=INFO

## Notes

The codebase provides a `PackageLogger` (in `src/personal_finance/logs/logger.py`) and
`loguru` compatibility wrapper (`src/personal_finance/logs/loguru_compat.py`).
These implement TRACE and the container-aware behavior described above.
