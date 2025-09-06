from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from personal_finance.assets.api.views import AssetViewSet
from personal_finance.assets.api.views import HoldingViewSet
from personal_finance.assets.api.views import PortfolioViewSet
from personal_finance.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("assets", AssetViewSet)
router.register("portfolios", PortfolioViewSet)
router.register("holdings", HoldingViewSet)


app_name = "api"
urlpatterns = router.urls
