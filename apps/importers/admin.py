from django.contrib import admin

from .models import ImportBatch


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = (
        "filename",
        "portfolio",
        "parser",
        "created_count",
        "skipped_count",
        "created_at",
    )
    readonly_fields = ("warnings",)
