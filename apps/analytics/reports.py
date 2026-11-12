"""Reports built from the ledger: realized gains, income, value over time."""

from __future__ import annotations

from bisect import bisect_right
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from apps.assets.models import AssetClass
from apps.core.money import ZERO
from apps.data_sources.models import FxRate, PriceQuote
from apps.portfolios.models import INCOME_KINDS, Portfolio, Transaction, TransactionKind
from apps.portfolios.services.positions import PositionError, compute_position


@dataclass
class MonthlyRealized:
    """Sales of one asset class in one month, in the assets' own currency.

    ``sales`` (gross proceeds) and ``gain`` are the two figures a Brazilian
    investor needs each month to work out whether tax is due. No tax rate is
    applied here: rules and exemptions change and depend on the investor.
    """

    month: date
    asset_class: str
    currency: str
    sales: Decimal = ZERO
    gain: Decimal = ZERO

    @property
    def asset_class_label(self) -> str:
        return dict(AssetClass.choices).get(self.asset_class, self.asset_class)


@dataclass
class MonthlyIncome:
    month: date
    kind: str
    currency: str
    amount: Decimal = ZERO

    @property
    def kind_label(self) -> str:
        return dict(TransactionKind.choices).get(self.kind, self.kind)


def _ledgers(portfolios: Iterable[Portfolio]) -> dict[tuple[int, int], list[Transaction]]:
    grouped: dict[tuple[int, int], list[Transaction]] = defaultdict(list)
    transactions = Transaction.objects.filter(portfolio__in=list(portfolios)).select_related(
        "asset"
    )
    for transaction in transactions:
        grouped[(transaction.portfolio_id, transaction.asset_id)].append(transaction)
    return grouped


def realized_by_month(portfolios: Iterable[Portfolio]) -> list[MonthlyRealized]:
    """Gross sales and realized gain per month, asset class and currency."""
    rows: dict[tuple[date, str, str], MonthlyRealized] = {}
    for entries in _ledgers(portfolios).values():
        asset = entries[0].asset
        try:
            position = compute_position(entries)
        except PositionError:
            continue  # flagged on the holding; an inconsistent ledger has no reliable gains
        for sale in position.sales:
            month = sale.trade_date.replace(day=1)
            key = (month, asset.asset_class, asset.currency)
            row = rows.setdefault(key, MonthlyRealized(month, asset.asset_class, asset.currency))
            row.sales += sale.proceeds
            row.gain += sale.gain
    return sorted(rows.values(), key=lambda r: (r.month, r.asset_class), reverse=True)


def income_by_month(portfolios: Iterable[Portfolio]) -> list[MonthlyIncome]:
    """Dividends, JCP and fund income received per month."""
    rows: dict[tuple[date, str, str], MonthlyIncome] = {}
    transactions = Transaction.objects.filter(
        portfolio__in=list(portfolios), kind__in=INCOME_KINDS
    ).select_related("asset")
    for transaction in transactions:
        month = transaction.trade_date.replace(day=1)
        currency = transaction.currency or transaction.asset.currency
        key = (month, transaction.kind, currency)
        row = rows.setdefault(key, MonthlyIncome(month, transaction.kind, currency))
        row.amount += transaction.amount
    return sorted(rows.values(), key=lambda r: (r.month, r.kind), reverse=True)


class _Series:
    """Values by date with 'latest on or before' lookup."""

    def __init__(self) -> None:
        self.days: list[date] = []
        self.values: list[Decimal] = []

    def add(self, day: date, value: Decimal) -> None:
        self.days.append(day)
        self.values.append(value)

    def at(self, day: date) -> Decimal | None:
        index = bisect_right(self.days, day)
        return self.values[index - 1] if index else None


def _sample_days(start: date, end: date, max_points: int) -> list[date]:
    """Evenly spaced days from ``start`` to ``end``, always ending on ``end``."""
    span = (end - start).days + 1
    step = max(1, span // max_points)
    days = [start + timedelta(days=offset) for offset in range(0, span, step)]
    if days[-1] != end:
        days.append(end)
    return days


def _load_series(queryset) -> dict:
    """Group ``(key, day, value)`` rows into one ``_Series`` per key."""
    series: dict = defaultdict(_Series)
    for key, day, value in queryset.order_by("day"):
        series[key].add(day, value)
    return series


class _Replay:
    """Shares held and last trade price per asset, advanced one entry at a time."""

    def __init__(self) -> None:
        self.quantities: dict[int, Decimal] = defaultdict(lambda: ZERO)
        self.trade_prices: dict[int, Decimal] = {}

    def apply(self, entry: Transaction) -> None:
        asset_id = entry.asset_id
        if entry.kind in (TransactionKind.BUY, TransactionKind.BONUS):
            self.quantities[asset_id] += entry.quantity
        elif entry.kind == TransactionKind.SELL:
            self.quantities[asset_id] -= entry.quantity
        elif entry.kind == TransactionKind.SPLIT and entry.quantity > 0:
            self.quantities[asset_id] *= entry.quantity
            if asset_id in self.trade_prices:
                self.trade_prices[asset_id] /= entry.quantity
        if entry.kind in (TransactionKind.BUY, TransactionKind.SELL) and entry.price:
            self.trade_prices[asset_id] = entry.price

    def held(self) -> list[tuple[int, Decimal]]:
        return [(asset_id, qty) for asset_id, qty in self.quantities.items() if qty > 0]


def _rate_on(series: _Series | None, day: date) -> Decimal | None:
    """Exchange rate on ``day``; before the first stored rate, the oldest one."""
    if series is None or not series.values:
        return None
    return series.at(day) or series.values[0]


def value_history(
    portfolios: Iterable[Portfolio],
    base_currency: str | None = None,
    max_points: int = 120,
) -> list[tuple[date, Decimal]]:
    """Market value of the holdings over time, in the base currency.

    Each point values the shares held on that day at the latest close on or
    before it. Before an asset has any stored close, its last trade price is
    used, so the line starts at cost instead of at zero.
    """
    base_currency = base_currency or settings.BASE_CURRENCY
    transactions = list(
        Transaction.objects.filter(portfolio__in=list(portfolios))
        .exclude(kind__in=INCOME_KINDS)
        .select_related("asset")
        .order_by("trade_date", "id")
    )
    if not transactions:
        return []

    currencies = {t.asset_id: t.asset.currency for t in transactions}
    prices = _load_series(
        PriceQuote.objects.filter(asset_id__in=currencies).values_list("asset_id", "day", "close")
    )
    rates = _load_series(
        FxRate.objects.filter(quote=base_currency).values_list("base", "day", "rate")
    )

    def value_of(asset_id: int, quantity: Decimal, day: date) -> Decimal:
        series = prices.get(asset_id)
        price = (series.at(day) if series else None) or replay.trade_prices.get(asset_id)
        currency = currencies[asset_id]
        rate = Decimal("1") if currency == base_currency else _rate_on(rates.get(currency), day)
        if price is None or rate is None:
            return ZERO
        return quantity * price * rate

    replay = _Replay()
    pending = iter(transactions)
    entry = next(pending, None)
    history = []
    for day in _sample_days(transactions[0].trade_date, timezone.localdate(), max_points):
        while entry is not None and entry.trade_date <= day:
            replay.apply(entry)
            entry = next(pending, None)
        total = sum((value_of(asset_id, qty, day) for asset_id, qty in replay.held()), ZERO)
        history.append((day, total))
    return history
