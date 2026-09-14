from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import JsonResponse
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token

from loguru import logger


def readiness_check(request):
    """Readiness probe that performs a lightweight DB ping.

    This endpoint is suitable for determining whether the app has
    successfully connected to required services (e.g., Postgres). It may be
    slower if DB is under load, so keep liveness separate.
    """
    try:
        # Basic Django health check: ensure DB responds
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse(
            {
                "status": "ready",
                "service": "personal-finance-django",
            }
        )
    except Exception:
        logger.exception("Readiness check failed")
        return JsonResponse(
            {"status": "not_ready", "service": "personal-finance-django"},
            status=503,
        )


def liveness_check(request):
    """Liveness probe that responds quickly without touching external services.

    Use this for simple container liveness checks; it should be fast and
    deterministic.
    """
    return JsonResponse(
        {"status": "alive", "service": "personal-finance-django"}
    )


urlpatterns = [
    path(
        "", TemplateView.as_view(template_name="pages/home.html"), name="home"
    ),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Liveness and readiness endpoints
    # Liveness: quick check that the process is alive (no DB hit)
    path("health/", liveness_check, name="health"),
    # Readiness: ensures DB and other services are reachable
    path("ready/", readiness_check, name="ready"),
    # Leapcell probes 0.0.0.0:$PORT/kaithhealth by default; expose a
    # fast alias so the platform health check succeeds.
    path("kaithhealth", liveness_check, name="kaithhealth"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("personal_finance.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path(
        "assets/", include("personal_finance.assets.urls", namespace="assets")
    ),
    path(
        "dashboard/",
        include(
            "personal_finance.visualization.urls", namespace="visualization"
        ),
    ),
    path(
        "realtime/",
        include("personal_finance.realtime.urls", namespace="realtime"),
    ),
    # ...
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local websockets
    urlpatterns += staticfiles_urlpatterns()

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("api/auth-token/", obtain_auth_token, name="obtain_auth_token"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
