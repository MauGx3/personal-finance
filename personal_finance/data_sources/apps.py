"""Data sources app configuration."""

from django.apps import AppConfig


class DataSourcesConfig(AppConfig):
    """Configuration for the data sources app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'personal_finance.data_sources'
    verbose_name = 'Financial Data Sources'