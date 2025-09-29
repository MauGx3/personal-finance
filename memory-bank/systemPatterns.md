# System Patterns

Last updated: 2025-09-28

This document captures key architectural patterns and decisions that guide implementation across the repository.

## Architecture overview

- Web application stack using Django-style project layout under `config/` with ASGI/WSGI entrypoints and URL routing.
- Background processing via Celery app stub (`config/celery_app.py`) for asynchronous tasks.
- Domain modules organized under `personal_finance/` (e.g., `analytics/`, `backtesting/`, `data_sources/`, `data_profiler/`).
- Documentation built with Sphinx (`docs/`) and developer usage guides in top-level `*_USAGE.md` files.
- Containerized runtime via Docker and Docker Compose for local, plus Portainer/Leapcell deployment artifacts.

## Configuration patterns

- 12-factor style configuration from environment variables; `.env` merging helpers exist for deployment.
- Separate compose files for local and production (`docker-compose.local.yml`, `docker-compose.production.yml`).
- Healthchecks and process managers defined by compose and Procfile for PaaS targets.

## Data and services patterns

- Data ingestion and market data adapters live under `personal_finance/data_sources/`. Aim for adapter pattern to allow provider swap (e.g., yfinance, mocks).
- Profiling and validation under `personal_finance/data_profiler/`, leveraging DataProfiler when available.
- Real-time capabilities planned under `personal_finance/realtime/` with asyncio/websocket-friendly design.

## Testing and quality

- Tests use `pytest` with configuration in `pytest.ini`.
- Prefer deterministic unit tests with network access disabled; use fixtures/mocks for external providers.
- Lint/format via project conventions (ruff/black if configured) and keep type hints where practical.

## Deployment

- Portainer stack support targeted; compose files and `deploy/` assets aim for simple rollout.
- PaaS compatibility (e.g., Leapcell) by minimizing stateful dependencies and using environment-driven config.
