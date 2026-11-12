"""Keep the ``Holding`` cache in step with the transaction ledger."""

from __future__ import annotations

from django.db import transaction as db_transaction

from apps.core.money import quantize_money
from apps.portfolios.models import Holding, Portfolio, Transaction

from .positions import PositionError, compute_position


@db_transaction.atomic
def rebuild_holding(portfolio_id: int, asset_id: int) -> Holding | None:
    """Recompute one holding from its transactions.

    A ledger that does not add up (a sale with no matching buy, usually because
    older statements have not been imported yet) does not raise: the holding is
    kept and flagged in ``ledger_error`` so the UI can point at it.
    """
    entries = list(Transaction.objects.filter(portfolio_id=portfolio_id, asset_id=asset_id))
    if not entries:
        Holding.objects.filter(portfolio_id=portfolio_id, asset_id=asset_id).delete()
        return None

    holding, _ = Holding.objects.get_or_create(portfolio_id=portfolio_id, asset_id=asset_id)
    try:
        position = compute_position(entries)
    except PositionError as exc:
        holding.ledger_error = str(exc)[:255]
        holding.save(update_fields=["ledger_error", "updated_at"])
        return holding

    holding.quantity = position.quantity
    holding.average_price = position.average_price
    holding.realized_gain = quantize_money(position.realized_gain)
    holding.income = quantize_money(position.income)
    holding.first_trade = position.first_trade
    holding.last_trade = position.last_trade
    holding.ledger_error = ""
    holding.save()
    return holding


def rebuild_portfolio(portfolio: Portfolio) -> int:
    """Recompute every holding of a portfolio. Returns how many were rebuilt."""
    asset_ids = set(
        Transaction.objects.filter(portfolio=portfolio).values_list("asset_id", flat=True)
    )
    Holding.objects.filter(portfolio=portfolio).exclude(asset_id__in=asset_ids).delete()
    for asset_id in asset_ids:
        rebuild_holding(portfolio.pk, asset_id)
    return len(asset_ids)
