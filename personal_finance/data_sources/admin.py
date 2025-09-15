"""Admin interface for data sources import functionality."""

from django.contrib import admin
from .models import DocumentImport


@admin.register(DocumentImport)
class DocumentImportAdmin(admin.ModelAdmin):
    """Admin interface for DocumentImport model."""

    list_display = [
        "original_filename",
        "document_type_display",
        "user",
        "status",
        "imported_transactions_count",
        "created",
    ]

    list_filter = [
        "document_type",
        "status",
        "created",
        "modified",
    ]

    search_fields = [
        "original_filename",
        "user__username",
        "user__email",
    ]

    readonly_fields = [
        "created",
        "modified",
        "imported_transactions_count",
        "processing_log",
    ]

    fieldsets = (
        (
            "Import Details",
            {
                "fields": (
                    "user",
                    "document_type",
                    "original_filename",
                    "file_path",
                    "status",
                )
            },
        ),
        (
            "Results",
            {
                "fields": (
                    "imported_transactions_count",
                    "error_message",
                )
            },
        ),
        (
            "Processing Information",
            {"fields": ("processing_log",), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created",
                    "modified",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Document Type")
    def document_type_display(self, obj):
        """Display human-readable document type."""
        return obj.get_document_type_display()

    def has_add_permission(self, request):
        """Disable manual creation of import records."""
        return False

    def has_change_permission(self, request, obj=None):
        """Allow viewing but limit editing."""
        return True

    def get_readonly_fields(self, request, obj=None):
        """Make most fields readonly for existing objects."""
        if obj:  # Editing an existing object
            return self.readonly_fields + [
                "user",
                "document_type",
                "original_filename",
                "file_path",
            ]
        return self.readonly_fields
