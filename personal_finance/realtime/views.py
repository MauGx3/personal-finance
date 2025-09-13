"""
Views for real-time dashboard and WebSocket integration.

Provides Django views for the real-time market data dashboard
and WebSocket status pages.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Graceful import handling for missing models
try:
    from personal_finance.portfolios.models import Portfolio
except ImportError:
    Portfolio = None
    
from personal_finance.assets.models import Asset
from personal_finance.realtime.connections import connection_manager
from personal_finance.realtime.services import price_feed_service


class RealtimeDashboardView(LoginRequiredMixin, TemplateView):
    """Real-time dashboard view with WebSocket integration."""
    
    template_name = 'realtime/dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Add context data for the dashboard."""
        context = super().get_context_data(**kwargs)
        
        # Get user's portfolios for subscription dropdown
        user_portfolios = Portfolio.objects.filter(
            user=self.request.user
        ).order_by('name')
        
        # Get popular assets for quick subscription
        popular_assets = Asset.objects.filter(
            is_active=True
        ).order_by('-current_price')[:20]
        
        # Get connection statistics
        connection_stats = connection_manager.get_stats()
        
        context.update({
            'user_portfolios': user_portfolios,
            'popular_assets': popular_assets,
            'connection_stats': connection_stats,
            'price_feed_status': {
                'is_running': price_feed_service.is_running,
                'update_interval': price_feed_service.update_interval,
                'max_batch_size': price_feed_service.max_batch_size
            }
        })
        
        return context


@login_required
def realtime_status(request):
    """
    API endpoint for real-time service status.
    
    Returns JSON status information about WebSocket connections
    and price feed service.
    """
    stats = connection_manager.get_stats()
    
    # Get user's active connections
    user_connections = connection_manager.get_user_connections(request.user.id)
    user_stats = {
        'connection_count': len(user_connections),
        'subscriptions': {
            'portfolios': set(),
            'assets': set()
        }
    }
    
    # Aggregate user subscriptions
    for connection_id in user_connections:
        if connection_id in connection_manager.connections:
            conn_info = connection_manager.connections[connection_id]
            user_stats['subscriptions']['portfolios'].update(conn_info['portfolios'])
            user_stats['subscriptions']['assets'].update(conn_info['assets'])
    
    # Convert sets to lists for JSON serialization
    user_stats['subscriptions']['portfolios'] = list(user_stats['subscriptions']['portfolios'])
    user_stats['subscriptions']['assets'] = list(user_stats['subscriptions']['assets'])
    
    return JsonResponse({
        'service_status': 'running' if price_feed_service.is_running else 'stopped',
        'global_stats': stats,
        'user_stats': user_stats,
        'price_feed': {
            'is_running': price_feed_service.is_running,
            'update_interval': price_feed_service.update_interval,
            'max_batch_size': price_feed_service.max_batch_size
        }
    })


@login_required
def websocket_info(request):
    """
    API endpoint for WebSocket connection information.
    
    Returns information needed to establish WebSocket connections.
    """
    # Determine WebSocket URL based on request
    is_secure = request.is_secure()
    host = request.get_host()
    ws_protocol = 'wss' if is_secure else 'ws'
    ws_url = f"{ws_protocol}://{host}/ws/realtime/"
    
    return JsonResponse({
        'websocket_url': ws_url,
        'connection_info': {
            'protocol': ws_protocol,
            'host': host,
            'path': '/ws/realtime/',
            'authentication': 'session-based'
        },
        'message_types': {
            'ping': 'Health check message',
            'subscribe_asset': 'Subscribe to asset price updates',
            'subscribe_portfolio': 'Subscribe to portfolio value updates',
            'unsubscribe_asset': 'Unsubscribe from asset updates',
            'unsubscribe_portfolio': 'Unsubscribe from portfolio updates',
            'get_portfolio_value': 'Request current portfolio value',
            'get_asset_price': 'Request current asset price'
        },
        'update_frequency': f'{price_feed_service.update_interval} seconds',
        'supported_features': [
            'Real-time asset price updates',
            'Live portfolio value tracking',
            'Multiple simultaneous subscriptions',
            'Automatic reconnection',
            'Error handling and logging'
        ]
    })


@csrf_exempt
def websocket_test(request):
    """
    Simple WebSocket connection test endpoint.
    
    Provides a basic test interface for WebSocket functionality.
    """
    if request.method == 'POST':
        # Handle test message sending
        message_type = request.POST.get('type', 'ping')
        
        # This would typically send a test message
        # For now, just return success
        return JsonResponse({
            'status': 'success',
            'message': f'Test message of type "{message_type}" would be sent',
            'service_available': price_feed_service.is_running
        })
    
    # GET request - return test form
    return render(request, 'realtime/test.html', {
        'websocket_url': '/ws/realtime/',
        'service_status': 'running' if price_feed_service.is_running else 'stopped'
    })