"""Portfolio management app configuration."""

from django.apps import AppConfig


class PortfoliosConfig(AppConfig):
    """Configuration for the portfolios app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'personal_finance.portfolios'
    verbose_name = 'Portfolio Management'