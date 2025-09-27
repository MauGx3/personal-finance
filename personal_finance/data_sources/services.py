"""Financial data source integrations with fallback mechanisms.

This module provides robust data source management with automatic failover
to ensure reliable access to financial data from multiple providers.
Implements the circuit breaker pattern for reliability.

The new DataSourceService class provides a modern, adapter-based interface
while maintaining backward compatibility with existing DataSourceBase implementations.
"""

# Handle optional dependencies gracefully
try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import datetime, date, timedelta
from dataclasses import dataclass

# For compatibility with built-in type hints
try:
    # Python 3.10+ has built-in union types, but keep Optional for compatibility
    from typing import Optional, Dict, List, Any
except ImportError:
    pass

try:
    from django.conf import settings
    from django.core.cache import cache
    from django.utils import timezone

    DJANGO_AVAILABLE = True
except ImportError:
    # Fallback for when Django is not available
    DJANGO_AVAILABLE = False
    settings = None

    class FakeCache:
        def get(self, key):
            return None

        def set(self, key, value, timeout=None):
            pass

    cache = FakeCache()

    class FakeTimezone:
        @staticmethod
        def now():
            return datetime.now()

    timezone = FakeTimezone()

# Import new types and adapters
from .types import PricePoint, HistoricalSeries, CompanyInfo
from .adapter import (
    BaseDataSourceAdapter,
    YFinanceAdapter,
    MockAdapter,
    DataSourceError,
)

# Using logger imported above


@dataclass
class PriceData:
    """Standardized price data structure.

    Represents price information from any data source in a consistent format
    for easy consumption by the application.
    """

    symbol: str
    current_price: Decimal
    previous_close: Optional[Decimal] = None
    day_high: Optional[Decimal] = None
    day_low: Optional[Decimal] = None
    volume: Optional[int] = None
    market_cap: Optional[Decimal] = None
    currency: str = "USD"
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = timezone.now()


@dataclass
class HistoricalData:
    """Historical price data structure."""

    symbol: str
    date: date
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    adjusted_close: Optional[Decimal] = None
    volume: int = 0
    dividend_amount: Decimal = Decimal("0")
    split_ratio: Decimal = Decimal("1")


class DataSourceError(Exception):
    """Base exception for data source errors."""

    pass


class RateLimitError(DataSourceError):
    """Exception raised when API rate limit is exceeded."""

    pass


class APIError(DataSourceError):
    """Exception raised for API-related errors."""

    pass


