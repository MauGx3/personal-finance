---
title: Portfolio - Technical Documentation
component_path: src/personal_finance/portfolio.py
version: 1.0
date_created: 2025-09-27
last_updated: 2025-09-27
owner: MauGx3 / personal-finance team
tags: [component, service, portfolio, documentation, architecture]
---

This document describes the object-oriented Portfolio component implemented in `src/personal_finance/portfolio.py`.

It targets developers and maintainers who need to understand, test, extend, or operate the portfolio functionality.

The component provides a small domain model (Portfolio + Position) and a `PortfolioManager` service class that
coordinates persistence (via `DatabaseManager`), price/historical-data lookups (via optional `stockdex` library),
and portfolio operations (add/remove positions, compute value and summaries).

## 1. Component Overview

### Purpose/Responsibility

- Provide a programmatic API to manage a user's portfolio: add/remove positions, load from JSON or database,
  compute current portfolio market value, fetch historical data, and produce position summaries.

### Scope

- Included: portfolio domain dataclass and manager methods in `PortfolioManager` that orchestrate DB operations
  and external price lookups.
- Excluded: UI, scheduled jobs, higher-level portfolio strategies, and direct HTTP APIs (these are handled elsewhere in the repo).

### System context and relationships

- This component depends primarily on:

  - `DatabaseManager` (`src/personal_finance/database.py`) — persistence layer for tickers, positions and historical prices.
  - `stockdex` (optional, imported as `sd`) — used to query Yahoo price data; the module is optional and the code
    contains fallbacks and warnings if the library is not installed.
  - `logger` from `src/personal_finance/logs` — centralized logging.

## 2. Architecture Section

- Design patterns and decisions:
  - Manager/Service pattern: `PortfolioManager` encapsulates high-level workflows and coordinates database + external calls.
  - Dataclass model: `Portfolio` and nested `Position` use `dataclasses` for simple data containers.
  - Defensive/optional dependency: `stockdex` is imported in a try/except and the code logs warnings when price fetching is unavailable.

- Internal and external dependencies with purpose:
  - `DatabaseManager` — required; persists and retrieves portfolio positions and ticker/historical price records.
  - `stockdex` — optional; fetches current and historical market data.
  - Python stdlib (`json`, `datetime`, `dataclasses`, `typing`) — routines and typing.

### Component Structure and Dependencies Diagram

```mermaid
graph TD
    subgraph "Portfolio Component"
        PM[PortfolioManager]
        P[Portfolio(dataclass)]
        Pos[Position(dataclass)]
    end

    subgraph "Internal"
        DB[DatabaseManager]
        Logger[Package Logger]
    end

    subgraph "External"
        SD[stockdex (optional)]
        YF[Yahoo / market API]
    end

    PM --> DB
    PM --> Logger
    PM --> SD
    SD --> YF
    P --> Pos

    classDiagram
        class Portfolio {
            +positions: dict
            +classes: str
        }
        class Position {
            +symbol: str
            +quantity: float
            +cost_basis: float
        }
        class PortfolioManager {
            +db_manager: DatabaseManager
            +portfolio: dict
            +load_portfolio(file_path: Optional[str])
            +add_position(symbol, name, quantity, buy_price, buy_date)
            +remove_position(symbol)
            +get_current_prices() -> Dict[str,float]
            +get_portfolio_value() -> float
            +get_historical_data(period: str) -> Dict
            +get_positions_summary() -> List[Dict]
        }
```

## 3. Interface Documentation

- Public classes and methods (high level):

