"""Parsers for the spreadsheets exported by B3's investor portal.

The portal ("Área do Investidor") offers two exports under Extratos:

* **Negociação**: one row per trade. Source of buys and sells.
* **Movimentação**: every movement in custody. Used here only for cash
  income (dividends, JCP, fund income); trades come from Negociação, which
  has the actual execution prices.
"""

from __future__ import annotations

from collections import Counter

from apps.assets.models import normalize_ticker
from apps.core.money import parse_date, parse_decimal

from ..base import ParsedRow, ParseResult, StatementParser, normalize_header

_UNSUPPORTED_MARKETS = ("opc", "termo", "futuro", "exercicio")


class B3NegociacaoParser(StatementParser):
    name = "b3_negociacao"
    label = "B3 – Negociação"
    required_headers = frozenset(
        {"data do negocio", "tipo de movimentacao", "codigo de negociacao", "quantidade", "preco"}
    )
    _kinds = {"compra": "BUY", "venda": "SELL"}

    def parse_row(self, cell, result: ParseResult) -> ParsedRow | None:
        market = normalize_header(cell("mercado"))
        raw_ticker = str(cell("codigo de negociacao")).strip()
        if any(word in market for word in _UNSUPPORTED_MARKETS):
            result.warnings.append(
                f"{raw_ticker}: {cell('mercado')} is not supported, row skipped."
            )
            return None
        kind = self._kinds.get(normalize_header(cell("tipo de movimentacao")))
        if kind is None:
            raise ValueError(f"unknown trade type {cell('tipo de movimentacao')!r}")
        quantity = parse_decimal(cell("quantidade"))
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        return ParsedRow(
            trade_date=parse_date(cell("data do negocio")),
            kind=kind,
            ticker=normalize_ticker(raw_ticker),
            quantity=quantity,
            price=parse_decimal(cell("preco")),
            currency="BRL",
            broker=str(cell("instituicao") or "").strip(),
        )


class B3MovimentacaoParser(StatementParser):
    name = "b3_movimentacao"
    label = "B3 – Movimentação (dividends, JCP, income)"
    required_headers = frozenset(
        {"entrada/saida", "data", "movimentacao", "produto", "valor da operacao"}
    )
    _kinds = {
        "dividendo": "DIVIDEND",
        "juros sobre capital proprio": "JCP",
        "rendimento": "INCOME",
    }

    def parse(self, table) -> ParseResult:
        self._ignored: Counter[str] = Counter()
        result = super().parse(table)
        for movement, count in sorted(self._ignored.items()):
            result.warnings.append(f"Ignored {count} '{movement}' row(s): not cash income.")
        return result

    def parse_row(self, cell, result: ParseResult) -> ParsedRow | None:
        movement = str(cell("movimentacao") or "").strip()
        kind = self._kinds.get(normalize_header(movement))
        if kind is None or not normalize_header(cell("entrada/saida")).startswith("credito"):
            self._ignored[movement or "(blank)"] += 1
            return None
        product = str(cell("produto") or "")
        ticker, _, name = product.partition(" - ")
        amount = parse_decimal(cell("valor da operacao"))
        if amount <= 0:
            raise ValueError(f"{ticker.strip()}: no cash amount for {movement}")
        return ParsedRow(
            trade_date=parse_date(cell("data")),
            kind=kind,
            ticker=normalize_ticker(ticker),
            quantity=parse_decimal(cell("quantidade")),
            amount=amount,
            currency="BRL",
            broker=str(cell("instituicao") or "").strip(),
            name=name.strip(),
        )