class DataSourceService:
    """Modern data source service with adapter pattern.

    This service provides a clean, testable interface for financial data
    by using dependency injection of data source adapters. It supports
    caching, error handling, and can be easily mocked for testing.
    """

    def __init__(
        self, adapter: BaseDataSourceAdapter, cache_timeout: int = 300
    ):
        """Initialize service with an adapter.

        Args:
            adapter: Data source adapter to use for fetching data
            cache_timeout: Cache timeout in seconds (default: 5 minutes)
        """
        self.adapter = adapter
        self.cache_timeout = cache_timeout

    def get_current_price(self, symbol: str) -> PricePoint | None:
        """Get current price for a symbol with caching.

        Args:
            symbol: Stock symbol (e.g., "AAPL")

        Returns:
            PricePoint with current price data or None if unavailable

        Raises:
            DataSourceError: If there's an error fetching data
        """
        if not symbol:
            return None

        # Clean symbol
        symbol = symbol.strip().upper()

        # Check cache first
        cache_key = f"price_{self.adapter.name}_{symbol}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for {symbol}")
            return cached_data

        try:
            price_point = self.adapter.get_current_price(symbol)

            if price_point:
                # Cache successful result
                cache.set(cache_key, price_point, self.cache_timeout)
                logger.info(
                    f"Fetched current price for {symbol}: ${price_point.price}"
                )

            return price_point

        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            raise DataSourceError(
                f"Failed to get current price for {symbol}: {e}"
            )

    def fetch_historical(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> HistoricalSeries:
        """Fetch historical data for a symbol.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            period: Time period (e.g., "1d", "5d", "1mo", "1y", etc.)
            interval: Data interval (e.g., "1d", "1wk", "1mo")

        Returns:
            HistoricalSeries with price data points

        Raises:
            DataSourceError: If there's an error fetching data
        """
        if not symbol:
            raise DataSourceError("Symbol cannot be empty")

        symbol = symbol.strip().upper()

        # Cache key includes period and interval
        cache_key = (
            f"historical_{self.adapter.name}_{symbol}_{period}_{interval}"
        )
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for historical data: {symbol}")
            return cached_data

        try:
            historical_series = self.adapter.fetch_historical(
                symbol, period, interval
            )

            # Cache for longer time since historical data doesn't change much
            cache.set(
                cache_key, historical_series, self.cache_timeout * 12
            )  # 1 hour default
            logger.info(
                f"Fetched {len(historical_series.data_points)} historical points for {symbol}"
            )

            return historical_series

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            raise DataSourceError(
                f"Failed to fetch historical data for {symbol}: {e}"
            )

    def bulk_get_current(
        self, symbols: list[str]
    ) -> dict[str, PricePoint | None]:
        """Get current prices for multiple symbols efficiently.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbols to PricePoint objects (None if unavailable)

        Raises:
            DataSourceError: If there's a critical error in bulk fetching
        """
        if not symbols:
            return {}

        # Clean and validate symbols
        cleaned_symbols = []
        for symbol in symbols:
            if symbol and isinstance(symbol, str):
                cleaned_symbols.append(symbol.strip().upper())

        if not cleaned_symbols:
            return {}

        # Check cache for each symbol first
        results = {}
        symbols_to_fetch = []

        for symbol in cleaned_symbols:
            cache_key = f"price_{self.adapter.name}_{symbol}"
            cached_data = cache.get(cache_key)
            if cached_data:
                results[symbol] = cached_data
            else:
                symbols_to_fetch.append(symbol)

        # Fetch uncached symbols
        if symbols_to_fetch:
            try:
                fetched_data = self.adapter.bulk_get_current(symbols_to_fetch)

                # Cache the results and merge with cached data
                for symbol, price_point in fetched_data.items():
                    results[symbol] = price_point
                    if price_point:
                        cache_key = f"price_{self.adapter.name}_{symbol}"
                        cache.set(cache_key, price_point, self.cache_timeout)

                logger.info(
                    f"Bulk fetched prices for {len(symbols_to_fetch)} symbols"
                )

            except Exception as e:
                logger.error(f"Error in bulk fetch: {e}")
                # Fall back to individual calls for unfetched symbols
                for symbol in symbols_to_fetch:
                    try:
                        results[symbol] = self.get_current_price(symbol)
                    except Exception as individual_error:
                        logger.warning(
                            f"Individual fetch failed for {symbol}: {individual_error}"
                        )
                        results[symbol] = None

        return results

    def get_company_info(self, symbol: str) -> CompanyInfo | None:
        """Get company information for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            CompanyInfo object or None if unavailable
        """
        if not symbol:
            return None

        symbol = symbol.strip().upper()

        # Cache company info for longer since it changes infrequently
        cache_key = f"company_{self.adapter.name}_{symbol}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            company_info = self.adapter.get_company_info(symbol)
            if company_info:
                cache.set(
                    cache_key, company_info, self.cache_timeout * 48
                )  # 4 hours default

            return company_info

        except Exception as e:
            logger.warning(f"Error fetching company info for {symbol}: {e}")
            return None


# Factory function to create service instances
def create_yfinance_service() -> DataSourceService:
    """Create a DataSourceService configured with YFinance adapter."""
    return DataSourceService(YFinanceAdapter())


def create_mock_service() -> DataSourceService:
    """Create a DataSourceService configured with Mock adapter for testing."""
    return DataSourceService(MockAdapter())


class DataSourceBase(ABC):
    """Abstract base class for financial data sources.

    Defines the interface that all data source implementations must follow,
    ensuring consistent behavior across different providers.
    """

    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key
        self._circuit_breaker_failures = 0
        self._circuit_breaker_last_failure = None
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_timeout = timedelta(minutes=15)

    @abstractmethod
    def get_current_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price data for a symbol.

        Args:
            symbol: Stock symbol or ticker

        Returns:
            PriceData object or None if unavailable

        Raises:
            DataSourceError: If there's an error fetching data
        """
        pass

    @abstractmethod
    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> List[HistoricalData]:
        """Get historical price data for a symbol.

        Args:
            symbol: Stock symbol or ticker
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            List of HistoricalData objects

        Raises:
            DataSourceError: If there's an error fetching data
        """
        pass

    @abstractmethod
    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        """Search for symbols matching a query.

        Args:
            query: Search query (company name, symbol, etc.)

        Returns:
            List of dictionaries with symbol information
        """
        pass

    @abstractmethod
    def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company/asset information.

        Args:
            symbol: Stock symbol or ticker

        Returns:
            Dictionary with company information or None
        """
        pass

    def is_available(self) -> bool:
        """Check if the data source is currently available.

        Implements circuit breaker pattern to avoid calling failing services.

        Returns:
            True if service is available, False otherwise
        """
        if self._circuit_breaker_failures >= self._circuit_breaker_threshold:
            if (
                self._circuit_breaker_last_failure
                and timezone.now() - self._circuit_breaker_last_failure
                < self._circuit_breaker_timeout
            ):
                return False
            else:
                # Reset circuit breaker after timeout
                self._circuit_breaker_failures = 0
                self._circuit_breaker_last_failure = None

        return True

    def _record_failure(self):
        """Record a failure for circuit breaker pattern."""
        self._circuit_breaker_failures += 1
        self._circuit_breaker_last_failure = timezone.now()
        logger.warning(
            f"Data source {self.name} failure #{self._circuit_breaker_failures}"
        )

    def _record_success(self):
        """Record a success, resetting circuit breaker."""
        self._circuit_breaker_failures = 0
        self._circuit_breaker_last_failure = None


class YahooFinanceSource(DataSourceBase):
    """Yahoo Finance data source implementation.

    Primary data source using yfinance library with comprehensive
    market data coverage and no API key requirements.
    """

    def __init__(self):
        super().__init__("Yahoo Finance")
        self._session = None

    def get_current_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price from Yahoo Finance.

        Uses yfinance library to fetch real-time price data.
        Implements caching to reduce API calls.
        """
        if not self.is_available():
            return None

        # Check cache first
        cache_key = f"yahoo_price_{symbol}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            # This is where we would use yfinance
            # For now, return a placeholder implementation
            logger.info("Fetching Yahoo Finance data for %s", symbol)

            # Placeholder implementation - would be replaced with actual yfinance calls
            price_data = PriceData(
                symbol=symbol,
                current_price=Decimal("100.00"),  # Placeholder
                previous_close=Decimal("99.50"),
                day_high=Decimal("101.00"),
                day_low=Decimal("98.50"),
                volume=1000000,
                currency="USD",
            )

            # Cache for 1 minute
            cache.set(cache_key, price_data, 60)

            self._record_success()
            return price_data

        except Exception as e:
            logger.error("Yahoo Finance error for %s: %s", symbol, e)
            self._record_failure()
            raise APIError(f"Yahoo Finance API error: {e}")

    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> List[HistoricalData]:
        """Get historical data from Yahoo Finance."""
        if not self.is_available():
            return []

        try:
            # Placeholder implementation
            logger.info(
                "Fetching Yahoo Finance historical data for %s", symbol
            )

            # Would implement actual yfinance historical data fetch here
            historical_data = []

            self._record_success()
            return historical_data

        except Exception as e:
            logger.error("Yahoo Finance historical data error: %s", e)
            self._record_failure()
            raise APIError(f"Yahoo Finance historical data error: {e}")

    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        """Search symbols using Yahoo Finance."""
        try:
            # Placeholder implementation
            return []
        except Exception as e:
            logger.error("Yahoo Finance search error: %s", e)
            return []

    def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company information from Yahoo Finance."""
        try:
            # Placeholder implementation
            return {}
        except Exception as e:
            logger.error("Yahoo Finance company info error: %s", e)
            return None


class StockdexSource(DataSourceBase):
    """Stockdx data source implementation.

    Alternative data source providing market data with
    fallback capabilities when Yahoo Finance is unavailable.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Stockdx", api_key)

    def get_current_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price from Stockdx."""
        if not self.is_available():
            return None

        try:
            # Placeholder implementation
            logger.info("Fetching Stockdx data for %s", symbol)

            # Would implement actual stockdx API calls here
            price_data = PriceData(
                symbol=symbol,
                current_price=Decimal("100.50"),  # Placeholder
                currency="USD",
            )

            self._record_success()
            return price_data

        except Exception as e:
            logger.error("Stockdx error for %s: %s", symbol, e)
            self._record_failure()
            raise APIError(f"Stockdx API error: {e}")

    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> List[HistoricalData]:
        """Get historical data from Stockdx."""
        if not self.is_available():
            return []

        try:
            # Placeholder implementation
            return []
        except Exception as e:
            logger.error("Stockdx historical data error: %s", e)
            self._record_failure()
            raise APIError(f"Stockdx historical data error: {e}")

    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        """Search symbols using Stockdx."""
        return []

    def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company information from Stockdx."""
        return {}


class AlphaVantageSource(DataSourceBase):
    """Alpha Vantage data source implementation.

    Backup data source with API key requirements but
    reliable service for critical data needs.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            "Alpha Vantage",
            api_key or getattr(settings, "ALPHA_VANTAGE_API_KEY", None),
        )

    def get_current_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price from Alpha Vantage."""
        if not self.is_available() or not self.api_key:
            return None

        try:
            # Placeholder implementation
            logger.info("Fetching Alpha Vantage data for %s", symbol)

            price_data = PriceData(
                symbol=symbol,
                current_price=Decimal("101.00"),  # Placeholder
                currency="USD",
            )

            self._record_success()
            return price_data

        except Exception as e:
            logger.error("Alpha Vantage error for %s: %s", symbol, e)
            self._record_failure()
            raise APIError(f"Alpha Vantage API error: {e}")

    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> List[HistoricalData]:
        """Get historical data from Alpha Vantage."""
        if not self.is_available() or not self.api_key:
            return []

        try:
            # Placeholder implementation
            return []
        except Exception as e:
            logger.error("Alpha Vantage historical data error: %s", e)
            self._record_failure()
            raise APIError(f"Alpha Vantage historical data error: {e}")

    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        """Search symbols using Alpha Vantage."""
        return []

    def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company information from Alpha Vantage."""
        return {}


