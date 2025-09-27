"""Tests for data source adapters interface compliance."""

import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import patch, MagicMock

from personal_finance.data_sources.adapter import (
    BaseDataSourceAdapter,
    YFinanceAdapter,
    MockAdapter,
    DataSourceError,
    InvalidSymbolError,
)
from personal_finance.data_sources.types import (
    PricePoint,
    HistoricalSeries,
    CompanyInfo,
)


class TestBaseDataSourceAdapter:
    """Test the abstract base adapter interface."""

    def test_cannot_instantiate_abstract_base(self):
        """Test that BaseDataSourceAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseDataSourceAdapter("Test")  # pylint: disable=E0110

    def test_symbol_validation(self):
        """Test symbol validation logic."""
        adapter = MockAdapter()  # Use mock since base is abstract

        # Valid symbols
        assert adapter._validate_symbol("AAPL") == "AAPL"
        assert adapter._validate_symbol("aapl") == "AAPL"
        assert adapter._validate_symbol(" MSFT ") == "MSFT"
        assert adapter._validate_symbol("BRK.B") == "BRK.B"
        assert adapter._validate_symbol("BRK-B") == "BRK-B"

        # Invalid symbols
        with pytest.raises(InvalidSymbolError):
            adapter._validate_symbol("")

        with pytest.raises(InvalidSymbolError):
            adapter._validate_symbol(None)

        with pytest.raises(InvalidSymbolError):
            adapter._validate_symbol("INVALID@SYMBOL")

        with pytest.raises(InvalidSymbolError):
            adapter._validate_symbol("TOOLONGSYMBOL")


class TestMockAdapter:
    """Test the MockAdapter implementation."""

    def setup_method(self):
        self.adapter = MockAdapter()

    def test_get_current_price(self):
        """Test current price fetching."""
        price_point = self.adapter.get_current_price("AAPL")

        assert isinstance(price_point, PricePoint)
        assert price_point.symbol == "AAPL"
        assert price_point.price == Decimal("150.00")
        assert price_point.currency == "USD"
        assert isinstance(price_point.timestamp, datetime)
        assert price_point.volume == 1000000

    def test_get_current_price_unknown_symbol(self):
        """Test current price for unknown symbol returns default."""
        price_point = self.adapter.get_current_price("UNKNOWN")

        assert isinstance(price_point, PricePoint)
        assert price_point.symbol == "UNKNOWN"
        assert price_point.price == Decimal("100.00")  # Default price

    def test_fetch_historical(self):
        """Test historical data fetching."""
        historical = self.adapter.fetch_historical("AAPL")

        assert isinstance(historical, HistoricalSeries)
        assert historical.symbol == "AAPL"
        assert len(historical.data_points) == 30  # Mock returns 30 days
        assert historical.start_date <= historical.end_date

        # Test data points are ordered by date
        dates = [point.date for point in historical.data_points]
        assert dates == sorted(dates)

        # Test data point structure
        point = historical.data_points[0]
        assert isinstance(point.open_price, Decimal)
        assert isinstance(point.high_price, Decimal)
        assert isinstance(point.low_price, Decimal)
        assert isinstance(point.close_price, Decimal)
        assert isinstance(point.volume, int)

    def test_bulk_get_current(self):
        """Test bulk price fetching."""
        symbols = ["AAPL", "MSFT", "INVALID@"]
        results = self.adapter.bulk_get_current(symbols)

        assert len(results) == 3
        assert isinstance(results["AAPL"], PricePoint)
        assert isinstance(results["MSFT"], PricePoint)
        assert results["INVALID@"] is None  # Invalid symbol

        assert results["AAPL"].price == Decimal("150.00")
        assert results["MSFT"].price == Decimal("300.00")

    def test_get_company_info(self):
        """Test company information fetching."""
        # Known company
        info = self.adapter.get_company_info("AAPL")
        assert isinstance(info, CompanyInfo)
        assert info.symbol == "AAPL"
        assert info.name == "Apple Inc."
        assert info.sector == "Technology"

        # Unknown company gets default info
        info = self.adapter.get_company_info("UNKNOWN")
        assert isinstance(info, CompanyInfo)
        assert info.symbol == "UNKNOWN"
        assert info.name == "UNKNOWN Corporation"


class TestYFinanceAdapter:
    """Test the YFinanceAdapter implementation with mocking."""

    def setup_method(self):
        self.adapter = YFinanceAdapter()

    @patch("yfinance.Ticker")
    def test_get_current_price_success(self, mock_ticker_class):
        """Test successful current price fetching."""
        # Mock yfinance response
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker

        # Create mock DataFrame-like object
        mock_hist = MagicMock()
        mock_hist.empty = False
        mock_hist.__getitem__.return_value.iloc = MagicMock()
        mock_hist["Close"].iloc.__getitem__.return_value = 150.50
        mock_hist["Volume"].iloc.__getitem__.return_value = 1000000
        mock_hist.index = [MagicMock()]
        mock_hist.index[-1].to_pydatetime.return_value = datetime(
            2023, 1, 1, 12, 0, 0
        )

        mock_ticker.history.return_value = mock_hist

        price_point = self.adapter.get_current_price("AAPL")

        assert isinstance(price_point, PricePoint)
        assert price_point.symbol == "AAPL"
        assert price_point.price == Decimal("150.50")
        assert price_point.volume == 1000000
        assert price_point.currency == "USD"

    @patch("yfinance.Ticker")
    def test_get_current_price_no_data(self, mock_ticker_class):
        """Test handling of no data available."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker

        mock_hist = MagicMock()
        mock_hist.empty = True
        mock_ticker.history.return_value = mock_hist

        price_point = self.adapter.get_current_price("AAPL")
        assert price_point is None

    def test_get_current_price_no_yfinance(self):
        """Test handling when yfinance is not available."""
        with patch.dict("sys.modules", {"yfinance": None}):
            with pytest.raises(
                DataSourceError, match="yfinance library not installed"
            ):
                self.adapter.get_current_price("AAPL")

    @patch("yfinance.Ticker")
    def test_fetch_historical_success(self, mock_ticker_class):
        """Test successful historical data fetching."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker

        # Create mock historical data
        mock_hist = MagicMock()
        mock_hist.empty = False
        mock_hist.iterrows.return_value = [
            (
                MagicMock(date=lambda: date(2023, 1, 1)),
                {
                    "Open": 100.0,
                    "High": 105.0,
                    "Low": 98.0,
                    "Close": 103.0,
                    "Volume": 1000000,
                },
            ),
            (
                MagicMock(date=lambda: date(2023, 1, 2)),
                {
                    "Open": 103.0,
                    "High": 108.0,
                    "Low": 101.0,
                    "Close": 106.0,
                    "Volume": 1200000,
                },
            ),
        ]
        mock_hist.index = [
            MagicMock(date=lambda: date(2023, 1, 1)),
            MagicMock(date=lambda: date(2023, 1, 2)),
        ]

        mock_ticker.history.return_value = mock_hist

        historical = self.adapter.fetch_historical("AAPL")

        assert isinstance(historical, HistoricalSeries)
        assert historical.symbol == "AAPL"
        assert len(historical.data_points) == 2

        point = historical.data_points[0]
        assert point.open_price == Decimal("100.0")
        assert point.close_price == Decimal("103.0")

    @patch("yfinance.Ticker")
    def test_bulk_get_current_success(self, mock_ticker_class):
        """Test successful bulk price fetching."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker

        # Mock the download function
        with patch("yfinance.download") as mock_download:
            mock_data = {"AAPL": MagicMock(), "MSFT": MagicMock()}

            for symbol, data in mock_data.items():
                data.empty = False
                data["Close"].iloc.__getitem__.return_value = (
                    150.0 if symbol == "AAPL" else 300.0
                )
                data["Volume"].iloc.__getitem__.return_value = 1000000
                data.index = [MagicMock()]
                data.index[-1].to_pydatetime.return_value = datetime(
                    2023, 1, 1, 12, 0, 0
                )

            mock_download.return_value = mock_data

            results = self.adapter.bulk_get_current(["AAPL", "MSFT"])

            assert len(results) == 2
            assert isinstance(results["AAPL"], PricePoint)
            assert isinstance(results["MSFT"], PricePoint)

    @patch("yfinance.Ticker")
    def test_get_company_info_success(self, mock_ticker_class):
        """Test successful company info fetching."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.info = {
            "longName": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "marketCap": 2500000000000,
            "currency": "USD",
            "exchange": "NASDAQ",
        }

        info = self.adapter.get_company_info("AAPL")

        assert isinstance(info, CompanyInfo)
        assert info.symbol == "AAPL"
        assert info.name == "Apple Inc."
        assert info.sector == "Technology"
        assert info.market_cap == Decimal("2500000000000")
