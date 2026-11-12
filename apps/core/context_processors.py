from django.conf import settings


def site(request) -> dict:
    return {"BASE_CURRENCY": settings.BASE_CURRENCY}
