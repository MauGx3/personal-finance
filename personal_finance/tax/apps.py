"""Tax reporting and optimization app configuration."""

from django.apps import AppConfig


class TaxConfig(AppConfig):
    """Configuration for the tax app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'personal_finance.tax'
    verbose_name = 'Tax Reporting'