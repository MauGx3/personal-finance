# AGENTS.md

This file is a concise, machine-focused guide for coding agents that will work on this repository.
It complements `README.md` and contains the exact commands, locations, and conventions an automated tool needs
to make safe, well-scoped changes.

## Project overview

- Language: Python (Django-based project).
- Entry points: `manage.py`, `run_finance.py`, `setup_database.py`.
- Config: Django settings in `config/` and an application structured under `personal_finance/`.
- Packaging/build: standard Python project (see `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`).
- Database: SQLite used by default (`db.sqlite3`, `test_db.sqlite3`); production may use a different DB (env-configured).
- **Security**: Recent Django security update (4.2.24) addresses CVE-2025-57833. CodeQL scanning active.
- **Documentation**: Process specifications in `/spec/` directory for CI/CD and other workflows.

Closest important files and folders:

- `manage.py` — Django management / runserver / migrations.
- `run_finance.py` — main runner for finance scripts.
- `setup_database.py` — database bootstrapping helper.
- `personal_finance/` — main Django app package and modules (tests under `personal_finance/` and `tests/`).
- `docker-compose*.yml`, `Dockerfile` — container development and deployment artifacts.
- `/spec/` — process and architecture specifications for agents.

## Agent contract (what you can do safely)

- Inputs: edit/update files under the repo, add tests, update docs.
- Outputs: changes must keep tests passing and linting green (where available), follow commit conventions below.
- Error modes: do not assume external network access for fetching secrets. Fail with a clear message if secrets are missing.
- **Security First**: All changes must maintain or improve security posture. Review CodeQL alerts and address vulnerabilities.
- **Specification Compliance**: Update relevant specifications in `/spec/` before making process changes.

Before making non-trivial changes, prefer to:

- Run tests locally (`pytest`) and ensure green.
- Add or update at least one focused unit/integration test that covers the changed behavior.
- Check for security implications, especially when handling financial/PII data.

## Setup (local environment) — fish shell

These commands assume a recent Python 3.10+ is available. Use a virtual environment.

### 1) Create and activate a venv (fish)

```fish
python -m venv .venv
source .venv/bin/activate.fish
```

### 2) Install dependencies

```fish
python -m pip install --upgrade pip setuptools
python -m pip install -r requirements.txt
# optional dev tools
python -m pip install -r requirements-dev.txt
```

### 3) Database bootstrap (sqlite by default)

```fish
# run Django migrations
python manage.py migrate
# convenience helper if present
python setup_database.py
```

### 4) Environment / secrets

- Do NOT hardcode secrets. Read secrets from environment variables or a `.env` loaded only in local/dev
  (use a secrets manager for CI/prod).
- When running containers, set secrets via env files passed to Docker Compose or via your CI secret store.

## Development workflow (common agent actions)

- Run the dev server:

```fish
python manage.py runserver
```

- Run the primary script (if experimenting):

```fish
python run_finance.py
```

- Start services with Docker Compose (local):

```fish
docker compose up --build
```

- Celery worker (project contains `config/celery_app.py`):

```fish
# from repo root
celery -A config worker -l info
```

Notes for agents:

- When changing Django models, add migrations: `python manage.py makemigrations` and run `migrate`.
- Keep changes minimal and add/adjust tests in `tests/` or `personal_finance/` corresponding test modules.

## Testing

- Run full test suite (fast path):

```fish
pytest -q
```

- Run a single test file or test case:

```fish
pytest path/to/test_file.py::test_name -q
```

- Focus by keyword:

```fish
pytest -k "keyword" -q
```

- If test failures depend on services (e.g., Redis for Celery), prefer to run those services in Docker Compose
  before running the tests:

```fish
docker compose up -d redis
```

Test locations and patterns:

- Unit/integration tests live under `personal_finance/` and the top-level `tests/` directory.
- Use `pytest -q` to run the suite; CI should run the same command.
- **CI Testing**: CI runs tests across Python 3.10 and 3.11 with security scanning (pip-audit) and linting (flake8).
- **Security Testing**: When adding code that handles sensitive data, ensure tests verify no accidental logging of PII/financial information.

## Code style, linting and formatting

- Follow repository conventions. Recommended commands (install dev deps first):

```fish
# formatting
black .
# linting
ruff check .
```

- If `pyproject.toml` or `requirements-dev.txt` contains formatters/linters, use those exact versions when available.
- When making edits, run formatting and lint checks and fix any obvious warnings before opening a PR.

## Build and deployment notes

- Docker-based deploys use `Dockerfile` and `docker-compose*.yml` files. For local testing:

```fish
docker compose -f docker-compose.local.yml up --build
```

- CI/CD: inspect `.github/workflows/` (if present) to reproduce pipeline steps used by CI.
- **Security-Enhanced CI**: The CI workflow (`.github/workflows/ci.yml`) includes:
  - Explicit GITHUB_TOKEN permissions (contents: read only)
  - Automated dependency security scanning via pip-audit
  - Multi-version Python testing (3.10, 3.11)
  - CodeQL security scanning for vulnerabilities
- **Specifications**: CI/CD processes are documented in `/spec/` directory. Update specifications before making workflow changes.

## Security and secrets (agent guidance)

- Never print or commit secrets or private keys. If a secret is required for a task, fail and ask the human for a credential.
- Validate any external URLs before the agent instructs the runtime to fetch them (SSRF protection).
- When touching code that handles PII/financial data, add or update tests that ensure no accidental logging of sensitive fields.
- **Recent Security Updates**: Django was updated to 4.2.24 to resolve CVE-2025-57833 (SQL injection vulnerability in FilteredRelation). Always ensure Django dependencies are kept current.
- **Code Scanning**: The project uses CodeQL for automated security scanning. All identified vulnerabilities should be addressed promptly.
- **CI/CD Security**: GitHub Actions workflows now include explicit GITHUB_TOKEN permissions (contents: read only) to follow principle of least privilege.

## Pull Request & commit conventions

- Use Conventional Commits for commit messages. Format:

```text
<type>[optional scope]: <description>
```

Example:

```text
fix(api): correct portfolio export boundary condition
```

- Types commonly used: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`.
- First line must not exceed 72 characters. Provide a brief PR description and include test-run notes in the PR body.

Agent PR checklist (automated):

- All new code has tests covering the behavior.
- `pytest` passes locally.
- Formatting and linting applied.
- No secrets or credentials in the diff.
- Security implications reviewed (especially for financial/PII data handling).
- Specifications updated if processes/workflows changed.

## Debugging and troubleshooting

- Reproduce locally with the same commands CI uses (usually `pytest` and `ruff`/`black`).
- If a test fails only in CI: compare Python versions and installed packages; run `pip freeze` locally and in CI to compare.
- For container issues, inspect `docker compose logs` and `docker inspect` for container state.

## Where to add more agent guidance

- If the repo grows into a monorepo or adds subpackages, add `AGENTS.md` to the subpackage root. The closest `AGENTS.md` wins for agents working in a subfolder.
- **Specifications Directory**: Process and architecture specifications are maintained in `/spec/`. Update relevant specifications before making changes to documented processes.

## Minimal example tasks an agent can perform safely

1. Fix a small bug and add a unit test that reproduces the bug and proves the fix.
2. Add typing to a module and ensure `mypy` (if used) still passes.
3. Improve and reformat documentation in `docs/` and the top-level README.

When performing these tasks, run tests and linters and include a Conventional Commit message with the PR.

---

If anything in this AGENTS.md becomes stale, update it alongside the code change so agents always have accurate instructions.