| Method/Property | Purpose | Parameters | Return Type | Usage Notes |
|---|---:|---|---:|---:|
| `Portfolio` | Dataclass container for positions | `positions: dict`, `classes: str` | dataclass | Lightweight container; `__post_init__` resets fields for backward compatibility |
| `Portfolio.Position` | Dataclass representing a single holding | `symbol`, `quantity`, `cost_basis` | dataclass | Nested dataclass for compact grouping |
| `PortfolioManager.__init__` | Construct manager | `db_manager: Optional[DatabaseManager]` | PortfolioManager | If `db_manager` not provided, a default `DatabaseManager()` is created |
| `load_portfolio(file_path: Optional[str])` | Load portfolio from file (legacy) or DB | `file_path` | None | If `file_path` provided tries JSON load; otherwise loads from DB using `get_portfolio_positions()` |
| `add_position(symbol, name, quantity, buy_price, buy_date)` | Add or update a position in persistence | `symbol: str`, `name: str`, `quantity: float`, `buy_price: float`, `buy_date: str (YYYY-MM-DD)` | None | Parses date; uses DB functions: `get_portfolio_position`, `update_portfolio_position`, `add_portfolio_position`, `add_or_update_ticker`. Raises on unexpected exceptions |
| `remove_position(symbol)` | Remove position by symbol | `symbol: str` | None | Calls `db_manager.remove_portfolio_position` and logs results |
| `get_current_prices()` | Fetch latest price for every position | None | Dict[str,float] | Uses `stockdex.Ticker.yahoo_api_price` when available; updates ticker price in DB; returns 0.0 when unavailable or on error |
| `get_portfolio_value()` | Compute portfolio market value | None | float | Multiplies current prices by quantities fetched from DB positions |
| `get_historical_data(period='1y')` | Fetch historical price series for positions | `period: str` | Dict[str, Any] | Uses `stockdex` to fetch range; stores per-day historical rows in DB via `add_historical_price` |
| `get_positions_summary()` | Summary of positions (market value, gain/loss, pct) | None | List[Dict] | Uses prices from `get_current_prices()` and DB positions to compute financial summary |

### Exceptions and error modes

- The manager logs errors and raises on unexpected exceptions in add/remove operations. Price/historical fetching handles exceptions by logging and returning default values (0.0 or None).

- Common error modes:

  - `FileNotFoundError` / `json.JSONDecodeError` in `load_portfolio(file_path)` — logged and not fatal.
  - External API errors or missing `stockdex` — logged, prices default to 0.0.
  - Database errors thrown by `DatabaseManager` — propagated (wrapped by try/except in some methods); callers should handle or let propagate.

## 4. Implementation Details

- Main classes and responsibilities:
  - `Portfolio` dataclass: simple container (currently unused by `PortfolioManager`; kept for backward compatibility / future use).
  - `PortfolioManager`: orchestrates CRUD operations for positions and coordinates data enrichment (prices, historical prices).

- Initialization & configuration
  - `PortfolioManager.__init__` accepts an optional `DatabaseManager`. If omitted, the manager constructs a default `DatabaseManager()`.
  - Logging is done via the package `logger` with varying levels (debug/info/warning/error).

- Key algorithms & business logic

- get_positions_summary() computes market values and gain/loss percentages using `current price * quantity` vs `buy price * quantity`.
- get_portfolio_value() aggregates market_value across positions.

- Persistence interactions (DatabaseManager API used)
  - get_portfolio_positions() -> returns iterable of position-like objects with properties: symbol, name, quantity, buy_price, buy_date
  - get_portfolio_position(symbol) -> optional existing position
  - update_portfolio_position(...)
  - add_portfolio_position(...)
  - add_or_update_ticker(symbol, name, last_price=None)
  - remove_portfolio_position(symbol)
  - add_historical_price(symbol, date, open_price, high_price, low_price, close_price, volume)

### Performance considerations and bottlenecks

- Network-bound calls: price and historical data fetching are network-bound and invoked per-position; consider batching or async/parallel calls for large portfolios.

- DB writes in `get_historical_data` iterate per-date/row and call `add_historical_price` for each; this can be slow — consider bulk insert if DB layer supports it.

### Security considerations

- Avoid logging sensitive data (quantities and prices are financial but not secrets; still avoid leaking PII). The module uses package `logger` and documents a `PORTFOLIO_LOG_LEVEL` control.

- Do not commit API keys or credentials. If adding external services, validate URLs and use allowlists to prevent SSRF.

