from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api"

router = DefaultRouter()
router.register("assets", views.AssetViewSet, basename="asset")
router.register("portfolios", views.PortfolioViewSet, basename="portfolio")
router.register("transactions", views.TransactionViewSet, basename="transaction")
router.register("holdings", views.HoldingViewSet, basename="holding")

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
    path("", include(router.urls)),
]
