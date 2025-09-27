"""
Tests for the RealtimeService and related functionality.

These tests validate the publish/subscribe semantics, subscription/notification 
behavior, and graceful shutdown using mock data source adapters.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal
from datetime import datetime

from personal_finance.realtime.services import (
    RealtimeService, 
    PricePoint,
    realtime_service,
    start_realtime_service,
    stop_realtime_service,
)


class TestPricePoint:
    """Test the PricePoint data structure."""
    
    def test_price_point_creation(self):
        """Test creating a PricePoint with minimal data."""
        price_point = PricePoint(symbol="AAPL", price=Decimal("150.25"))
        
        assert price_point.symbol == "AAPL"
        assert price_point.price == Decimal("150.25")
        assert price_point.timestamp is not None
        assert price_point.source == "realtime"
        
    def test_price_point_full_data(self):
        """Test creating a PricePoint with all data."""
        timestamp = datetime.now()
        price_point = PricePoint(
            symbol="GOOGL",
            price=Decimal("2500.50"),
            change=Decimal("25.50"),
            change_percent=Decimal("1.03"),
            volume=1000000,
            high=Decimal("2520.00"),
            low=Decimal("2480.00"),
            timestamp=timestamp,
            source="yahoo",
        )
        
        assert price_point.symbol == "GOOGL"
        assert price_point.price == Decimal("2500.50")
        assert price_point.change == Decimal("25.50")
        assert price_point.change_percent == Decimal("1.03")
        assert price_point.volume == 1000000
        assert price_point.timestamp == timestamp
        assert price_point.source == "yahoo"
        
    def test_price_point_to_dict(self):
        """Test converting PricePoint to dictionary."""
        price_point = PricePoint(
            symbol="MSFT",
            price=Decimal("300.75"),
            change=Decimal("-5.25"),
            volume=500000
        )
        
        data = price_point.to_dict()
        
        assert data["symbol"] == "MSFT"
        assert data["price"] == 300.75
        assert data["change"] == -5.25
        assert data["volume"] == 500000
        assert "timestamp" in data


@pytest.mark.asyncio
class TestRealtimeService:
    """Test the RealtimeService class."""
    
    async def test_service_initialization(self):
        """Test RealtimeService initialization."""
        service = RealtimeService(mode="polling", update_interval=5, max_batch_size=10)
        
        assert service.mode == "polling"
        assert service.update_interval == 5
        assert service.max_batch_size == 10
        assert not service.is_running
        assert len(service.subscribers) == 0
        
    async def test_service_start_stop(self):
        """Test starting and stopping the service."""
        service = RealtimeService(mode="polling", update_interval=1)
        
        # Start the service
        await service.start()
        assert service.is_running
        assert service.update_task is not None
        
        # Stop the service
        await service.stop()
        assert not service.is_running
        
    async def test_invalid_mode_raises_error(self):
        """Test that invalid mode raises ValueError."""
        service = RealtimeService(mode="invalid")
        
        with pytest.raises(ValueError, match="Invalid mode"):
            await service.start()
            
    async def test_subscribe_unsubscribe(self):
        """Test subscription and unsubscription functionality."""
        service = RealtimeService(mode="polling")
        callback = Mock()
        
        # Subscribe to symbols
        await service.subscribe(["AAPL", "GOOGL"], callback)
        
        symbols = await service.get_subscribed_symbols()
        assert "AAPL" in symbols
        assert "GOOGL" in symbols
        assert callback in service.subscribers["AAPL"]
        assert callback in service.subscribers["GOOGL"]
        
        # Unsubscribe from one symbol
        await service.unsubscribe(["AAPL"], callback)
        
        symbols = await service.get_subscribed_symbols()
        assert "AAPL" not in symbols
        assert "GOOGL" in symbols
        
        # Unsubscribe from remaining symbol
        await service.unsubscribe(["GOOGL"], callback)
        
        symbols = await service.get_subscribed_symbols()
        assert len(symbols) == 0
        
    async def test_multiple_callbacks_per_symbol(self):
        """Test multiple callbacks for the same symbol."""
        service = RealtimeService(mode="polling")
        callback1 = Mock()
        callback2 = Mock()
        
        # Subscribe multiple callbacks to the same symbol
        await service.subscribe(["AAPL"], callback1)
        await service.subscribe(["AAPL"], callback2)
        
        assert len(service.subscribers["AAPL"]) == 2
        assert callback1 in service.subscribers["AAPL"]
        assert callback2 in service.subscribers["AAPL"]
        
    async def test_notify_subscribers(self):
        """Test that subscribers are notified with price updates."""
        service = RealtimeService(mode="polling")
        
        # Track callback calls
        callback_calls = []
        
        def test_callback(price_point):
            callback_calls.append(price_point)
            
        await service.subscribe(["AAPL"], test_callback)
        
        # Create a price point and notify subscribers
        price_point = PricePoint(symbol="AAPL", price=Decimal("150.00"))
        await service._notify_subscribers("AAPL", price_point)
        
        # Check that callback was called
        assert len(callback_calls) == 1
        assert callback_calls[0].symbol == "AAPL"
        assert callback_calls[0].price == Decimal("150.00")
        
    async def test_async_callback(self):
        """Test async callbacks are properly awaited."""
        service = RealtimeService(mode="polling")
        
        callback_calls = []
        
        async def async_callback(price_point):
            callback_calls.append(price_point)
            
        await service.subscribe(["MSFT"], async_callback)
        
        price_point = PricePoint(symbol="MSFT", price=Decimal("300.00"))
        await service._notify_subscribers("MSFT", price_point)
        
        assert len(callback_calls) == 1
        assert callback_calls[0].symbol == "MSFT"
        
    async def test_callback_error_handling(self):
        """Test that callback errors don't crash the service."""
        service = RealtimeService(mode="polling")
        
        def error_callback(price_point):
            raise Exception("Test error")
            
        successful_calls = []
        
        def success_callback(price_point):
            successful_calls.append(price_point)
            
        await service.subscribe(["AAPL"], error_callback)
        await service.subscribe(["AAPL"], success_callback)
        
        price_point = PricePoint(symbol="AAPL", price=Decimal("150.00"))
        await service._notify_subscribers("AAPL", price_point)
        
        # Success callback should still be called despite error callback failing
        assert len(successful_calls) == 1
        
    async def test_mock_price_generation(self):
        """Test mock price data generation."""
        service = RealtimeService(mode="polling")
        
        mock_prices = service._generate_mock_prices(["AAPL", "GOOGL"])
        
        assert "AAPL" in mock_prices
        assert "GOOGL" in mock_prices
        assert isinstance(mock_prices["AAPL"], PricePoint)
        assert isinstance(mock_prices["GOOGL"], PricePoint)
        assert mock_prices["AAPL"].source == "mock"
        
    @patch('personal_finance.realtime.services.data_source_manager', None)
    async def test_fetch_prices_with_no_data_manager(self):
        """Test price fetching when data_source_manager is not available."""
        service = RealtimeService(mode="polling")
        
        prices = await service._fetch_prices(["AAPL"])
        
        # Should fall back to mock data
        assert "AAPL" in prices
        assert prices["AAPL"].source == "mock"
        
    async def test_polling_loop_integration(self):
        """Test the polling loop with short intervals."""
        service = RealtimeService(mode="polling", update_interval=0.1)  # Very short interval for testing
        
        callback_calls = []
        
        def test_callback(price_point):
            callback_calls.append(price_point)
            
        await service.subscribe(["AAPL"], test_callback)
        await service.start()
        
        # Wait for at least one polling cycle
        await asyncio.sleep(0.2)
        
        await service.stop()
        
        # Should have received at least one update
        assert len(callback_calls) >= 1
        assert callback_calls[0].symbol == "AAPL"


@pytest.mark.asyncio 
class TestGlobalServiceFunctions:
    """Test the global service functions."""
    
    async def test_start_stop_realtime_service(self):
        """Test global start/stop functions."""
        # Stop any existing service first
        await stop_realtime_service()
        
        # Start new service
        await start_realtime_service(mode="polling", update_interval=1)
        
        assert realtime_service.is_running
        assert realtime_service.mode == "polling"
        assert realtime_service.update_interval == 1
        
        # Stop the service
        await stop_realtime_service()
        
        assert not realtime_service.is_running


class TestSynchronousWrapper:
    """Test synchronous wrapper functions."""
    
    def test_subscribe_to_prices_wrapper(self):
        """Test the synchronous subscription wrapper."""
        # This is tricky to test due to event loop management
        # In a real application, we'd have proper async context
        
        # For now, just verify the function exists and can be imported
        from personal_finance.realtime.services import subscribe_to_prices
        assert callable(subscribe_to_prices)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])