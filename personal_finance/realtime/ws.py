"""
WebSocket endpoint for realtime price streaming.

This module provides an ASGI websocket endpoint that accepts client subscriptions
and pushes price updates in real-time using the RealtimeService.
"""

import json
from typing import Dict, Any, List
from loguru import logger

try:
    import websockets
    from websockets.server import WebSocketServerProtocol

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    websockets = None
    WebSocketServerProtocol = None
    WEBSOCKETS_AVAILABLE = False

from .services import realtime_service, PricePoint


class WebSocketPriceEndpoint:
    """WebSocket endpoint for price subscriptions."""

    def __init__(self):
        self.connections: Dict[str, WebSocketServerProtocol] = {}
        self.connection_subscriptions: Dict[
            str, List[str]
        ] = {}  # connection_id -> [symbols]

    async def handle_connection(
        self, websocket: WebSocketServerProtocol, path: str
    ):
        """Handle a new WebSocket connection."""
        connection_id = f"ws_{id(websocket)}"
        self.connections[connection_id] = websocket
        self.connection_subscriptions[connection_id] = []

        logger.info(f"WebSocket connection established: {connection_id}")

        try:
            await self._send_message(
                websocket,
                {
                    "type": "connected",
                    "connection_id": connection_id,
                    "message": "WebSocket connection established",
                },
            )

            async for message in websocket:
                await self._handle_message(connection_id, websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket error for {connection_id}: {e}")
        finally:
            await self._cleanup_connection(connection_id)

    async def _handle_message(
        self,
        connection_id: str,
        websocket: WebSocketServerProtocol,
        message: str,
    ):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            payload = data.get("data", {})

            if message_type == "subscribe":
                await self._handle_subscribe(connection_id, websocket, payload)
            elif message_type == "unsubscribe":
                await self._handle_unsubscribe(
                    connection_id, websocket, payload
                )
            elif message_type == "ping":
                await self._send_message(
                    websocket,
                    {"type": "pong", "timestamp": payload.get("timestamp")},
                )
            else:
                await self._send_error(
                    websocket, f"Unknown message type: {message_type}"
                )

        except json.JSONDecodeError:
            await self._send_error(websocket, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error handling message from {connection_id}: {e}")
            await self._send_error(websocket, "Internal server error")

    async def _handle_subscribe(
        self,
        connection_id: str,
        websocket: WebSocketServerProtocol,
        payload: Dict[str, Any],
    ):
        """Handle subscription requests."""
        symbols = payload.get("symbols", [])
        if not symbols:
            await self._send_error(
                websocket, "No symbols provided for subscription"
            )
            return

        # Add to connection subscriptions
        self.connection_subscriptions[connection_id].extend(symbols)

        # Create a callback for this connection
        async def price_callback(price_point: PricePoint):
            await self._send_price_update(websocket, price_point)

        # Subscribe to realtime service
        await realtime_service.subscribe(symbols, price_callback)

        await self._send_message(
            websocket,
            {
                "type": "subscribed",
                "symbols": symbols,
                "message": f"Subscribed to {len(symbols)} symbols",
            },
        )

        logger.info(f"Connection {connection_id} subscribed to {symbols}")

    async def _handle_unsubscribe(
        self,
        connection_id: str,
        websocket: WebSocketServerProtocol,
        payload: Dict[str, Any],
    ):
        """Handle unsubscription requests."""
        symbols = payload.get("symbols", [])
        if not symbols:
            await self._send_error(
                websocket, "No symbols provided for unsubscription"
            )
            return

        # Remove from connection subscriptions
        for symbol in symbols:
            if symbol in self.connection_subscriptions[connection_id]:
                self.connection_subscriptions[connection_id].remove(symbol)

        # Note: For simplicity, we don't unsubscribe from realtime_service here
        # as we'd need to track callbacks per connection, which adds complexity.
        # In a production system, you'd want proper callback management.

        await self._send_message(
            websocket,
            {
                "type": "unsubscribed",
                "symbols": symbols,
                "message": f"Unsubscribed from {len(symbols)} symbols",
            },
        )

        logger.info(f"Connection {connection_id} unsubscribed from {symbols}")

    async def _send_price_update(
        self, websocket: WebSocketServerProtocol, price_point: PricePoint
    ):
        """Send price update to a specific WebSocket connection."""
        message = {"type": "price_update", "data": price_point.to_dict()}
        await self._send_message(websocket, message)

    async def _send_message(
        self, websocket: WebSocketServerProtocol, message: Dict[str, Any]
    ):
        """Send a message to a WebSocket connection."""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            # Connection is closed, ignore
            pass
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def _send_error(
        self, websocket: WebSocketServerProtocol, error: str
    ):
        """Send an error message to a WebSocket connection."""
        message = {"type": "error", "error": error}
        await self._send_message(websocket, message)

    async def _cleanup_connection(self, connection_id: str):
        """Clean up a closed connection."""
        if connection_id in self.connections:
            del self.connections[connection_id]
        if connection_id in self.connection_subscriptions:
            del self.connection_subscriptions[connection_id]
        logger.info(f"Cleaned up connection: {connection_id}")


# Global endpoint instance
websocket_endpoint = WebSocketPriceEndpoint()


async def start_websocket_server(host: str = "localhost", port: int = 8765):
    """
    Start the WebSocket server.

    Args:
        host: Host address to bind to
        port: Port number to bind to
    """
    if not WEBSOCKETS_AVAILABLE:
        logger.error(
            "websockets library not available. Install with: pip install websockets"
        )
        return None

    logger.info(f"Starting WebSocket server on {host}:{port}")

    # Start the realtime service if not already running
    if not realtime_service.is_running:
        await realtime_service.start()

    server = await websockets.serve(
        websocket_endpoint.handle_connection, host, port
    )

    logger.info(f"WebSocket server started on ws://{host}:{port}")
    return server


# ASGI application for Django Channels integration
class ASGIWebSocketApp:
    """ASGI application for Django Channels integration."""

    def __init__(self):
        self.endpoint = WebSocketPriceEndpoint()

    async def __call__(self, scope, receive, send):
        """ASGI application callable."""
        if scope["type"] != "websocket":
            await send({"type": "websocket.close", "code": 4000})
            return

        # Accept the connection
        await send({"type": "websocket.accept"})

        connection_id = f"asgi_{id(scope)}"

        try:
            while True:
                message = await receive()

                if message["type"] == "websocket.connect":
                    # Connection handled above
                    continue
                elif message["type"] == "websocket.disconnect":
                    break
                elif message["type"] == "websocket.receive":
                    text_data = message.get("text")
                    if text_data:
                        await self._handle_asgi_message(
                            connection_id, send, text_data
                        )

        except Exception as e:
            logger.error(f"ASGI WebSocket error: {e}")
        finally:
            await self._cleanup_asgi_connection(connection_id)

    async def _handle_asgi_message(
        self, connection_id: str, send, message: str
    ):
        """Handle ASGI WebSocket messages."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            payload = data.get("data", {})

            if message_type == "subscribe":
                symbols = payload.get("symbols", [])
                if symbols:
                    # Create callback for ASGI
                    async def asgi_callback(price_point: PricePoint):
                        await send(
                            {
                                "type": "websocket.send",
                                "text": json.dumps(
                                    {
                                        "type": "price_update",
                                        "data": price_point.to_dict(),
                                    }
                                ),
                            }
                        )

                    await realtime_service.subscribe(symbols, asgi_callback)

                    await send(
                        {
                            "type": "websocket.send",
                            "text": json.dumps(
                                {
                                    "type": "subscribed",
                                    "symbols": symbols,
                                    "message": f"Subscribed to {len(symbols)} symbols",
                                }
                            ),
                        }
                    )
            elif message_type == "ping":
                await send(
                    {
                        "type": "websocket.send",
                        "text": json.dumps(
                            {
                                "type": "pong",
                                "timestamp": payload.get("timestamp"),
                            }
                        ),
                    }
                )

        except json.JSONDecodeError:
            await send(
                {
                    "type": "websocket.send",
                    "text": json.dumps(
                        {"type": "error", "error": "Invalid JSON format"}
                    ),
                }
            )
        except Exception as e:
            logger.error(f"Error handling ASGI message: {e}")

    async def _cleanup_asgi_connection(self, connection_id: str):
        """Clean up ASGI connection."""
        logger.info(f"ASGI connection cleaned up: {connection_id}")


# ASGI application instance
asgi_app = ASGIWebSocketApp()
