"""Assets admin configuration."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Asset, Holding, Portfolio


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """Admin configuration for Asset model."""

    list_display = [
        "ticker",
        "name",
        "asset_type",
        "country",
        "market",
        "currency",
        "is_active",
        "created_at",
    ]
    list_filter = [
        "asset_type",
        "country",
        "market",
        "currency",
        "is_active",
        "sector",
        "industry",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "ticker",
        "name",
        "isin",
        "cusip",
        "sedol",
        "description",
    ]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["ticker", "name"]

    fieldsets = [
        (
            _("Basic Information"),
            {
                "fields": [
                    "ticker",
                    "name",
                    "asset_type",
                    "description",
                ]
            },
        ),
        (
            _("Location & Market"),
            {
                "fields": [
                    "country",
                    "market",
                    "currency",
                ]
            },
        ),
        (
            _("Identification"),
            {
                "fields": [
                    "isin",
                    "cusip",
                    "sedol",
                ]
            },
        ),
        (
            _("Classification"),
            {
                "fields": [
                    "sector",
                    "industry",
                ]
            },
        ),
        (
            _("Status & Metadata"),
            {
                "fields": [
                    "is_active",
                    "metadata",
                ]
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": [
                    "created_at",
                    "updated_at",
                ],
                "classes": ["collapse"],
            },
        ),
    ]

    def get_queryset(self, request):
        """Optimize queryset for admin list view."""
        return super().get_queryset(request).select_related()


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    """Admin configuration for Portfolio model."""

    list_display = [
        "name",
        "user",
        "is_default",
        "is_active",
        "holdings_count",
        "total_value",
        "created_at",
    ]
    list_filter = [
        "is_default",
        "is_active",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "name",
        "description",
        "user__email",
        "user__username",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
        "holdings_count",
        "total_value",
    ]
    ordering = ["-is_default", "name"]

    fieldsets = [
        (
            _("Basic Information"),
            {
                "fields": [
                    "user",
                    "name",
                    "description",
                ]
            },
        ),
        (
            _("Settings"),
            {
                "fields": [
                    "is_default",
                    "is_active",
                ]
            },
        ),
        (
            _("Statistics"),
            {
                "fields": [
                    "holdings_count",
                    "total_value",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": [
                    "created_at",
                    "updated_at",
                ],
                "classes": ["collapse"],
            },
        ),
    ]

    def get_queryset(self, request):
        """Optimize queryset for admin list view."""
        return super().get_queryset(request).select_related("user")


@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    """Admin configuration for Holding model."""

    list_display = [
        "user",
        "asset",
        "portfolio",
        "quantity",
        "average_price",
        "currency",
        "total_cost_basis",
        "current_value",
        "unrealized_gain_loss",
        "is_active",
        "created_at",
    ]
    list_filter = [
        "currency",
        "is_active",
        "portfolio",
        "asset__asset_type",
        "asset__country",
        "asset__market",
        "created_at",
        "updated_at",
        "acquired_at",
        "last_transaction_at",
    ]
    search_fields = [
        "user__email",
        "user__username",
        "asset__ticker",
        "asset__name",
        "portfolio__name",
        "notes",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
        "total_cost_basis",
        "current_value",
        "unrealized_gain_loss",
    ]
    ordering = ["-created_at"]
    raw_id_fields = ["user", "asset", "portfolio"]

    fieldsets = [
        (
            _("Ownership"),
            {
                "fields": [
                    "user",
                    "asset",
                    "portfolio",
                ]
            },
        ),
        (
            _("Position Details"),
            {
                "fields": [
                    "quantity",
                    "average_price",
                    "currency",
                ]
            },
        ),
        (
            _("Transaction History"),
            {
                "fields": [
                    "acquired_at",
                    "last_transaction_at",
                ]
            },
        ),
        (
            _("Financial Summary"),
            {
                "fields": [
                    "total_cost_basis",
                    "current_value",
                    "unrealized_gain_loss",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            _("Status & Notes"),
            {
                "fields": [
                    "is_active",
                    "notes",
                    "metadata",
                ]
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": [
                    "created_at",
                    "updated_at",
                ],
                "classes": ["collapse"],
            },
        ),
    ]

    def get_queryset(self, request):
        """Optimize queryset for admin list view."""
        return (
            super()
            .get_queryset(request)
            .select_related("user", "asset", "portfolio")
        )
