# Progress

Last updated: 2026-11-11

## Works (covered by tests)

- Asset catalog with B3 ticker normalization and class guessing.
- Portfolios, transactions (buy, sell, dividend, JCP, income, split, bonus), derived holdings.
- Valuation in base currency, allocation by class and currency.
- Price and FX sync through a provider interface; yfinance provider.
- Imports: B3 Negociação, B3 Movimentação, generic CSV; dedupe, preview, undo.
- Dashboard, transactions, import, asset and reports pages; REST API with OpenAPI.
- Monthly sales/realized gain and income reports; value history.

## Not verified

- Live yfinance calls (blocked in the development sandbox; the provider is
  exercised only through a fake in tests).
- Docker image build.
- B3 parsers against real exports (built from the documented column headers).

## Next

1. Verify the items above on real data.
2. Banco Inter parser (issue #66), brokerage-note PDFs (#48).
3. Cost in BRL at purchase-date exchange rate for foreign assets.
4. Benchmarks (IBOV, CDI, S&P 500) on the value chart; use `analytics/metrics.py`.
5. Asset study page with fundamentals (issues #90, #107, #126).
