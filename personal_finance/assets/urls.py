from django.urls import path
from .views import AssetsView

app_name = "assets"
urlpatterns = [
    path("", AssetsView.as_view(), name="list"),
]