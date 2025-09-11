"""
WebSocket URL routing for real-time updates.

Defines URL patterns for WebSocket connections and message routing.
"""

from django.urls import path
from . import websocket

websocket_urlpatterns = [
    path('ws/realtime/', websocket.websocket_application),
]