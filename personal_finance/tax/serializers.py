"""API serializers for tax models."""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    TaxYear, TaxLot, CapitalGainLoss, DividendIncome,
    TaxLossHarvestingOpportunity, TaxOptimizationRecommendation, TaxReport
)

User = get_user_model()


class TaxYearSerializer(serializers.ModelSerializer):
    """Serializer for TaxYear model."""
    
    class Meta:
        model = TaxYear
        fields = [
            'id', 'year', 'filing_deadline', 'standard_deduction_single',
            'standard_deduction_married', 'long_term_capital_gains_thresholds',
            'short_term_capital_gains_rate'
        ]
        read_only_fields = ['id']


class TaxLotSerializer(serializers.ModelSerializer):
    """Serializer for TaxLot model."""
    
    asset_symbol = serializers.CharField(source='position.asset.symbol', read_only=True)
    asset_name = serializers.CharField(source='position.asset.name', read_only=True)
    portfolio_name = serializers.CharField(source='position.portfolio.name', read_only=True)
    current_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    unrealized_gain_loss = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_long_term = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = TaxLot
        fields = [
            'id', 'position', 'asset_symbol', 'asset_name', 'portfolio_name',
            'acquisition_date', 'original_quantity', 'remaining_quantity',
            'cost_basis_per_share', 'total_cost_basis', 'current_value',
            'unrealized_gain_loss', 'is_long_term', 'transaction',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_cost_basis', 'current_value', 'unrealized_gain_loss',
            'is_long_term', 'created_at', 'updated_at'
        ]


class CapitalGainLossSerializer(serializers.ModelSerializer):
    """Serializer for CapitalGainLoss model."""
    
    asset_symbol = serializers.CharField(source='position.asset.symbol', read_only=True)
    asset_name = serializers.CharField(source='position.asset.name', read_only=True)
    portfolio_name = serializers.CharField(source='position.portfolio.name', read_only=True)
    tax_year_display = serializers.CharField(source='tax_year.year', read_only=True)
    term_display = serializers.CharField(source='get_term_display', read_only=True)
    
    class Meta:
        model = CapitalGainLoss
        fields = [
            'id', 'user', 'tax_year', 'tax_year_display', 'position',
            'asset_symbol', 'asset_name', 'portfolio_name', 'transaction',
            'tax_lot', 'sale_date', 'sale_price_per_share', 'quantity_sold',
            'gross_proceeds', 'cost_basis_per_share', 'total_cost_basis',
            'gain_loss_amount', 'term', 'term_display', 'wash_sale_adjustment',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'gain_loss_amount', 'created_at', 'updated_at'
        ]


class DividendIncomeSerializer(serializers.ModelSerializer):
    """Serializer for DividendIncome model."""
    
    asset_symbol = serializers.CharField(source='position.asset.symbol', read_only=True)
    asset_name = serializers.CharField(source='position.asset.name', read_only=True)
    portfolio_name = serializers.CharField(source='position.portfolio.name', read_only=True)
    tax_year_display = serializers.CharField(source='tax_year.year', read_only=True)
    dividend_type_display = serializers.CharField(source='get_dividend_type_display', read_only=True)
    
    class Meta:
        model = DividendIncome
        fields = [
            'id', 'user', 'tax_year', 'tax_year_display', 'position',
            'asset_symbol', 'asset_name', 'portfolio_name', 'payment_date',
            'ex_dividend_date', 'dividend_type', 'dividend_type_display',
            'amount_per_share', 'shares_held', 'total_amount', 'tax_withheld',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_amount', 'created_at', 'updated_at'
        ]


class TaxLossHarvestingOpportunitySerializer(serializers.ModelSerializer):
    """Serializer for TaxLossHarvestingOpportunity model."""
    
    asset_symbol = serializers.CharField(source='position.asset.symbol', read_only=True)
    asset_name = serializers.CharField(source='position.asset.name', read_only=True)
    portfolio_name = serializers.CharField(source='position.portfolio.name', read_only=True)
    tax_year_display = serializers.CharField(source='tax_year.year', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TaxLossHarvestingOpportunity
        fields = [
            'id', 'user', 'position', 'asset_symbol', 'asset_name',
            'portfolio_name', 'tax_year', 'tax_year_display', 'identified_date',
            'potential_loss_amount', 'current_unrealized_loss', 'wash_sale_end_date',
            'status', 'status_display', 'recommended_sale_date',
            'alternative_investments', 'tax_benefit_estimate',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'identified_date', 'created_at', 'updated_at'
        ]


class TaxOptimizationRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for TaxOptimizationRecommendation model."""
    
    user_display = serializers.CharField(source='user.username', read_only=True)
    portfolio_name = serializers.CharField(source='portfolio.name', read_only=True)
    tax_year_display = serializers.CharField(source='tax_year.year', read_only=True)
    recommendation_type_display = serializers.CharField(source='get_recommendation_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = TaxOptimizationRecommendation
        fields = [
            'id', 'user', 'user_display', 'tax_year', 'tax_year_display',
            'portfolio', 'portfolio_name', 'recommendation_type',
            'recommendation_type_display', 'priority', 'priority_display',
            'title', 'description', 'estimated_tax_savings', 'implementation_cost',
            'action_required', 'deadline', 'is_implemented', 'implementation_date',
            'implementation_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaxReportSerializer(serializers.ModelSerializer):
    """Serializer for TaxReport model."""
    
    user_display = serializers.CharField(source='user.username', read_only=True)
    tax_year_display = serializers.CharField(source='tax_year.year', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    net_short_term = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    net_long_term = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = TaxReport
        fields = [
            'id', 'user', 'user_display', 'tax_year', 'tax_year_display',
            'report_type', 'report_type_display', 'generated_date',
            'total_short_term_gains', 'total_short_term_losses',
            'total_long_term_gains', 'total_long_term_losses',
            'net_capital_gain_loss', 'total_dividend_income',
            'net_short_term', 'net_long_term', 'pdf_file',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'generated_date', 'net_short_term', 'net_long_term',
            'created_at', 'updated_at'
        ]


class TaxSummarySerializer(serializers.Serializer):
    """Serializer for tax summary data."""
    
    capital_gains = serializers.DictField()
    dividends = serializers.DictField()
    tax_estimates = serializers.DictField()
    optimization = serializers.DictField()
    summary_metrics = serializers.DictField()
    
    class Meta:
        fields = [
            'capital_gains', 'dividends', 'tax_estimates',
            'optimization', 'summary_metrics'
        ]


class TaxCalculationRequestSerializer(serializers.Serializer):
    """Serializer for tax calculation requests."""
    
    year = serializers.IntegerField(required=False, help_text="Tax year (current year if not specified)")
    portfolio_id = serializers.IntegerField(required=False, help_text="Specific portfolio ID (all portfolios if not specified)")
    reprocess = serializers.BooleanField(default=False, help_text="Reprocess existing calculations")
    
    class Meta:
        fields = ['year', 'portfolio_id', 'reprocess']


class LossHarvestingAnalysisSerializer(serializers.Serializer):
    """Serializer for loss harvesting analysis requests."""
    
    minimum_loss_threshold = serializers.DecimalField(
        max_digits=10, decimal_places=2, default=100.00,
        help_text="Minimum loss amount to consider"
    )
    generate_recommendations = serializers.BooleanField(
        default=True, help_text="Generate specific recommendations"
    )
    
    class Meta:
        fields = ['minimum_loss_threshold', 'generate_recommendations']