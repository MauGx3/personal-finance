"""Django app configuration for visualization module."""

from django.apps import AppConfig


class VisualizationConfig(AppConfig):
    """Configuration for the visualization app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'personal_finance.visualization'
    verbose_name = 'Financial Visualization'