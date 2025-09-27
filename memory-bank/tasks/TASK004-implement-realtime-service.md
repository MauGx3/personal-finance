# [TASK004] - Implement realtime price streamer/service

**Status:** Pending
**Added:** 2025-09-27
**Updated:** 2025-09-27

## Overview

Replace the NotImplementedError and placeholder return values in `personal_finance/realtime/services.py` with an MVP realtime pricing service. The goal is to provide a simple websocket-based or polling-based streamer that other parts of the app (GUI, API) can subscribe to for near-real-time price updates.

## Scope

Included:

- Implement a `RealtimeService` with two modes: `polling` (periodic HTTP/yfinance queries) and `ws` (websocket server endpoint to push updates to clients).
- Provide a simple in-process publish/subscribe API (subscribe(symbols, callback)).
- Add tests that verify subscription/notification behavior using the mock data source adapter (from TASK003).

Excluded:

- High-scale websocket infrastructure (use PaaS/containerized services later).
- Historical replay or persistence (use data_sources + db for that).

## Technical Requirements

- Minimal external dependencies; prefer Python stdlib asyncio + websockets or Django Channels if already used.
- Ensure threads/async safety and graceful shutdown (signals). Use Small API surface for ease of testing.
- Respect rate limits from data providers; default to a safe polling interval (e.g., 15s) and allow configuration via environment variable.

## Implementation Plan

1. Add `RealtimeService` class in `personal_finance/realtime/services.py`.
2. Implement a `PollingAgent` that retrieves current prices via the `DataSourceService` adapter and publishes updates.
3. Implement a `WebsocketEndpoint` (ASGI) under `personal_finance/realtime/ws.py` to accept client subscriptions and push updates.
4. Add unit tests under `personal_finance/realtime/tests/` to validate publish/subscribe semantics and graceful shutdown.
5. Add a small example usage in `docs/` or `README` showing how to subscribe from a simple script.

## Acceptance Criteria

- Subscribing to symbols results in callbacks being called with expected structured `PricePoint` objects within the configured polling interval.
- The websocket endpoint accepts subscription messages (e.g., JSON {"subscribe": ["AAPL"]}) and pushes updates.
- Tests run offline using mock adapters and pass in CI.

## Priority

Priority: High — enables realtime UI updates and improves user experience.

## Dependencies

- **Blocked by:** TASK003 (data source adapter/service)
- **Blocks:** GUI realtime features, realtime alerts

## Implementation Size

- Estimated effort: Medium (3-5 days)
- Sub-issues:
  - Polling agent
  - Websocket endpoint
  - Pub/Sub API and tests
