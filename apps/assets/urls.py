"""Assets app URLs."""

from django.urls import path

from . import views

app_name = "assets"

urlpatterns = [
    path("portfolio/", views.portfolio_detail, name="portfolio-detail"),
    path("portfolio/<int:portfolio_id>/", views.portfolio_detail, name="portfolio-detail-id"),
]
