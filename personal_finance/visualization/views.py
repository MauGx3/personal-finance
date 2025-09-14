"""Dashboard views for portfolio visualization and analytics.

This module provides Django views for rendering interactive financial dashboards
using the chart generation utilities and portfolio analytics.
"""

import logging
from typing import Dict, Any
from datetime import datetime, date, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.utils import timezone

# Graceful import handling for missing models
try:
    from personal_finance.portfolios.models import Portfolio
except ImportError:
    Portfolio = None
    
from personal_finance.assets.models import Asset
from personal_finance.visualization.charts import PortfolioCharts, AssetCharts

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view showing portfolio overview and charts."""
    
    template_name = 'visualization/dashboard.html'
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add portfolio data to template context.
        
        Returns:
            Context dictionary with user portfolios and chart data
        """
        context = super().get_context_data(**kwargs)
        
        # Get user's portfolios
        portfolios = Portfolio.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('name')
        
        context.update({
            'portfolios': portfolios,
            'total_portfolios': portfolios.count(),
            'active_assets': self._get_active_assets_count(),
            'dashboard_title': 'Personal Finance Dashboard'
        })
        
        return context
    
    def _get_active_assets_count(self) -> int:
        """Get count of unique assets across all user portfolios."""
        portfolios = Portfolio.objects.filter(user=self.request.user)
        asset_ids = set()
        
        for portfolio in portfolios:
            for position in portfolio.positions.filter(is_active=True):
                asset_ids.add(position.asset.id)
        
        return len(asset_ids)


class PortfolioDetailView(LoginRequiredMixin, TemplateView):
    """Detailed portfolio view with comprehensive analytics and charts."""
    
    template_name = 'visualization/portfolio_detail.html'
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add portfolio-specific data to template context."""
        context = super().get_context_data(**kwargs)
        
        portfolio_id = self.kwargs.get('portfolio_id')
        portfolio = get_object_or_404(
            Portfolio,
            id=portfolio_id,
            user=self.request.user
        )
        
        # Get positions for the portfolio
        positions = portfolio.positions.filter(is_active=True).select_related('asset')
        
        context.update({
            'portfolio': portfolio,
            'positions': positions,
            'total_positions': positions.count(),
            'portfolio_value': portfolio.total_value,
            'dashboard_title': f'{portfolio.name} - Detailed View'
        })
        
        return context


@login_required
def portfolio_performance_chart_api(request: HttpRequest, portfolio_id: int) -> JsonResponse:
    """API endpoint for portfolio performance chart data.
    
    Args:
        request: HTTP request object
        portfolio_id: Portfolio ID to generate chart for
        
    Returns:
        JSON response containing chart data
    """
    try:
        portfolio = get_object_or_404(
            Portfolio,
            id=portfolio_id,
            user=request.user
        )
        
        # Get date range from query parameters
        days = int(request.GET.get('days', 365))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Generate chart
        chart_generator = PortfolioCharts()
        chart_data = chart_generator.create_portfolio_performance_chart(
            portfolio, start_date, end_date
        )
        
        return JsonResponse(chart_data)
        
    except Exception as e:
        logger.error(f"Error generating performance chart: {e}")
        return JsonResponse({
            'error': 'Failed to generate performance chart',
            'message': str(e)
        }, status=500)


@login_required
def portfolio_allocation_chart_api(request: HttpRequest, portfolio_id: int) -> JsonResponse:
    """API endpoint for portfolio allocation pie chart data.
    
    Args:
        request: HTTP request object
        portfolio_id: Portfolio ID to generate chart for
        
    Returns:
        JSON response containing chart data
    """
    try:
        portfolio = get_object_or_404(
            Portfolio,
            id=portfolio_id,
            user=request.user
        )
        
        # Generate allocation chart
        chart_generator = PortfolioCharts()
        chart_data = chart_generator.create_asset_allocation_chart(portfolio)
        
        return JsonResponse(chart_data)
        
    except Exception as e:
        logger.error(f"Error generating allocation chart: {e}")
        return JsonResponse({
            'error': 'Failed to generate allocation chart',
            'message': str(e)
        }, status=500)


@login_required
def portfolio_risk_metrics_chart_api(request: HttpRequest, portfolio_id: int) -> JsonResponse:
    """API endpoint for portfolio risk metrics visualization.
    
    Args:
        request: HTTP request object
        portfolio_id: Portfolio ID to generate chart for
        
    Returns:
        JSON response containing chart data
    """
    try:
        portfolio = get_object_or_404(
            Portfolio,
            id=portfolio_id,
            user=request.user
        )
        
        # Generate risk metrics chart
        chart_generator = PortfolioCharts()
        chart_data = chart_generator.create_risk_metrics_chart(portfolio)
        
        return JsonResponse(chart_data)
        
    except Exception as e:
        logger.error(f"Error generating risk metrics chart: {e}")
        return JsonResponse({
            'error': 'Failed to generate risk metrics chart',
            'message': str(e)
        }, status=500)


@login_required
def asset_price_chart_api(request: HttpRequest, asset_id: int) -> JsonResponse:
    """API endpoint for asset price chart with technical indicators.
    
    Args:
        request: HTTP request object
        asset_id: Asset ID to generate chart for
        
    Returns:
        JSON response containing chart data
    """
    try:
        asset = get_object_or_404(Asset, id=asset_id)
        
        # Get parameters from query string
        days = int(request.GET.get('days', 252))
        indicators = request.GET.getlist('indicators')
        
        # Generate price chart
        chart_generator = AssetCharts()
        chart_data = chart_generator.create_price_chart_with_indicators(
            asset, days=days, indicators=indicators
        )
        
        return JsonResponse(chart_data)
        
    except Exception as e:
        logger.error(f"Error generating asset price chart: {e}")
        return JsonResponse({
            'error': 'Failed to generate asset price chart',
            'message': str(e)
        }, status=500)


@login_required
def dashboard_summary_api(request: HttpRequest) -> JsonResponse:
    """API endpoint for dashboard summary statistics.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON response containing summary statistics
    """
    try:
        user = request.user
        portfolios = Portfolio.objects.filter(user=user, is_active=True)
        
        # Calculate summary statistics
        total_value = sum(portfolio.total_value for portfolio in portfolios)
        total_positions = sum(
            portfolio.positions.filter(is_active=True).count()
            for portfolio in portfolios
        )
        
        # Get top performing assets
        top_performers = []
        for portfolio in portfolios:
            for position in portfolio.positions.filter(is_active=True):
                return_pct = position.total_return_percent
                if return_pct is not None:
                    top_performers.append({
                        'symbol': position.asset.symbol,
                        'name': position.asset.name,
                        'return': float(return_pct),
                        'value': float(position.current_value)
                    })
        
        # Sort by return and take top 5
        top_performers.sort(key=lambda x: x['return'], reverse=True)
        top_performers = top_performers[:5]
        
        summary_data = {
            'total_portfolios': portfolios.count(),
            'total_value': float(total_value),
            'total_positions': total_positions,
            'top_performers': top_performers,
            'last_updated': timezone.now().isoformat()
        }
        
        return JsonResponse(summary_data)
        
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {e}")
        return JsonResponse({
            'error': 'Failed to generate dashboard summary',
            'message': str(e)
        }, status=500)