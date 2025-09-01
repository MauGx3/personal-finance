from unittest.mock import Mock, patch
import pytest
from . import portfolio
from portfolio import PortfolioManager


class TestPortfolioManager:
    @pytest.fixture
    def portfolio_manager(self):
        return PortfolioManager()

    @pytest.fixture
    def mock_ticker(self):
        with patch("stockdex.Ticker") as mock:
            yield mock

    def test_init_empty_portfolio(self, portfolio_manager):
        """Test portfolio initialization"""
        assert portfolio_manager.portfolio == {"tickers": {}}

    def test_add_position(self, portfolio_manager):
        """Test adding a new position"""
        portfolio_manager.add_position("AAPL", 10)
        assert portfolio_manager.portfolio["tickers"]["AAPL"] == 10

    def test_add_to_existing_position(self, portfolio_manager):
        """Test adding to existing position"""
        portfolio_manager.add_position("AAPL", 10)
        portfolio_manager.add_position("AAPL", 5)
        assert portfolio_manager.portfolio["tickers"]["AAPL"] == 15

    def test_remove_position(self, portfolio_manager):
        """Test removing a position"""
        portfolio_manager.add_position("AAPL", 10)
        portfolio_manager.remove_position("AAPL")
        assert "AAPL" not in portfolio_manager.portfolio["tickers"]

    def test_get_portfolio_value(self, portfolio_manager, mock_ticker):
        """Test portfolio value calculation"""
        # Setup
        portfolio_manager.portfolio = {"tickers": {"AAPL": 10, "GOOGL": 5}}
        mock_instance = Mock()
        mock_instance.yahoo_api_price.side_effect = [
            {"AAPL": 150.0},
            {"GOOGL": 2800.0},
        ]
        mock_ticker.return_value = mock_instance

        # Execute
        value = portfolio_manager.get_portfolio_value()

        # Verify
        expected_value = (150.0 * 10) + (2800.0 * 5)
        assert value == expected_value

    def test_invalid_ticker_symbol(self, portfolio_manager):
        """Test adding invalid ticker symbol"""
        with pytest.raises(ValueError):
            portfolio_manager.add_position("", 10)

    def test_invalid_position_size(self, portfolio_manager):
        """Test adding invalid position size"""
        with pytest.raises(ValueError):
            portfolio_manager.add_position("AAPL", -5)

    @patch("logging.error")
    def test_price_fetch_error_logging(
        self, mock_error, portfolio_manager, mock_ticker
    ):
        """Test error logging when price fetch fails"""
        # Setup
        portfolio_manager.portfolio = {"tickers": {"AAPL": 10}}
        mock_instance = Mock()
        mock_instance.yahoo_api_price.side_effect = Exception("API Error")
        mock_ticker.return_value = mock_instance

        # Execute
        portfolio_manager.get_current_prices()

        # Verify
        mock_error.assert_called_once_with(
            "Failed to fetch price for %s: %s", "AAPL", "API Error"
        )
