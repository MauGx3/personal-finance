"""
Tests for the WebSocket price streaming functionality.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from decimal import Decimal

from personal_finance.realtime.services import PricePoint
from personal_finance.realtime.ws import WebSocketPriceEndpoint, ASGIWebSocketApp


@pytest.mark.asyncio
class TestWebSocketPriceEndpoint:
    """Test the WebSocket price endpoint."""
    
    async def test_endpoint_initialization(self):
        """Test endpoint initialization."""
        endpoint = WebSocketPriceEndpoint()
        
        assert len(endpoint.connections) == 0
        assert len(endpoint.connection_subscriptions) == 0
        
    async def test_send_message(self):
        """Test sending messages to WebSocket."""
        endpoint = WebSocketPriceEndpoint()
        
        # Mock WebSocket
        mock_websocket = AsyncMock()
        
        message = {"type": "test", "data": "hello"}
        await endpoint._send_message(mock_websocket, message)
        
        mock_websocket.send.assert_called_once_with(json.dumps(message))
        
    async def test_send_error(self):
        """Test sending error messages."""
        endpoint = WebSocketPriceEndpoint()
        mock_websocket = AsyncMock()
        
        await endpoint._send_error(mock_websocket, "Test error")
        
        expected_message = {"type": "error", "error": "Test error"}
        mock_websocket.send.assert_called_once_with(json.dumps(expected_message))
        
    async def test_handle_ping_message(self):
        """Test handling ping messages."""
        endpoint = WebSocketPriceEndpoint()
        mock_websocket = AsyncMock()
        
        ping_message = json.dumps({
            "type": "ping",
            "data": {"timestamp": "2024-01-01T00:00:00"}
        })
        
        await endpoint._handle_message("test_conn", mock_websocket, ping_message)
        
        # Should respond with pong
        pong_message = {"type": "pong", "timestamp": "2024-01-01T00:00:00"}
        mock_websocket.send.assert_called_with(json.dumps(pong_message))
        
    async def test_handle_invalid_json(self):
        """Test handling invalid JSON messages."""
        endpoint = WebSocketPriceEndpoint()
        mock_websocket = AsyncMock()
        
        invalid_json = "{ invalid json"
        await endpoint._handle_message("test_conn", mock_websocket, invalid_json)
        
        error_message = {"type": "error", "error": "Invalid JSON format"}
        mock_websocket.send.assert_called_with(json.dumps(error_message))
        
    async def test_handle_unknown_message_type(self):
        """Test handling unknown message types."""
        endpoint = WebSocketPriceEndpoint()
        mock_websocket = AsyncMock()
        
        unknown_message = json.dumps({
            "type": "unknown_type",
            "data": {}
        })
        
        await endpoint._handle_message("test_conn", mock_websocket, unknown_message)
        
        error_message = {"type": "error", "error": "Unknown message type: unknown_type"}
        mock_websocket.send.assert_called_with(json.dumps(error_message))
        
    async def test_send_price_update(self):
        """Test sending price updates."""
        endpoint = WebSocketPriceEndpoint()
        mock_websocket = AsyncMock()
        
        price_point = PricePoint(
            symbol="AAPL",
            price=Decimal("150.25"),
            change=Decimal("2.50")
        )
        
        await endpoint._send_price_update(mock_websocket, price_point)
        
        expected_message = {
            "type": "price_update",
            "data": price_point.to_dict()
        }
        mock_websocket.send.assert_called_with(json.dumps(expected_message))
        
    async def test_cleanup_connection(self):
        """Test connection cleanup."""
        endpoint = WebSocketPriceEndpoint()
        
        # Setup connection
        connection_id = "test_conn"
        endpoint.connections[connection_id] = Mock()
        endpoint.connection_subscriptions[connection_id] = ["AAPL"]
        
        # Cleanup
        await endpoint._cleanup_connection(connection_id)
        
        assert connection_id not in endpoint.connections
        assert connection_id not in endpoint.connection_subscriptions


@pytest.mark.asyncio
class TestASGIWebSocketApp:
    """Test the ASGI WebSocket application."""
    
    async def test_asgi_app_initialization(self):
        """Test ASGI app initialization."""
        app = ASGIWebSocketApp()
        assert app.endpoint is not None
        
    async def test_non_websocket_scope_rejected(self):
        """Test that non-WebSocket scopes are rejected."""
        app = ASGIWebSocketApp()
        
        scope = {"type": "http"}
        receive = AsyncMock()
        send = AsyncMock()
        
        await app(scope, receive, send)
        
        send.assert_called_with({"type": "websocket.close", "code": 4000})
        
    async def test_websocket_accept(self):
        """Test WebSocket connection acceptance."""
        app = ASGIWebSocketApp()
        
        scope = {"type": "websocket"}
        receive = AsyncMock()
        send = AsyncMock()
        
        # Mock receive to return disconnect immediately to end the loop
        receive.side_effect = [
            {"type": "websocket.connect"},
            {"type": "websocket.disconnect"}
        ]
        
        await app(scope, receive, send)
        
        # Should accept the connection
        calls = send.call_args_list
        assert any(call[0][0]["type"] == "websocket.accept" for call in calls)


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality."""
    
    def test_websocket_imports(self):
        """Test that WebSocket modules can be imported."""
        # Test that the module imports work even if websockets is not available
        from personal_finance.realtime.ws import (
            WebSocketPriceEndpoint,
            ASGIWebSocketApp,
            websocket_endpoint,
            asgi_app
        )
        
        assert WebSocketPriceEndpoint is not None
        assert ASGIWebSocketApp is not None
        assert websocket_endpoint is not None
        assert asgi_app is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])