from django.urls import path

from . import views

app_name = "assets"

urlpatterns = [path("<int:pk>/", views.AssetDetailView.as_view(), name="detail")]
