"""Look up the configured price provider."""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .base import PriceProvider


def get_provider(name: str | None = None) -> PriceProvider:
    name = name or settings.PRICE_PROVIDER
    try:
        path = settings.PRICE_PROVIDERS[name]
    except KeyError as exc:
        known = ", ".join(sorted(settings.PRICE_PROVIDERS))
        raise ImproperlyConfigured(f"Unknown price provider {name!r}. Known: {known}.") from exc
    return import_string(path)()
