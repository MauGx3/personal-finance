"""Portfolio admin interface."""

from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html

from .models import Portfolio, Position, Transaction, PortfolioSnapshot


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    """Admin interface for Portfolio model."""
    
    list_display = ['name', 'user', 'total_value_display', 'total_return_display', 'is_active', 'created']
    list_filter = ['is_active', 'created', 'user']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['created', 'modified', 'total_value_display', 'total_return_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'is_active')
        }),
        ('Performance', {
            'fields': ('total_value_display', 'total_return_display'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def total_value_display(self, obj):
        """Display formatted total portfolio value."""
        value = obj.total_value
        if value:
            return format_html('<strong>${:,.2f}</strong>', value)
        return '-'
    total_value_display.short_description = 'Total Value'
    
    def total_return_display(self, obj):
        """Display formatted total return with color coding."""
        return_pct = obj.total_return_percentage
        if return_pct is not None:
            color = 'green' if return_pct >= 0 else 'red'
            return format_html(
                '<span style="color: {};">{:+.2f}%</span>',
                color, return_pct
            )
        return '-'
    total_return_display.short_description = 'Total Return'


class TransactionInline(admin.TabularInline):
    """Inline admin for transactions."""
    model = Transaction
    extra = 0
    readonly_fields = ['created', 'modified', 'total_value']
    fields = ['transaction_type', 'quantity', 'price', 'fees', 'transaction_date', 'total_value', 'notes']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """Admin interface for Position model."""
    
    list_display = [
        'portfolio', 'asset_symbol', 'quantity', 'average_cost', 
        'current_value_display', 'unrealized_return_display', 'is_active'
    ]
    list_filter = ['is_active', 'portfolio__user', 'asset__asset_type', 'first_purchase_date']
    search_fields = ['asset__symbol', 'asset__name', 'portfolio__name']
    readonly_fields = [
        'created', 'modified', 'current_value_display', 
        'unrealized_return_display', 'total_cost_basis'
    ]
    inlines = [TransactionInline]
    
    fieldsets = (
        ('Position Details', {
            'fields': ('portfolio', 'asset', 'quantity', 'average_cost', 'first_purchase_date')
        }),
        ('Performance', {
            'fields': ('current_value_display', 'total_cost_basis', 'unrealized_return_display'),
            'classes': ('collapse',)
        }),
        ('Status & Notes', {
            'fields': ('is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def asset_symbol(self, obj):
        """Display asset symbol."""
        return obj.asset.symbol
    asset_symbol.short_description = 'Symbol'
    asset_symbol.admin_order_field = 'asset__symbol'
    
    def current_value_display(self, obj):
        """Display formatted current value."""
        value = obj.current_value
        return format_html('<strong>${:,.2f}</strong>', value)
    current_value_display.short_description = 'Current Value'
    
    def unrealized_return_display(self, obj):
        """Display formatted unrealized return with color coding."""
        return_pct = obj.unrealized_return_percentage
        if return_pct is not None:
            color = 'green' if return_pct >= 0 else 'red'
            return format_html(
                '<span style="color: {};">{:+.2f}%</span>',
                color, return_pct
            )
        return '-'
    unrealized_return_display.short_description = 'Unrealized Return'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction model."""
    
    list_display = [
        'position_portfolio', 'position_asset', 'transaction_type', 
        'quantity', 'price', 'total_value', 'transaction_date'
    ]
    list_filter = ['transaction_type', 'transaction_date', 'position__portfolio__user']
    search_fields = ['position__asset__symbol', 'position__portfolio__name']
    readonly_fields = ['created', 'modified', 'total_value']
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('position', 'transaction_type', 'quantity', 'price', 'fees', 'transaction_date')
        }),
        ('Calculated Values', {
            'fields': ('total_value',),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def position_portfolio(self, obj):
        """Display portfolio name."""
        return obj.position.portfolio.name
    position_portfolio.short_description = 'Portfolio'
    position_portfolio.admin_order_field = 'position__portfolio__name'
    
    def position_asset(self, obj):
        """Display asset symbol."""
        return obj.position.asset.symbol
    position_asset.short_description = 'Asset'
    position_asset.admin_order_field = 'position__asset__symbol'


@admin.register(PortfolioSnapshot)
class PortfolioSnapshotAdmin(admin.ModelAdmin):
    """Admin interface for PortfolioSnapshot model."""
    
    list_display = [
        'portfolio', 'snapshot_date', 'total_value', 
        'return_percentage_display', 'cash_balance'
    ]
    list_filter = ['snapshot_date', 'portfolio__user']
    search_fields = ['portfolio__name', 'portfolio__user__username']
    readonly_fields = ['created', 'modified', 'return_percentage_display', 'total_return']
    date_hierarchy = 'snapshot_date'
    
    fieldsets = (
        ('Snapshot Details', {
            'fields': ('portfolio', 'snapshot_date', 'total_value', 'total_cost_basis', 'cash_balance')
        }),
        ('Calculated Values', {
            'fields': ('total_return', 'return_percentage_display'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def return_percentage_display(self, obj):
        """Display formatted return percentage with color coding."""
        return_pct = obj.return_percentage
        if return_pct is not None:
            color = 'green' if return_pct >= 0 else 'red'
            return format_html(
                '<span style="color: {};">{:+.2f}%</span>',
                color, return_pct
            )
        return '-'
    return_percentage_display.short_description = 'Return %'