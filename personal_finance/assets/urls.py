from django.urls import path
from . import views

app_name = "assets"

urlpatterns = [
    # Asset URLs
    path("", views.AssetListView.as_view(), name="list"),  # Keep old name for backward compatibility
    path("", views.AssetListView.as_view(), name="asset_list"),  # Also provide new descriptive name
    path("assets/add/", views.AssetCreateView.as_view(), name="asset_add"),
    path("assets/<int:pk>/", views.AssetDetailView.as_view(), name="asset_detail"),
    path("assets/<int:pk>/edit/", views.AssetUpdateView.as_view(), name="asset_edit"),
    path("assets/<int:pk>/delete/", views.AssetDeleteView.as_view(), name="asset_delete"),
    
    # Portfolio URLs
    path("portfolios/", views.PortfolioListView.as_view(), name="portfolio_list"),
    path("portfolios/add/", views.PortfolioCreateView.as_view(), name="portfolio_add"),
    path("portfolios/<int:pk>/", views.PortfolioDetailView.as_view(), name="portfolio_detail"),
    path("portfolios/<int:pk>/edit/", views.PortfolioUpdateView.as_view(), name="portfolio_edit"),
    path("portfolios/<int:pk>/delete/", views.PortfolioDeleteView.as_view(), name="portfolio_delete"),
    
    # Holding URLs  
    path("holdings/", views.HoldingListView.as_view(), name="holding_list"),
    path("holdings/add/", views.HoldingCreateView.as_view(), name="holding_add"),
    path("holdings/<int:pk>/", views.HoldingDetailView.as_view(), name="holding_detail"),
    path("holdings/<int:pk>/edit/", views.HoldingUpdateView.as_view(), name="holding_edit"),
    path("holdings/<int:pk>/delete/", views.HoldingDeleteView.as_view(), name="holding_delete"),
]
