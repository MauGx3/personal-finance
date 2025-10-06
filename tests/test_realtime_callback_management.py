"""
Tests for real-time WebSocket callback management.

This module tests the callback management functionality for unsubscribe operations
to ensure proper cleanup and prevent memory leaks.
"""

import pytest
from unittest.mock import Mock
from personal_finance.realtime.connections import ConnectionManager


class TestCallbackManagement:
    """Test cases for WebSocket callback management."""

    @pytest.fixture
    def connection_manager(self):
        """Create a fresh ConnectionManager instance for each test."""
        return ConnectionManager()

    @pytest.fixture
    def mock_callback(self):
        """Create a mock callback function."""
        return Mock()

    @pytest.fixture
    def mock_callback2(self):
        """Create a second mock callback function."""
        return Mock()

    async def test_portfolio_subscription_with_callback(
        self, connection_manager, mock_callback
    ):
        """Test portfolio subscription with cleanup callback registration."""
        connection_id = "test_conn_1"
        portfolio_id = 123

        # Connect first
        await connection_manager.connect(connection_id, user_id=1)

        # Subscribe with callback
        await connection_manager.subscribe_to_portfolio(
            connection_id, portfolio_id, cleanup_callback=mock_callback
        )

        # Verify subscription
        assert (
            portfolio_id
            in connection_manager.connections[connection_id]["portfolios"]
        )
        assert (
            connection_id
            in connection_manager.portfolio_subscriptions[portfolio_id]
        )

        # Verify callback is registered
        callback_key = f"{connection_id}:{portfolio_id}"
        assert callback_key in connection_manager.portfolio_cleanup_callbacks
        assert (
            mock_callback
            in connection_manager.portfolio_cleanup_callbacks[callback_key]
        )

    async def test_asset_subscription_with_callback(
        self, connection_manager, mock_callback
    ):
        """Test asset subscription with cleanup callback registration."""
        connection_id = "test_conn_1"
        asset_symbol = "AAPL"

        # Connect first
        await connection_manager.connect(connection_id, user_id=1)

        # Subscribe with callback
        await connection_manager.subscribe_to_asset(
            connection_id, asset_symbol, cleanup_callback=mock_callback
        )

        # Verify subscription
        assert (
            asset_symbol
            in connection_manager.connections[connection_id]["assets"]
        )
        assert (
            connection_id
            in connection_manager.asset_subscriptions[asset_symbol]
        )

        # Verify callback is registered
        callback_key = f"{connection_id}:{asset_symbol}"
        assert callback_key in connection_manager.asset_cleanup_callbacks
        assert (
            mock_callback
            in connection_manager.asset_cleanup_callbacks[callback_key]
        )

    async def test_portfolio_unsubscribe_executes_callbacks(
        self, connection_manager, mock_callback, mock_callback2
    ):
        """Test that portfolio unsubscribe executes cleanup callbacks."""
        connection_id = "test_conn_1"
        portfolio_id = 123

        # Connect and subscribe with multiple callbacks
        await connection_manager.connect(connection_id, user_id=1)
        await connection_manager.subscribe_to_portfolio(
            connection_id, portfolio_id, cleanup_callback=mock_callback
        )
        await connection_manager.subscribe_to_portfolio(
            connection_id, portfolio_id, cleanup_callback=mock_callback2
        )

        # Unsubscribe
        await connection_manager.unsubscribe_from_portfolio(
            connection_id, portfolio_id
        )

        # Verify callbacks were executed
        mock_callback.assert_called_once()
        mock_callback2.assert_called_once()

        # Verify callbacks are cleaned up
        callback_key = f"{connection_id}:{portfolio_id}"
        assert (
            callback_key not in connection_manager.portfolio_cleanup_callbacks
        )

    async def test_asset_unsubscribe_executes_callbacks(
        self, connection_manager, mock_callback, mock_callback2
    ):
        """Test that asset unsubscribe executes cleanup callbacks."""
        connection_id = "test_conn_1"
        asset_symbol = "AAPL"

        # Connect and subscribe with multiple callbacks
        await connection_manager.connect(connection_id, user_id=1)
        await connection_manager.subscribe_to_asset(
            connection_id, asset_symbol, cleanup_callback=mock_callback
        )
        await connection_manager.subscribe_to_asset(
            connection_id, asset_symbol, cleanup_callback=mock_callback2
        )

        # Unsubscribe
        await connection_manager.unsubscribe_from_asset(
            connection_id, asset_symbol
        )

        # Verify callbacks were executed
        mock_callback.assert_called_once()
        mock_callback2.assert_called_once()

        # Verify callbacks are cleaned up
        callback_key = f"{connection_id}:{asset_symbol}"
        assert callback_key not in connection_manager.asset_cleanup_callbacks

    async def test_disconnect_executes_all_callbacks(
        self, connection_manager, mock_callback, mock_callback2
    ):
        """Test that disconnect executes all cleanup callbacks."""
        connection_id = "test_conn_1"
        portfolio_id = 123
        asset_symbol = "AAPL"

        # Connect and subscribe with callbacks
        await connection_manager.connect(connection_id, user_id=1)
        await connection_manager.subscribe_to_portfolio(
            connection_id, portfolio_id, cleanup_callback=mock_callback
        )
        await connection_manager.subscribe_to_asset(
            connection_id, asset_symbol, cleanup_callback=mock_callback2
        )

        # Disconnect
        await connection_manager.disconnect(connection_id)

        # Verify callbacks were executed
        mock_callback.assert_called_once()
        mock_callback2.assert_called_once()

        # Verify all callbacks are cleaned up
        portfolio_key = f"{connection_id}:{portfolio_id}"
        asset_key = f"{connection_id}:{asset_symbol}"
        assert (
            portfolio_key not in connection_manager.portfolio_cleanup_callbacks
        )
        assert asset_key not in connection_manager.asset_cleanup_callbacks

    async def test_subscription_without_callback_works(
        self, connection_manager
    ):
        """Test that subscription still works without providing callbacks."""
        connection_id = "test_conn_1"
        portfolio_id = 123
        asset_symbol = "AAPL"

        # Connect first
        await connection_manager.connect(connection_id, user_id=1)

        # Subscribe without callbacks (backward compatibility)
        await connection_manager.subscribe_to_portfolio(
            connection_id, portfolio_id
        )
        await connection_manager.subscribe_to_asset(
            connection_id, asset_symbol
        )

        # Verify subscriptions work
        assert (
            portfolio_id
            in connection_manager.connections[connection_id]["portfolios"]
        )
        assert (
            asset_symbol
            in connection_manager.connections[connection_id]["assets"]
        )

        # Unsubscribe should work without errors
        await connection_manager.unsubscribe_from_portfolio(
            connection_id, portfolio_id
        )
        await connection_manager.unsubscribe_from_asset(
            connection_id, asset_symbol
        )

    async def test_callback_execution_error_handling(self, connection_manager):
        """Test that callback execution errors are handled gracefully."""
        connection_id = "test_conn_1"
        portfolio_id = 123

        # Create a callback that raises an exception
        def failing_callback():
            raise Exception("Test callback error")

        def working_callback():
            pass

        working_mock = Mock(side_effect=working_callback)

        # Connect and subscribe with both failing and working callbacks
        await connection_manager.connect(connection_id, user_id=1)
        await connection_manager.subscribe_to_portfolio(
            connection_id, portfolio_id, cleanup_callback=failing_callback
        )
        await connection_manager.subscribe_to_portfolio(
            connection_id, portfolio_id, cleanup_callback=working_mock
        )

        # Unsubscribe should not raise exception despite failing callback
        await connection_manager.unsubscribe_from_portfolio(
            connection_id, portfolio_id
        )

        # Working callback should still be executed
        working_mock.assert_called_once()

        # Callbacks should be cleaned up despite errors
        callback_key = f"{connection_id}:{portfolio_id}"
        assert (
            callback_key not in connection_manager.portfolio_cleanup_callbacks
        )

    async def test_multiple_connections_callback_isolation(
        self, connection_manager, mock_callback, mock_callback2
    ):
        """Test that callbacks are properly isolated between different connections."""
        connection_id_1 = "test_conn_1"
        connection_id_2 = "test_conn_2"
        portfolio_id = 123

        # Connect both connections
        await connection_manager.connect(connection_id_1, user_id=1)
        await connection_manager.connect(connection_id_2, user_id=2)

        # Subscribe with different callbacks
        await connection_manager.subscribe_to_portfolio(
            connection_id_1, portfolio_id, cleanup_callback=mock_callback
        )
        await connection_manager.subscribe_to_portfolio(
            connection_id_2, portfolio_id, cleanup_callback=mock_callback2
        )

        # Unsubscribe only the first connection
        await connection_manager.unsubscribe_from_portfolio(
            connection_id_1, portfolio_id
        )

        # Only the first callback should be executed
        mock_callback.assert_called_once()
        mock_callback2.assert_not_called()

        # Only the first callback should be cleaned up
        callback_key_1 = f"{connection_id_1}:{portfolio_id}"
        callback_key_2 = f"{connection_id_2}:{portfolio_id}"
        assert (
            callback_key_1
            not in connection_manager.portfolio_cleanup_callbacks
        )
        assert callback_key_2 in connection_manager.portfolio_cleanup_callbacks

    async def test_nonexistent_connection_unsubscribe_safe(
        self, connection_manager, mock_callback
    ):
        """Test that unsubscribing a nonexistent connection is safe."""
        connection_id = "nonexistent_conn"
        portfolio_id = 123
        asset_symbol = "AAPL"

        # Unsubscribe without connecting first - should not raise exceptions
        await connection_manager.unsubscribe_from_portfolio(
            connection_id, portfolio_id
        )
        await connection_manager.unsubscribe_from_asset(
            connection_id, asset_symbol
        )

        # Callback should not be executed (none were registered)
        mock_callback.assert_not_called()
