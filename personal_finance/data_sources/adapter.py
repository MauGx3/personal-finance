"""Data source adapters for financial data.

This module implements the adapter pattern to provide a consistent interface
for different financial data providers. Adapters can be swapped for testing
or to change data providers without affecting business logic.
"""

import re
from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import datetime, date, timedelta

# Handle optional dependencies gracefully
try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

from .types import (
    PricePoint,
    HistoricalSeries,
    HistoricalPricePoint,
    CompanyInfo,
)


class DataSourceError(Exception):
    """Base exception for data source errors."""

    pass


class RateLimitError(DataSourceError):
    """Exception raised when API rate limit is exceeded."""

    pass


class InvalidSymbolError(DataSourceError):
    """Exception raised for invalid stock symbols."""

    pass


class BaseDataSourceAdapter(ABC):
    """Abstract base class for data source adapters.

    Defines the interface that all data source adapters must implement,
    ensuring consistent behavior across different providers.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_current_price(self, symbol: str) -> PricePoint | None:
        """Get current price for a symbol.

        Args:
            symbol: Stock symbol or ticker (e.g., "AAPL", "MSFT")

        Returns:
            PricePoint with current price data or None if unavailable

        Raises:
            DataSourceError: If there's an error fetching data
            InvalidSymbolError: If the symbol is invalid
        """
        pass

    @abstractmethod
    def fetch_historical(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> HistoricalSeries:
        """Fetch historical data for a symbol.

        Args:
            symbol: Stock symbol or ticker
            period: Time period (e.g., "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
            interval: Data interval (e.g., "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")

        Returns:
            HistoricalSeries with price data points

        Raises:
            DataSourceError: If there's an error fetching data
            InvalidSymbolError: If the symbol is invalid
        """
        pass

    @abstractmethod
    def bulk_get_current(
        self, symbols: list[str]
    ) -> dict[str, PricePoint | None]:
        """Get current prices for multiple symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbols to PricePoint objects (or None if unavailable)

        Raises:
            DataSourceError: If there's an error fetching data
        """
        pass

    @abstractmethod
    def get_company_info(self, symbol: str) -> CompanyInfo | None:
        """Get company information for a symbol.

        Args:
            symbol: Stock symbol or ticker

        Returns:
            CompanyInfo object or None if unavailable

        Raises:
            DataSourceError: If there's an error fetching data
        """
        pass

    def _validate_symbol(self, symbol: str) -> str:
        """Validate and normalize symbol format.

        Args:
            symbol: Raw symbol input

        Returns:
            Normalized symbol

        Raises:
            InvalidSymbolError: If symbol format is invalid
        """
        if not symbol or not isinstance(symbol, str):
            raise InvalidSymbolError("Symbol must be a non-empty string")

        # Clean and normalize symbol
        symbol = symbol.strip().upper()

        # Basic validation - alphanumeric and common separators
        if not re.match(r"^[A-Z0-9.\-^]+$", symbol):
            raise InvalidSymbolError(f"Invalid symbol format: {symbol}")

        # Prevent excessively long symbols (security measure)
        if len(symbol) > 10:
            raise InvalidSymbolError(f"Symbol too long: {symbol}")

        return symbol


class YFinanceAdapter(BaseDataSourceAdapter):
    """Yahoo Finance adapter using yfinance library."""

    def __init__(self):
        super().__init__("Yahoo Finance")
        self._session = None

    def get_current_price(self, symbol: str) -> PricePoint | None:
        """Get current price from Yahoo Finance."""
        symbol = self._validate_symbol(symbol)

        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            # Get the most recent day's data
            hist = ticker.history(period="1d", interval="1m")

            if hist.empty:
                logger.warning(f"No current price data available for {symbol}")
                return None

            # Get the latest price point
            latest_price = hist["Close"].iloc[-1]
            latest_timestamp = hist.index[-1].to_pydatetime()
            latest_volume = (
                int(hist["Volume"].iloc[-1])
                if not hist["Volume"].empty
                else None
            )

            return PricePoint(
                symbol=symbol,
                price=Decimal(str(latest_price)),
                timestamp=latest_timestamp,
                volume=latest_volume,
                currency="USD",  # yfinance typically returns USD
            )

        except ImportError:
            logger.error("yfinance library not available")
            raise DataSourceError("yfinance library not installed")
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            raise DataSourceError(
                f"Failed to fetch current price for {symbol}: {e}"
            )

    def fetch_historical(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> HistoricalSeries:
        """Fetch historical data from Yahoo Finance."""
        symbol = self._validate_symbol(symbol)

        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                logger.warning(f"No historical data available for {symbol}")
                return HistoricalSeries(
                    symbol=symbol,
                    data_points=[],
                    start_date=date.today() - timedelta(days=365),
                    end_date=date.today(),
                )

            data_points = []
            for idx, row in hist.iterrows():
                data_points.append(
                    HistoricalPricePoint(
                        symbol=symbol,
                        date=idx.date(),
                        open_price=Decimal(str(row["Open"])),
                        high_price=Decimal(str(row["High"])),
                        low_price=Decimal(str(row["Low"])),
                        close_price=Decimal(str(row["Close"])),
                        volume=int(row["Volume"])
                        if not row["Volume"] != row["Volume"]
                        else 0,  # Check for NaN
                        adjusted_close=Decimal(
                            str(row["Close"])
                        ),  # yfinance typically returns adjusted close
                    )
                )

            start_date = hist.index[0].date()
            end_date = hist.index[-1].date()

            return HistoricalSeries(
                symbol=symbol,
                data_points=data_points,
                start_date=start_date,
                end_date=end_date,
            )

        except ImportError:
            logger.error("yfinance library not available")
            raise DataSourceError("yfinance library not installed")
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            raise DataSourceError(
                f"Failed to fetch historical data for {symbol}: {e}"
            )

    def bulk_get_current(
        self, symbols: list[str]
    ) -> dict[str, PricePoint | None]:
        """Get current prices for multiple symbols."""
        results = {}

        # Validate all symbols first
        validated_symbols = []
        for symbol in symbols:
            try:
                validated_symbols.append(self._validate_symbol(symbol))
            except InvalidSymbolError as e:
                logger.warning(f"Skipping invalid symbol {symbol}: {e}")
                results[symbol] = None

        if not validated_symbols:
            return results

        try:
            import yfinance as yf

            # yfinance can handle multiple symbols with space-separated string
            symbols_str = " ".join(validated_symbols)
            data = yf.download(
                symbols_str,
                period="1d",
                interval="1m",
                group_by="ticker",
                progress=False,
            )

            for symbol in validated_symbols:
                try:
                    if len(validated_symbols) == 1:
                        # Single symbol returns different structure
                        symbol_data = data
                    else:
                        symbol_data = data[symbol]

                    if symbol_data.empty:
                        results[symbol] = None
                        continue

                    latest_price = symbol_data["Close"].iloc[-1]
                    latest_timestamp = symbol_data.index[-1].to_pydatetime()
                    latest_volume = (
                        int(symbol_data["Volume"].iloc[-1])
                        if not symbol_data["Volume"].empty
                        else None
                    )

                    results[symbol] = PricePoint(
                        symbol=symbol,
                        price=Decimal(str(latest_price)),
                        timestamp=latest_timestamp,
                        volume=latest_volume,
                        currency="USD",
                    )

                except Exception as e:
                    logger.warning(f"Error processing data for {symbol}: {e}")
                    results[symbol] = None

        except ImportError:
            logger.error("yfinance library not available")
            raise DataSourceError("yfinance library not installed")
        except Exception as e:
            logger.error(f"Error in bulk fetch: {e}")
            # Fall back to individual calls
            for symbol in validated_symbols:
                try:
                    results[symbol] = self.get_current_price(symbol)
                except Exception as individual_error:
                    logger.warning(
                        f"Individual fetch also failed for {symbol}: {individual_error}"
                    )
                    results[symbol] = None

        return results

    def get_company_info(self, symbol: str) -> CompanyInfo | None:
        """Get company information from Yahoo Finance."""
        symbol = self._validate_symbol(symbol)

        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                return None

            return CompanyInfo(
                symbol=symbol,
                name=info.get("longName", info.get("shortName", symbol)),
                sector=info.get("sector"),
                industry=info.get("industry"),
                market_cap=Decimal(str(info["marketCap"]))
                if info.get("marketCap")
                else None,
                currency=info.get("currency", "USD"),
                exchange=info.get("exchange"),
            )

        except ImportError:
            logger.error("yfinance library not available")
            raise DataSourceError("yfinance library not installed")
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {e}")
            return None


class MockAdapter(BaseDataSourceAdapter):
    """Mock adapter for testing that returns deterministic values."""

    def __init__(self):
        super().__init__("Mock Data Source")
        self._prices = {
            "AAPL": Decimal("150.00"),
            "MSFT": Decimal("300.00"),
            "GOOGL": Decimal("2500.00"),
            "TSLA": Decimal("800.00"),
        }

    def get_current_price(self, symbol: str) -> PricePoint | None:
        """Return mock price data."""
        symbol = self._validate_symbol(symbol)

        price = self._prices.get(symbol, Decimal("100.00"))

        return PricePoint(
            symbol=symbol,
            price=price,
            timestamp=datetime.now(),
            volume=1000000,
            currency="USD",
        )

    def fetch_historical(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> HistoricalSeries:
        """Return mock historical data."""
        symbol = self._validate_symbol(symbol)

        base_price = self._prices.get(symbol, Decimal("100.00"))
        data_points = []

        # Generate 30 days of mock data
        for i in range(30):
            day_date = date.today() - timedelta(days=29 - i)

            # Simulate price fluctuation
            price_variation = Decimal(
                str(0.95 + (i % 10) * 0.01)
            )  # ±5% variation
            day_price = base_price * price_variation

            data_points.append(
                HistoricalPricePoint(
                    symbol=symbol,
                    date=day_date,
                    open_price=day_price * Decimal("0.995"),
                    high_price=day_price * Decimal("1.02"),
                    low_price=day_price * Decimal("0.98"),
                    close_price=day_price,
                    volume=1000000 + (i * 10000),
                    adjusted_close=day_price,
                )
            )

        return HistoricalSeries(
            symbol=symbol,
            data_points=data_points,
            start_date=date.today() - timedelta(days=29),
            end_date=date.today(),
        )

    def bulk_get_current(
        self, symbols: list[str]
    ) -> dict[str, PricePoint | None]:
        """Return mock prices for multiple symbols."""
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.get_current_price(symbol)
            except InvalidSymbolError:
                results[symbol] = None
        return results

    def get_company_info(self, symbol: str) -> CompanyInfo | None:
        """Return mock company information."""
        symbol = self._validate_symbol(symbol)

        mock_companies = {
            "AAPL": CompanyInfo(
                symbol=symbol,
                name="Apple Inc.",
                sector="Technology",
                industry="Consumer Electronics",
                market_cap=Decimal("2500000000000"),
                exchange="NASDAQ",
            ),
            "MSFT": CompanyInfo(
                symbol=symbol,
                name="Microsoft Corporation",
                sector="Technology",
                industry="Software",
                market_cap=Decimal("2300000000000"),
                exchange="NASDAQ",
            ),
        }

        return mock_companies.get(
            symbol,
            CompanyInfo(
                symbol=symbol,
                name=f"{symbol} Corporation",
                sector="Technology",
                industry="Software",
            ),
        )
