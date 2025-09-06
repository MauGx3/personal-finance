from django.urls import path

from .views import AssetCreateView
from .views import AssetDeleteView
from .views import AssetDetailView
from .views import AssetListView
from .views import AssetsView
from .views import AssetUpdateView

app_name = "assets"

urlpatterns = [
    # Root assets page (used by site: /assets/)
    path("", AssetsView.as_view(), name="list"),
    path("add/", AssetCreateView.as_view(), name="asset_add"),
    path("<int:pk>/", AssetDetailView.as_view(), name="asset_detail"),
    path("<int:pk>/edit/", AssetUpdateView.as_view(), name="asset_edit"),
    path("<int:pk>/delete/", AssetDeleteView.as_view(), name="asset_delete"),
    # keep a secondary listing route for the detailed asset list
    path("all/", AssetListView.as_view(), name="asset_list"),
]
