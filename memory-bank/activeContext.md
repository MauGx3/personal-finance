# Active context

Last updated: 2026-11-11

## Current state

Version 0.2 replaced the previous code on `main` (a cookiecutter-django project
that no longer started) with a lean rewrite. It follows the `apps/` + `config/`
layout, uv, ruff, Django 5.2 and Decimal rules from the owner's
`new-codebase-structure` branch, without that template's enterprise parts
(OpenSearch, OpenTelemetry, Sentry, Kubernetes, 2FA, Celery, Channels).

## Decisions

- Ledger is the source of truth; holdings are derived.
- Weighted average cost, the Brazilian convention.
- SQLite default, no Redis/Celery; a loop container syncs prices.
- Built-in Django auth with email login instead of allauth.
- Reports give tax inputs (monthly sales and gain); no tax rates are encoded.
- Carried over from old `main`: `analytics/metrics.py` and its tests.

## Open questions for the owner

- Banco Inter and PDF brokerage notes: need real sample files to build parsers.
- Should foreign assets track cost in BRL at the purchase-date rate?
- Which of the old open PRs and branches should be closed.
