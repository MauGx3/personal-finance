# AGENTS.md

Instructions for coding agents working on this repository. `README.md` is the
human overview; this file is the working contract.

## What this is

A single-user, self-hosted investment tracker for a Brazilian investor (B3 and
US assets, totals in BRL), deployed as a small Docker stack on a NAS.
Optimise for correctness of the numbers and low maintenance, not for scale or
multi-tenancy.

## Stack

- Python 3.12+ (CI runs 3.12 and 3.13), Django 5.2 LTS, Django REST Framework.
- `uv` for dependencies (`pyproject.toml` + `uv.lock`). No `requirements*.txt`.
- SQLite by default; PostgreSQL through `DATABASE_URL`.
- `ruff` for linting and formatting (line length 100). `pytest` + `pytest-django`.
- No Redis, Celery, Channels or front-end build. Do not add them without the
  owner asking: a NAS-friendly footprint is a requirement.

## Layout

| Path | Purpose |
| --- | --- |
| `config/` | settings (`base`, `dev`, `prod`, `test`), root URLs |
| `apps/core/` | `money.py` (Decimal and parsing), dashboard, template filters |
| `apps/assets/` | asset catalog |
| `apps/portfolios/` | Portfolio, Transaction, Holding; `services/positions.py`, `holdings.py`, `valuation.py` |
| `apps/data_sources/` | `PriceProvider` interface, yfinance provider, PriceQuote, FxRate, `sync_prices` |
| `apps/importers/` | readers, `StatementParser`, B3 and generic CSV parsers, `import_statement` |
| `apps/analytics/` | reports, value history, `metrics.py` formulas |
| `apps/api/` | REST API |
| `templates/`, `static/` | server-rendered UI, one CSS file, one small JS file |
| `tests/` | all tests; `tests/fakes.py` holds the fake price provider |
| `docs/`, `memory-bank/`, `spec/` | documentation, agent context, process specs |
| `notebooks/` | the owner's exploratory notebooks; leave them alone |

## Commands

```bash
uv sync                                   # install
uv run python manage.py migrate
uv run python manage.py runserver
uv run pytest                             # all tests, no network needed
uv run pytest tests/test_positions.py -q  # one file
uv run ruff check . && uv run ruff format --check .
uv run python manage.py makemigrations --check --dry-run
```

All four checks (ruff check, ruff format, pytest, migration check) must pass
before a commit. CI runs the same, plus `pip-audit`.

## Rules for changes

1. **Money is `Decimal`.** Never `float` for prices, quantities or amounts.
   Parse outside values with `apps.core.money`.
2. **The ledger is the source of truth.** Never write `Holding` directly;
   change transactions and let `rebuild_holding` run.
3. **Keep rules out of views.** Put logic in a service function and call it
   from the view, the API and the command.
4. **Tests never touch the network.** Use `tests.fakes.FakeProvider` (already
   the provider in `config.settings.test`).
5. **Every query is scoped to the owner** (`portfolio__user=request.user`).
6. **Do not encode tax rates or exemptions** unless the owner supplies the rule;
   reports give the inputs, not the tax.
7. New behaviour comes with tests for the normal case and the edge cases
   (empty input, wrong owner, malformed file).
8. Changing a model means a migration in the same commit.
9. No secrets in the repository; configuration comes from environment
   variables (`.env.example` lists them).
10. Use the available MCP servers when they fit the task: GitHub operations
    through the GitHub MCP server, library documentation through context7.

## Commits and pull requests

- Conventional commits: `<type>[scope]: <imperative description>`, 72 characters
  or fewer. Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`,
  `ci`, `chore`.
- Update `spec/` before changing CI, and `memory-bank/` when the direction or
  state of the project changes.
- Mention migrations in the PR body.

## Where to look first

- A number looks wrong: `apps/portfolios/services/positions.py`, then `valuation.py`.
- An import misreads a file: the parser in `apps/importers/parsers/`, then `apps/core/money.py`.
- Prices are missing: `apps/data_sources/services.py`; check `Asset.quote_symbol`.
