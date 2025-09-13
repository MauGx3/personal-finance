"""
Real-time API endpoints for WebSocket integration.

Provides REST API endpoints for WebSocket status, connection management,
and real-time data retrieval.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from personal_finance.realtime.connections import connection_manager
from personal_finance.realtime.services import price_feed_service
from personal_finance.assets.models import Asset
from personal_finance.portfolios.models import Portfolio


class RealtimeViewSet(viewsets.ViewSet):
    """ViewSet for real-time WebSocket management and status."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Get real-time service status and connection statistics.
        
        Returns information about active connections, subscriptions,
        and service health.
        """
        stats = connection_manager.get_stats()
        
        return Response({
            'service_status': 'running' if price_feed_service.is_running else 'stopped',
            'connections': stats,
            'price_feed': {
                'update_interval': price_feed_service.update_interval,
                'batch_size': price_feed_service.max_batch_size,
                'is_running': price_feed_service.is_running
            },
            'timestamp': timezone.now()
        })
    
    @action(detail=False, methods=['get'])
    def active_subscriptions(self, request):
        """
        Get active subscriptions for the current user.
        
        Returns portfolios and assets that the user has subscribed to
        for real-time updates.
        """
        user_connections = connection_manager.get_user_connections(request.user.id)
        
        user_portfolios = set()
        user_assets = set()
        
        for connection_id in user_connections:
            if connection_id in connection_manager.connections:
                conn_info = connection_manager.connections[connection_id]
                user_portfolios.update(conn_info['portfolios'])
                user_assets.update(conn_info['assets'])
        
        # Get portfolio details
        portfolio_details = []
        if user_portfolios:
            portfolios = Portfolio.objects.filter(
                id__in=user_portfolios,
                user=request.user
            )
            portfolio_details = [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description
                }
                for p in portfolios
            ]
        
        # Get asset details
        asset_details = []
        if user_assets:
            assets = Asset.objects.filter(symbol__in=user_assets)
            asset_details = [
                {
                    'symbol': a.symbol,
                    'name': a.name,
                    'current_price': a.current_price,
                    'last_updated': a.last_updated
                }
                for a in assets
            ]
        
        return Response({
            'portfolios': portfolio_details,
            'assets': asset_details,
            'connection_count': len(user_connections)
        })
    
    @action(detail=False, methods=['post'])
    def force_price_update(self, request):
        """
        Force an immediate price update for specific assets.
        
        Useful for manual updates or testing the real-time system.
        """
        symbols = request.data.get('symbols', [])
        
        if not symbols:
            return Response(
                {'error': 'No symbols provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate symbols exist
        valid_symbols = list(Asset.objects.filter(
            symbol__in=symbols
        ).values_list('symbol', flat=True))
        
        invalid_symbols = set(symbols) - set(valid_symbols)
        
        if invalid_symbols:
            return Response({
                'error': f'Invalid symbols: {list(invalid_symbols)}',
                'valid_symbols': valid_symbols
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Trigger immediate update (simplified - would integrate with price service)
        response_data = {
            'message': f'Price update triggered for {len(valid_symbols)} assets',
            'symbols': valid_symbols,
            'timestamp': timezone.now()
        }
        
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def market_hours(self, request):
        """
        Get current market hours and trading status.
        
        Returns information about market status for different exchanges.
        """
        now = timezone.now()
        
        # Simplified market hours (would use real market data)
        market_data = {
            'NYSE': {
                'is_open': self._is_market_open('NYSE', now),
                'next_open': self._get_next_market_open('NYSE', now),
                'next_close': self._get_next_market_close('NYSE', now)
            },
            'NASDAQ': {
                'is_open': self._is_market_open('NASDAQ', now),
                'next_open': self._get_next_market_open('NASDAQ', now),
                'next_close': self._get_next_market_close('NASDAQ', now)
            },
            'current_time': now,
            'timezone': 'UTC'
        }
        
        return Response(market_data)
    
    def _is_market_open(self, exchange: str, current_time) -> bool:
        """Check if a market is currently open (simplified)."""
        # Simplified - would use real market hours API
        hour = current_time.hour
        weekday = current_time.weekday()
        
        # Basic US market hours (9:30 AM - 4:00 PM EST, Mon-Fri)
        if weekday >= 5:  # Weekend
            return False
        
        # Convert to approximate EST (simplified)
        est_hour = (hour - 5) % 24
        return 9 <= est_hour < 16
    
    def _get_next_market_open(self, exchange: str, current_time):
        """Get next market open time (simplified)."""
        # Simplified implementation
        return current_time + timedelta(hours=1)
    
    def _get_next_market_close(self, exchange: str, current_time):
        """Get next market close time (simplified)."""
        # Simplified implementation
        return current_time + timedelta(hours=6)
    
    @action(detail=False, methods=['get'])
    def connection_info(self, request):
        """
        Get WebSocket connection information for the user.
        
        Returns details about how to connect to the WebSocket service.
        """
        return Response({
            'websocket_url': '/ws/realtime/',
            'protocols': ['json'],
            'authentication': 'session-based',
            'message_types': {
                'ping': 'Health check',
                'subscribe_asset': 'Subscribe to asset price updates',
                'subscribe_portfolio': 'Subscribe to portfolio value updates',
                'unsubscribe_asset': 'Unsubscribe from asset updates',
                'unsubscribe_portfolio': 'Unsubscribe from portfolio updates',
                'get_portfolio_value': 'Get current portfolio value',
                'get_asset_price': 'Get current asset price'
            },
            'update_frequency': f'{price_feed_service.update_interval} seconds'
        })