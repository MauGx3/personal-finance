"""
WebSocket connection manager for real-time updates.

This module handles WebSocket connections, user authentication,
and message broadcasting for live market data updates.
"""

import json
from loguru import logger
from typing import Dict, Set, Optional, Any, Callable, List
from datetime import datetime
from decimal import Decimal

# Using loguru logger imported above


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.

    Handles user authentication, connection lifecycle, and
    targeted message delivery for real-time updates.
    """

    def __init__(self):
        """Initialize the connection manager."""
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.user_connections: Dict[int, Set[str]] = {}
        self.portfolio_subscriptions: Dict[int, Set[str]] = {}
        self.asset_subscriptions: Dict[str, Set[str]] = {}
        # Callback registries for cleanup operations
        self.portfolio_cleanup_callbacks: Dict[
            str, List[Callable[[], None]]
        ] = {}
        self.asset_cleanup_callbacks: Dict[str, List[Callable[[], None]]] = {}

    async def connect(self, connection_id: str, user_id: Optional[int] = None):
        """
        Register a new WebSocket connection.

        Args:
            connection_id: Unique identifier for the connection
            user_id: ID of the authenticated user (if any)
        """
        self.connections[connection_id] = {
            "user_id": user_id,
            "connected_at": datetime.now(),
            "portfolios": set(),
            "assets": set(),
        }

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)

        logger.info(
            "WebSocket connected: %s, user: %s", connection_id, user_id
        )

    async def disconnect(self, connection_id: str):
        """
        Unregister a WebSocket connection.

        Args:
            connection_id: Unique identifier for the connection
        """
        if connection_id not in self.connections:
            return

        connection_info = self.connections[connection_id]
        user_id = connection_info["user_id"]

        # Clean up user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Clean up portfolio subscriptions
        for portfolio_id in connection_info["portfolios"]:
            if portfolio_id in self.portfolio_subscriptions:
                self.portfolio_subscriptions[portfolio_id].discard(
                    connection_id
                )
                if not self.portfolio_subscriptions[portfolio_id]:
                    del self.portfolio_subscriptions[portfolio_id]
            # Execute cleanup callbacks for portfolio
            await self._execute_portfolio_callbacks(
                connection_id, portfolio_id
            )

        # Clean up asset subscriptions
        for asset_symbol in connection_info["assets"]:
            if asset_symbol in self.asset_subscriptions:
                self.asset_subscriptions[asset_symbol].discard(connection_id)
                if not self.asset_subscriptions[asset_symbol]:
                    del self.asset_subscriptions[asset_symbol]
            # Execute cleanup callbacks for asset
            await self._execute_asset_callbacks(connection_id, asset_symbol)

        del self.connections[connection_id]
        logger.info("WebSocket disconnected: %s", connection_id)

    def _register_portfolio_callback(
        self,
        connection_id: str,
        portfolio_id: int,
        callback: Callable[[], None],
    ):
        """Register a cleanup callback for portfolio subscription."""
        callback_key = f"{connection_id}:{portfolio_id}"
        if callback_key not in self.portfolio_cleanup_callbacks:
            self.portfolio_cleanup_callbacks[callback_key] = []
        self.portfolio_cleanup_callbacks[callback_key].append(callback)

    def _register_asset_callback(
        self,
        connection_id: str,
        asset_symbol: str,
        callback: Callable[[], None],
    ):
        """Register a cleanup callback for asset subscription."""
        callback_key = f"{connection_id}:{asset_symbol}"
        if callback_key not in self.asset_cleanup_callbacks:
            self.asset_cleanup_callbacks[callback_key] = []
        self.asset_cleanup_callbacks[callback_key].append(callback)

    async def _execute_portfolio_callbacks(
        self, connection_id: str, portfolio_id: int
    ):
        """Execute and remove cleanup callbacks for portfolio subscription."""
        callback_key = f"{connection_id}:{portfolio_id}"
        callbacks = self.portfolio_cleanup_callbacks.pop(callback_key, [])

        for callback in callbacks:
            try:
                callback()
                logger.debug(
                    f"Executed portfolio cleanup callback for {callback_key}"
                )
            except Exception as e:
                logger.error(
                    f"Error executing portfolio cleanup callback for {callback_key}: {e}"
                )

    async def _execute_asset_callbacks(
        self, connection_id: str, asset_symbol: str
    ):
        """Execute and remove cleanup callbacks for asset subscription."""
        callback_key = f"{connection_id}:{asset_symbol}"
        callbacks = self.asset_cleanup_callbacks.pop(callback_key, [])

        for callback in callbacks:
            try:
                callback()
                logger.debug(
                    f"Executed asset cleanup callback for {callback_key}"
                )
            except Exception as e:
                logger.error(
                    f"Error executing asset cleanup callback for {callback_key}: {e}"
                )

    async def subscribe_to_portfolio(
        self,
        connection_id: str,
        portfolio_id: int,
        cleanup_callback: Optional[Callable[[], None]] = None,
    ):
        """
        Subscribe a connection to portfolio updates.

        Args:
            connection_id: Unique identifier for the connection
            portfolio_id: ID of the portfolio to subscribe to
            cleanup_callback: Optional callback to execute when unsubscribing
        """
        if connection_id not in self.connections:
            return

        self.connections[connection_id]["portfolios"].add(portfolio_id)

        if portfolio_id not in self.portfolio_subscriptions:
            self.portfolio_subscriptions[portfolio_id] = set()
        self.portfolio_subscriptions[portfolio_id].add(connection_id)

        # Register cleanup callback if provided
        if cleanup_callback:
            self._register_portfolio_callback(
                connection_id, portfolio_id, cleanup_callback
            )

        logger.debug(
            f"Connection {connection_id} subscribed to portfolio {portfolio_id}"
        )

    async def subscribe_to_asset(
        self,
        connection_id: str,
        asset_symbol: str,
        cleanup_callback: Optional[Callable[[], None]] = None,
    ):
        """
        Subscribe a connection to asset price updates.

        Args:
            connection_id: Unique identifier for the connection
            asset_symbol: Symbol of the asset to subscribe to
            cleanup_callback: Optional callback to execute when unsubscribing
        """
        if connection_id not in self.connections:
            return

        self.connections[connection_id]["assets"].add(asset_symbol)

        if asset_symbol not in self.asset_subscriptions:
            self.asset_subscriptions[asset_symbol] = set()
        self.asset_subscriptions[asset_symbol].add(connection_id)

        # Register cleanup callback if provided
        if cleanup_callback:
            self._register_asset_callback(
                connection_id, asset_symbol, cleanup_callback
            )

        logger.debug(
            f"Connection {connection_id} subscribed to asset {asset_symbol}"
        )

    async def unsubscribe_from_portfolio(
        self, connection_id: str, portfolio_id: int
    ):
        """
        Unsubscribe a connection from portfolio updates.

        Args:
            connection_id: Unique identifier for the connection
            portfolio_id: ID of the portfolio to unsubscribe from
        """
        if connection_id not in self.connections:
            return

        self.connections[connection_id]["portfolios"].discard(portfolio_id)

        if portfolio_id in self.portfolio_subscriptions:
            self.portfolio_subscriptions[portfolio_id].discard(connection_id)
            if not self.portfolio_subscriptions[portfolio_id]:
                del self.portfolio_subscriptions[portfolio_id]

        # Execute cleanup callbacks
        await self._execute_portfolio_callbacks(connection_id, portfolio_id)

    async def unsubscribe_from_asset(
        self, connection_id: str, asset_symbol: str
    ):
        """
        Unsubscribe a connection from asset price updates.

        Args:
            connection_id: Unique identifier for the connection
            asset_symbol: Symbol of the asset to unsubscribe from
        """
        if connection_id not in self.connections:
            return

        self.connections[connection_id]["assets"].discard(asset_symbol)

        if asset_symbol in self.asset_subscriptions:
            self.asset_subscriptions[asset_symbol].discard(connection_id)
            if not self.asset_subscriptions[asset_symbol]:
                del self.asset_subscriptions[asset_symbol]

        # Execute cleanup callbacks
        await self._execute_asset_callbacks(connection_id, asset_symbol)

    def get_portfolio_subscribers(self, portfolio_id: int) -> Set[str]:
        """
        Get all connection IDs subscribed to a portfolio.

        Args:
            portfolio_id: ID of the portfolio

        Returns:
            Set of connection IDs subscribed to the portfolio
        """
        return self.portfolio_subscriptions.get(portfolio_id, set())

    def get_asset_subscribers(self, asset_symbol: str) -> Set[str]:
        """
        Get all connection IDs subscribed to an asset.

        Args:
            asset_symbol: Symbol of the asset

        Returns:
            Set of connection IDs subscribed to the asset
        """
        return self.asset_subscriptions.get(asset_symbol, set())

    def get_user_connections(self, user_id: int) -> Set[str]:
        """
        Get all connection IDs for a user.

        Args:
            user_id: ID of the user

        Returns:
            Set of connection IDs for the user
        """
        return self.user_connections.get(user_id, set())

    def get_connection_count(self) -> int:
        """Get the total number of active connections."""
        return len(self.connections)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get connection statistics.

        Returns:
            Dictionary containing connection statistics
        """
        return {
            "total_connections": len(self.connections),
            "authenticated_users": len(self.user_connections),
            "portfolio_subscriptions": len(self.portfolio_subscriptions),
            "asset_subscriptions": len(self.asset_subscriptions),
            "connection_details": {
                connection_id: {
                    "user_id": info["user_id"],
                    "connected_at": info["connected_at"].isoformat(),
                    "portfolios": list(info["portfolios"]),
                    "assets": list(info["assets"]),
                }
                for connection_id, info in self.connections.items()
            },
        }


# Global connection manager instance
connection_manager = ConnectionManager()


class MessageEncoder(json.JSONEncoder):
    """Custom JSON encoder for WebSocket messages."""

    def default(self, obj):
        """Handle custom object serialization."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def encode_message(message_type: str, data: Dict[str, Any]) -> str:
    """
    Encode a message for WebSocket transmission.

    Args:
        message_type: Type of the message
        data: Message data

    Returns:
        JSON-encoded message string
    """
    message = {
        "type": message_type,
        "timestamp": datetime.now().isoformat(),
        "data": data,
    }
    return json.dumps(message, cls=MessageEncoder)
