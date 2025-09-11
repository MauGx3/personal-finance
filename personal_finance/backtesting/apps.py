"""Backtesting Django app configuration."""

from django.apps import AppConfig


class BacktestingConfig(AppConfig):
    """Django app configuration for backtesting module."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "personal_finance.backtesting"
    verbose_name = "Backtesting Engine"
    
    def ready(self):
        """Initialize app when Django starts."""
        pass