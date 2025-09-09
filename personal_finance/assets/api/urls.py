"""Assets API URL routing."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AssetViewSet, PriceHistoryViewSet

router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'price-history', PriceHistoryViewSet, basename='price-history')

app_name = 'assets-api'
urlpatterns = [
    path('', include(router.urls)),
]