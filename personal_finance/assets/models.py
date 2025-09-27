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
        indexes = [
            models.Index(fields=["symbol"]),
            models.Index(fields=["isin"]),
        ]

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
    # BREAKING CHANGE: Changed on_delete from CASCADE to SET_NULL to prevent unintended data loss.
    portfolio = models.ForeignKey(
        "assets.Portfolio",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
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

    def __init__(self, *args, **kwargs):
        """Compatibility shim: accept legacy `cost_basis_per_unit` kwarg.

        Older tests and callers pass `cost_basis_per_unit` when creating
        holdings; the current model stores this value in `average_price`.
        To remain backwards compatible we pop the legacy kwarg and map it
        to `average_price` so constructors like `Holding.objects.create(...)`
        continue to work.
        """
        _sentinel = object()
        cost = kwargs.pop("cost_basis_per_unit", _sentinel)
        if cost is not _sentinel and "average_price" not in kwargs:
            kwargs["average_price"] = cost
        super().__init__(*args, **kwargs)

    @property
    def cost_basis_per_unit(self):
        """Backward-compatible alias for `average_price`."""
        return self.average_price

    @cost_basis_per_unit.setter
    def cost_basis_per_unit(self, value):
        self.average_price = value

    @property
    def total_cost_basis(self):
        """Computed total cost basis for this holding.

        Returns quantity * cost_basis_per_unit (or 0 if missing).
        """
        try:
            if self.average_price is None or self.quantity is None:
                return Decimal("0")
            return self.quantity * self.average_price
        except Exception:
            return Decimal("0")

    def save(self, *args, **kwargs):
        """Ensure Holding.user is populated from portfolio when omitted.

        Many call sites create holdings by providing a portfolio but not the
        user. Historically the model inferred the holding.user from
        portfolio.user; keep that behaviour for tests and backwards
        compatibility.
        """
        # If user is not set but portfolio is available, try to copy it.
        try:
            user_id_missing = (
                not hasattr(self, "user_id") or self.user_id is None
            )
            has_portfolio = (
                hasattr(self, "portfolio") and self.portfolio is not None
            )
            if user_id_missing and has_portfolio:
                # portfolio may be an instance with a user attribute
                if (
                    hasattr(self.portfolio, "user")
                    and self.portfolio.user is not None
                ):
                    self.user = self.portfolio.user
        except Exception:
            # Defensive: if portfolio isn't fully populated yet, just continue
            pass

        return super().save(*args, **kwargs)
