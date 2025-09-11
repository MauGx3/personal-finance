"""
WebSocket application for real-time market data and portfolio updates.

Handles WebSocket connections, authentication, and real-time message broadcasting
for live price feeds and portfolio value updates.
"""

import json
import logging
import uuid
from urllib.parse import parse_qs
from typing import Optional, Dict, Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.auth import get_user

from personal_finance.realtime.connections import connection_manager, encode_message
from personal_finance.realtime.services import price_feed_service

User = get_user_model()
logger = logging.getLogger(__name__)


class WebSocketHandler:
    """Handles WebSocket connections and message routing."""
    
    def __init__(self, scope, receive, send):
        self.scope = scope
        self.receive = receive
        self.send = send
        self.connection_id = str(uuid.uuid4())
        self.user = None
        self.is_authenticated = False
    
    async def connect(self):
        """Handle WebSocket connection."""
        # Accept the connection
        await self.send({"type": "websocket.accept"})
        
        # Try to authenticate user
        self.user = await self.get_user()
        self.is_authenticated = self.user and not isinstance(self.user, AnonymousUser)
        
        # Register connection
        user_id = self.user.id if self.is_authenticated else None
        await connection_manager.connect(self.connection_id, user_id)
        
        # Send welcome message
        welcome_msg = encode_message('connection', {
            'status': 'connected',
            'connection_id': self.connection_id,
            'authenticated': self.is_authenticated,
            'user_id': user_id
        })
        await self.send({
            "type": "websocket.send",
            "text": welcome_msg
        })
        
        logger.info(f"WebSocket connected: {self.connection_id}, user: {user_id}")
    
    async def disconnect(self):
        """Handle WebSocket disconnection."""
        await connection_manager.disconnect(self.connection_id)
        logger.info(f"WebSocket disconnected: {self.connection_id}")
    
    async def receive_message(self, text_data: str):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            payload = data.get('data', {})
            
            # Route message based on type
            if message_type == 'ping':
                await self.handle_ping()
            elif message_type == 'subscribe_asset':
                await self.handle_subscribe_asset(payload)
            elif message_type == 'unsubscribe_asset':
                await self.handle_unsubscribe_asset(payload)
            elif message_type == 'subscribe_portfolio':
                await self.handle_subscribe_portfolio(payload)
            elif message_type == 'unsubscribe_portfolio':
                await self.handle_unsubscribe_portfolio(payload)
            elif message_type == 'get_portfolio_value':
                await self.handle_get_portfolio_value(payload)
            elif message_type == 'get_asset_price':
                await self.handle_get_asset_price(payload)
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_error("Internal server error")
    
    async def handle_ping(self):
        """Handle ping message."""
        pong_msg = encode_message('pong', {'timestamp': 'now'})
        await self.send({
            "type": "websocket.send",
            "text": pong_msg
        })
    
    async def handle_subscribe_asset(self, payload: Dict[str, Any]):
        """Handle asset subscription."""
        symbol = payload.get('symbol')
        if not symbol:
            await self.send_error("Symbol is required for asset subscription")
            return
        
        await price_feed_service.subscribe_to_asset(self.connection_id, symbol)
        
        response = encode_message('subscription_confirmed', {
            'type': 'asset',
            'symbol': symbol
        })
        await self.send({
            "type": "websocket.send",
            "text": response
        })
    
    async def handle_unsubscribe_asset(self, payload: Dict[str, Any]):
        """Handle asset unsubscription."""
        symbol = payload.get('symbol')
        if not symbol:
            await self.send_error("Symbol is required for asset unsubscription")
            return
        
        await connection_manager.unsubscribe_from_asset(self.connection_id, symbol)
        
        response = encode_message('unsubscription_confirmed', {
            'type': 'asset',
            'symbol': symbol
        })
        await self.send({
            "type": "websocket.send",
            "text": response
        })
    
    async def handle_subscribe_portfolio(self, payload: Dict[str, Any]):
        """Handle portfolio subscription."""
        if not self.is_authenticated:
            await self.send_error("Authentication required for portfolio subscription")
            return
        
        portfolio_id = payload.get('portfolio_id')
        if not portfolio_id:
            await self.send_error("Portfolio ID is required for portfolio subscription")
            return
        
        # Verify user owns the portfolio
        if not await self.user_owns_portfolio(portfolio_id):
            await self.send_error("Access denied to portfolio")
            return
        
        await price_feed_service.subscribe_to_portfolio(self.connection_id, portfolio_id)
        
        response = encode_message('subscription_confirmed', {
            'type': 'portfolio',
            'portfolio_id': portfolio_id
        })
        await self.send({
            "type": "websocket.send",
            "text": response
        })
    
    async def handle_unsubscribe_portfolio(self, payload: Dict[str, Any]):
        """Handle portfolio unsubscription."""
        portfolio_id = payload.get('portfolio_id')
        if not portfolio_id:
            await self.send_error("Portfolio ID is required for portfolio unsubscription")
            return
        
        await connection_manager.unsubscribe_from_portfolio(self.connection_id, portfolio_id)
        
        response = encode_message('unsubscription_confirmed', {
            'type': 'portfolio',
            'portfolio_id': portfolio_id
        })
        await self.send({
            "type": "websocket.send",
            "text": response
        })
    
    async def handle_get_portfolio_value(self, payload: Dict[str, Any]):
        """Handle request for current portfolio value."""
        if not self.is_authenticated:
            await self.send_error("Authentication required")
            return
        
        portfolio_id = payload.get('portfolio_id')
        if not portfolio_id:
            await self.send_error("Portfolio ID is required")
            return
        
        # Verify user owns the portfolio
        if not await self.user_owns_portfolio(portfolio_id):
            await self.send_error("Access denied to portfolio")
            return
        
        # Get portfolio value (simplified implementation)
        response = encode_message('portfolio_value', {
            'portfolio_id': portfolio_id,
            'value': 0,  # Would calculate actual value
            'timestamp': 'now'
        })
        await self.send({
            "type": "websocket.send",
            "text": response
        })
    
    async def handle_get_asset_price(self, payload: Dict[str, Any]):
        """Handle request for current asset price."""
        symbol = payload.get('symbol')
        if not symbol:
            await self.send_error("Symbol is required")
            return
        
        # Get asset price (simplified implementation)
        response = encode_message('asset_price', {
            'symbol': symbol,
            'price': 0,  # Would get actual price
            'timestamp': 'now'
        })
        await self.send({
            "type": "websocket.send",
            "text": response
        })
    
    async def send_error(self, message: str):
        """Send error message to client."""
        error_msg = encode_message('error', {'message': message})
        await self.send({
            "type": "websocket.send",
            "text": error_msg
        })
    
    @database_sync_to_async
    def get_user(self):
        """Get the authenticated user from the scope."""
        # Extract user from scope (Django Channels style)
        return getattr(self.scope, 'user', AnonymousUser())
    
    @database_sync_to_async
    def user_owns_portfolio(self, portfolio_id: int) -> bool:
        """Check if the current user owns the portfolio."""
        if not self.is_authenticated:
            return False
        
        from personal_finance.portfolios.models import Portfolio
        try:
            Portfolio.objects.get(id=portfolio_id, user=self.user)
            return True
        except Portfolio.DoesNotExist:
            return False


async def websocket_application(scope, receive, send):
    """Main WebSocket application handler."""
    handler = WebSocketHandler(scope, receive, send)
    
    # Handle connection lifecycle
    await handler.connect()
    
    try:
        while True:
            event = await receive()
            
            if event["type"] == "websocket.disconnect":
                break
            
            if event["type"] == "websocket.receive":
                text_data = event.get("text", "")
                await handler.receive_message(text_data)
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await handler.disconnect()
