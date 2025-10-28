"""
URL configuration for Personal Finance project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Core app (includes index, health checks)
    path("", include("apps.core.urls")),
    # API
    path("api/", include("apps.api.urls")),
    # Users
    path("users/", include("apps.users.urls")),
    # Allauth
    path("accounts/", include("allauth.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
