# Personal Finance

A self-hosted tracker for my own investments: B3 (stocks, FIIs, ETFs, BDRs) and
US assets, with totals in reais. One user, one small Docker stack, SQLite by
default. It runs comfortably on a NAS.

## What it does

- **Ledger first.** Every buy, sell, dividend, JCP, fund income, split and bonus
  is a transaction. Positions, average price ("preço médio"), realized gains
  and income are always recomputed from the ledger, never typed in.
- **Imports B3 statements.** Upload the Negociação and Movimentação spreadsheets
  from B3's investor portal. Fractional-market tickers (`PETR4F`) are merged
  into the main one. Importing the same file twice creates nothing new, and any
  import can be undone.
- **Generic CSV** for US trades or any broker without a dedicated parser.
- **Prices and exchange rates** from Yahoo Finance (`yfinance`), stored locally,
  so the dashboard works offline and history accumulates.
- **Dashboard**: market value, unrealized and realized gain, income, value over
  time, allocation by asset class and currency, positions.
- **Monthly report** of gross sales and realized gain per asset class, and of
  income received: the figures needed to work out tax on sales. It does not
  calculate tax.
- **REST API** with token auth and an OpenAPI page at `/api/docs/`.
- Money is `Decimal` end to end.

## Run it locally

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser   # your login (email + password)
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000>, then **Import** your B3 statements or **Add
transaction**, and press **Update prices**.

## Run it on a NAS (Docker / Portainer)

```bash
cp .env.example .env        # set DJANGO_SECRET_KEY and DJANGO_ALLOWED_HOSTS
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

The stack has two containers: `web` (the app) and `prices` (runs `sync_prices`
every six hours). All data lives in the `data` volume as one SQLite file, so a
backup is a copy of that file. To use PostgreSQL instead, set `DATABASE_URL`.
See [docs/deployment.md](docs/deployment.md).

## Everyday commands

| Task | Command |
| --- | --- |
| Update prices | `uv run python manage.py sync_prices` |
| Import from the shell | `uv run python manage.py import_statement file.xlsx` |
| Preview an import | add `--dry-run` |
| Tests | `uv run pytest` |
| Lint and format | `uv run ruff check . && uv run ruff format .` |

With [`just`](https://just.systems) installed: `just dev`, `just test`, `just check`.

## How the code is organised

```
config/              settings (base, dev, prod, test) and URLs
apps/core/           Decimal and parsing helpers, dashboard, template filters
apps/users/          email-login user
apps/assets/         asset catalog (ticker, exchange, class, currency)
apps/portfolios/     portfolios, transactions, holdings; position and valuation services
apps/data_sources/   price provider interface, yfinance provider, stored quotes and FX
apps/importers/      statement parsers (B3, generic CSV) and the import service
apps/analytics/      monthly reports, value history, metric formulas
apps/api/            REST API
```

Each app keeps its rules in plain functions (`services/`, `reports.py`) that
the web pages, the API and the commands all call. Two extension points are
plain settings:

- `PRICE_PROVIDERS`: add a class implementing `apps.data_sources.base.PriceProvider`.
- `IMPORT_PARSERS`: add a class extending `apps.importers.base.StatementParser`.

More in [docs/architecture.md](docs/architecture.md) and [docs/importing.md](docs/importing.md).

## Known limits

- Totals convert foreign assets at the latest stored exchange rate. The gain
  shown for a US asset is its price gain in dollars; currency gain since
  purchase is not separated out.
- New assets get a class guessed from the ticker. Suffix `11` is treated as a
  FII, which is wrong for ETFs and units: fix it on the asset page.
- Options, futures and term contracts in B3 files are skipped with a warning.
- There is no Banco Inter or PDF brokerage-note parser yet (issues #48, #66).

## License

MIT
