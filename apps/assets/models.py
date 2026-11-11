"""Asset catalog: one row per tradable thing, shared by all portfolios."""

from __future__ import annotations

import re

from django.core.validators import RegexValidator
from django.db import models


class AssetClass(models.TextChoices):
    STOCK = "STOCK", "Stock"
    FII = "FII", "FII"
    ETF = "ETF", "ETF"
    BDR = "BDR", "BDR"
    REIT = "REIT", "REIT"
    FIXED_INCOME = "FIXED_INCOME", "Fixed income"
    FUND = "FUND", "Fund"
    CRYPTO = "CRYPTO", "Crypto"
    OTHER = "OTHER", "Other"


class Exchange(models.TextChoices):
    B3 = "B3", "B3 (Brazil)"
    NYSE = "NYSE", "NYSE"
    NASDAQ = "NASDAQ", "NASDAQ"
    CRYPTO = "CRYPTO", "Crypto"
    OTHER = "OTHER", "Other"


# Currency traded on each exchange, used as the default for new assets.
EXCHANGE_CURRENCY = {
    Exchange.B3: "BRL",
    Exchange.NYSE: "USD",
    Exchange.NASDAQ: "USD",
    Exchange.CRYPTO: "USD",
}

_B3_TICKER = re.compile(r"^[A-Z]{4}\d{1,2}$")
_BDR_SUFFIXES = {"31", "32", "33", "34", "35", "39"}


def normalize_ticker(raw: str, exchange: str = Exchange.B3) -> str:
    """Return the canonical ticker.

    On B3 the fractional market lists the same share with a trailing ``F``
    (``PETR4F``); both are the same asset, so the suffix is dropped.
    """
    ticker = (raw or "").strip().upper()
    if exchange == Exchange.B3 and ticker.endswith("F") and _B3_TICKER.match(ticker[:-1]):
        ticker = ticker[:-1]
    return ticker


def guess_asset_class(ticker: str, exchange: str = Exchange.B3) -> str:
    """Best-effort class for a new asset, from the B3 ticker suffix.

    This is a heuristic: suffix ``11`` is shared by FIIs, ETFs and units, so
    the guess is FII (the most common case for individual investors) and the
    import report asks for a review of newly created assets.
    """
    if exchange != Exchange.B3 or not _B3_TICKER.match(ticker):
        return AssetClass.STOCK if exchange != Exchange.CRYPTO else AssetClass.CRYPTO
    suffix = ticker[4:]
    if suffix in _BDR_SUFFIXES:
        return AssetClass.BDR
    if suffix == "11":
        return AssetClass.FII
    return AssetClass.STOCK


class Asset(models.Model):
    ticker = models.CharField(
        max_length=20,
        validators=[RegexValidator(r"^[A-Z0-9\-_.=^]+$", "Use upper-case letters and digits.")],
    )
    exchange = models.CharField(max_length=10, choices=Exchange.choices, default=Exchange.B3)
    name = models.CharField(max_length=200, blank=True)
    asset_class = models.CharField(
        max_length=20, choices=AssetClass.choices, default=AssetClass.STOCK
    )
    currency = models.CharField(max_length=3, default="BRL")
    isin = models.CharField("ISIN", max_length=12, blank=True)
    sector = models.CharField(max_length=100, blank=True)
    provider_symbol = models.CharField(
        max_length=30,
        blank=True,
        help_text="Symbol used by the price provider. Leave blank to derive it from the ticker.",
    )
    is_active = models.BooleanField(default=True, help_text="Inactive assets are not price-synced.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ticker"]
        constraints = [
            models.UniqueConstraint(
                fields=["ticker", "exchange"], name="unique_ticker_per_exchange"
            ),
        ]

    def __str__(self) -> str:
        return self.ticker

    def save(self, *args, **kwargs) -> None:
        self.ticker = normalize_ticker(self.ticker, self.exchange)
        self.currency = (self.currency or "").upper()
        super().save(*args, **kwargs)

    @property
    def quote_symbol(self) -> str:
        """Symbol to ask the price provider for (Yahoo convention by default)."""
        if self.provider_symbol:
            return self.provider_symbol
        if self.exchange == Exchange.B3:
            return f"{self.ticker}.SA"
        if self.exchange == Exchange.CRYPTO:
            return f"{self.ticker}-{self.currency}"
        return self.ticker

    @classmethod
    def get_or_create_for_ticker(
        cls, raw_ticker: str, exchange: str = Exchange.B3, **defaults
    ) -> tuple[Asset, bool]:
        """Find an asset by ticker, creating it with sensible defaults if new."""
        ticker = normalize_ticker(raw_ticker, exchange)
        defaults.setdefault("asset_class", guess_asset_class(ticker, exchange))
        defaults.setdefault("currency", EXCHANGE_CURRENCY.get(exchange, "USD"))
        return cls.objects.get_or_create(ticker=ticker, exchange=exchange, defaults=defaults)
