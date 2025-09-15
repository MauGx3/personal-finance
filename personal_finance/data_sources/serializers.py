"""Serializers for data sources import functionality."""

from rest_framework import serializers
from .models import DocumentImport


class DocumentImportSerializer(serializers.ModelSerializer):
    """Serializer for DocumentImport model."""
    
    document_type_display = serializers.CharField(
        source='get_document_type_display', 
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = DocumentImport
        fields = [
            'id',
            'document_type',
            'document_type_display',
            'original_filename',
            'status',
            'status_display',
            'error_message',
            'imported_transactions_count',
            'processing_log',
            'created',
            'modified'
        ]
        read_only_fields = [
            'id',
            'status',
            'error_message', 
            'imported_transactions_count',
            'processing_log',
            'created',
            'modified'
        ]


class DocumentUploadRequestSerializer(serializers.Serializer):
    """Serializer for document upload requests."""
    
    file = serializers.FileField(
        help_text='Document file to import'
    )
    document_type = serializers.ChoiceField(
        choices=DocumentImport.DOCUMENT_TYPES,
        help_text='Type of document being imported'
    )
    
    def validate_file(self, value):
        """Validate uploaded file."""
        # Check file size (limit to 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f'File size too large. Maximum size is {max_size // (1024*1024)}MB'
            )
        
        # Check file extension
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.pdf']
        file_ext = value.name.lower().split('.')[-1] if '.' in value.name else ''
        if f'.{file_ext}' not in allowed_extensions:
            raise serializers.ValidationError(
                f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}'
            )
        
        return value


class DocumentImportStatsSerializer(serializers.Serializer):
    """Serializer for import statistics."""
    
    total_imports = serializers.IntegerField()
    completed_imports = serializers.IntegerField() 
    failed_imports = serializers.IntegerField()
    pending_imports = serializers.IntegerField()
    total_transactions_imported = serializers.IntegerField()
    
    by_document_type = serializers.DictField(
        child=serializers.IntegerField(),
        help_text='Count of imports by document type'
    )
    
    recent_imports = DocumentImportSerializer(
        many=True,
        help_text='5 most recent imports'
    )