# AGENTS.md

Comprehensive instructions for autonomous coding agents working on this repository. This file complements `README.md` by providing actionable, machine-focused guidance.

## 1. Project Overview

- **Purpose**: Personal finance web platform built on Django, offering analytics, portfolio tooling, ETL jobs, and automation scripts.
- **Runtime**: Python 3.10/3.11 (validated in CI against both versions).
- **Primary stack**: Django, Celery, Channels/WebSockets, PostgreSQL (optional), Redis (for async tasks), Polars/finance utilities, pytest.
- **Security posture**: Django 4.2.24 (patched for CVE-2025-57833), CodeQL scanning enabled, CI enforces dependency audits via `pip-audit`.

### Architecture Snapshot

| Component | Location | Notes |
|-----------|----------|-------|
| Django project | `config/` + `personal_finance/` | Settings split under `config/settings/`; apps live under `personal_finance/` (analytics, assets, backtesting, etc.). |
| Celery workers | `config/celery_app.py` | Requires Redis; start separately. |
| Background scripts | `run_finance.py`, `setup_database.py`, `alembic/` | ETL + DB bootstrap. |
| Infrastructure | `docker-compose*.yml`, `Dockerfile`, `render.yaml`, `Procfile` | Local/production orchestrations. |
| Documentation | `/spec/`, `/docs/`, `/memory-bank/` | Specifications, Sphinx docs, running context. |

### Repository Layout Highlights

- `manage.py` — Django entry point for admin tasks, migrations, and dev server.
- `personal_finance/` — Main app modules, including API views, serializers, services, and tests.
- `tests/` — Pytest-based integration/unit suites.
- `config/` — Django settings, ASGI/WSGI endpoints, routers, Celery configuration.
- `alembic/` — Database migration scripts for non-Django schema changes.
- `spec/` — Process specs (CI/CD, PR checks). Update these before altering workflows.
- `memory-bank/` — Project intelligence used by agents after environment resets.

## 2. Environment Setup (fish shell)

### Prerequisites

- Python 3.10 or 3.11
- Redis (for Celery + websockets) — optional for basic dev but required for async features
- PostgreSQL optional (SQLite default if `DATABASE_URL` absent)

### Create and Activate Virtual Environment

```fish
python -m venv .venv
source .venv/bin/activate.fish
```

### Install Dependencies

```fish
python -m pip install --upgrade pip setuptools
python -m pip install -r requirements.txt
# Development extras (linters, formatters, docs)
python -m pip install -r requirements-dev.txt
```

### Configure Environment Variables

1. Copy template if needed:

    ```fish
    cp .env.example .env
    ```

2. Populate `.env` with local secrets (never commit secrets):
   - `DATABASE_URL` (falls back to SQLite if unset)
   - `REDIS_URL` (for Celery/WebSockets)
   - `DJANGO_SECRET_KEY`, `DJANGO_SETTINGS_MODULE` (see `config/settings/`)
   - API keys for external data sources (if required by analytics tasks)

### Database Bootstrap

```fish
python manage.py migrate
# Optional convenience bootstrap (seeds demo data, syncs fixtures)
python setup_database.py
```

Alembic migrations (if modifying non-Django-managed schemas):

```fish
alembic upgrade head
```

## 3. Daily Development Workflow

### Run Services

```fish
# Django development server
python manage.py runserver

# Celery worker
celery -A config worker -l info

# Optional: start redis + postgres locally
docker compose up -d redis postgres
```

### Helpful Django Commands

- `python manage.py shell` — interactive shell with project context.
- `python manage.py check` — fast config validation (mirrors CI pre-test check).
- `python manage.py createsuperuser` — create admin login for local testing.
- `python manage.py makemigrations` then `python manage.py migrate` when modifying models.

### Additional Scripts

- `python run_finance.py` — orchestrates analytics/backtesting routines.
- `python personal_finance/scripts/<name>.py` — bespoke ETL utilities (inspect script headers for usage).

## 4. Testing Instructions

Default framework: **pytest** with Django + Celery fixtures configured in `personal_finance/conftest.py`.

| Scenario | Command |
|----------|---------|
| Run full suite | ```fish
pytest -q
``` |
| Single file | ```fish
pytest tests/test_file.py -q
``` |
| Single test | ```fish
pytest tests/test_file.py::test_case -q
``` |
| Keyword match | ```fish
pytest -k "portfolio" -q
``` |
| Measure coverage (optional) | ```fish
pytest --cov=personal_finance --cov-report=term-missing
``` |

