from django.contrib import admin

from .models import FxRate, PriceQuote


@admin.register(PriceQuote)
class PriceQuoteAdmin(admin.ModelAdmin):
    list_display = ("asset", "day", "close", "source")
    list_filter = ("source",)
    search_fields = ("asset__ticker",)
    date_hierarchy = "day"


@admin.register(FxRate)
class FxRateAdmin(admin.ModelAdmin):
    list_display = ("base", "quote", "day", "rate", "source")
    list_filter = ("base", "quote")
    date_hierarchy = "day"
