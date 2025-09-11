"""Django admin configuration for tax models."""

from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import (
    TaxYear, TaxLot, CapitalGainLoss, DividendIncome,
    TaxLossHarvestingOpportunity, TaxOptimizationRecommendation, TaxReport
)


@admin.register(TaxYear)
class TaxYearAdmin(admin.ModelAdmin):
    """Admin interface for TaxYear model."""
    
    list_display = [
        'year', 'filing_deadline', 'standard_deduction_single', 
        'standard_deduction_married', 'short_term_capital_gains_rate'
    ]
    list_filter = ['year']
    search_fields = ['year']
    ordering = ['-year']


@admin.register(TaxLot)
class TaxLotAdmin(admin.ModelAdmin):
    """Admin interface for TaxLot model."""
    
    list_display = [
        'asset_symbol', 'acquisition_date', 'remaining_quantity', 
        'cost_basis_per_share', 'current_value_display', 'unrealized_gain_loss_display',
        'is_long_term', 'created_at'
    ]
    list_filter = [
        'acquisition_date', 'position__asset__asset_type', 
        'position__portfolio__user', 'created_at'
    ]
    search_fields = [
        'position__asset__symbol', 'position__asset__name',
        'position__portfolio__user__username'
    ]
    readonly_fields = [
        'total_cost_basis', 'current_value', 'unrealized_gain_loss', 
        'is_long_term', 'created_at', 'updated_at'
    ]
    raw_id_fields = ['position', 'transaction']
    ordering = ['-acquisition_date']
    
    def asset_symbol(self, obj):
        """Display asset symbol."""
        return obj.position.asset.symbol
    asset_symbol.short_description = 'Symbol'
    asset_symbol.admin_order_field = 'position__asset__symbol'
    
    def current_value_display(self, obj):
        """Display current value with formatting."""
        value = obj.current_value
        return f"${value:,.2f}" if value else "N/A"
    current_value_display.short_description = 'Current Value'
    
    def unrealized_gain_loss_display(self, obj):
        """Display unrealized gain/loss with color coding."""
        gain_loss = obj.unrealized_gain_loss
        if gain_loss > 0:
            return format_html(
                '<span style="color: green;">${:,.2f}</span>', 
                gain_loss
            )
        elif gain_loss < 0:
            return format_html(
                '<span style="color: red;">${:,.2f}</span>', 
                gain_loss
            )
        return "${:,.2f}".format(gain_loss)
    unrealized_gain_loss_display.short_description = 'Unrealized Gain/Loss'


@admin.register(CapitalGainLoss)
class CapitalGainLossAdmin(admin.ModelAdmin):
    """Admin interface for CapitalGainLoss model."""
    
    list_display = [
        'asset_symbol', 'sale_date', 'term', 'quantity_sold',
        'gross_proceeds_display', 'total_cost_basis_display', 
        'gain_loss_amount_display', 'wash_sale_adjustment_display'
    ]
    list_filter = [
        'sale_date', 'term', 'user', 'tax_year__year',
        'position__asset__asset_type'
    ]
    search_fields = [
        'position__asset__symbol', 'position__asset__name',
        'user__username'
    ]
    readonly_fields = [
        'gain_loss_amount', 'created_at', 'updated_at'
    ]
    raw_id_fields = ['user', 'position', 'transaction', 'tax_lot']
    date_hierarchy = 'sale_date'
    ordering = ['-sale_date']
    
    def asset_symbol(self, obj):
        """Display asset symbol."""
        return obj.position.asset.symbol
    asset_symbol.short_description = 'Symbol'
    asset_symbol.admin_order_field = 'position__asset__symbol'
    
    def gross_proceeds_display(self, obj):
        """Display gross proceeds formatted."""
        return f"${obj.gross_proceeds:,.2f}"
    gross_proceeds_display.short_description = 'Gross Proceeds'
    gross_proceeds_display.admin_order_field = 'gross_proceeds'
    
    def total_cost_basis_display(self, obj):
        """Display total cost basis formatted."""
        return f"${obj.total_cost_basis:,.2f}"
    total_cost_basis_display.short_description = 'Cost Basis'
    total_cost_basis_display.admin_order_field = 'total_cost_basis'
    
    def gain_loss_amount_display(self, obj):
        """Display gain/loss with color coding."""
        amount = obj.gain_loss_amount
        if amount > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">${:,.2f}</span>', 
                amount
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">${:,.2f}</span>', 
                amount
            )
    gain_loss_amount_display.short_description = 'Gain/Loss'
    gain_loss_amount_display.admin_order_field = 'gain_loss_amount'
    
    def wash_sale_adjustment_display(self, obj):
        """Display wash sale adjustment."""
        if obj.wash_sale_adjustment:
            return format_html(
                '<span style="color: orange;">${:,.2f}</span>', 
                obj.wash_sale_adjustment
            )
        return "-"
    wash_sale_adjustment_display.short_description = 'Wash Sale Adj.'


