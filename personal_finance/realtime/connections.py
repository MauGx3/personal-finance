"""
WebSocket connection manager for real-time updates.

This module handles WebSocket connections, user authentication,
and message broadcasting for live market data updates.
"""

import json
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


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
    
    async def connect(self, connection_id: str, user_id: Optional[int] = None):
        """
        Register a new WebSocket connection.
        
        Args:
            connection_id: Unique identifier for the connection
            user_id: ID of the authenticated user (if any)
        """
        self.connections[connection_id] = {
            'user_id': user_id,
            'connected_at': datetime.now(),
            'portfolios': set(),
            'assets': set(),
        }
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
            
        logger.info(f"WebSocket connected: {connection_id}, user: {user_id}")
    
    async def disconnect(self, connection_id: str):
        """
        Unregister a WebSocket connection.
        
        Args:
            connection_id: Unique identifier for the connection
        """
        if connection_id not in self.connections:
            return
            
        connection_info = self.connections[connection_id]
        user_id = connection_info['user_id']
        
        # Clean up user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Clean up portfolio subscriptions
        for portfolio_id in connection_info['portfolios']:
            if portfolio_id in self.portfolio_subscriptions:
                self.portfolio_subscriptions[portfolio_id].discard(connection_id)
                if not self.portfolio_subscriptions[portfolio_id]:
                    del self.portfolio_subscriptions[portfolio_id]
        
        # Clean up asset subscriptions
        for asset_symbol in connection_info['assets']:
            if asset_symbol in self.asset_subscriptions:
                self.asset_subscriptions[asset_symbol].discard(connection_id)
                if not self.asset_subscriptions[asset_symbol]:
                    del self.asset_subscriptions[asset_symbol]
        
        del self.connections[connection_id]
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def subscribe_to_portfolio(self, connection_id: str, portfolio_id: int):
        """
        Subscribe a connection to portfolio updates.
        
        Args:
            connection_id: Unique identifier for the connection
            portfolio_id: ID of the portfolio to subscribe to
        """
        if connection_id not in self.connections:
            return
            
        self.connections[connection_id]['portfolios'].add(portfolio_id)
        
        if portfolio_id not in self.portfolio_subscriptions:
            self.portfolio_subscriptions[portfolio_id] = set()
        self.portfolio_subscriptions[portfolio_id].add(connection_id)
        
        logger.debug(f"Connection {connection_id} subscribed to portfolio {portfolio_id}")
    
    async def subscribe_to_asset(self, connection_id: str, asset_symbol: str):
        """
        Subscribe a connection to asset price updates.
        
        Args:
            connection_id: Unique identifier for the connection
            asset_symbol: Symbol of the asset to subscribe to
        """
        if connection_id not in self.connections:
            return
            
        self.connections[connection_id]['assets'].add(asset_symbol)
        
        if asset_symbol not in self.asset_subscriptions:
            self.asset_subscriptions[asset_symbol] = set()
        self.asset_subscriptions[asset_symbol].add(connection_id)
        
        logger.debug(f"Connection {connection_id} subscribed to asset {asset_symbol}")
    
    async def unsubscribe_from_portfolio(self, connection_id: str, portfolio_id: int):
        """
        Unsubscribe a connection from portfolio updates.
        
        Args:
            connection_id: Unique identifier for the connection
            portfolio_id: ID of the portfolio to unsubscribe from
        """
        if connection_id not in self.connections:
            return
            
        self.connections[connection_id]['portfolios'].discard(portfolio_id)
        
        if portfolio_id in self.portfolio_subscriptions:
            self.portfolio_subscriptions[portfolio_id].discard(connection_id)
            if not self.portfolio_subscriptions[portfolio_id]:
                del self.portfolio_subscriptions[portfolio_id]
    
    async def unsubscribe_from_asset(self, connection_id: str, asset_symbol: str):
        """
        Unsubscribe a connection from asset price updates.
        
        Args:
            connection_id: Unique identifier for the connection
            asset_symbol: Symbol of the asset to unsubscribe from
        """
        if connection_id not in self.connections:
            return
            
        self.connections[connection_id]['assets'].discard(asset_symbol)
        
        if asset_symbol in self.asset_subscriptions:
            self.asset_subscriptions[asset_symbol].discard(connection_id)
            if not self.asset_subscriptions[asset_symbol]:
                del self.asset_subscriptions[asset_symbol]
    
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
            'total_connections': len(self.connections),
            'authenticated_users': len(self.user_connections),
            'portfolio_subscriptions': len(self.portfolio_subscriptions),
            'asset_subscriptions': len(self.asset_subscriptions),
            'connection_details': {
                connection_id: {
                    'user_id': info['user_id'],
                    'connected_at': info['connected_at'].isoformat(),
                    'portfolios': list(info['portfolios']),
                    'assets': list(info['assets']),
                }
                for connection_id, info in self.connections.items()
            }
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
        'type': message_type,
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    return json.dumps(message, cls=MessageEncoder)