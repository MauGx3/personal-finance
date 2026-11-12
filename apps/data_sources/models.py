"""Stored market data: daily closes and exchange rates."""

from django.db import models

from apps.assets.models import Asset


class PriceQuote(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="quotes")
    day = models.DateField()
    close = models.DecimalField(max_digits=20, decimal_places=8)
    source = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["asset", "day"]
        constraints = [
            models.UniqueConstraint(fields=["asset", "day"], name="unique_quote_per_asset_day"),
        ]

    def __str__(self) -> str:
        return f"{self.asset} {self.day} {self.close}"


class FxRate(models.Model):
    """Price of one unit of ``base`` in ``quote`` on ``day``."""

    base = models.CharField(max_length=3)
    quote = models.CharField(max_length=3)
    day = models.DateField()
    rate = models.DecimalField(max_digits=20, decimal_places=8)
    source = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["base", "quote", "day"]
        constraints = [
            models.UniqueConstraint(fields=["base", "quote", "day"], name="unique_fx_rate_per_day"),
        ]

    def __str__(self) -> str:
        return f"{self.base}/{self.quote} {self.day} {self.rate}"
