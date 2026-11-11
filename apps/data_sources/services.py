"""Fetch market data into the database, and read it back."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.db.models import Max, Min
from django.utils import timezone

from apps.assets.models import Asset

from .base import PriceProvider, ProviderError
from .models import FxRate, PriceQuote
from .registry import get_provider

logger = logging.getLogger(__name__)

DEFAULT_LOOKBACK = timedelta(days=365)


@dataclass
class SyncReport:
    quotes: dict[str, int] = field(default_factory=dict)
    fx: dict[str, int] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.quotes.values()) + sum(self.fx.values())


def _today() -> date:
    return timezone.localdate()


def sync_asset(asset: Asset, provider: PriceProvider, start: date | None = None) -> int:
    """Store daily closes for ``asset`` from ``start`` to today.

    Without ``start`` the sync is incremental: it resumes from the last stored
    day (re-fetching it, since it may have been stored before the close), or,
    for a new asset, from its first transaction or one year back.
    """
    today = _today()
    if start is None:
        last = asset.quotes.aggregate(last=Max("day"))["last"]
        first_trade = asset.transactions.aggregate(first=Min("trade_date"))["first"]
        start = last or first_trade or today - DEFAULT_LOOKBACK
    closes = provider.daily_closes(asset.quote_symbol, start, today)
    PriceQuote.objects.bulk_create(
        [PriceQuote(asset=asset, day=c.day, close=c.close, source=provider.name) for c in closes],
        update_conflicts=True,
        unique_fields=["asset", "day"],
        update_fields=["close", "source"],
    )
    return len(closes)


def sync_fx(base: str, quote: str, provider: PriceProvider, start: date | None = None) -> int:
    """Store daily rates for one unit of ``base`` priced in ``quote``."""
    today = _today()
    if start is None:
        last = FxRate.objects.filter(base=base, quote=quote).aggregate(last=Max("day"))["last"]
        start = last or today - DEFAULT_LOOKBACK
    closes = provider.daily_closes(provider.fx_symbol(base, quote), start, today)
    FxRate.objects.bulk_create(
        [
            FxRate(base=base, quote=quote, day=c.day, rate=c.close, source=provider.name)
            for c in closes
        ],
        update_conflicts=True,
        unique_fields=["base", "quote", "day"],
        update_fields=["rate", "source"],
    )
    return len(closes)


def sync_all(
    provider: PriceProvider | None = None,
    *,
    include_unheld: bool = False,
    start: date | None = None,
) -> SyncReport:
    """Sync prices for held assets and the exchange rates they need.

    One failing symbol never stops the run; failures are collected in the report.
    """
    provider = provider or get_provider()
    base_currency = settings.BASE_CURRENCY
    assets = Asset.objects.filter(is_active=True)
    if not include_unheld:
        assets = assets.filter(holdings__quantity__gt=0).distinct()

    report = SyncReport()
    currencies = set()
    for asset in assets:
        currencies.add(asset.currency)
        try:
            report.quotes[asset.ticker] = sync_asset(asset, provider, start)
        except ProviderError as exc:
            logger.warning("Price sync failed for %s: %s", asset.ticker, exc)
            report.errors[asset.ticker] = str(exc)

    for currency in sorted(currencies - {base_currency}):
        pair = f"{currency}/{base_currency}"
        try:
            report.fx[pair] = sync_fx(currency, base_currency, provider, start)
        except ProviderError as exc:
            logger.warning("FX sync failed for %s: %s", pair, exc)
            report.errors[pair] = str(exc)
    return report


def latest_quotes(asset_ids) -> dict[int, PriceQuote]:
    """Most recent stored quote for each asset id that has one."""
    latest: dict[int, PriceQuote] = {}
    for quote in PriceQuote.objects.filter(asset_id__in=list(asset_ids)).order_by(
        "asset_id", "day"
    ):
        latest[quote.asset_id] = quote  # ordered by day, so the last one wins
    return latest


def fx_rate(base: str, quote: str, on: date | None = None) -> Decimal | None:
    """Rate to convert ``base`` into ``quote``: the latest one on or before ``on``.

    Falls back to the inverse pair. Returns ``None`` when no rate is stored.
    """
    if base == quote:
        return Decimal("1")
    for first, second, invert in ((base, quote, False), (quote, base, True)):
        rates = FxRate.objects.filter(base=first, quote=second)
        if on is not None:
            rates = rates.filter(day__lte=on)
        found = rates.order_by("-day").first()
        if found and found.rate:
            return Decimal("1") / found.rate if invert else found.rate
    return None