@admin.register(DividendIncome)
class DividendIncomeAdmin(admin.ModelAdmin):
    """Admin interface for DividendIncome model."""
    
    list_display = [
        'asset_symbol', 'payment_date', 'dividend_type', 'shares_held',
        'amount_per_share_display', 'total_amount_display', 'tax_withheld_display'
    ]
    list_filter = [
        'payment_date', 'dividend_type', 'user', 'tax_year__year',
        'position__asset__asset_type'
    ]
    search_fields = [
        'position__asset__symbol', 'position__asset__name',
        'user__username'
    ]
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    raw_id_fields = ['user', 'position']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']
    
    def asset_symbol(self, obj):
        """Display asset symbol."""
        return obj.position.asset.symbol
    asset_symbol.short_description = 'Symbol'
    asset_symbol.admin_order_field = 'position__asset__symbol'
    
    def amount_per_share_display(self, obj):
        """Display amount per share formatted."""
        return f"${obj.amount_per_share:.4f}"
    amount_per_share_display.short_description = 'Per Share'
    amount_per_share_display.admin_order_field = 'amount_per_share'
    
    def total_amount_display(self, obj):
        """Display total amount formatted."""
        return f"${obj.total_amount:,.2f}"
    total_amount_display.short_description = 'Total Amount'
    total_amount_display.admin_order_field = 'total_amount'
    
    def tax_withheld_display(self, obj):
        """Display tax withheld formatted."""
        if obj.tax_withheld:
            return f"${obj.tax_withheld:,.2f}"
        return "-"
    tax_withheld_display.short_description = 'Tax Withheld'


@admin.register(TaxLossHarvestingOpportunity)
class TaxLossHarvestingOpportunityAdmin(admin.ModelAdmin):
    """Admin interface for TaxLossHarvestingOpportunity model."""
    
    list_display = [
        'asset_symbol', 'status', 'potential_loss_amount_display',
        'current_unrealized_loss_display', 'tax_benefit_estimate_display',
        'wash_sale_end_date', 'recommended_sale_date'
    ]
    list_filter = [
        'status', 'identified_date', 'user', 'tax_year__year',
        'position__asset__asset_type'
    ]
    search_fields = [
        'position__asset__symbol', 'position__asset__name',
        'user__username'
    ]
    readonly_fields = [
        'identified_date', 'created_at', 'updated_at'
    ]
    raw_id_fields = ['user', 'position']
    ordering = ['-potential_loss_amount', '-identified_date']
    
    def asset_symbol(self, obj):
        """Display asset symbol."""
        return obj.position.asset.symbol
    asset_symbol.short_description = 'Symbol'
    asset_symbol.admin_order_field = 'position__asset__symbol'
    
    def potential_loss_amount_display(self, obj):
        """Display potential loss amount formatted."""
        return format_html(
            '<span style="color: red; font-weight: bold;">${:,.2f}</span>', 
            obj.potential_loss_amount
        )
    potential_loss_amount_display.short_description = 'Potential Loss'
    potential_loss_amount_display.admin_order_field = 'potential_loss_amount'
    
    def current_unrealized_loss_display(self, obj):
        """Display current unrealized loss formatted."""
        return format_html(
            '<span style="color: red;">${:,.2f}</span>', 
            abs(obj.current_unrealized_loss)
        )
    current_unrealized_loss_display.short_description = 'Current Loss'
    current_unrealized_loss_display.admin_order_field = 'current_unrealized_loss'
    
    def tax_benefit_estimate_display(self, obj):
        """Display tax benefit estimate formatted."""
        if obj.tax_benefit_estimate:
            return format_html(
                '<span style="color: green;">${:,.2f}</span>', 
                obj.tax_benefit_estimate
            )
        return "-"
    tax_benefit_estimate_display.short_description = 'Tax Benefit'


