"""Value holdings at the latest stored prices, in the base currency."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from django.conf import settings

from apps.assets.models import Asset
from apps.core.money import ZERO
from apps.data_sources.services import fx_rate, latest_quotes
from apps.portfolios.models import Holding, Portfolio

HUNDRED = Decimal("100")


@dataclass
class PositionRow:
    holding: Holding
    asset: Asset
    quantity: Decimal
    average_price: Decimal
    cost: Decimal
    price: Decimal | None
    price_day: date | None
    value: Decimal  # in the asset's currency; cost when there is no price yet
    value_base: Decimal | None  # None when the exchange rate is missing
    weight: Decimal = ZERO

    @property
    def priced(self) -> bool:
        return self.price is not None

    @property
    def gain(self) -> Decimal | None:
        return self.value - self.cost if self.priced else None

    @property
    def gain_pct(self) -> Decimal | None:
        if not self.priced or self.cost == 0:
            return None
        return (self.value - self.cost) / self.cost * HUNDRED


@dataclass
class Slice:
    label: str
    value: Decimal
    weight: Decimal


@dataclass
class Snapshot:
    """A point-in-time valuation.

    Amounts are converted to the base currency at the latest stored rate. That
    makes totals comparable, but it means the gain on a foreign asset reflects
    its price move only, not the currency move since it was bought.
    """

    base_currency: str
    rows: list[PositionRow] = field(default_factory=list)
    total_value: Decimal = ZERO
    total_cost: Decimal = ZERO
    realized_gain: Decimal = ZERO
    income: Decimal = ZERO
    by_class: list[Slice] = field(default_factory=list)
    by_currency: list[Slice] = field(default_factory=list)
    unpriced: list[str] = field(default_factory=list)
    missing_fx: list[str] = field(default_factory=list)
    ledger_errors: list[Holding] = field(default_factory=list)
    as_of: date | None = None

    @property
    def unrealized_gain(self) -> Decimal:
        return self.total_value - self.total_cost

    @property
    def unrealized_pct(self) -> Decimal | None:
        if self.total_cost == 0:
            return None
        return self.unrealized_gain / self.total_cost * HUNDRED


def _slices(totals: dict[str, Decimal], grand_total: Decimal) -> list[Slice]:
    return [
        Slice(label, value, value / grand_total * HUNDRED if grand_total else ZERO)
        for label, value in sorted(totals.items(), key=lambda item: -item[1])
    ]


def _position_row(holding: Holding, quote, rate: Decimal | None) -> PositionRow:
    """Value one holding at ``quote`` (or at cost when there is none)."""
    cost = holding.cost_basis
    value = holding.quantity * quote.close if quote else cost
    return PositionRow(
        holding=holding,
        asset=holding.asset,
        quantity=holding.quantity,
        average_price=holding.average_price,
        cost=cost,
        price=quote.close if quote else None,
        price_day=quote.day if quote else None,
        value=value,
        value_base=value * rate if rate is not None else None,
    )


def snapshot(portfolios: Iterable[Portfolio], base_currency: str | None = None) -> Snapshot:
    """Value every holding of ``portfolios`` and aggregate the result."""
    base_currency = base_currency or settings.BASE_CURRENCY
    holdings = list(
        Holding.objects.filter(portfolio__in=list(portfolios)).select_related("asset", "portfolio")
    )
    quotes = latest_quotes({h.asset_id for h in holdings})
    rates = {
        currency: fx_rate(currency, base_currency)
        for currency in sorted({h.asset.currency for h in holdings})
    }
    result = Snapshot(base_currency=base_currency)
    result.missing_fx = [currency for currency, rate in rates.items() if rate is None]
    result.ledger_errors = [h for h in holdings if h.ledger_error]
    class_totals: dict[str, Decimal] = defaultdict(lambda: ZERO)
    currency_totals: dict[str, Decimal] = defaultdict(lambda: ZERO)

    for holding in holdings:
        asset = holding.asset
        rate = rates[asset.currency]
        if rate is not None:
            result.realized_gain += holding.realized_gain * rate
            result.income += holding.income * rate
        if holding.quantity <= 0:
            continue

        row = _position_row(holding, quotes.get(asset.pk), rate)
        result.rows.append(row)
        if not row.priced:
            result.unpriced.append(asset.ticker)
        if row.value_base is not None:
            result.total_value += row.value_base
            result.total_cost += row.cost * rate
            class_totals[asset.get_asset_class_display()] += row.value_base
            currency_totals[asset.currency] += row.value_base

    result.as_of = max((row.price_day for row in result.rows if row.price_day), default=None)
    for row in result.rows:
        if row.value_base is not None and result.total_value:
            row.weight = row.value_base / result.total_value * HUNDRED
    result.rows.sort(key=lambda r: -(r.value_base or ZERO))
    result.by_class = _slices(class_totals, result.total_value)
    result.by_currency = _slices(currency_totals, result.total_value)
    return result
