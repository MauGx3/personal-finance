# Importing statements

Go to **Import**, choose the portfolio and the file. The format is detected
from the column headers. Tick **Preview only** to see what would happen first.

## B3 – Negociação (trades)

Expected columns: `Data do Negócio`, `Tipo de Movimentação` (Compra / Venda),
`Mercado`, `Prazo/Vencimento`, `Instituição`, `Código de Negociação`,
`Quantidade`, `Preço`, `Valor`.

- Tickers from the fractional market (`PETR4F`) become `PETR4`.
- Rows whose market is an option, term or future are skipped with a warning.
- The file has no brokerage fees. Add them by editing a transaction if you
  want them in the average price.

## B3 – Movimentação (income)

Expected columns: `Entrada/Saída`, `Data`, `Movimentação`, `Produto`,
`Instituição`, `Quantidade`, `Preço unitário`, `Valor da Operação`.

Only credited `Dividendo`, `Juros Sobre Capital Próprio` and `Rendimento` rows
are imported. Everything else (settlements, transfers, corporate events) is
counted and reported as ignored. Splits and bonus shares must be entered by
hand as SPLIT or BONUS transactions.

## Generic CSV

```csv
date,type,ticker,quantity,price,fees,amount,currency,exchange,broker,notes
2024-01-10,BUY,AAPL,10,150.25,1.00,,USD,NASDAQ,IBKR,
2024-02-15,DIVIDEND,AAPL,,,,2.40,USD,NASDAQ,IBKR,
```

`type`: BUY, SELL, DIVIDEND, JCP, INCOME, SPLIT, BONUS. `exchange`: B3 (default),
NYSE, NASDAQ, CRYPTO, OTHER. Dates may be `YYYY-MM-DD` or `DD/MM/YYYY`; numbers
may use either decimal convention.

## Duplicates and undo

Each imported row gets a fingerprint (parser, date, type, ticker, quantity,
price, amount, broker, and its position among identical rows). A row whose
fingerprint is already in the portfolio is skipped, so overlapping exports are
safe. **Undo** on the import page deletes exactly the rows that import created.

## Writing a parser

```python
class MyBrokerParser(StatementParser):
    name = "my_broker"
    label = "My Broker"
    required_headers = frozenset({"data", "ativo", "quantidade"})  # normalized

    def parse_row(self, cell, result):
        return ParsedRow(
            trade_date=parse_date(cell("data")),
            kind="BUY",
            ticker=str(cell("ativo")),
            quantity=parse_decimal(cell("quantidade")),
        )
```

Add its dotted path to `IMPORT_PARSERS`. Headers are matched lower-case with
accents removed. Raise `ValueError` for an unreadable row: it becomes a warning
with the line number and the rest of the file is still imported.
