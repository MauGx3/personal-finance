from django.urls import path
from . import views

app_name = "assets"

urlpatterns = [
    path("", views.AssetListView.as_view(), name="asset_list"),
    path("add/", views.AssetCreateView.as_view(), name="asset_add"),
    path("<int:pk>/", views.AssetDetailView.as_view(), name="asset_detail"),
    path("<int:pk>/edit/", views.AssetUpdateView.as_view(), name="asset_edit"),
    path("<int:pk>/delete/", views.AssetDeleteView.as_view(), name="asset_delete"),
]
from django.urls import path
from .views import AssetsView

app_name = "assets"
urlpatterns = [
    path("", AssetsView.as_view(), name="list"),
]
