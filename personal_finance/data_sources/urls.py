"""URL patterns for data sources import functionality."""

from django.urls import path
from .import_views import (
    DocumentUploadView,
    DocumentImportListView, 
    DocumentImportDetailView,
    supported_document_types,
    retry_import
)

app_name = 'data_sources'

urlpatterns = [
    # Document import endpoints
    path('import/upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('import/', DocumentImportListView.as_view(), name='import-list'),
    path('import/<int:import_id>/', DocumentImportDetailView.as_view(), name='import-detail'),
    path('import/<int:import_id>/retry/', retry_import, name='import-retry'),
    
    # Metadata endpoints
    path('import/types/', supported_document_types, name='supported-types'),
]