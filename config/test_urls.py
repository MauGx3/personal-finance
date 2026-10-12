"""
Simple URL configuration for testing.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def health_check(request):
    """Simple health check for tests."""
    return JsonResponse({"status": "test_ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),
]