## 5. Usage Examples

### Basic Usage

```python
from personal_finance.portfolio import PortfolioManager

pm = PortfolioManager()
pm.load_portfolio()  # loads from DB by default
print(pm.get_positions_summary())
print(f"Portfolio value: ${pm.get_portfolio_value():,.2f}")
```

### Adding a position (simple)

```python
pm.add_position(
    symbol="AAPL",
    name="Apple Inc.",
    quantity=10.0,
    buy_price=150.0,
    buy_date="2023-06-01",
)
```

### Advanced usage: dependency injection and mocking (for tests)

```python
from unittest.mock import MagicMock
from personal_finance.portfolio import PortfolioManager

mock_db = MagicMock()
mock_db.get_portfolio_positions.return_value = []

pm = PortfolioManager(db_manager=mock_db)
Now all DB interactions are under the test's control.
```

## 6. Quality Attributes

- Security: Uses structured logging and avoids basicConfig; ensure secrets are stored in environment/secret store, not in code.
- Performance: Network and DB IO are the main bottlenecks (see suggestions to batch or bulk insert historical prices).
- Reliability: The manager logs and returns safe defaults when price/historical providers are missing. Database errors can still propagate — callers should catch where appropriate.
- Maintainability: Clear separation between DB manager and portfolio orchestration improves testability. `Portfolio` dataclass appears under-used; consider removing or fully integrating it to avoid stale code.
- Extensibility: New data sources (another market data provider) can be integrated by adding a price adapter and keeping `stockdex` usage behind a thin wrapper.

## 7. Reference Information

- Source files and locations:
  - Component: `src/personal_finance/portfolio.py`
  - Persistence: `src/personal_finance/database.py` (DatabaseManager)
  - Logging: `src/personal_finance/logs` (package logger)

- Dependencies (note: versions must be verified in environment):
  - Optional: `stockdex` (used as `sd`) — used for `Ticker.yahoo_api_price` calls
  - Python stdlib: `json`, `datetime`, `dataclasses`, `typing`

### Testing guidelines and mocks

- Unit tests should:

  - Mock `DatabaseManager` to control returned positions and assert calls to add/update/remove methods.
  - Mock `stockdex.Ticker.yahoo_api_price` (or replace `sd` with a test double) to simulate price series and error conditions.
  - Assert logging of error/warning scenarios (use `caplog` in pytest).

Example pytest outline:

```python
def test_get_portfolio_value_with_mocked_prices(monkeypatch, mock_db):
    mock_db.get_portfolio_positions.return_value = [SimpleNamespace(symbol='AAPL', name='Apple', quantity=2, buy_price=100, buy_date=datetime(2023,1,1))]
    pm = PortfolioManager(db_manager=mock_db)

    class FakeTicker:
        def __init__(self, ticker):
            pass
        def yahoo_api_price(self, **kwargs):
            import pandas as pd
            return pd.DataFrame({'Close':[200]})

    monkeypatch.setattr('personal_finance.portfolio.sd', SimpleNamespace(Ticker=lambda ticker: FakeTicker(ticker)))
    assert pm.get_portfolio_value() == 400
```

### Troubleshooting (common issues)

- Missing `stockdex`: code will warn and return prices=0.0. Install `stockdex` or provide a test double in tests.

- Slow historical ingest: switch to DB bulk insert or rate-limit per-day inserts.

- Datetime parsing errors: ensure `buy_date` uses `YYYY-MM-DD` format.

## Change history & migration notes

- 2025-09-27: v1.0 — Initial documentation for `PortfolioManager` and related dataclasses. Recommendations added for batching historical writes and better integration of `Portfolio` dataclass.

---

If you'd like, I can also:

- Generate unit tests scaffolding for `PortfolioManager` in `tests/` that mock `DatabaseManager` and `stockdex`.
- Create a small adapter/wrapper around `stockdex` to centralize calls and make the code easier to test and swap providers.

Tell me which of the follow-ups you'd like me to perform next.
