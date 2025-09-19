"""URL patterns for analytics app including stock analysis."""

from django.urls import path, include
from .api import stock_views

app_name = "analytics"

# Stock Analysis API URLs
stock_api_urlpatterns = [
    path(
        'stock/<str:symbol>/analysis/',
        stock_views.stock_analysis,
        name='stock-analysis'
    ),
    path(
        'stock/<str:symbol>/financials/',
        stock_views.stock_financials,
        name='stock-financials'
    ),
    path(
        'stock/<str:symbol>/technical/',
        stock_views.stock_technical_analysis,
        name='stock-technical'
    ),
    path(
        'stock/<str:symbol>/quote/',
        stock_views.stock_real_time_quote,
        name='stock-quote'
    ),
    path(
        'stock/<str:symbol>/sentiment/',
        stock_views.stock_market_sentiment,
        name='stock-sentiment'
    ),
    path(
        'stock/<str:symbol>/sector-comparison/',
        stock_views.stock_sector_comparison,
        name='stock-sector-comparison'
    ),
    path(
        'stocks/compare/',
        stock_views.compare_stocks,
        name='compare-stocks'
    ),
]

urlpatterns = [
    # API endpoints
    path('api/', include(stock_api_urlpatterns)),
]