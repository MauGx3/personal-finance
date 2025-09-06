from django.urls import path

from .views import AssetCreateView
from .views import AssetDeleteView
from .views import AssetDetailView
from .views import AssetListView
from .views import AssetsView
from .views import AssetUpdateView

app_name = "assets"

urlpatterns = [
    path("", AssetListView.as_view(), name="asset_list"),
    path("add/", AssetCreateView.as_view(), name="asset_add"),
    path("<int:pk>/", AssetDetailView.as_view(), name="asset_detail"),
    path("<int:pk>/edit/", AssetUpdateView.as_view(), name="asset_edit"),
    path("<int:pk>/delete/", AssetDeleteView.as_view(), name="asset_delete"),
    path("all/", AssetsView.as_view(), name="list"),
]
