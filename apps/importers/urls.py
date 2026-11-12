from django.urls import path

from . import views

app_name = "importers"

urlpatterns = [
    path("", views.import_view, name="import"),
    path("<int:pk>/undo/", views.undo_view, name="undo"),
]
