from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter
import importlib
import logging


# Helper: lazy-import a symbol from a module path. Returns the attribute or
# None on failure and logs a debug message. This keeps URLConf import-time
# light-weight in minimal runtime images where optional deps may be missing.
def _lazy_import(module_path: str, symbol: str):
    try:
        module = importlib.import_module(module_path)
        return getattr(module, symbol)
    except Exception:  # pragma: no cover - runtime resilience
        logging.exception("lazy import failed: %s.%s", module_path, symbol)
        return None


router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# User management (lazy import)
UserViewSet = _lazy_import("personal_finance.users.api.views", "UserViewSet")
if UserViewSet:
    router.register("users", UserViewSet)

# Asset management (lazy import)
AssetViewSet = _lazy_import(
    "personal_finance.assets.api.views", "AssetViewSet"
)
HoldingViewSet = _lazy_import(
    "personal_finance.assets.api.views", "HoldingViewSet"
)
LegacyPortfolioViewSet = _lazy_import(
    "personal_finance.assets.api.views", "PortfolioViewSet"
)
PriceHistoryViewSet = _lazy_import(
    "personal_finance.assets.api.views", "PriceHistoryViewSet"
)

if AssetViewSet:
    router.register("assets", AssetViewSet)
else:  # pragma: no cover - runtime resilience
    logging.debug(
        "AssetViewSet not available; skipping assets router registration"
    )

if PriceHistoryViewSet:
    router.register("price-history", PriceHistoryViewSet)
else:  # pragma: no cover - optional
    logging.debug("PriceHistoryViewSet not available; skipping price-history")

# Portfolio management (new comprehensive system)
# Portfolio management (lazy import)
PortfolioViewSet = _lazy_import(
    "personal_finance.portfolios.api.views", "PortfolioViewSet"
)
PositionViewSet = _lazy_import(
    "personal_finance.portfolios.api.views", "PositionViewSet"
)
TransactionViewSet = _lazy_import(
    "personal_finance.portfolios.api.views", "TransactionViewSet"
)
PortfolioSnapshotViewSet = _lazy_import(
    "personal_finance.portfolios.api.views", "PortfolioSnapshotViewSet"
)

if PortfolioViewSet:
    router.register("portfolios", PortfolioViewSet)
if PositionViewSet:
    router.register("positions", PositionViewSet)
if TransactionViewSet:
    router.register("transactions", TransactionViewSet)
if PortfolioSnapshotViewSet:
    router.register("portfolio-snapshots", PortfolioSnapshotViewSet)

# Legacy endpoints for backward compatibility
if LegacyPortfolioViewSet:
    router.register("legacy-portfolios", LegacyPortfolioViewSet)
else:  # pragma: no cover - optional
    logging.debug(
        "LegacyPortfolioViewSet not available; skipping legacy-portfolios"
    )

if HoldingViewSet:
    router.register("holdings", HoldingViewSet)
else:  # pragma: no cover - optional
    logging.debug(
        "HoldingViewSet not available; skipping holdings registration"
    )

# Real-time WebSocket management
RealtimeViewSet = _lazy_import(
    "personal_finance.realtime.api", "RealtimeViewSet"
)
if RealtimeViewSet:
    router.register("realtime", RealtimeViewSet, basename="realtime")

# Tax reporting and optimization
TaxYearViewSet = _lazy_import("personal_finance.tax.views", "TaxYearViewSet")
TaxLotViewSet = _lazy_import("personal_finance.tax.views", "TaxLotViewSet")
CapitalGainLossViewSet = _lazy_import(
    "personal_finance.tax.views", "CapitalGainLossViewSet"
)
DividendIncomeViewSet = _lazy_import(
    "personal_finance.tax.views", "DividendIncomeViewSet"
)
TaxLossHarvestingOpportunityViewSet = _lazy_import(
    "personal_finance.tax.views", "TaxLossHarvestingOpportunityViewSet"
)
TaxOptimizationRecommendationViewSet = _lazy_import(
    "personal_finance.tax.views", "TaxOptimizationRecommendationViewSet"
)
TaxReportViewSet = _lazy_import(
    "personal_finance.tax.views", "TaxReportViewSet"
)
TaxAnalyticsViewSet = _lazy_import(
    "personal_finance.tax.views", "TaxAnalyticsViewSet"
)

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