Testing tips:

- Initialize Redis (`docker compose up -d redis`) before running async tests.
- New features must include tests covering success and edge cases (empty datasets, permissions, rate limits).
- When tests need PII/financial data, scrub fixtures and assert logging omits sensitive fields.

## 5. Code Style & Quality Gates

- **Formatter**: `black` targeting 88 columns.
- **Linting**: `ruff` (broad rules) + targeted `flake8` checks in CI (E9, F63, F7, F82).
- **Typing**: No enforced mypy config yet; prefer adding type hints on new modules.

Run locally before committing:

```fish
ruff check .
black .
flake8 src tests --max-line-length=88 --select=E9,F63,F7,F82
```

If adding dependencies, update `requirements.txt`, any relevant `requirements-*.txt`, and verify constraints in `constraints*.txt`.

## 6. Build & Deployment

- **Docker (local)**:

    ```fish
    docker compose -f docker-compose.local.yml up --build
    ```

    Spins up Django, Redis, Postgres, Celery worker, and ancillary services.

- **Production artifacts**:
  - `docker-compose.production.yml` for multi-service deploys.
  - `render.yaml` / `Procfile` for platform-specific hosting.
  - Static files handled via Django’s `collectstatic` (configure storage backend per environment).

- **Environment promotion**: ensure migrations and `pip-audit` are green before deploying.

## 7. CI/CD Summary

- Workflow: `.github/workflows/ci.yml` (matrix Python 3.10 & 3.11).
- Steps: dependency install → flake8 lint → `python -m django check` → pytest (exit 5 tolerated) → `pip-audit` security scan.
- Token permissions: `contents: read` (least privilege in place to satisfy CodeQL security guidance).
- Reference spec: `spec/spec-process-cicd-ci.md` (update spec first when adjusting pipelines).

## 8. Security Considerations

- **Secrets**: never commit; rely on environment variables or secret managers (GitHub Actions secrets, Render env vars, etc.).
- **CVE tracking**: keep Django ≥ 4.2.24; monitor Dependabot alerts and CodeQL issues.
- **Logging**: avoid printing account numbers, personally identifiable data, or API tokens. Use structured logging and redact sensitive fields.
- **Outbound requests**: validate user-provided URLs to prevent SSRF; prefer allow-lists.
- **Data access**: enforce Django permissions/context checks before exposing analytics endpoints.

## 9. Pull Requests & Conventional Commits

- Commit message format: `<type>[optional scope]: <imperative description>` (≤72 chars).
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore`.
- PR checklist before requesting review:
  1. All tests (`pytest -q`) pass locally.
  2. Lint/format (`ruff check`, `black`, `flake8`) clean.
  3. No secrets in diff; `.env` and credential files ignored.
  4. Update relevant `/spec/` documents when changing workflows/policies.
  5. Mention migrations or data backfills explicitly in PR body.
  6. Add screenshots or sample responses for UI/API changes when applicable.

## 10. Debugging & Troubleshooting

- **Migrations stuck**: run `python manage.py showmigrations` to inspect; fake migrations with `--fake` only after validating manually.
- **Redis/Celery issues**: check `docker compose logs redis` and worker logs; ensure Redis URL matches running instance.
- **WebSocket problems**: confirm Channels layer configured via `config/websocket.py` and ASGI settings.
- **Test flakiness**: re-run with `pytest -k <target> --maxfail=1 -vv`; check Celery tasks using `CELERY_TASK_ALWAYS_EAGER=true` for deterministic runs.
- **Static files**: run `python manage.py collectstatic --noinput` locally to reproduce pipeline errors.
- General advice: compare environment packages using `pip freeze`, ensure `.venv` activated.

## 11. Additional Resources

- `README.md` — high-level project narrative and onboarding.
- `docs/` — Sphinx documentation, developer guides.
- `memory-bank/` — persistent context for AI agents (review before major work sessions).
- `spec/` — authoritative workflow/process specs (must stay in sync with automation).
- `BACKTESTING_USAGE.md`, `REALTIME_USAGE.md`, `VISUALIZATION_USAGE.md` — domain-specific run books.

---

Treat this file as living documentation. Update it whenever tooling, workflows, or security posture changes so future agents remain productive and safe.
