"""Portfolio API URL routing."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PortfolioViewSet, PositionViewSet, TransactionViewSet, PortfolioSnapshotViewSet

router = DefaultRouter()
router.register(r'portfolios', PortfolioViewSet, basename='portfolio')
router.register(r'positions', PositionViewSet, basename='position')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'snapshots', PortfolioSnapshotViewSet, basename='portfolio-snapshot')

app_name = 'portfolios-api'
urlpatterns = [
    path('', include(router.urls)),
]