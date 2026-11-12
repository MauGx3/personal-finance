from django.apps import AppConfig


class PortfoliosConfig(AppConfig):
    name = "apps.portfolios"
    label = "portfolios"

    def ready(self) -> None:
        from . import signals  # noqa: F401
