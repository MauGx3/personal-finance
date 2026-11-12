from django.contrib import admin

from .models import Asset


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("ticker", "exchange", "name", "asset_class", "currency", "is_active")
    list_filter = ("exchange", "asset_class", "currency", "is_active")
    search_fields = ("ticker", "name", "isin")
    list_editable = ("asset_class",)
