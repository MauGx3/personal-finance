"""Type definitions for financial data sources.

This module contains dataclasses and type definitions used across
the data sources system to ensure consistent data structures and
type safety.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, date

# For compatibility with built-in type hints
try:
    from typing import Optional, List
except ImportError:
    pass


@dataclass
class PricePoint:
    """Single price point with metadata.

    Represents a price at a specific point in time with all necessary
    metadata for portfolio valuation and analysis.
    """

    symbol: str
    price: Decimal
    timestamp: datetime
    currency: str = "USD"
    volume: int | None = None

    def __post_init__(self):
        """Ensure price is a Decimal for precision."""
        if not isinstance(self.price, Decimal):
            self.price = Decimal(str(self.price))


@dataclass
class HistoricalPricePoint:
    """Historical price data point with OHLCV data."""

    symbol: str
    date: date
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int = 0
    adjusted_close: Decimal | None = None
    dividend_amount: Decimal = Decimal("0")
    split_ratio: Decimal = Decimal("1")

    def __post_init__(self):
        """Ensure all prices are Decimals for precision."""
        for field in ["open_price", "high_price", "low_price", "close_price"]:
            value = getattr(self, field)
            if not isinstance(value, Decimal):
                setattr(self, field, Decimal(str(value)))

        if self.adjusted_close is not None and not isinstance(
            self.adjusted_close, Decimal
        ):
            self.adjusted_close = Decimal(str(self.adjusted_close))

        if not isinstance(self.dividend_amount, Decimal):
            self.dividend_amount = Decimal(str(self.dividend_amount))

        if not isinstance(self.split_ratio, Decimal):
            self.split_ratio = Decimal(str(self.split_ratio))


@dataclass
class HistoricalSeries:
    """Collection of historical price points for a symbol."""

    symbol: str
    data_points: list[HistoricalPricePoint]
    start_date: date
    end_date: date

    def __post_init__(self):
        """Sort data points by date and validate date range."""
        self.data_points.sort(key=lambda x: x.date)

        if self.data_points:
            actual_start = self.data_points[0].date
            actual_end = self.data_points[-1].date

            # Update date range to actual data range
            self.start_date = min(self.start_date, actual_start)
            self.end_date = max(self.end_date, actual_end)


@dataclass
class CompanyInfo:
    """Basic company/asset information."""

    symbol: str
    name: str
    sector: str | None = None
    industry: str | None = None
    market_cap: Decimal | None = None
    currency: str = "USD"
    exchange: str | None = None

    def __post_init__(self):
        """Ensure market_cap is a Decimal if provided."""
        if self.market_cap is not None and not isinstance(
            self.market_cap, Decimal
        ):
            self.market_cap = Decimal(str(self.market_cap))
