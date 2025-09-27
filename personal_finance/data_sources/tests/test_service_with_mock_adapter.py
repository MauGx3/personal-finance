"""Tests for DataSourceService with mock adapters."""

import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import patch, MagicMock

from personal_finance.data_sources.services import DataSourceService, create_mock_service
from personal_finance.data_sources.adapter import MockAdapter, DataSourceError
from personal_finance.data_sources.types import PricePoint, HistoricalSeries


class TestDataSourceService:
    """Test DataSourceService business logic."""
    
    def setup_method(self):
        """Set up test with mock adapter to avoid network calls."""
        self.service = create_mock_service()
        self.mock_adapter = self.service.adapter
    
    def test_get_current_price_success(self):
        """Test successful current price fetching."""
        price_point = self.service.get_current_price("AAPL")
        
        assert isinstance(price_point, PricePoint)
        assert price_point.symbol == "AAPL"
        assert price_point.price == Decimal("150.00")
        assert price_point.currency == "USD"
        assert isinstance(price_point.timestamp, datetime)
    
    def test_get_current_price_empty_symbol(self):
        """Test handling of empty symbol."""
        assert self.service.get_current_price("") is None
        assert self.service.get_current_price(None) is None
        assert self.service.get_current_price("   ") is None
    
    def test_get_current_price_symbol_normalization(self):
        """Test that symbols are properly normalized."""
        price_point = self.service.get_current_price("  aapl  ")
        
        assert price_point is not None
        assert price_point.symbol == "AAPL"
    
    @patch('personal_finance.data_sources.services.cache')
    def test_get_current_price_caching(self, mock_cache):
        """Test that results are properly cached."""
        # Mock cache miss, then hit
        mock_cache.get.side_effect = [None, "cached_result"]
        
        # First call should fetch from adapter
        self.service.get_current_price("AAPL")
        mock_cache.set.assert_called_once()
        
        # Second call should return cached result
        mock_cache.get.return_value = PricePoint(
            symbol="AAPL", 
            price=Decimal("150.00"), 
            timestamp=datetime.now()
        )
        result = self.service.get_current_price("AAPL")
        
        assert mock_cache.get.call_count >= 2
    
    def test_fetch_historical_success(self):
        """Test successful historical data fetching."""
        historical = self.service.fetch_historical("AAPL")
        
        assert isinstance(historical, HistoricalSeries)
        assert historical.symbol == "AAPL"
        assert len(historical.data_points) == 30  # Mock returns 30 days
        assert all(point.symbol == "AAPL" for point in historical.data_points)
    
    def test_fetch_historical_empty_symbol(self):
        """Test handling of empty symbol for historical data."""
        with pytest.raises(DataSourceError, match="Symbol cannot be empty"):
            self.service.fetch_historical("")
    
    def test_fetch_historical_with_parameters(self):
        """Test historical data fetching with custom parameters."""
        historical = self.service.fetch_historical("AAPL", period="6mo", interval="1wk")
        
        assert isinstance(historical, HistoricalSeries)
        assert historical.symbol == "AAPL"
        # Mock adapter ignores period/interval but service should pass them through
    
    @patch('personal_finance.data_sources.services.cache')
    def test_fetch_historical_caching(self, mock_cache):
        """Test that historical data is cached with longer timeout."""
        mock_cache.get.return_value = None  # Cache miss
        
        self.service.fetch_historical("AAPL")
        
        # Should cache with longer timeout (12x default)
        mock_cache.set.assert_called_once()
        args, kwargs = mock_cache.set.call_args
        assert args[2] == self.service.cache_timeout * 12  # 12x timeout for historical
    
    def test_bulk_get_current_success(self):
        """Test successful bulk price fetching."""
        symbols = ["AAPL", "MSFT", "GOOGL"]
        results = self.service.bulk_get_current(symbols)
        
        assert len(results) == 3
        for symbol in symbols:
            assert symbol in results
            assert isinstance(results[symbol], PricePoint)
            assert results[symbol].symbol == symbol
    
    def test_bulk_get_current_empty_list(self):
        """Test handling of empty symbol list."""
        results = self.service.bulk_get_current([])
        assert results == {}
        
        results = self.service.bulk_get_current(None)
        assert results == {}
    
    def test_bulk_get_current_invalid_symbols(self):
        """Test handling of invalid symbols in bulk request."""
        symbols = ["AAPL", "", None, "MSFT", 123]
        results = self.service.bulk_get_current(symbols)
        
        # Should only process valid string symbols
        assert "AAPL" in results
        assert "MSFT" in results
        assert len([k for k in results.keys() if k]) == 2  # Only valid symbols
    
    def test_bulk_get_current_symbol_normalization(self):
        """Test that symbols are normalized in bulk requests."""
        symbols = ["  aapl  ", "MSFT", "googl"]
        results = self.service.bulk_get_current(symbols)
        
        assert "AAPL" in results
        assert "MSFT" in results  
        assert "GOOGL" in results
    
    @patch('personal_finance.data_sources.services.cache')
    def test_bulk_get_current_partial_cache_hit(self, mock_cache):
        """Test bulk request with some symbols cached."""
        # AAPL is cached, MSFT is not
        def cache_side_effect(key):
            if "AAPL" in key:
                return PricePoint(symbol="AAPL", price=Decimal("150.00"), timestamp=datetime.now())
            return None
        
        mock_cache.get.side_effect = cache_side_effect
        
        symbols = ["AAPL", "MSFT"]
        results = self.service.bulk_get_current(symbols)
        
        assert len(results) == 2
        assert "AAPL" in results
        assert "MSFT" in results
        
        # Should have cached the new result for MSFT
        mock_cache.set.assert_called()
    
    def test_get_company_info_success(self):
        """Test successful company info fetching."""
        info = self.service.get_company_info("AAPL")
        
        assert info is not None
        assert info.symbol == "AAPL"
        assert info.name == "Apple Inc."
        assert info.sector == "Technology"
    
    def test_get_company_info_empty_symbol(self):
        """Test handling of empty symbol for company info."""
        assert self.service.get_company_info("") is None
        assert self.service.get_company_info(None) is None
    
    @patch('personal_finance.data_sources.services.cache')
    def test_get_company_info_caching(self, mock_cache):
        """Test that company info is cached with longer timeout."""
        mock_cache.get.return_value = None  # Cache miss
        
        self.service.get_company_info("AAPL")
        
        # Should cache with longer timeout (48x default)
        mock_cache.set.assert_called_once()
        args, kwargs = mock_cache.set.call_args
        assert args[2] == self.service.cache_timeout * 48  # 48x timeout for company info


