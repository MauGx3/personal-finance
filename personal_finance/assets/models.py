from decimal import Decimal

from django.conf import settings
from django.db import models


class Asset(models.Model):
    """Canonical asset metadata for many asset types (stock, bond, crypto, etc.)."""

    ASSET_STOCK = "STOCK"
    ASSET_BOND = "BOND"
    ASSET_CRYPTO = "CRYPTO"
    ASSET_CASH = "CASH"
    ASSET_FUND = "FUND"
    ASSET_ETF = "ETF"
    ASSET_FOREX = "FOREX"
    ASSET_FOREIGN = "FOREIGN_STOCK"

    ASSET_TYPE_CHOICES = [
        (ASSET_STOCK, "Stock"),
        (ASSET_BOND, "Bond"),
        (ASSET_CRYPTO, "Crypto"),
        (ASSET_CASH, "Cash"),
        (ASSET_FUND, "Fund"),
        (ASSET_ETF, "ETF"),
        (ASSET_FOREX, "Forex"),
        (ASSET_FOREIGN, "Foreign stock"),
    ]

    symbol = models.CharField(max_length=64, db_index=True)
    name = models.CharField(max_length=255, blank=True)
    asset_type = models.CharField(
        max_length=32,
        choices=ASSET_TYPE_CHOICES,
        db_index=True,
    )
    currency = models.CharField(max_length=10, blank=True)
    exchange = models.CharField(max_length=64, blank=True)
    isin = models.CharField(max_length=32, blank=True, db_index=True)
    cusip = models.CharField(max_length=32, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["symbol", "name"]
        indexes = [models.Index(fields=["symbol"]), models.Index(fields=["isin"])]

    def __str__(self) -> str:
        return f"{self.symbol} — {self.name or self.asset_type}"


class Portfolio(models.Model):
    """A user-owned portfolio grouping (optional)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolios",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.user})"


class Holding(models.Model):
    """A user's holding / position in an asset (optionally attached to a portfolio)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="holdings",
    )
    asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.CASCADE,
        related_name="holdings",
    )
    portfolio = models.ForeignKey(
        "assets.Portfolio",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="holdings",
    )

    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal("0"),
    )
    average_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
    )
    currency = models.CharField(max_length=10, blank=True)

    acquired_at = models.DateTimeField(null=True, blank=True)
    in_portfolio = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "asset", "portfolio"],
                name="unique_user_asset_portfolio",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.asset} ({self.quantity})"
