# Progress

Last updated: 2025-09-28

## What works

- Repository structure stable with Django entrypoints (ASGI/WSGI) and Celery stub.
- Docs scaffold (Sphinx) and multiple usage guides present.
- Docker/Compose definitions for local and production.
- Memory Bank initialized with core context and tasks.

## What's left to build

- Data source service (yfinance adapter) with tests (TASK003)
- Realtime streaming/polling service (TASK004)
- DataProfiler services & validators (TASK005)
- Finalize Portainer PR metadata (labels/reviewers) (TASK002)

## Current status

- Active focus on deployment readiness and core data services.
- Portainer PR created (per task log) and awaiting labels/reviewers.

## Known issues

- Network-dependent tests must be avoided; need fixture strategy for market data.
- Ensure Decimal usage for monetary fields across services to avoid float drift.

## Next steps

1) Land TASK002 by adding reviewers/labels and merging after CI.
2) Implement TASK003 adapter/service with tests and fixtures.
3) Build TASK004 realtime polling with mock adapter; add websocket endpoint if feasible.
4) Finish TASK005 validation/profile flow.
