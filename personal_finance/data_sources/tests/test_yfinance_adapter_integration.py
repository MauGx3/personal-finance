"""Integration tests for YFinanceAdapter with recorded fixtures.

These tests can be run with real network calls but by default use
recorded fixtures to avoid external dependencies in CI/CD.
"""

import pytest
import json
from decimal import Decimal
from datetime import datetime, date
from pathlib import Path
from unittest.mock import patch, MagicMock

from personal_finance.data_sources.adapter import (
    YFinanceAdapter,
    DataSourceError,
)
from personal_finance.data_sources.services import (
    DataSourceService,
    create_yfinance_service,
)
from personal_finance.data_sources.types import PricePoint, HistoricalSeries


# Skip these tests by default in CI - can be enabled with --external-api flag
pytestmark = pytest.mark.external_api


@pytest.fixture
def fixture_path():
    """Path to test fixtures."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_yfinance_data():
    """Mock yfinance data for offline testing."""
    return {
        "AAPL": {
            "current_price": {
                "Close": 150.50,
                "Volume": 45000000,
                "timestamp": "2023-01-01T16:00:00",
            },
            "historical_data": [
                {
                    "date": "2023-01-01",
                    "Open": 148.0,
                    "High": 152.0,
                    "Low": 147.0,
                    "Close": 150.50,
                    "Volume": 45000000,
                },
                {
                    "date": "2023-01-02",
                    "Open": 150.50,
                    "High": 153.0,
                    "Low": 149.0,
                    "Close": 152.0,
                    "Volume": 42000000,
                },
            ],
            "company_info": {
                "longName": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "marketCap": 2500000000000,
                "currency": "USD",
                "exchange": "NASDAQ",
            },
        }
    }


class TestYFinanceAdapterIntegration:
    """Integration tests using mocked yfinance responses."""

    def setup_method(self):
        self.adapter = YFinanceAdapter()

    @patch("yfinance.Ticker")
    def test_get_current_price_with_fixtures(
        self, mock_ticker_class, mock_yfinance_data
    ):
        """Test current price using recorded fixture data."""
        # Setup mock ticker
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker

        # Create mock history DataFrame
        mock_hist = MagicMock()
        mock_hist.empty = False

        # Mock the Close and Volume series
        mock_close = MagicMock()
        mock_close.iloc = MagicMock()
        mock_close.iloc.__getitem__.return_value = mock_yfinance_data["AAPL"][
            "current_price"
        ]["Close"]

        mock_volume = MagicMock()
        mock_volume.iloc = MagicMock()
        mock_volume.iloc.__getitem__.return_value = mock_yfinance_data["AAPL"][
            "current_price"
        ]["Volume"]
        mock_volume.empty = False

        mock_hist.__getitem__.side_effect = lambda key: {
            "Close": mock_close,
            "Volume": mock_volume,
        }[key]

        # Mock timestamp
        mock_timestamp = MagicMock()
        mock_timestamp.to_pydatetime.return_value = datetime(
            2023, 1, 1, 16, 0, 0
        )
        mock_hist.index = [mock_timestamp]

        mock_ticker.history.return_value = mock_hist

        # Test the adapter
        price_point = self.adapter.get_current_price("AAPL")

        assert isinstance(price_point, PricePoint)
        assert price_point.symbol == "AAPL"
        assert price_point.price == Decimal("150.50")
        assert price_point.volume == 45000000
        assert price_point.currency == "USD"
        assert isinstance(price_point.timestamp, datetime)

        # Verify the ticker was called with correct parameters
        mock_ticker.history.assert_called_once_with(period="1d", interval="1m")

    @patch("yfinance.Ticker")
    def test_fetch_historical_with_fixtures(
        self, mock_ticker_class, mock_yfinance_data
    ):
        """Test historical data using recorded fixture data."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker

        # Create mock historical DataFrame
        mock_hist = MagicMock()
        mock_hist.empty = False

        # Mock iterrows
        historical_data = mock_yfinance_data["AAPL"]["historical_data"]
        mock_rows = []
        for i, day_data in enumerate(historical_data):
            mock_index = MagicMock()
            mock_index.date.return_value = date.fromisoformat(day_data["date"])
            mock_rows.append((mock_index, day_data))

        mock_hist.iterrows.return_value = iter(mock_rows)

        # Mock index for date range
        mock_hist.index = [
            MagicMock(date=lambda: date(2023, 1, 1)),
            MagicMock(date=lambda: date(2023, 1, 2)),
        ]

        mock_ticker.history.return_value = mock_hist

        # Test the adapter
        historical = self.adapter.fetch_historical("AAPL", "1mo", "1d")

        assert isinstance(historical, HistoricalSeries)
        assert historical.symbol == "AAPL"
        assert len(historical.data_points) == 2

        # Check first data point
        point = historical.data_points[0]
        assert point.symbol == "AAPL"
        assert point.date == date(2023, 1, 1)
        assert point.open_price == Decimal("148.0")
        assert point.close_price == Decimal("150.50")
        assert point.volume == 45000000

        # Verify method was called with correct parameters
        mock_ticker.history.assert_called_once_with(
            period="1mo", interval="1d"
        )

    @patch("yfinance.download")
    def test_bulk_get_current_with_fixtures(
        self, mock_download, mock_yfinance_data
    ):
        """Test bulk price fetching using fixtures."""
        # Setup mock download response
        mock_data = MagicMock()

        # For multiple symbols, yfinance returns nested structure
        mock_aapl_data = MagicMock()
        mock_aapl_data.empty = False
        mock_aapl_data["Close"].iloc.__getitem__.return_value = 150.50
        mock_aapl_data["Volume"].iloc.__getitem__.return_value = 45000000
        mock_aapl_data.index = [MagicMock()]
        mock_aapl_data.index[-1].to_pydatetime.return_value = datetime(
            2023, 1, 1, 16, 0, 0
        )

        mock_msft_data = MagicMock()
        mock_msft_data.empty = False
        mock_msft_data["Close"].iloc.__getitem__.return_value = 300.75
        mock_msft_data["Volume"].iloc.__getitem__.return_value = 30000000
        mock_msft_data.index = [MagicMock()]
        mock_msft_data.index[-1].to_pydatetime.return_value = datetime(
            2023, 1, 1, 16, 0, 0
        )

        mock_data.__getitem__.side_effect = lambda key: {
            "AAPL": mock_aapl_data,
            "MSFT": mock_msft_data,
        }[key]

        mock_download.return_value = mock_data

        # Test bulk request
        results = self.adapter.bulk_get_current(["AAPL", "MSFT"])

        assert len(results) == 2
        assert "AAPL" in results
        assert "MSFT" in results

        # Check AAPL result
        aapl_result = results["AAPL"]
        assert isinstance(aapl_result, PricePoint)
        assert aapl_result.symbol == "AAPL"
        assert aapl_result.price == Decimal("150.50")

        # Check MSFT result
        msft_result = results["MSFT"]
        assert isinstance(msft_result, PricePoint)
        assert msft_result.symbol == "MSFT"
        assert msft_result.price == Decimal("300.75")

    @patch("yfinance.Ticker")
    def test_get_company_info_with_fixtures(
        self, mock_ticker_class, mock_yfinance_data
    ):
        """Test company info using fixtures."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.info = mock_yfinance_data["AAPL"]["company_info"]

        info = self.adapter.get_company_info("AAPL")

        assert info is not None
        assert info.symbol == "AAPL"
        assert info.name == "Apple Inc."
        assert info.sector == "Technology"
        assert info.industry == "Consumer Electronics"
        assert info.market_cap == Decimal("2500000000000")
        assert info.currency == "USD"
        assert info.exchange == "NASDAQ"


class TestDataSourceServiceIntegration:
    """Integration tests for DataSourceService with YFinance adapter."""

    def setup_method(self):
        self.service = create_yfinance_service()

    @patch("yfinance.Ticker")
    def test_service_current_price_integration(
        self, mock_ticker_class, mock_yfinance_data
    ):
        """Test service-level current price with caching."""
        # Setup mocks as before
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker

        mock_hist = MagicMock()
        mock_hist.empty = False

        mock_close = MagicMock()
        mock_close.iloc = MagicMock()
        mock_close.iloc.__getitem__.return_value = mock_yfinance_data["AAPL"][
            "current_price"
        ]["Close"]

        mock_volume = MagicMock()
        mock_volume.iloc = MagicMock()
        mock_volume.iloc.__getitem__.return_value = mock_yfinance_data["AAPL"][
            "current_price"
        ]["Volume"]
        mock_volume.empty = False

        mock_hist.__getitem__.side_effect = lambda key: {
            "Close": mock_close,
            "Volume": mock_volume,
        }[key]

        mock_timestamp = MagicMock()
        mock_timestamp.to_pydatetime.return_value = datetime(
            2023, 1, 1, 16, 0, 0
        )
        mock_hist.index = [mock_timestamp]

        mock_ticker.history.return_value = mock_hist

        # Test service call
        price_point = self.service.get_current_price("AAPL")

        assert isinstance(price_point, PricePoint)
        assert price_point.symbol == "AAPL"
        assert price_point.price == Decimal("150.50")

    @patch("yfinance.Ticker")
    def test_service_error_handling_integration(self, mock_ticker_class):
        """Test service error handling with real adapter."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.history.side_effect = Exception("Network timeout")

        with pytest.raises(DataSourceError):
            self.service.get_current_price("AAPL")

    def test_service_invalid_symbol_handling(self):
        """Test service handling of invalid symbols."""
        with pytest.raises(DataSourceError):
            self.service.get_current_price("INVALID@SYMBOL")


@pytest.mark.slow
class TestRealYFinanceIntegration:
    """Real integration tests that make actual network calls.

    These are marked as 'slow' and should only be run manually
    or in specific test environments with network access.
    """

    def setup_method(self):
        self.adapter = YFinanceAdapter()

    @pytest.mark.skip(reason="Requires network access - enable manually")
    def test_real_current_price_fetch(self):
        """Test fetching real current price - requires network."""
        price_point = self.adapter.get_current_price("AAPL")

        if price_point is not None:  # May be None if markets are closed
            assert isinstance(price_point, PricePoint)
            assert price_point.symbol == "AAPL"
            assert price_point.price > Decimal("0")
            assert price_point.currency == "USD"

    @pytest.mark.skip(reason="Requires network access - enable manually")
    def test_real_historical_data_fetch(self):
        """Test fetching real historical data - requires network."""
        historical = self.adapter.fetch_historical("AAPL", "5d", "1d")

        assert isinstance(historical, HistoricalSeries)
        assert historical.symbol == "AAPL"
        assert len(historical.data_points) > 0

        # Data should be sorted by date
        dates = [point.date for point in historical.data_points]
        assert dates == sorted(dates)
