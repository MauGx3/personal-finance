from decimal import Decimal
from typing import Optional
from datetime import datetime, date

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel


class Asset(TimeStampedModel):
    """Canonical asset metadata for many asset types (stock, bond, crypto, etc.).
    
    Enhanced with additional finance-specific fields and methods for
    comprehensive asset data management and price tracking.
    """

    ASSET_STOCK = "STOCK"
    ASSET_BOND = "BOND"
    ASSET_CRYPTO = "CRYPTO"
    ASSET_CASH = "CASH"
    ASSET_FUND = "FUND"
    ASSET_ETF = "ETF"
    ASSET_FOREX = "FOREX"
    ASSET_FOREIGN = "FOREIGN_STOCK"
    ASSET_REIT = "REIT"
    ASSET_COMMODITY = "COMMODITY"
    ASSET_OPTION = "OPTION"
    ASSET_FUTURE = "FUTURE"

    ASSET_TYPE_CHOICES = [
        (ASSET_STOCK, "Stock"),
        (ASSET_BOND, "Bond"),
        (ASSET_CRYPTO, "Cryptocurrency"),
        (ASSET_CASH, "Cash"),
        (ASSET_FUND, "Mutual Fund"),
        (ASSET_ETF, "Exchange-Traded Fund"),
        (ASSET_FOREX, "Foreign Exchange"),
        (ASSET_FOREIGN, "Foreign Stock"),
        (ASSET_REIT, "Real Estate Investment Trust"),
        (ASSET_COMMODITY, "Commodity"),
        (ASSET_OPTION, "Option"),
        (ASSET_FUTURE, "Future"),
    ]

    # Core identification fields
    symbol = models.CharField(
        max_length=64, 
        db_index=True,
        help_text="Trading symbol or ticker"
    )
    name = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Full name of the asset"
    )
    asset_type = models.CharField(
        max_length=32,
        choices=ASSET_TYPE_CHOICES,
        db_index=True,
        help_text="Type of financial asset"
    )
    
    # Market information
    currency = models.CharField(
        max_length=10, 
        default='USD',
        help_text="Currency the asset is denominated in"
    )
    exchange = models.CharField(
        max_length=64, 
        blank=True,
        help_text="Exchange where the asset is traded"
    )
    primary_exchange = models.CharField(
        max_length=64,
        blank=True,
        help_text="Primary exchange for cross-listed assets"
    )
    
    # Identifiers
    isin = models.CharField(
        max_length=32, 
        blank=True, 
        db_index=True,
        help_text="International Securities Identification Number"
    )
    cusip = models.CharField(
        max_length=32, 
        blank=True,
        help_text="Committee on Uniform Securities Identification Procedures number"
    )
    figi = models.CharField(
        max_length=32,
        blank=True,
        help_text="Financial Instrument Global Identifier"
    )
    
    # Current market data
    current_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Current market price"
    )
    previous_close = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Previous trading day's closing price"
    )
    day_high = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Highest price during current trading day"
    )
    day_low = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Lowest price during current trading day"
    )
    volume = models.BigIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Trading volume for current day"
    )
    
    # Company/Fund information
    market_cap = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Market capitalization"
    )
    sector = models.CharField(
        max_length=100,
        blank=True,
        help_text="Business sector (for stocks)"
    )
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="Industry classification"
    )
    
    # Data quality and tracking
    last_price_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When price data was last updated"
    )
    data_source = models.CharField(
        max_length=50,
        blank=True,
        help_text="Source of the price data (yfinance, stockdx, etc.)"
    )
    is_tradeable = models.BooleanField(
        default=True,
        help_text="Whether this asset can currently be traded"
    )
    
    # Extended metadata
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional asset-specific metadata"
    )
    
    # Status fields
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this asset is actively tracked"
    )

    class Meta:
        ordering = ["symbol", "name"]
        indexes = [
            models.Index(fields=["symbol"]),
            models.Index(fields=["isin"]),
            models.Index(fields=["asset_type"]),
            models.Index(fields=["exchange"]),
            models.Index(fields=["sector"]),
            models.Index(fields=["last_price_update"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["symbol", "exchange"],
                name="unique_symbol_exchange"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.symbol} — {self.name or self.asset_type}"
    
    @property
    def price_change(self) -> Optional[Decimal]:
        """Calculate price change from previous close.
        
        Returns:
            Price change amount or None if data unavailable.
        """
        if self.current_price and self.previous_close:
            return self.current_price - self.previous_close
        return None
    
    @property
    def price_change_percentage(self) -> Optional[Decimal]:
        """Calculate percentage price change from previous close.
        
        Returns:
            Percentage change or None if data unavailable.
        """
        if self.price_change and self.previous_close and self.previous_close != 0:
            return (self.price_change / self.previous_close) * 100
        return None
    
    @property
    def is_stock_like(self) -> bool:
        """Check if asset behaves like a stock for analysis purposes."""
        return self.asset_type in [
            self.ASSET_STOCK, 
            self.ASSET_ETF, 
            self.ASSET_REIT,
            self.ASSET_FOREIGN
        ]
    
    def update_price_data(self, 
                         price: Decimal, 
                         volume: Optional[int] = None,
                         day_high: Optional[Decimal] = None,
                         day_low: Optional[Decimal] = None,
                         source: str = "manual") -> None:
        """Update current price and related market data.
        
        Args:
            price: New current price
            volume: Trading volume (optional)
            day_high: Day's high price (optional)
            day_low: Day's low price (optional)
            source: Data source identifier
        """
        self.previous_close = self.current_price
        self.current_price = price
        
        if volume is not None:
            self.volume = volume
        if day_high is not None:
            self.day_high = day_high
        if day_low is not None:
            self.day_low = day_low
            
        self.data_source = source
        self.last_price_update = timezone.now()
        self.save(update_fields=[
            'previous_close', 'current_price', 'volume', 
            'day_high', 'day_low', 'data_source', 'last_price_update'
        ])


class PriceHistory(TimeStampedModel):
    """Historical price data for assets.
    
    Stores daily OHLCV (Open, High, Low, Close, Volume) data
    for technical analysis and performance calculations.
    """
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='price_history',
        help_text="Asset this price data belongs to"
    )
    date = models.DateField(
        help_text="Trading date for this price data"
    )
    
    # OHLCV data
    open_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Opening price"
    )
    high_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Highest price during the day"
    )
    low_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Lowest price during the day"
    )
    close_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Closing price"
    )
    adjusted_close = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Adjusted closing price (accounts for splits/dividends)"
    )
    volume = models.BigIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Trading volume"
    )
    
    # Additional data
    dividend_amount = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Dividend paid on this date"
    )
    split_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('1'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Stock split ratio (1.0 = no split)"
    )
    
    # Data source tracking
    data_source = models.CharField(
        max_length=50,
        help_text="Source of this price data"
    )
    
    class Meta:
        ordering = ['-date']
        unique_together = ['asset', 'date']
        indexes = [
            models.Index(fields=['asset', '-date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self) -> str:
        return f"{self.asset.symbol} - {self.date} (${self.close_price})"
    
    @property
    def daily_return(self) -> Optional[Decimal]:
        """Calculate daily return percentage.
        
        Returns:
            Daily return percentage or None if no previous day data.
        """
        try:
            previous_day = PriceHistory.objects.filter(
                asset=self.asset,
                date__lt=self.date
            ).order_by('-date').first()
            
            if previous_day and previous_day.close_price != 0:
                return ((self.close_price - previous_day.close_price) / 
                       previous_day.close_price) * 100
        except PriceHistory.DoesNotExist:
            pass
        return None


# Legacy models - these will be migrated to the new portfolios app
# Keeping for backward compatibility during transition

class Portfolio(models.Model):
    """A user-owned portfolio grouping (legacy - use portfolios.Portfolio instead)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="legacy_portfolios",
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
    """A user's holding / position in an asset (legacy - use portfolios.Position instead)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="legacy_holdings",
    )
    asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.CASCADE,
        related_name="legacy_holdings",
    )
    portfolio = models.ForeignKey(
        "assets.Portfolio",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="legacy_holdings",
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
                name="unique_user_asset_portfolio_legacy",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.asset} ({self.quantity})"