@admin.register(TaxOptimizationRecommendation)
class TaxOptimizationRecommendationAdmin(admin.ModelAdmin):
    """Admin interface for TaxOptimizationRecommendation model."""
    
    list_display = [
        'title', 'recommendation_type', 'priority', 'estimated_tax_savings_display',
        'deadline', 'is_implemented', 'created_at'
    ]
    list_filter = [
        'recommendation_type', 'priority', 'is_implemented', 
        'user', 'tax_year__year', 'created_at'
    ]
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'portfolio']
    ordering = ['-estimated_tax_savings', '-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user', 'tax_year', 'portfolio', 'recommendation_type',
                'priority', 'title', 'description'
            )
        }),
        ('Financial Impact', {
            'fields': (
                'estimated_tax_savings', 'implementation_cost'
            )
        }),
        ('Implementation', {
            'fields': (
                'action_required', 'deadline', 'is_implemented',
                'implementation_date', 'implementation_notes'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def estimated_tax_savings_display(self, obj):
        """Display estimated tax savings formatted."""
        if obj.estimated_tax_savings:
            return format_html(
                '<span style="color: green; font-weight: bold;">${:,.2f}</span>', 
                obj.estimated_tax_savings
            )
        return "-"
    estimated_tax_savings_display.short_description = 'Tax Savings'
    estimated_tax_savings_display.admin_order_field = 'estimated_tax_savings'


@admin.register(TaxReport)
class TaxReportAdmin(admin.ModelAdmin):
    """Admin interface for TaxReport model."""
    
    list_display = [
        'user', 'tax_year', 'report_type', 'generated_date',
        'net_capital_gain_loss_display', 'total_dividend_income_display',
        'view_report_link'
    ]
    list_filter = [
        'report_type', 'generated_date', 'user', 'tax_year__year'
    ]
    search_fields = ['user__username', 'tax_year__year']
    readonly_fields = [
        'generated_date', 'report_data', 'created_at', 'updated_at'
    ]
    raw_id_fields = ['user']
    ordering = ['-generated_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'tax_year', 'report_type', 'generated_date')
        }),
        ('Summary Totals', {
            'fields': (
                'total_short_term_gains', 'total_short_term_losses',
                'total_long_term_gains', 'total_long_term_losses',
                'net_capital_gain_loss', 'total_dividend_income'
            )
        }),
        ('Report Data', {
            'fields': ('report_data',),
            'classes': ('collapse',)
        }),
        ('File Storage', {
            'fields': ('pdf_file',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def net_capital_gain_loss_display(self, obj):
        """Display net capital gain/loss with color coding."""
        amount = obj.net_capital_gain_loss
        if amount > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">${:,.2f}</span>', 
                amount
            )
        elif amount < 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">${:,.2f}</span>', 
                amount
            )
        return "${:,.2f}".format(amount)
    net_capital_gain_loss_display.short_description = 'Net Capital Gain/Loss'
    net_capital_gain_loss_display.admin_order_field = 'net_capital_gain_loss'
    
    def total_dividend_income_display(self, obj):
        """Display total dividend income formatted."""
        if obj.total_dividend_income:
            return f"${obj.total_dividend_income:,.2f}"
        return "-"
    total_dividend_income_display.short_description = 'Dividend Income'
    total_dividend_income_display.admin_order_field = 'total_dividend_income'
    
    def view_report_link(self, obj):
        """Display link to view full report."""
        if obj.report_data:
            return format_html(
                '<a href="#" onclick="alert(\'Report data available in Report Data field\')">View Data</a>'
            )
        return "-"
    view_report_link.short_description = 'Actions'


# Customize admin site header
admin.site.site_header = "Personal Finance Tax Administration"
admin.site.site_title = "Tax Admin"
admin.site.index_title = "Tax Management Dashboard"