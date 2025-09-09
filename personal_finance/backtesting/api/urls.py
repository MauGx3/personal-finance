"""URL configuration for backtesting API."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    StrategyViewSet, BacktestViewSet, BacktestResultViewSet,
    BacktestComparisonView, quick_backtest
)

app_name = 'backtesting_api'

# Create router
router = DefaultRouter()
router.register(r'strategies', StrategyViewSet, basename='strategy')
router.register(r'backtests', BacktestViewSet, basename='backtest')
router.register(r'results', BacktestResultViewSet, basename='result')
router.register(r'comparison', BacktestComparisonView, basename='comparison')

urlpatterns = [
    path('', include(router.urls)),
    path('quick-backtest/', quick_backtest, name='quick-backtest'),
]