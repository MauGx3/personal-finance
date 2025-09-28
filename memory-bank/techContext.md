# Tech Context

Last updated: 2025-09-28

## Languages & Frameworks

- Python 3.11+/3.13 (pyproject and compiled caches suggest 3.13 present)
- Django-style project layout with ASGI/WSGI entrypoints (`config/asgi.py`, `config/wsgi.py`)
- Celery for background tasks (`config/celery_app.py`)

## Key Libraries

- Polars (preferred over pandas for analytics per project instructions)
- DataProfiler for data quality/PII detection
- yfinance for market data (planned)
- pytest for testing; pytest-benchmark optionally
- ruff for linting/formatting (if configured)

## Tooling

- Docker + Docker Compose for local and production-like environments
- Procfile for PaaS runtimes
- Sphinx for docs
- Justfile for developer shortcuts

## Environments

- Local development via `docker-compose.local.yml` and `just` recipes
- Production via `docker-compose.production.yml` and Portainer stack definitions
- Leapcell targeted PaaS with environment-driven configuration

## Constraints

• Avoid network access in unit tests; prefer recorded fixtures and mocks
• Ensure deterministic data types (Decimal for monetary amounts)
• Keep secrets out of repo; use environment variables
