from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from personal_finance.assets.api.views import AssetViewSet
from personal_finance.assets.api.views import HoldingViewSet, PortfolioViewSet as LegacyPortfolioViewSet

# Graceful import handling for missing views
try:
    from personal_finance.assets.api.views import PriceHistoryViewSet
except ImportError:
    PriceHistoryViewSet = None

try:
    from personal_finance.portfolios.api.views import (
        PortfolioViewSet, PositionViewSet, TransactionViewSet, PortfolioSnapshotViewSet
    )
except ImportError:
    PortfolioViewSet = PositionViewSet = TransactionViewSet = PortfolioSnapshotViewSet = None

try:
    from personal_finance.users.api.views import UserViewSet
except ImportError:
    UserViewSet = None

try:
    from personal_finance.realtime.api import RealtimeViewSet
except ImportError:
    RealtimeViewSet = None

try:
    from personal_finance.tax.views import (
        TaxYearViewSet, TaxLotViewSet, CapitalGainLossViewSet,
        DividendIncomeViewSet, TaxLossHarvestingOpportunityViewSet,
        TaxOptimizationRecommendationViewSet, TaxReportViewSet,
        TaxAnalyticsViewSet
    )
except ImportError:
    TaxYearViewSet = TaxLotViewSet = CapitalGainLossViewSet = None
    DividendIncomeViewSet = TaxLossHarvestingOpportunityViewSet = None
    TaxOptimizationRecommendationViewSet = TaxReportViewSet = None
    TaxAnalyticsViewSet = None

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# User management
if UserViewSet:
    router.register("users", UserViewSet)

# Asset management
router.register("assets", AssetViewSet)
if PriceHistoryViewSet:
    router.register("price-history", PriceHistoryViewSet)

# Portfolio management (new comprehensive system)
if PortfolioViewSet:
    router.register("portfolios", PortfolioViewSet)
if PositionViewSet:
    router.register("positions", PositionViewSet)
if TransactionViewSet:
    router.register("transactions", TransactionViewSet)
if PortfolioSnapshotViewSet:
    router.register("portfolio-snapshots", PortfolioSnapshotViewSet)

# Legacy endpoints for backward compatibility
router.register("legacy-portfolios", LegacyPortfolioViewSet)
router.register("holdings", HoldingViewSet)

# Real-time WebSocket management
if RealtimeViewSet:
    router.register("realtime", RealtimeViewSet, basename='realtime')

# Tax reporting and optimization
if TaxYearViewSet:
    router.register("tax/tax-years", TaxYearViewSet, basename='tax-taxyear')
if TaxLotViewSet:
    router.register("tax/tax-lots", TaxLotViewSet, basename='tax-taxlot')
if CapitalGainLossViewSet:
    router.register("tax/capital-gains-losses", CapitalGainLossViewSet, basename='tax-capitalgainloss')
if DividendIncomeViewSet:
    router.register("tax/dividend-income", DividendIncomeViewSet, basename='tax-dividendincome')
if TaxLossHarvestingOpportunityViewSet:
    router.register("tax/loss-harvesting", TaxLossHarvestingOpportunityViewSet, basename='tax-lossharvesting')
if TaxOptimizationRecommendationViewSet:
    router.register("tax/recommendations", TaxOptimizationRecommendationViewSet, basename='tax-recommendations')
if TaxReportViewSet:
    router.register("tax/reports", TaxReportViewSet, basename='tax-reports')
if TaxAnalyticsViewSet:
    router.register("tax/analytics", TaxAnalyticsViewSet, basename='tax-analytics')

app_name = "api"
urlpatterns = router.urls
