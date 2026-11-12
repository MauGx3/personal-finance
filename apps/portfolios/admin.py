from django.contrib import admin

from .models import Holding, Portfolio, Transaction


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "is_default")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "trade_date",
        "kind",
        "asset",
        "quantity",
        "price",
        "amount",
        "portfolio",
        "broker",
    )
    list_filter = ("kind", "portfolio", "broker")
    search_fields = ("asset__ticker", "notes")
    date_hierarchy = "trade_date"
    autocomplete_fields = ("asset",)


@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    """Read-only: holdings are derived from transactions."""

    list_display = (
        "asset",
        "portfolio",
        "quantity",
        "average_price",
        "realized_gain",
        "ledger_error",
    )
    list_filter = ("portfolio",)

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False
