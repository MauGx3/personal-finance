from django.contrib import admin

from . import models


@admin.register(models.Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("symbol", "name", "asset_type", "currency", "is_active")
    search_fields = ("symbol", "name", "isin", "cusip")
    list_filter = ("asset_type", "is_active")


@admin.register(models.Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "is_default")
    search_fields = ("name", "user__username", "user__name")


@admin.register(models.Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = ("user", "asset", "portfolio", "quantity", "average_price")
    search_fields = ("user__username", "asset__symbol", "asset__name")
    list_filter = ("currency",)
