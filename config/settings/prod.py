"""Production settings (Docker on a NAS or any small server)."""

from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

if SECRET_KEY.startswith("django-insecure"):
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY to a long random value.")

# The app usually sits behind a reverse proxy on the home network. Cookies are
# only marked secure when the proxy terminates TLS (set HTTPS=true).
HTTPS = env.bool("HTTPS", default=False)
SESSION_COOKIE_SECURE = HTTPS
CSRF_COOKIE_SECURE = HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if HTTPS else None
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
