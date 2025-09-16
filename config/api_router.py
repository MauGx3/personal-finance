from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from personal_finance.assets.api.views import AssetViewSet
from personal_finance.assets.api.views import (
    HoldingViewSet,
    PortfolioViewSet as LegacyPortfolioViewSet,
)

# Import the Django feature registry for structured component management
from .django_feature_registry import register_optional_viewsets, get_viewset

# Register optional ViewSets using structured feature registry
# This replaces fragile try/except blocks with explicit feature management

# Asset-related optional ViewSets
asset_viewsets = register_optional_viewsets(
    "asset_features",
    "personal_finance.assets.api.views",
    ["PriceHistoryViewSet"],
)
PriceHistoryViewSet = asset_viewsets["PriceHistoryViewSet"]

# Portfolio management ViewSets
portfolio_viewsets = register_optional_viewsets(
    "portfolio_features",
    "personal_finance.portfolios.api.views",
    [
        "PortfolioViewSet",
        "PositionViewSet",
        "TransactionViewSet",
        "PortfolioSnapshotViewSet",
    ],
)
PortfolioViewSet = portfolio_viewsets["PortfolioViewSet"]
PositionViewSet = portfolio_viewsets["PositionViewSet"]
TransactionViewSet = portfolio_viewsets["TransactionViewSet"]
PortfolioSnapshotViewSet = portfolio_viewsets["PortfolioSnapshotViewSet"]

# User management ViewSets
user_viewsets = register_optional_viewsets(
    "user_features", "personal_finance.users.api.views", ["UserViewSet"]
)
UserViewSet = user_viewsets["UserViewSet"]

# Real-time ViewSets
realtime_viewsets = register_optional_viewsets(
    "realtime_features", "personal_finance.realtime.api", ["RealtimeViewSet"]
)
RealtimeViewSet = realtime_viewsets["RealtimeViewSet"]

# Tax management ViewSets
tax_viewsets = register_optional_viewsets(
    "tax_features",
    "personal_finance.tax.views",
    [
        "TaxYearViewSet",
        "TaxLotViewSet",
        "CapitalGainLossViewSet",
        "DividendIncomeViewSet",
        "TaxLossHarvestingOpportunityViewSet",
        "TaxOptimizationRecommendationViewSet",
        "TaxReportViewSet",
        "TaxAnalyticsViewSet",
    ],
)
TaxYearViewSet = tax_viewsets["TaxYearViewSet"]
TaxLotViewSet = tax_viewsets["TaxLotViewSet"]
CapitalGainLossViewSet = tax_viewsets["CapitalGainLossViewSet"]
DividendIncomeViewSet = tax_viewsets["DividendIncomeViewSet"]
TaxLossHarvestingOpportunityViewSet = tax_viewsets[
    "TaxLossHarvestingOpportunityViewSet"
]
TaxOptimizationRecommendationViewSet = tax_viewsets[
    "TaxOptimizationRecommendationViewSet"
]
TaxReportViewSet = tax_viewsets["TaxReportViewSet"]
TaxAnalyticsViewSet = tax_viewsets["TaxAnalyticsViewSet"]

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
