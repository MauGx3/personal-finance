from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter
from loguru import logger

# Import viewsets defensively: some optional features pull heavy deps (pandas,
# polars, yfinance, etc.) that may not be available in minimal runtime images.
# If any import fails for any reason, log and fall back to None so URLConf can
# be imported for light-weight operations such as the health endpoint.
try:
    from personal_finance.assets.api.views import AssetViewSet
    from personal_finance.assets.api.views import (
        HoldingViewSet,
        PortfolioViewSet as LegacyPortfolioViewSet,
    )
except Exception:  # pragma: no cover - runtime resilience
    logger.exception("Failed to import assets viewsets")
    AssetViewSet = HoldingViewSet = LegacyPortfolioViewSet = None

try:  # optional price history
    from personal_finance.assets.api.views import PriceHistoryViewSet
except Exception:  # pragma: no cover - optional
    logger.exception("PriceHistoryViewSet import failed")
    PriceHistoryViewSet = None

try:
    from personal_finance.portfolios.api.views import (
        PortfolioViewSet,
        PositionViewSet,
        TransactionViewSet,
        PortfolioSnapshotViewSet,
    )
except Exception:  # pragma: no cover - optional
    logger.exception("Portfolios viewsets import failed")
    PortfolioViewSet = PositionViewSet = TransactionViewSet = (
        PortfolioSnapshotViewSet
    ) = None

try:
    from personal_finance.users.api.views import UserViewSet
except Exception:  # pragma: no cover - optional
    logger.exception("UserViewSet import failed")
    UserViewSet = None

try:
    from personal_finance.realtime.api import RealtimeViewSet
except Exception:  # pragma: no cover - optional
    logger.exception("RealtimeViewSet import failed")
    RealtimeViewSet = None

try:
    from personal_finance.tax.views import (
        TaxYearViewSet,
        TaxLotViewSet,
        CapitalGainLossViewSet,
        DividendIncomeViewSet,
        TaxLossHarvestingOpportunityViewSet,
        TaxOptimizationRecommendationViewSet,
        TaxReportViewSet,
        TaxAnalyticsViewSet,
    )
except Exception:  # pragma: no cover - optional
    logger.exception("Tax viewsets import failed")
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
    router.register("realtime", RealtimeViewSet, basename="realtime")

# Tax reporting and optimization
if TaxYearViewSet:
    router.register("tax/tax-years", TaxYearViewSet, basename="tax-taxyear")
if TaxLotViewSet:
    router.register("tax/tax-lots", TaxLotViewSet, basename="tax-taxlot")
if CapitalGainLossViewSet:
    router.register(
        "tax/capital-gains-losses",
        CapitalGainLossViewSet,
        basename="tax-capitalgainloss",
    )
if DividendIncomeViewSet:
    router.register(
        "tax/dividend-income",
        DividendIncomeViewSet,
        basename="tax-dividendincome",
    )
if TaxLossHarvestingOpportunityViewSet:
    router.register(
        "tax/loss-harvesting",
        TaxLossHarvestingOpportunityViewSet,
        basename="tax-lossharvesting",
    )
if TaxOptimizationRecommendationViewSet:
    router.register(
        "tax/recommendations",
        TaxOptimizationRecommendationViewSet,
        basename="tax-recommendations",
    )
if TaxReportViewSet:
    router.register("tax/reports", TaxReportViewSet, basename="tax-reports")
if TaxAnalyticsViewSet:
    router.register(
        "tax/analytics", TaxAnalyticsViewSet, basename="tax-analytics"
    )

app_name = "api"
urlpatterns = router.urls
