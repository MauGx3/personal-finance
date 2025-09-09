"""Financial data source integrations with fallback mechanisms.

This module provides robust data source management with automatic failover
to ensure reliable access to financial data from multiple providers.
Implements the circuit breaker pattern for reliability.
"""

import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, timedelta
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


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
    currency: str = 'USD'
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
    dividend_amount: Decimal = Decimal('0')
    split_ratio: Decimal = Decimal('1')


class DataSourceError(Exception):
    """Base exception for data source errors."""
    pass


class RateLimitError(DataSourceError):
    """Exception raised when API rate limit is exceeded."""
    pass


class APIError(DataSourceError):
    """Exception raised for API-related errors."""
    pass


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
    def get_historical_data(self, 
                          symbol: str, 
                          start_date: date, 
                          end_date: date) -> List[HistoricalData]:
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
            if (self._circuit_breaker_last_failure and 
                timezone.now() - self._circuit_breaker_last_failure < self._circuit_breaker_timeout):
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
        logger.warning(f"Data source {self.name} failure #{self._circuit_breaker_failures}")
    
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
            logger.info(f"Fetching Yahoo Finance data for {symbol}")
            
            # Placeholder implementation - would be replaced with actual yfinance calls
            price_data = PriceData(
                symbol=symbol,
                current_price=Decimal('100.00'),  # Placeholder
                previous_close=Decimal('99.50'),
                day_high=Decimal('101.00'),
                day_low=Decimal('98.50'),
                volume=1000000,
                currency='USD'
            )
            
            # Cache for 1 minute
            cache.set(cache_key, price_data, 60)
            
            self._record_success()
            return price_data
            
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            self._record_failure()
            raise APIError(f"Yahoo Finance API error: {e}")
    
    def get_historical_data(self, 
                          symbol: str, 
                          start_date: date, 
                          end_date: date) -> List[HistoricalData]:
        """Get historical data from Yahoo Finance."""
        if not self.is_available():
            return []
        
        try:
            # Placeholder implementation
            logger.info(f"Fetching Yahoo Finance historical data for {symbol}")
            
            # Would implement actual yfinance historical data fetch here
            historical_data = []
            
            self._record_success()
            return historical_data
            
        except Exception as e:
            logger.error(f"Yahoo Finance historical data error: {e}")
            self._record_failure()
            raise APIError(f"Yahoo Finance historical data error: {e}")
    
    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        """Search symbols using Yahoo Finance."""
        try:
            # Placeholder implementation
            return []
        except Exception as e:
            logger.error(f"Yahoo Finance search error: {e}")
            return []
    
    def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company information from Yahoo Finance."""
        try:
            # Placeholder implementation
            return {}
        except Exception as e:
            logger.error(f"Yahoo Finance company info error: {e}")
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
            logger.info(f"Fetching Stockdx data for {symbol}")
            
            # Would implement actual stockdx API calls here
            price_data = PriceData(
                symbol=symbol,
                current_price=Decimal('100.50'),  # Placeholder
                currency='USD'
            )
            
            self._record_success()
            return price_data
            
        except Exception as e:
            logger.error(f"Stockdx error for {symbol}: {e}")
            self._record_failure()
            raise APIError(f"Stockdx API error: {e}")
    
    def get_historical_data(self, 
                          symbol: str, 
                          start_date: date, 
                          end_date: date) -> List[HistoricalData]:
        """Get historical data from Stockdx."""
        if not self.is_available():
            return []
        
        try:
            # Placeholder implementation
            return []
        except Exception as e:
            logger.error(f"Stockdx historical data error: {e}")
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
        super().__init__("Alpha Vantage", api_key or getattr(settings, 'ALPHA_VANTAGE_API_KEY', None))
    
    def get_current_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price from Alpha Vantage."""
        if not self.is_available() or not self.api_key:
            return None
        
        try:
            # Placeholder implementation
            logger.info(f"Fetching Alpha Vantage data for {symbol}")
            
            price_data = PriceData(
                symbol=symbol,
                current_price=Decimal('101.00'),  # Placeholder
                currency='USD'
            )
            
            self._record_success()
            return price_data
            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            self._record_failure()
            raise APIError(f"Alpha Vantage API error: {e}")
    
    def get_historical_data(self, 
                          symbol: str, 
                          start_date: date, 
                          end_date: date) -> List[HistoricalData]:
        """Get historical data from Alpha Vantage."""
        if not self.is_available() or not self.api_key:
            return []
        
        try:
            # Placeholder implementation
            return []
        except Exception as e:
            logger.error(f"Alpha Vantage historical data error: {e}")
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
                        logger.info(f"Successfully fetched {symbol} from {source.name}")
                        self._record_source_success(source.name)
                        return price_data
            except (APIError, RateLimitError) as e:
                logger.warning(f"Source {source.name} failed for {symbol}: {e}")
                self._record_source_failure(source.name)
                continue
            except Exception as e:
                logger.error(f"Unexpected error from {source.name}: {e}")
                continue
        
        logger.error(f"All data sources failed for symbol: {symbol}")
        return None
    
    def get_historical_data(self, 
                          symbol: str, 
                          start_date: date, 
                          end_date: date) -> List[HistoricalData]:
        """Get historical data with automatic fallback."""
        for source in self.sources:
            try:
                if source.is_available():
                    historical_data = source.get_historical_data(symbol, start_date, end_date)
                    if historical_data:
                        logger.info(f"Successfully fetched historical data for {symbol} from {source.name}")
                        return historical_data
            except (APIError, RateLimitError) as e:
                logger.warning(f"Historical data source {source.name} failed: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected historical data error from {source.name}: {e}")
                continue
        
        logger.error(f"All sources failed for historical data: {symbol}")
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
                        symbol = result.get('symbol', '')
                        if symbol and symbol not in seen_symbols:
                            all_results.append(result)
                            seen_symbols.add(symbol)
            except Exception as e:
                logger.warning(f"Symbol search failed for {source.name}: {e}")
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
                'available': source.is_available(),
                'failures': source._circuit_breaker_failures,
                'last_failure': source._circuit_breaker_last_failure,
                'performance': self._source_performance.get(source.name, {})
            }
        return status
    
    def _record_source_success(self, source_name: str):
        """Record successful data fetch for performance tracking."""
        if source_name not in self._source_performance:
            self._source_performance[source_name] = {
                'successes': 0, 
                'failures': 0, 
                'last_success': None
            }
        
        self._source_performance[source_name]['successes'] += 1
        self._source_performance[source_name]['last_success'] = timezone.now()
    
    def _record_source_failure(self, source_name: str):
        """Record failed data fetch for performance tracking."""
        if source_name not in self._source_performance:
            self._source_performance[source_name] = {
                'successes': 0, 
                'failures': 0, 
                'last_failure': None
            }
        
        self._source_performance[source_name]['failures'] += 1
        self._source_performance[source_name]['last_failure'] = timezone.now()


# Global data source manager instance
data_source_manager = DataSourceManager()