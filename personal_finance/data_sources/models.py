"""Data source import models."""

from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel

User = get_user_model()


class DocumentImport(TimeStampedModel):
    """Track document import operations."""
    
    DOCUMENT_TYPES = [
        ('BANCO_INTER_MONTHLY_REPORT', 'Banco Inter - Relatório Mensal de Investimentos'),
        ('BANCO_INTER_BROKERAGE_NOTE', 'Banco Inter - Nota de Corretagem'),
        ('BANCO_INTER_EXTRACT', 'Banco Inter - Extrato'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_imports',
        help_text='User who initiated the import'
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES,
        help_text='Type of document being imported'
    )
    original_filename = models.CharField(
        max_length=255,
        help_text='Original filename of uploaded document'
    )
    file_path = models.CharField(
        max_length=500,
        help_text='Path to stored file'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text='Import status'
    )
    error_message = models.TextField(
        blank=True,
        help_text='Error message if import failed'
    )
    imported_transactions_count = models.IntegerField(
        default=0,
        help_text='Number of transactions successfully imported'
    )
    processing_log = models.JSONField(
        default=dict,
        blank=True,
        help_text='Detailed processing log and metadata'
    )

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['document_type']),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.original_filename} ({self.status})"