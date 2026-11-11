"""Portfolios, the transaction ledger, and the holdings derived from it."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.assets.models import Asset
from apps.core.money import ZERO


class Portfolio(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolios"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "name"]
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="unique_portfolio_name_per_user"),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        # The first portfolio is the default; there is only ever one default.
        if not Portfolio.objects.filter(user=self.user).exclude(pk=self.pk).exists():
            self.is_default = True
        super().save(*args, **kwargs)
        if self.is_default:
            Portfolio.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(
                is_default=False
            )

    @classmethod
    def default_for(cls, user) -> Portfolio:
        """Return the user's default portfolio, creating one if there is none."""
        portfolio = cls.objects.filter(user=user).first()
        if portfolio is None:
            portfolio = cls.objects.create(user=user, name="Main")
        return portfolio


class TransactionKind(models.TextChoices):
    BUY = "BUY", "Buy"
    SELL = "SELL", "Sell"
    DIVIDEND = "DIVIDEND", "Dividend"
    JCP = "JCP", "Interest on equity (JCP)"
    INCOME = "INCOME", "Fund income (rendimento)"
    SPLIT = "SPLIT", "Split / reverse split"
    BONUS = "BONUS", "Bonus shares"


TRADE_KINDS = {TransactionKind.BUY, TransactionKind.SELL, TransactionKind.BONUS}
INCOME_KINDS = {TransactionKind.DIVIDEND, TransactionKind.JCP, TransactionKind.INCOME}


class Transaction(models.Model):
    """One line of the ledger. Holdings are always recomputed from these."""

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="transactions")
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="transactions")
    kind = models.CharField(max_length=10, choices=TransactionKind)
    trade_date = models.DateField()
    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=ZERO,
        help_text="Shares traded. For a split, the ratio of new to old shares.",
    )
    price = models.DecimalField(
        max_digits=20, decimal_places=8, default=ZERO, help_text="Price per share."
    )
    fees = models.DecimalField(max_digits=20, decimal_places=2, default=ZERO)
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=ZERO,
        help_text="Cash received, for dividends, JCP and fund income.",
    )
    currency = models.CharField(max_length=3, blank=True)
    broker = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    import_batch = models.ForeignKey(
        "importers.ImportBatch",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transactions",
    )
    fingerprint = models.CharField(
        max_length=64,
        blank=True,
        editable=False,
        help_text="Hash of the source row, used to skip rows that were already imported.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-trade_date", "-id"]
        indexes = [models.Index(fields=["portfolio", "asset", "trade_date"])]
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "fingerprint"],
                condition=~models.Q(fingerprint=""),
                name="unique_import_fingerprint_per_portfolio",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=0)
                & models.Q(price__gte=0)
                & models.Q(fees__gte=0),
                name="transaction_values_not_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.trade_date} {self.kind} {self.asset}"

    def save(self, *args, **kwargs) -> None:
        if not self.currency and self.asset_id:
            self.currency = self.asset.currency
        super().save(*args, **kwargs)

    def clean(self) -> None:
        errors = {}
        if self.kind in TRADE_KINDS and self.quantity <= 0:
            errors["quantity"] = "Quantity must be greater than zero."
        if self.kind == TransactionKind.SPLIT and self.quantity <= 0:
            errors["quantity"] = "Enter the split ratio (2 for a 2-for-1 split)."
        if self.kind in INCOME_KINDS and self.amount <= 0:
            errors["amount"] = "Enter the cash amount received."
        if errors:
            raise ValidationError(errors)

    @property
    def total(self) -> Decimal:
        """Cash moved by this transaction, always positive."""
        if self.kind in INCOME_KINDS:
            return self.amount
        if self.kind == TransactionKind.SELL:
            return self.quantity * self.price - self.fees
        if self.kind in (TransactionKind.BUY, TransactionKind.BONUS):
            return self.quantity * self.price + self.fees
        return ZERO


class Holding(models.Model):
    """Current position in one asset. A cache: rebuilt from the ledger, never edited."""

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="holdings")
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="holdings")
    quantity = models.DecimalField(max_digits=20, decimal_places=8, default=ZERO)
    average_price = models.DecimalField(max_digits=20, decimal_places=8, default=ZERO)
    realized_gain = models.DecimalField(max_digits=20, decimal_places=2, default=ZERO)
    income = models.DecimalField(max_digits=20, decimal_places=2, default=ZERO)
    first_trade = models.DateField(null=True, blank=True)
    last_trade = models.DateField(null=True, blank=True)
    ledger_error = models.CharField(
        max_length=255, blank=True, help_text="Set when the ledger for this asset is inconsistent."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["asset__ticker"]
        constraints = [
            models.UniqueConstraint(fields=["portfolio", "asset"], name="unique_holding_per_asset"),
        ]

    def __str__(self) -> str:
        return f"{self.asset} × {self.quantity.normalize()}"

    @property
    def cost_basis(self) -> Decimal:
        return self.quantity * self.average_price
