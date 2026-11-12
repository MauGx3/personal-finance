# Architecture

## Principles

1. **The ledger is the source of truth.** `Transaction` rows are the only thing
   a person or an importer writes. `Holding` is a cache rebuilt from them.
2. **Rules live in plain functions.** `positions.compute_position` has no
   database access; `valuation.snapshot`, `reports.*` and
   `importers.services.import_statement` are called the same way from pages,
   the API and management commands.
3. **Decimal everywhere.** Outside values enter through `apps/core/money.py`.
4. **Small footprint.** No Redis, Celery or JavaScript build. A loop container
   runs `sync_prices`; SQLite is the default database.

## Data flow

```
B3 xlsx / CSV ──► importers.readers ──► StatementParser ──► ParsedRow
                                                            │ fingerprint, skip duplicates
manual form / API ─────────────────────────────────────────►▼
                                                       Transaction (ledger)
                                                            │ signals / rebuild_holding
                                                            ▼
yfinance ──► PriceProvider ──► PriceQuote, FxRate ──►  Holding ──► valuation.snapshot ──► dashboard, API
                                                            └────► analytics.reports ──► reports page
```

## Position rules

Implemented in `apps/portfolios/services/positions.py` and covered by
`tests/test_positions.py`.

| Kind | Effect |
| --- | --- |
| BUY | adds shares; fees are part of the cost; average price is re-weighted |
| SELL | removes shares at the average price; fees reduce proceeds; realizes gain |
| SPLIT | quantity is the ratio of new to old shares; cost basis unchanged |
| BONUS | adds shares at the stated cost per share |
| DIVIDEND, JCP, INCOME | adds `amount` to income |

Entries are replayed by date; on the same day, corporate actions come first,
then buys, then sells. A sale larger than the position does not crash anything:
the holding is flagged (`ledger_error`) and shown on the dashboard, because the
usual cause is an older statement that has not been imported yet.

## Adding a price provider

Subclass `PriceProvider` (`daily_closes`, optionally `info` and `fx_symbol`),
then register it:

```python
PRICE_PROVIDERS = {"yfinance": "...", "brapi": "apps.data_sources.providers.brapi.BrapiProvider"}
PRICE_PROVIDER = "brapi"
```

## Security

- Every page and API endpoint requires login; querysets are filtered by the
  portfolio's owner.
- Uploads are limited to 10 MB, read in memory, never stored or executed.
- `config.settings.prod` refuses to start with the development secret key.
- The app makes outbound requests only to the price provider, with symbols
  taken from the asset catalog, never from a user-supplied URL.
