from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("sync-prices/", views.sync_prices, name="sync-prices"),
    path("healthz/", views.health, name="health"),
]
