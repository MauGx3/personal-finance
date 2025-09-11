"""URL patterns for visualization dashboard."""

from django.urls import path
from . import views

app_name = 'visualization'

urlpatterns = [
    # Dashboard views
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('portfolio/<int:portfolio_id>/', views.PortfolioDetailView.as_view(), name='portfolio_detail'),
    
    # Chart API endpoints
    path('api/portfolio/<int:portfolio_id>/performance/', 
         views.portfolio_performance_chart_api, 
         name='portfolio_performance_api'),
    
    path('api/portfolio/<int:portfolio_id>/allocation/', 
         views.portfolio_allocation_chart_api, 
         name='portfolio_allocation_api'),
    
    path('api/portfolio/<int:portfolio_id>/risk/', 
         views.portfolio_risk_metrics_chart_api, 
         name='portfolio_risk_api'),
    
    path('api/asset/<int:asset_id>/price/', 
         views.asset_price_chart_api, 
         name='asset_price_api'),
    
    path('api/dashboard/summary/', 
         views.dashboard_summary_api, 
         name='dashboard_summary_api'),
]