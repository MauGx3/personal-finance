"""URL configuration for backtesting app."""

from django.urls import include, path

app_name = "backtesting"

urlpatterns = [
    path("api/", include("personal_finance.backtesting.api.urls")),
]
