"""Import a statement file into a portfolio's ledger."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass, field
from typing import BinaryIO

from django.conf import settings
from django.db import transaction as db_transaction
from django.utils.module_loading import import_string

from apps.assets.models import Asset, normalize_ticker
from apps.portfolios.models import Portfolio, Transaction
from apps.portfolios.services.holdings import rebuild_holding, rebuild_portfolio

from .base import ParsedRow, StatementError, StatementParser
from .models import ImportBatch
from .readers import read_table


@dataclass
class ImportOutcome:
    parser: StatementParser
    created: int = 0
    skipped: int = 0
    warnings: list[str] = field(default_factory=list)
    new_assets: list[str] = field(default_factory=list)
    batch: ImportBatch | None = None
    dry_run: bool = False


def available_parsers() -> list[StatementParser]:
    return [import_string(path)() for path in settings.IMPORT_PARSERS]


def pick_parser(table, parser_name: str | None = None) -> StatementParser:
    """Return the named parser, or the first one that recognises the file."""
    parsers = available_parsers()
    if parser_name:
        for parser in parsers:
            if parser.name == parser_name:
                return parser
        raise StatementError(f"Unknown parser {parser_name!r}.")
    for parser in parsers:
        if parser.find_header(table) is not None:
            return parser
    labels = ", ".join(parser.label for parser in parsers)
    raise StatementError(f"File format not recognised. Supported formats: {labels}.")


def _fingerprints(parser: StatementParser, rows: list[ParsedRow]) -> list[str]:
    """One stable hash per row.

    Two identical trades on the same day are legitimate, so the hash includes
    how many times the same row has already appeared in the file. Importing
    the same statement (or an overlapping one) twice then creates nothing new.
    """
    seen: Counter[str] = Counter()
    fingerprints = []
    for row in rows:
        key = "|".join(
            str(part)
            for part in (
                parser.name,
                row.trade_date.isoformat(),
                row.kind,
                row.exchange,
                row.ticker,
                row.quantity.normalize(),
                row.price.normalize(),
                row.amount.normalize(),
                row.broker,
            )
        )
        seen[key] += 1
        fingerprints.append(hashlib.sha256(f"{key}|{seen[key]}".encode()).hexdigest())
    return fingerprints


@db_transaction.atomic
def import_statement(
    portfolio: Portfolio,
    file: BinaryIO,
    filename: str,
    parser_name: str | None = None,
    dry_run: bool = False,
) -> ImportOutcome:
    """Parse ``file`` and add its rows to ``portfolio``.

    Rows already imported are skipped. With ``dry_run`` nothing is written and
    the outcome reports what would happen.

    Raises:
        StatementError: if the file cannot be read or matched to a parser.
    """
    table = read_table(file, filename)
    parser = pick_parser(table, parser_name)
    parsed = parser.parse(table)
    outcome = ImportOutcome(parser=parser, warnings=list(parsed.warnings), dry_run=dry_run)

    fingerprints = _fingerprints(parser, parsed.rows)
    existing = set(
        Transaction.objects.filter(portfolio=portfolio, fingerprint__in=fingerprints).values_list(
            "fingerprint", flat=True
        )
    )
    fresh = [
        (row, fp) for row, fp in zip(parsed.rows, fingerprints, strict=True) if fp not in existing
    ]
    outcome.skipped = len(parsed.rows) - len(fresh)
    outcome.created = len(fresh)

    known = {
        (ticker, exchange) for ticker, exchange in Asset.objects.values_list("ticker", "exchange")
    }
    outcome.new_assets = sorted(
        {
            row.ticker
            for row, _ in fresh
            if (normalize_ticker(row.ticker, row.exchange), row.exchange) not in known
        }
    )
    if outcome.new_assets:
        outcome.warnings.append(
            "New assets were created with a guessed class; review them: "
            + ", ".join(outcome.new_assets)
        )
    if dry_run or not fresh:
        return outcome

    batch = ImportBatch.objects.create(
        portfolio=portfolio,
        filename=filename[:255],
        parser=parser.name,
        created_count=outcome.created,
        skipped_count=outcome.skipped,
        warnings=outcome.warnings,
    )
    assets: dict[tuple[str, str], Asset] = {}
    transactions = []
    for row, fingerprint in fresh:
        key = (row.ticker, row.exchange)
        if key not in assets:
            defaults = {"name": row.name} if row.name else {}
            if row.currency:
                defaults["currency"] = row.currency
            assets[key], _ = Asset.get_or_create_for_ticker(row.ticker, row.exchange, **defaults)
        asset = assets[key]
        transactions.append(
            Transaction(
                portfolio=portfolio,
                asset=asset,
                kind=row.kind,
                trade_date=row.trade_date,
                quantity=row.quantity,
                price=row.price,
                fees=row.fees,
                amount=row.amount,
                currency=row.currency or asset.currency,
                broker=row.broker[:100],
                notes=row.notes,
                import_batch=batch,
                fingerprint=fingerprint,
            )
        )
    Transaction.objects.bulk_create(transactions)
    for asset in assets.values():
        rebuild_holding(portfolio.pk, asset.pk)
    outcome.batch = batch
    return outcome


@db_transaction.atomic
def undo_import(batch: ImportBatch) -> int:
    """Delete the transactions a batch created, then the batch itself."""
    portfolio = batch.portfolio
    deleted, _ = Transaction.objects.filter(import_batch=batch).delete()
    batch.delete()
    rebuild_portfolio(portfolio)
    return deleted
