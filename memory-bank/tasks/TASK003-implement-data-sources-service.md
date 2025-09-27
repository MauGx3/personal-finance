# [TASK003] - Implement robust data source service (yfinance)

**Status:** Pending

**Added:** 2025-09-27

**Updated:** 2025-09-27

## Overview

Replace the placeholder implementations in `personal_finance/data_sources/services.py` with a robust, testable MVP that fetches current and historical prices using `yfinance` (or a clear adapter layer that can be swapped for test doubles). This will enable accurate portfolio valuation and historical analysis.

## Scope

Included:

- Implement a `DataSourceService` class with methods: `get_current_price(symbol)`, `fetch_historical(symbol, period, interval)`, `bulk_get_current(symbols)`.
- Add adapter pattern so the implementation can be swapped (e.g., `YFinanceAdapter`, `MockAdapter`).
- Add unit tests and small integration tests that run offline using recorded fixtures (VCR or saved JSON).
- Input validation and SSRF-safe URL handling (none expected but follow security guidance).

Excluded:

- Advanced rate-limiting/backoff for heavy production workloads (can be added later).
- Real-time streaming/websocket (handled by TASK004).

## Technical Requirements

- Use `yfinance` as the primary data provider. If not available, provide a clear adapter interface and a fallback mock that returns deterministic values for tests.
- Methods must return typed dataclasses or simple dictionaries with Decimal-typed prices and ISO 8601 datetimes.
- Avoid network calls in unit tests; use fixtures or the mock adapter.
- Follow secure coding guidance: no secrets, validate inputs, and prevent injection.

## Implementation Plan

1. Create a new module `personal_finance/data_sources/adapter.py` exposing an abstract `BaseDataSourceAdapter` and `YFinanceAdapter`.
2. Implement `DataSourceService` in `personal_finance/data_sources/services.py` to use adapters by dependency injection.
3. Add dataclasses in `personal_finance/data_sources/types.py` for return shapes: `PricePoint`, `HistoricalSeries`.
4. Write unit tests in `personal_finance/data_sources/tests/`:
   - `test_adapter_interface.py` (ensures adapters conform)
   - `test_service_with_mock_adapter.py` (service logic, aggregation)
   - `test_yfinance_adapter_integration.py` (skipped by default or uses recorded fixture)
5. Add lightweight fixtures in `tests/fixtures/data_sources/` for historical and current price responses.

Example (concept):

```python
from decimal import Decimal
from datetime import datetime

PricePoint = dict(symbol=str, price=Decimal, timestamp=datetime)

def get_current_price(symbol) -> PricePoint:
    # adapter returns Decimal for price and datetime for timestamp
    return {"symbol": symbol, "price": Decimal("123.45"), "timestamp": datetime.utcnow()}
```

## Acceptance Criteria

- `DataSourceService.get_current_price("AAPL")` returns a dict-like object with keys `symbol`, `price` (Decimal), `timestamp` (datetime).
- `fetch_historical` returns a list of `PricePoint` ordered ascending by timestamp.
- Unit tests pass (`pytest -q`) without network access by using mock adapters/fixtures.
- New code has type hints and docstrings; follow project linting styles.

## Priority

Priority: High — portfolio valuation depends on correct price feeds.

## Dependencies

- **Blocked by:** none
- **Blocks:** portfolio valuation, reporting features

## Implementation Size

- Estimated effort: Medium (2-4 days)
- Sub-issues:
  - Adapter interface and datatypes
  - YFinance adapter implementation
  - Service wiring and tests
