"""
Abstract framework for financial data sources.

This module provides the base classes and interfaces for implementing
financial data providers in a modular and extensible way.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any


class DataSourceError(Exception):
    """Base exception for data source errors."""

    pass


class RateLimitError(DataSourceError):
    """Raised when rate limits are exceeded."""

    pass


class AuthenticationError(DataSourceError):
    """Raised when authentication fails."""

    pass


class DataUnavailableError(DataSourceError):
    """Raised when requested data is not available."""

    pass


class DataSourceType(Enum):
    """Types of data sources."""

    STOCK_API = "stock_api"
    CRYPTO_API = "crypto_api"
    FOREX_API = "forex_api"
    NEWS_API = "news_api"
    FUNDAMENTALS_API = "fundamentals_api"


@dataclass
class PriceData:
    """Represents a single price data point."""

    date: datetime
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    close: Decimal | None = None
    volume: int | None = None
    adjusted_close: Decimal | None = None


@dataclass
class CompanyInfo:
    """Represents company fundamental information."""

    symbol: str
    name: str | None = None
    sector: str | None = None
    industry: str | None = None
    country: str | None = None
    market_cap: Decimal | None = None
    pe_ratio: Decimal | None = None
    pb_ratio: Decimal | None = None
    dividend_yield: Decimal | None = None
    beta: Decimal | None = None
    fifty_two_week_high: Decimal | None = None
    fifty_two_week_low: Decimal | None = None
    average_volume: int | None = None
    currency: str | None = None
    exchange: str | None = None
    isin: str | None = None
    cusip: str | None = None
    sedol: str | None = None


@dataclass
class NewsItem:
    """Represents a news item."""

    title: str
    url: str
    published_at: datetime
    summary: str | None = None
    source: str | None = None
    author: str | None = None
    tags: list[str] | None = None


@dataclass
class AnalystRecommendation:
    """Represents analyst recommendations."""

    firm: str
    recommendation: str  # "buy", "hold", "sell", etc.
    date: datetime
    target_price: Decimal | None = None
    currency: str | None = None


@dataclass
class FinancialStatement:
    """Represents financial statement data."""

    period_end: date
    revenue: Decimal | None = None
    cost_of_revenue: Decimal | None = None
    gross_profit: Decimal | None = None
    operating_expenses: Decimal | None = None
    operating_income: Decimal | None = None
    net_income: Decimal | None = None
    eps: Decimal | None = None
    diluted_eps: Decimal | None = None


class BaseDataSource(ABC):
    """
    Abstract base class for financial data sources.

    This class defines the interface that all data source implementations
    must follow, providing a consistent API for accessing financial data.
    """

    def __init__(self, api_key: str | None = None, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self._last_request_time: datetime | None = None
        self._request_count = 0

    @property
    @abstractmethod
    def source_type(self) -> DataSourceType:
        """Return the type of this data source."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the human-readable name of this data source."""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return the base URL for API requests."""
        pass

    @abstractmethod
    def get_price_history(
        self,
        symbol: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        interval: str = "1d",
    ) -> list[PriceData]:
        """
        Get historical price data for a symbol.

        Args:
            symbol: The ticker symbol
            start_date: Start date for data (optional)
            end_date: End date for data (optional)
            interval: Data interval ("1d", "1h", "1m", etc.)

        Returns:
            List of PriceData objects
        """
        pass

    @abstractmethod
    def get_company_info(self, symbol: str) -> CompanyInfo:
        """
        Get fundamental company information.

        Args:
            symbol: The ticker symbol

        Returns:
            CompanyInfo object
        """
        pass

    @abstractmethod
    def get_news(self, symbol: str, limit: int = 10) -> list[NewsItem]:
        """
        Get recent news for a symbol.

        Args:
            symbol: The ticker symbol
            limit: Maximum number of news items to return

        Returns:
            List of NewsItem objects
        """
        pass

    def get_analyst_recommendations(self, symbol: str) -> list[AnalystRecommendation]:  # noqa: ARG002
        """
        Get analyst recommendations for a symbol.

        Args:
            symbol: The ticker symbol

        Returns:
            List of AnalystRecommendation objects
        """
        # Default implementation returns empty list
        return []

    def get_income_statement(
        self,
        symbol: str,
        annual: bool = True,
        limit: int = 4,
    ) -> list[FinancialStatement]:
        """
        Get income statement data.

        Args:
            symbol: The ticker symbol
            annual: If True, get annual data; if False, get quarterly
            limit: Number of periods to return

        Returns:
            List of FinancialStatement objects
        """
        # Default implementation returns empty list
        return []

    def get_balance_sheet(
        self,
        symbol: str,
        annual: bool = True,
        limit: int = 4,
    ) -> list[dict[str, Any]]:
        """
        Get balance sheet data.

        Args:
            symbol: The ticker symbol
            annual: If True, get annual data; if False, get quarterly
            limit: Number of periods to return

        Returns:
            List of dictionaries containing balance sheet data
        """
        # Default implementation returns empty list
        return []

    def get_cash_flow(
        self,
        symbol: str,
        annual: bool = True,
        limit: int = 4,
    ) -> list[dict[str, Any]]:
        """
        Get cash flow statement data.

        Args:
            symbol: The ticker symbol
            annual: If True, get annual data; if False, get quarterly
            limit: Number of periods to return

        Returns:
            List of dictionaries containing cash flow data
        """
        # Default implementation returns empty list
        return []

    def get_dividends(self, _symbol: str) -> list[dict[str, Any]]:
        """
        Get dividend history for a symbol.

        Args:
            symbol: The ticker symbol

        Returns:
            List of dictionaries with dividend data
        """
        # Default implementation returns empty list
        return []

    def get_splits(self, _symbol: str) -> list[dict[str, Any]]:
        # noqa: ARG002
        """
        Get stock split history for a symbol.

        Args:
            symbol: The ticker symbol

        Returns:
            List of dictionaries with split data
        """
        # Default implementation returns empty list
        return []

    def get_options_chain(self, _symbol: str) -> dict[str, Any]:
        # noqa: ARG002
        """
        Get options chain data for a symbol.

        Args:
            symbol: The ticker symbol

        Returns:
            Dictionary containing options data
        """
        # Default implementation returns empty dict
        return {}

    def search_symbols(
        self,
        query: str,  # noqa: ARG002
        limit: int = 10,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        # noqa: ARG002
        """
        Search for symbols matching a query.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of dictionaries with symbol information
        """
        # Default implementation returns empty list
        return []

    def is_available(self) -> bool:
        """
        Check if the data source is currently available.

        Returns:
            True if available, False otherwise
        """
        try:
            # Simple availability check - try to get a well-known symbol
            self.get_company_info("AAPL")
            return True
        except Exception:
            return False

    def get_rate_limit_info(self) -> dict[str, Any]:
        """
        Get information about current rate limiting status.

        Returns:
            Dictionary with rate limit information
        """
        return {
            "requests_made": self._request_count,
            "last_request": (
                self._last_request_time.isoformat() if self._last_request_time else None
            ),
        }


class CachingDataSourceMixin:
    """
    Mixin class that adds caching capabilities to data sources.

    This mixin provides methods for caching data to improve performance
    and reduce API calls.
    """

    def __init__(self, *args, cache_backend: Any | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_backend = cache_backend

    def _get_cache_key(self, method: str, *args, **kwargs) -> str:
        """Generate a cache key for a method call."""
        key_parts = [self.__class__.__name__, method]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return ":".join(key_parts)

    def _get_cached_data(self, key: str) -> Any | None:
        """Get data from cache if available."""
        if self.cache_backend:
            return self.cache_backend.get(key)
        return None

    def _set_cached_data(self, key: str, data: Any, ttl: int = 3600) -> None:
        """Store data in cache with TTL."""
        if self.cache_backend:
            self.cache_backend.set(key, data, ttl)

    def cached_method(self, ttl: int = 3600):
        """
        Decorator to add caching to a method.

        Args:
            ttl: Time to live in seconds
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                cache_key = self._get_cache_key(func.__name__, *args, **kwargs)
                cached_data = self._get_cached_data(cache_key)
                if cached_data is not None:
                    return cached_data

                result = func(*args, **kwargs)
                self._set_cached_data(cache_key, result, ttl)
                return result

            return wrapper

        return decorator


class RateLimitedDataSourceMixin:
    """
    Mixin class that adds rate limiting capabilities to data sources.

    This mixin helps prevent hitting API rate limits by tracking request
    frequency and implementing delays when necessary.
    """

    def __init__(self, *args, requests_per_minute: int = 60, **kwargs):
        super().__init__(*args, **kwargs)
        self.requests_per_minute = requests_per_minute
        self._request_times: list[datetime] = []

    def _check_rate_limit(self) -> None:
        """Check if we're within rate limits and wait if necessary."""
        import time
        from datetime import timedelta

        now = datetime.now()
        # Remove requests older than 1 minute
        cutoff = now - timedelta(minutes=1)
        self._request_times = [t for t in self._request_times if t > cutoff]

        if len(self._request_times) >= self.requests_per_minute:
            # Calculate wait time until we can make another request
            oldest_request = min(self._request_times)
            wait_seconds = (oldest_request + timedelta(minutes=1) - now).total_seconds()
            if wait_seconds > 0:
                time.sleep(wait_seconds)

        self._request_times.append(now)

    def _make_request(self, *_args, **_kwargs) -> Any:
        """Make a request with rate limiting."""
        self._check_rate_limit()
        # This would be implemented by subclasses
        raise NotImplementedError