class TestDataSourceServiceErrorHandling:
    """Test error handling in DataSourceService."""
    
    def setup_method(self):
        """Set up test with mocked adapter that can simulate errors."""
        self.mock_adapter = MagicMock()
        self.mock_adapter.name = "MockErrorAdapter"
        self.service = DataSourceService(self.mock_adapter)
    
    def test_adapter_error_propagation(self):
        """Test that adapter errors are properly propagated."""
        self.mock_adapter.get_current_price.side_effect = Exception("Network error")
        
        with pytest.raises(DataSourceError, match="Failed to get current price"):
            self.service.get_current_price("AAPL")
    
    def test_bulk_fallback_on_error(self):
        """Test that bulk requests fall back to individual calls on error."""
        # Bulk method fails, individual calls succeed
        self.mock_adapter.bulk_get_current.side_effect = Exception("Bulk failed")
        self.mock_adapter.get_current_price.return_value = PricePoint(
            symbol="AAPL", price=Decimal("150.00"), timestamp=datetime.now()
        )
        
        results = self.service.bulk_get_current(["AAPL"])
        
        assert "AAPL" in results
        assert isinstance(results["AAPL"], PricePoint)
        
        # Should have attempted bulk first, then fallen back
        self.mock_adapter.bulk_get_current.assert_called_once()
        self.mock_adapter.get_current_price.assert_called_once()
    
    def test_bulk_individual_fallback_partial_failure(self):
        """Test individual fallback handles partial failures gracefully."""
        self.mock_adapter.bulk_get_current.side_effect = Exception("Bulk failed")
        
        def individual_side_effect(symbol):
            if symbol == "AAPL":
                return PricePoint(symbol="AAPL", price=Decimal("150.00"), timestamp=datetime.now())
            else:
                raise Exception("Individual failed")
        
        self.mock_adapter.get_current_price.side_effect = individual_side_effect
        
        results = self.service.bulk_get_current(["AAPL", "MSFT"])
        
        assert "AAPL" in results
        assert isinstance(results["AAPL"], PricePoint)
        assert "MSFT" in results  
        assert results["MSFT"] is None  # Failed individual call
    
    def test_company_info_error_handling(self):
        """Test that company info errors are handled gracefully."""
        self.mock_adapter.get_company_info.side_effect = Exception("API error")
        
        # Should return None instead of raising exception
        result = self.service.get_company_info("AAPL")
        assert result is None


class TestServiceFactoryFunctions:
    """Test factory functions for creating service instances."""
    
    def test_create_mock_service(self):
        """Test mock service factory."""
        service = create_mock_service()
        
        assert isinstance(service, DataSourceService)
        assert isinstance(service.adapter, MockAdapter)
        assert service.adapter.name == "Mock Data Source"
    
    @patch('personal_finance.data_sources.services.YFinanceAdapter')
    def test_create_yfinance_service(self, mock_yfinance_adapter):
        """Test yfinance service factory."""
        from personal_finance.data_sources.services import create_yfinance_service
        
        service = create_yfinance_service()
        
        assert isinstance(service, DataSourceService)
        mock_yfinance_adapter.assert_called_once()


class TestDataSourceServiceConfiguration:
    """Test service configuration options."""
    
    def test_custom_cache_timeout(self):
        """Test service with custom cache timeout."""
        adapter = MockAdapter()
        service = DataSourceService(adapter, cache_timeout=600)  # 10 minutes
        
        assert service.cache_timeout == 600
        assert service.adapter == adapter
    
    def test_default_cache_timeout(self):
        """Test service with default cache timeout."""
        adapter = MockAdapter()
        service = DataSourceService(adapter)
        
        assert service.cache_timeout == 300  # 5 minutes default