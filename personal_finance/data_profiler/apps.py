"""Django app configuration for data profiler module."""

from django.apps import AppConfig


class DataProfilerConfig(AppConfig):
    """Configuration for the data profiler app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'personal_finance.data_profiler'
    verbose_name = 'Data Profiler'
    
    def ready(self):
        """Initialize the app when Django starts."""
        # Import any signals or perform initialization here
        pass