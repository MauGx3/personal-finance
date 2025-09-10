"""Assets API URL routing."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AssetViewSet

# Graceful import for PriceHistoryViewSet
try:
    from .views import PriceHistoryViewSet
except ImportError:
    PriceHistoryViewSet = None

router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')

# Only register if PriceHistoryViewSet is available
if PriceHistoryViewSet:
    router.register(r'price-history', PriceHistoryViewSet, basename='price-history')

app_name = 'assets-api'
urlpatterns = [
    path('', include(router.urls)),
]