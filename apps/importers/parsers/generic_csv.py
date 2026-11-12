"""A plain CSV format for anything without a dedicated parser.

Columns (header row required, extra columns ignored)::

    date, type, ticker, quantity, price, fees, amount, currency, exchange, broker, notes

``type`` is one of BUY, SELL, DIVIDEND, JCP, INCOME, SPLIT, BONUS.
Only ``date``, ``type`` and ``ticker`` are mandatory.
"""

from __future__ import annotations

from apps.assets.models import Exchange, normalize_ticker
from apps.core.money import parse_date, parse_decimal
from apps.portfolios.models import TransactionKind

from ..base import ParsedRow, ParseResult, StatementParser


class GenericCsvParser(StatementParser):
    name = "generic_csv"
    label = "Generic CSV"
    required_headers = frozenset({"date", "type", "ticker"})

    def parse_row(self, cell, result: ParseResult) -> ParsedRow | None:
        kind = str(cell("type")).strip().upper()
        if kind not in TransactionKind.values:
            raise ValueError(f"unknown type {kind!r}")
        exchange = str(cell("exchange") or Exchange.B3).strip().upper()
        if exchange not in Exchange.values:
            raise ValueError(f"unknown exchange {exchange!r}")
        return ParsedRow(
            trade_date=parse_date(cell("date")),
            kind=kind,
            ticker=normalize_ticker(str(cell("ticker")), exchange),
            quantity=parse_decimal(cell("quantity")),
            price=parse_decimal(cell("price")),
            fees=parse_decimal(cell("fees")),
            amount=parse_decimal(cell("amount")),
            exchange=exchange,
            currency=str(cell("currency") or "").strip().upper(),
            broker=str(cell("broker") or "").strip(),
            notes=str(cell("notes") or "").strip(),
        )
