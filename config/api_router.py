from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from personal_finance.assets.api.views import AssetViewSet, PriceHistoryViewSet
from personal_finance.assets.api.views import HoldingViewSet, PortfolioViewSet as LegacyPortfolioViewSet
from personal_finance.portfolios.api.views import (
    PortfolioViewSet, PositionViewSet, TransactionViewSet, PortfolioSnapshotViewSet
)
from personal_finance.users.api.views import UserViewSet
from personal_finance.realtime.api import RealtimeViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# User management
router.register("users", UserViewSet)

# Asset management
router.register("assets", AssetViewSet)
router.register("price-history", PriceHistoryViewSet)

# Portfolio management (new comprehensive system)
router.register("portfolios", PortfolioViewSet)
router.register("positions", PositionViewSet)
router.register("transactions", TransactionViewSet)
router.register("portfolio-snapshots", PortfolioSnapshotViewSet)

# Legacy endpoints for backward compatibility
router.register("legacy-portfolios", LegacyPortfolioViewSet)
router.register("holdings", HoldingViewSet)

# Real-time WebSocket management
router.register("realtime", RealtimeViewSet, basename='realtime')

app_name = "api"
urlpatterns = router.urls