class DataSourceManager:
    """Manages multiple data sources with automatic fallbacks.

    Implements robust data fetching with multiple source fallbacks,
    circuit breaker patterns, and intelligent source selection based
    on reliability and performance.
    """

    def __init__(self):
        """Initialize with default data sources in priority order."""
        self.sources = [
            YahooFinanceSource(),
            StockdexSource(),
            AlphaVantageSource(),
        ]
        self._source_performance = {}

    def add_source(self, source: DataSourceBase, priority: int = None):
        """Add a new data source.

        Args:
            source: DataSourceBase implementation
            priority: Insert position (None to append)
        """
        if priority is not None:
            self.sources.insert(priority, source)
        else:
            self.sources.append(source)

    def get_current_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price with automatic fallback.

        Tries each data source in order until one succeeds or all fail.

        Args:
            symbol: Stock symbol to fetch

        Returns:
            PriceData object or None if all sources fail
        """
        for source in self.sources:
            try:
                if source.is_available():
                    price_data = source.get_current_price(symbol)
                    if price_data:
                        logger.info(
                            f"Successfully fetched {symbol} from {source.name}"
                        )
                        self._record_source_success(source.name)
                        return price_data
            except (APIError, RateLimitError) as e:
                logger.warning(
                    f"Source {source.name} failed for {symbol}: {e}"
                )
                self._record_source_failure(source.name)
                continue
            except Exception as e:
                logger.error("Unexpected error from %s: %s", source.name, e)
                continue

        logger.error("All data sources failed for symbol: %s", symbol)
        return None

    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> List[HistoricalData]:
        """Get historical data with automatic fallback."""
        for source in self.sources:
            try:
                if source.is_available():
                    historical_data = source.get_historical_data(
                        symbol, start_date, end_date
                    )
                    if historical_data:
                        logger.info(
                            f"Successfully fetched historical data for {symbol} from {source.name}"
                        )
                        return historical_data
            except (APIError, RateLimitError) as e:
                logger.warning(
                    f"Historical data source {source.name} failed: {e}"
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected historical data error from {source.name}: {e}"
                )
                continue

        logger.error("All sources failed for historical data: %s", symbol)
        return []

    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        """Search symbols across all available sources."""
        all_results = []
        seen_symbols = set()

        for source in self.sources:
            try:
                if source.is_available():
                    results = source.search_symbol(query)
                    for result in results:
                        symbol = result.get("symbol", "")
                        if symbol and symbol not in seen_symbols:
                            all_results.append(result)
                            seen_symbols.add(symbol)
            except Exception as e:
                logger.warning(
                    "Symbol search failed for %s: %s", source.name, e
                )
                continue

        return all_results

    def get_source_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all data sources.

        Returns:
            Dictionary with source names and their status information
        """
        status = {}
        for source in self.sources:
            status[source.name] = {
                "available": source.is_available(),
                "failures": source._circuit_breaker_failures,
                "last_failure": source._circuit_breaker_last_failure,
                "performance": self._source_performance.get(source.name, {}),
            }
        return status

    def _record_source_success(self, source_name: str):
        """Record successful data fetch for performance tracking."""
        if source_name not in self._source_performance:
            self._source_performance[source_name] = {
                "successes": 0,
                "failures": 0,
                "last_success": None,
            }

        self._source_performance[source_name]["successes"] += 1
        self._source_performance[source_name]["last_success"] = timezone.now()

    def _record_source_failure(self, source_name: str):
        """Record failed data fetch for performance tracking."""
        if source_name not in self._source_performance:
            self._source_performance[source_name] = {
                "successes": 0,
                "failures": 0,
                "last_failure": None,
            }

        self._source_performance[source_name]["failures"] += 1
        self._source_performance[source_name]["last_failure"] = timezone.now()


# Global data source manager instance (legacy)
data_source_manager = DataSourceManager()

# Global modern data source service instance
data_source_service = create_yfinance_service()
