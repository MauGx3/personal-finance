"""Assets models."""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Asset(models.Model):
    """Financial asset model for storing asset metadata."""

    # Asset type choices
    ASSET_STOCK = "STOCK"
    ASSET_BOND = "BOND"
    ASSET_CRYPTO = "CRYPTO"
    ASSET_CASH = "CASH"
    ASSET_FUND = "FUND"
    ASSET_ETF = "ETF"
    ASSET_FOREX = "FOREX"
    ASSET_COMMODITY = "COMMODITY"
    ASSET_REAL_ESTATE = "REAL_ESTATE"
    ASSET_DERIVATIVE = "DERIVATIVE"

    ASSET_TYPE_CHOICES = [
        (ASSET_STOCK, _("Stock")),
        (ASSET_BOND, _("Bond")),
        (ASSET_CRYPTO, _("Cryptocurrency")),
        (ASSET_CASH, _("Cash")),
        (ASSET_FUND, _("Fund")),
        (ASSET_ETF, _("ETF")),
        (ASSET_FOREX, _("Forex")),
        (ASSET_COMMODITY, _("Commodity")),
        (ASSET_REAL_ESTATE, _("Real Estate")),
        (ASSET_DERIVATIVE, _("Derivative")),
    ]

    # Market choices (major exchanges/markets)
    MARKET_NYSE = "NYSE"
    MARKET_NASDAQ = "NASDAQ"
    MARKET_AMEX = "AMEX"
    MARKET_LSE = "LSE"
    MARKET_TSE = "TSE"
    MARKET_HKEX = "HKEX"
    MARKET_SSE = "SSE"
    MARKET_SZSE = "SZSE"
    MARKET_EURONEXT = "EURONEXT"
    MARKET_CRYPTO = "CRYPTO"
    MARKET_FOREX = "FOREX"
    MARKET_COMMODITY = "COMMODITY"
    MARKET_OTHER = "OTHER"

    MARKET_CHOICES = [
        (MARKET_NYSE, _("New York Stock Exchange")),
        (MARKET_NASDAQ, _("NASDAQ")),
        (MARKET_AMEX, _("American Stock Exchange")),
        (MARKET_LSE, _("London Stock Exchange")),
        (MARKET_TSE, _("Toronto Stock Exchange")),
        (MARKET_HKEX, _("Hong Kong Stock Exchange")),
        (MARKET_SSE, _("Shanghai Stock Exchange")),
        (MARKET_SZSE, _("Shenzhen Stock Exchange")),
        (MARKET_EURONEXT, _("Euronext")),
        (MARKET_CRYPTO, _("Cryptocurrency Exchange")),
        (MARKET_FOREX, _("Foreign Exchange")),
        (MARKET_COMMODITY, _("Commodity Market")),
        (MARKET_OTHER, _("Other")),
    ]

    # Country choices (ISO 3166-1 alpha-2 codes for major markets)
    COUNTRY_US = "US"
    COUNTRY_CA = "CA"
    COUNTRY_GB = "GB"
    COUNTRY_DE = "DE"
    COUNTRY_FR = "FR"
    COUNTRY_NL = "NL"
    COUNTRY_JP = "JP"
    COUNTRY_CN = "CN"
    COUNTRY_HK = "HK"
    COUNTRY_AU = "AU"
    COUNTRY_CH = "CH"
    COUNTRY_SE = "SE"
    COUNTRY_NO = "NO"
    COUNTRY_DK = "DK"
    COUNTRY_FI = "FI"
    COUNTRY_SG = "SG"
    COUNTRY_KR = "KR"
    COUNTRY_IN = "IN"
    COUNTRY_BR = "BR"
    COUNTRY_MX = "MX"
    COUNTRY_AR = "AR"
    COUNTRY_CL = "CL"
    COUNTRY_CO = "CO"
    COUNTRY_PE = "PE"
    COUNTRY_ZA = "ZA"
    COUNTRY_EG = "EG"
    COUNTRY_TR = "TR"
    COUNTRY_RU = "RU"
    COUNTRY_PL = "PL"
    COUNTRY_CZ = "CZ"
    COUNTRY_HU = "HU"
    COUNTRY_RO = "RO"
    COUNTRY_GR = "GR"
    COUNTRY_PT = "PT"
    COUNTRY_ES = "ES"
    COUNTRY_IT = "IT"
    COUNTRY_AT = "AT"
    COUNTRY_BE = "BE"
    COUNTRY_IE = "IE"
    COUNTRY_LU = "LU"
    COUNTRY_MT = "MT"
    COUNTRY_CY = "CY"
    COUNTRY_SI = "SI"
    COUNTRY_SK = "SK"
    COUNTRY_EE = "EE"
    COUNTRY_LV = "LV"
    COUNTRY_LT = "LT"
    COUNTRY_HR = "HR"
    COUNTRY_BA = "BA"
    COUNTRY_ME = "ME"
    COUNTRY_MK = "MK"
    COUNTRY_AL = "AL"
    COUNTRY_RS = "RS"
    COUNTRY_XK = "XK"
    COUNTRY_IS = "IS"
    COUNTRY_LI = "LI"
    COUNTRY_MC = "MC"
    COUNTRY_SM = "SM"
    COUNTRY_VA = "VA"
    COUNTRY_AD = "AD"
    COUNTRY_GI = "GI"
    COUNTRY_JE = "JE"
    COUNTRY_GG = "GG"
    COUNTRY_IM = "IM"
    COUNTRY_FO = "FO"
    COUNTRY_GL = "GL"
    COUNTRY_AX = "AX"
    COUNTRY_BV = "BV"
    COUNTRY_HM = "HM"
    COUNTRY_PM = "PM"
    COUNTRY_ST = "ST"
    COUNTRY_SH = "SH"
    COUNTRY_IO = "IO"
    COUNTRY_CX = "CX"
    COUNTRY_CC = "CC"
    COUNTRY_NF = "NF"
    COUNTRY_TF = "TF"
    COUNTRY_HM_ALT = "HM"
    COUNTRY_PN = "PN"
    COUNTRY_GS = "GS"
    COUNTRY_FK = "FK"
    COUNTRY_AI = "AI"
    COUNTRY_MS = "MS"
    COUNTRY_TC = "TC"
    COUNTRY_VG = "VG"
    COUNTRY_VI = "VI"
    COUNTRY_PR = "PR"
    COUNTRY_AS = "AS"
    COUNTRY_GU = "GU"
    COUNTRY_MP = "MP"
    COUNTRY_UM = "UM"
    COUNTRY_FM = "FM"
    COUNTRY_MH = "MH"
    COUNTRY_PW = "PW"
    COUNTRY_NR = "NR"
    COUNTRY_TV = "TV"
    COUNTRY_KI = "KI"
    COUNTRY_NU = "NU"
    COUNTRY_PF = "PF"
    COUNTRY_WS = "WS"
    COUNTRY_SB = "SB"
    COUNTRY_VU = "VU"
    COUNTRY_NC = "NC"
    COUNTRY_TK = "TK"
    COUNTRY_TO = "TO"
    COUNTRY_WF = "WF"
    COUNTRY_CK = "CK"
    COUNTRY_NZ = "NZ"
    COUNTRY_PG = "PG"
    COUNTRY_SB_ALT = "SB"
    COUNTRY_VU_ALT = "VU"
    COUNTRY_FJ = "FJ"
    COUNTRY_WF_ALT = "WF"
    COUNTRY_AS_ALT = "AS"
    COUNTRY_WS_ALT = "WS"
    COUNTRY_KI_ALT = "KI"
    COUNTRY_NR_ALT = "NR"
    COUNTRY_TV_ALT = "TV"
    COUNTRY_PF_ALT = "PF"
    COUNTRY_NC_ALT = "NC"
    COUNTRY_TK_ALT = "TK"
    COUNTRY_TO_ALT = "TO"
    COUNTRY_CK_ALT = "CK"
    COUNTRY_NZ_ALT = "NZ"
    COUNTRY_PG_ALT = "PG"
    COUNTRY_FJ_ALT = "FJ"
    COUNTRY_GLOBAL = "GLOBAL"

    COUNTRY_CHOICES = [
        (COUNTRY_US, _("United States")),
        (COUNTRY_CA, _("Canada")),
        (COUNTRY_GB, _("United Kingdom")),
        (COUNTRY_DE, _("Germany")),
        (COUNTRY_FR, _("France")),
        (COUNTRY_NL, _("Netherlands")),
        (COUNTRY_JP, _("Japan")),
        (COUNTRY_CN, _("China")),
        (COUNTRY_HK, _("Hong Kong")),
        (COUNTRY_AU, _("Australia")),
        (COUNTRY_CH, _("Switzerland")),
        (COUNTRY_SE, _("Sweden")),
        (COUNTRY_NO, _("Norway")),
        (COUNTRY_DK, _("Denmark")),
        (COUNTRY_FI, _("Finland")),
        (COUNTRY_SG, _("Singapore")),
        (COUNTRY_KR, _("South Korea")),
        (COUNTRY_IN, _("India")),
        (COUNTRY_BR, _("Brazil")),
        (COUNTRY_MX, _("Mexico")),
        (COUNTRY_AR, _("Argentina")),
        (COUNTRY_CL, _("Chile")),
        (COUNTRY_CO, _("Colombia")),
        (COUNTRY_PE, _("Peru")),
        (COUNTRY_ZA, _("South Africa")),
        (COUNTRY_EG, _("Egypt")),
        (COUNTRY_TR, _("Turkey")),
        (COUNTRY_RU, _("Russia")),
        (COUNTRY_PL, _("Poland")),
        (COUNTRY_CZ, _("Czech Republic")),
        (COUNTRY_HU, _("Hungary")),
        (COUNTRY_RO, _("Romania")),
        (COUNTRY_GR, _("Greece")),
        (COUNTRY_PT, _("Portugal")),
        (COUNTRY_ES, _("Spain")),
        (COUNTRY_IT, _("Italy")),
        (COUNTRY_AT, _("Austria")),
        (COUNTRY_BE, _("Belgium")),
        (COUNTRY_IE, _("Ireland")),
        (COUNTRY_LU, _("Luxembourg")),
        (COUNTRY_MT, _("Malta")),
        (COUNTRY_CY, _("Cyprus")),
        (COUNTRY_SI, _("Slovenia")),
        (COUNTRY_SK, _("Slovakia")),
        (COUNTRY_EE, _("Estonia")),
        (COUNTRY_LV, _("Latvia")),
        (COUNTRY_LT, _("Lithuania")),
        (COUNTRY_HR, _("Croatia")),
        (COUNTRY_BA, _("Bosnia and Herzegovina")),
        (COUNTRY_ME, _("Montenegro")),
        (COUNTRY_MK, _("North Macedonia")),
        (COUNTRY_AL, _("Albania")),
        (COUNTRY_RS, _("Serbia")),
        (COUNTRY_XK, _("Kosovo")),
        (COUNTRY_IS, _("Iceland")),
        (COUNTRY_LI, _("Liechtenstein")),
        (COUNTRY_MC, _("Monaco")),
        (COUNTRY_SM, _("San Marino")),
        (COUNTRY_VA, _("Vatican City")),
        (COUNTRY_AD, _("Andorra")),
        (COUNTRY_GI, _("Gibraltar")),
        (COUNTRY_JE, _("Jersey")),
        (COUNTRY_GG, _("Guernsey")),
        (COUNTRY_IM, _("Isle of Man")),
        (COUNTRY_GLOBAL, _("Global/International")),
    ]

    # Core required fields
    ticker = models.CharField(
        _("ticker symbol"),
        max_length=20,
        unique=True,
        db_index=True,
        help_text=_("The asset's ticker symbol (e.g., AAPL, BTC-USD)"),
    )
    name = models.CharField(
        _("name"),
        max_length=255,
        help_text=_("The full name of the asset"),
    )
    asset_type = models.CharField(
        _("asset type"),
        max_length=20,
        choices=ASSET_TYPE_CHOICES,
        db_index=True,
        help_text=_("The type of financial asset"),
    )

    # Location fields
    country = models.CharField(
        _("country"),
        max_length=10,
        choices=COUNTRY_CHOICES,
        db_index=True,
        help_text=_("Country where asset is primarily traded"),
    )
    market = models.CharField(
        _("market"),
        max_length=20,
        choices=MARKET_CHOICES,
        db_index=True,
        help_text=_("Primary market/exchange for trading"),
    )

    # Optional descriptive field
    description = models.TextField(
        _("description"),
        blank=True,
        help_text=_("Optional description of the asset"),
    )

    # Additional identification fields
    isin = models.CharField(
        _("ISIN"),
        max_length=12,
        blank=True,
        unique=True,
        db_index=True,
        help_text=_("International Securities Identification Number"),
    )
    cusip = models.CharField(
        _("CUSIP"),
        max_length=9,
        blank=True,
        db_index=True,
        help_text=_("CUSIP identifier"),
    )
    sedol = models.CharField(
        _("SEDOL"),
        max_length=7,
        blank=True,
        db_index=True,
        help_text=_("Stock Exchange Daily Official List identifier"),
    )

    # Financial attributes
    currency = models.CharField(
        _("currency"),
        max_length=3,
        default="USD",
        help_text=_("Asset currency (ISO 4217 code)"),
    )
    sector = models.CharField(
        _("sector"),
        max_length=100,
        blank=True,
        help_text=_("The sector or industry category of the asset"),
    )
    industry = models.CharField(
        _("industry"),
        max_length=100,
        blank=True,
        help_text=_("The specific industry within the sector"),
    )

    # Status and metadata
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        db_index=True,
        help_text=_("Whether the asset is currently active and tradable"),
    )
    metadata = models.JSONField(
        _("metadata"),
        default=dict,
        blank=True,
        help_text=_("Additional metadata stored as JSON"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("asset")
        verbose_name_plural = _("assets")
        ordering = ["ticker", "name"]
        indexes = [
            models.Index(fields=["ticker"]),
            models.Index(fields=["name"]),
            models.Index(fields=["asset_type", "country"]),
            models.Index(fields=["market", "is_active"]),
            models.Index(fields=["isin"]),
            models.Index(fields=["cusip"]),
            models.Index(fields=["sedol"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(ticker__regex=r"^[A-Z0-9\-_.]+$"),
                name="ticker_format_check",
            ),
        ]

    def __str__(self) -> str:
        """String representation of the asset."""
        return f"{self.ticker} - {self.name}"

    def get_display_name(self) -> str:
        """Get a user-friendly display name for the asset."""
        return f"{self.name} ({self.ticker})"

    def get_full_description(self) -> str:
        """Get a comprehensive description including type and location."""
        parts = [self.name, f"({self.ticker})"]
        if self.asset_type:
            parts.append(f"- {self.get_asset_type_display()}")
        if self.market:
            parts.append(f"on {self.get_market_display()}")
        if self.country:
            parts.append(f"({self.get_country_display()})")
        return " ".join(parts)

    @property
    def is_crypto(self) -> bool:
        """Check if the asset is a cryptocurrency."""
        return self.asset_type == self.ASSET_CRYPTO

    @property
    def is_equity(self) -> bool:
        """Check if the asset is an equity (stock or ETF)."""
        return self.asset_type in [self.ASSET_STOCK, self.ASSET_ETF]

    @property
    def is_fixed_income(self) -> bool:
        """Check if the asset is fixed income (bond)."""
        return self.asset_type == self.ASSET_BOND


class Portfolio(models.Model):
    """A user-owned portfolio grouping holdings."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolios",
        help_text=_("The user who owns this portfolio"),
    )
    name = models.CharField(
        _("name"),
        max_length=150,
        help_text=_("Portfolio name"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        help_text=_("Optional portfolio description"),
    )
    is_default = models.BooleanField(
        _("is default"),
        default=False,
        help_text=_("Whether this is the user's default portfolio"),
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        help_text=_("Whether this portfolio is active"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("portfolio")
        verbose_name_plural = _("portfolios")
        ordering = ["-is_default", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_user_portfolio_name",
            ),
        ]

    def __str__(self) -> str:
        """String representation of the portfolio."""
        return f"{self.name} ({self.user.email})"

    def save(self, *args, **kwargs):
        """Ensure only one default portfolio per user."""
        if self.is_default:
            # Set all other portfolios for this user to non-default
            Portfolio.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(
                is_default=False
            )
        super().save(*args, **kwargs)

    @property
    def total_value(self) -> Decimal:
        """Calculate total portfolio value."""
        # This will be implemented when we add pricing data
        return Decimal("0.00")

    @property
    def holdings_count(self) -> int:
        """Get the number of holdings in this portfolio."""
        return self.holdings.count()


class Holding(models.Model):
    """A user's holding/position in an asset."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="holdings",
        help_text=_("The user who owns this holding"),
    )
    asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.CASCADE,
        related_name="holdings",
        help_text=_("The asset being held"),
    )
    portfolio = models.ForeignKey(
        "assets.Portfolio",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="holdings",
        help_text=_("Portfolio containing this holding (optional)"),
    )

    quantity = models.DecimalField(
        _("quantity"),
        max_digits=20,
        decimal_places=8,
        default=Decimal("0"),
        help_text=_("Number of shares/units held"),
    )
    average_price = models.DecimalField(
        _("average price"),
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text=_("Average purchase price per share/unit"),
    )
    currency = models.CharField(
        _("currency"),
        max_length=3,
        default="USD",
        help_text=_("Currency of the holding"),
    )

    # Transaction tracking
    acquired_at = models.DateTimeField(
        _("acquired at"),
        null=True,
        blank=True,
        help_text=_("When the holding was first acquired"),
    )
    last_transaction_at = models.DateTimeField(
        _("last transaction at"),
        null=True,
        blank=True,
        help_text=_("Date of the last transaction"),
    )

    # Status
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        help_text=_("Whether this holding is still active"),
    )

    # Notes and metadata
    notes = models.TextField(
        _("notes"),
        blank=True,
        help_text=_("Optional notes about this holding"),
    )
    metadata = models.JSONField(
        _("metadata"),
        default=dict,
        blank=True,
        help_text=_("Additional metadata stored as JSON"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("holding")
        verbose_name_plural = _("holdings")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "asset", "portfolio"],
                name="unique_user_asset_portfolio_holding",
            ),
            models.CheckConstraint(
                check=models.Q(quantity__gte=0),
                name="quantity_non_negative",
            ),
        ]

    def __str__(self) -> str:
        """String representation of the holding."""
        portfolio_name = f" in {self.portfolio.name}" if self.portfolio else ""
        return f"{self.user.email} - {self.asset.ticker} " f"({self.quantity}){portfolio_name}"

    def save(self, *args, **kwargs) -> None:
        """Ensure holding.user matches portfolio.user when portfolio is set."""
        if self.portfolio and not self.user_id:
            self.user = self.portfolio.user
        super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        """Compatibility shim: accept legacy `cost_basis_per_unit` kwarg."""
        _sentinel = object()
        cost = kwargs.pop("cost_basis_per_unit", _sentinel)
        if cost is not _sentinel and "average_price" not in kwargs:
            kwargs["average_price"] = cost
        super().__init__(*args, **kwargs)

    @property
    def cost_basis_per_unit(self) -> Decimal:
        """Backward-compatible alias for `average_price`."""
        return self.average_price or Decimal("0")

    @cost_basis_per_unit.setter
    def cost_basis_per_unit(self, value):
        """Set average price via legacy property."""
        self.average_price = value

    @property
    def total_cost_basis(self) -> Decimal:
        """Computed total cost basis for this holding."""
        if self.average_price is None or self.quantity is None:
            return Decimal("0")
        return self.quantity * self.average_price

    @property
    def current_value(self) -> Decimal:
        """Calculate current value (placeholder for future implementation)."""
        # This will be implemented when we add pricing data
        return Decimal("0.00")

    @property
    def unrealized_gain_loss(self) -> Decimal:
        """Calculate unrealized gain/loss (placeholder for future
        implementation)."""
        return self.current_value - self.total_cost_basis
