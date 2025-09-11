"""Serializers for portfolio API endpoints."""

from decimal import Decimal
from typing import Dict, Any
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Portfolio, Position, Transaction, PortfolioSnapshot
from personal_finance.assets.models import Asset

User = get_user_model()


class PortfolioListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for portfolio list views."""
    
    total_value = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    total_cost_basis = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    total_return = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    total_return_percentage = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    position_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'name', 'description', 'is_active', 'created', 'modified',
            'total_value', 'total_cost_basis', 'total_return', 
            'total_return_percentage', 'position_count'
        ]
        read_only_fields = ['created', 'modified']
    
    def to_representation(self, instance):
        """Add calculated fields to the representation."""
        data = super().to_representation(instance)
        
        # Add position count
        data['position_count'] = instance.positions.filter(is_active=True).count()
        
        return data


class PortfolioDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for portfolio detail views."""
    
    user = serializers.StringRelatedField(read_only=True)
    total_value = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    total_cost_basis = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    total_return = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    total_return_percentage = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'user', 'name', 'description', 'is_active', 
            'created', 'modified', 'total_value', 'total_cost_basis', 
            'total_return', 'total_return_percentage'
        ]
        read_only_fields = ['user', 'created', 'modified']


class AssetSummarySerializer(serializers.ModelSerializer):
    """Lightweight asset serializer for nested use."""
    
    price_change = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    price_change_percentage = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'symbol', 'name', 'asset_type', 'current_price', 
            'previous_close', 'price_change', 'price_change_percentage',
            'currency', 'exchange', 'last_price_update'
        ]


class PositionSerializer(serializers.ModelSerializer):
    """Serializer for portfolio positions."""
    
    asset = AssetSummarySerializer(read_only=True)
    asset_id = serializers.IntegerField(write_only=True)
    portfolio_name = serializers.CharField(source='portfolio.name', read_only=True)
    
    # Calculated fields
    total_cost_basis = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    current_value = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    unrealized_gain_loss = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    unrealized_return_percentage = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    class Meta:
        model = Position
        fields = [
            'id', 'portfolio', 'portfolio_name', 'asset', 'asset_id',
            'quantity', 'average_cost', 'first_purchase_date', 'is_active',
            'notes', 'created', 'modified', 'total_cost_basis', 'current_value',
            'unrealized_gain_loss', 'unrealized_return_percentage'
        ]
        read_only_fields = ['created', 'modified']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for investment transactions."""
    
    position_info = serializers.SerializerMethodField(read_only=True)
    total_value = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'position', 'position_info', 'transaction_type', 'quantity',
            'price', 'fees', 'transaction_date', 'notes', 'created', 'modified',
            'total_value'
        ]
        read_only_fields = ['created', 'modified']
    
    def get_position_info(self, obj):
        """Get position information for the transaction."""
        return {
            'portfolio_name': obj.position.portfolio.name,
            'asset_symbol': obj.position.asset.symbol,
            'asset_name': obj.position.asset.name
        }


class PortfolioSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for portfolio performance snapshots."""
    
    total_return = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    return_percentage = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    class Meta:
        model = PortfolioSnapshot
        fields = [
            'id', 'portfolio', 'snapshot_date', 'total_value', 
            'total_cost_basis', 'cash_balance', 'created', 'modified',
            'total_return', 'return_percentage'
        ]
        read_only_fields = ['created', 'modified']


class PortfolioCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating portfolios."""
    
    class Meta:
        model = Portfolio
        fields = ['name', 'description', 'is_active']
    
    def validate_name(self, value):
        """Validate portfolio name is unique for the user."""
        user = self.context['request'].user
        portfolio = self.instance
        
        queryset = Portfolio.objects.filter(user=user, name=value)
        if portfolio:
            queryset = queryset.exclude(pk=portfolio.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "You already have a portfolio with this name."
            )
        return value


class PositionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating positions."""
    
    class Meta:
        model = Position
        fields = [
            'portfolio', 'asset', 'quantity', 'average_cost', 
            'first_purchase_date', 'notes', 'is_active'
        ]
    
    def validate(self, attrs):
        """Validate position data."""
        portfolio = attrs.get('portfolio')
        asset = attrs.get('asset')
        
        # Check if position already exists for this portfolio/asset combination
        if not self.instance:  # Creating new position
            if Position.objects.filter(portfolio=portfolio, asset=asset).exists():
                raise serializers.ValidationError(
                    "A position for this asset already exists in the portfolio."
                )
        
        # Validate portfolio ownership
        request = self.context.get('request')
        if request and portfolio.user != request.user:
            raise serializers.ValidationError(
                "You can only create positions in your own portfolios."
            )
        
        return attrs


class TransactionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating transactions."""
    
    class Meta:
        model = Transaction
        fields = [
            'position', 'transaction_type', 'quantity', 'price', 
            'fees', 'transaction_date', 'notes'
        ]
    
    def validate(self, attrs):
        """Validate transaction data."""
        position = attrs.get('position')
        
        # Validate position ownership
        request = self.context.get('request')
        if request and position.portfolio.user != request.user:
            raise serializers.ValidationError(
                "You can only create transactions for your own positions."
            )
        
        return attrs


class PerformanceMetricsSerializer(serializers.Serializer):
    """Serializer for portfolio performance metrics."""
    
    # Basic metrics
    total_return = serializers.DecimalField(max_digits=20, decimal_places=4, read_only=True)
    total_return_percentage = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    annualized_return = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    # Risk metrics
    volatility = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    sharpe_ratio = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    max_drawdown = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    var_95 = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    # Additional metrics
    beta = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    alpha = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    sortino_ratio = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    calmar_ratio = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    # Time period info
    start_date = serializers.DateField(read_only=True)
    end_date = serializers.DateField(read_only=True)
    days_analyzed = serializers.IntegerField(read_only=True)


class AllocationDataSerializer(serializers.Serializer):
    """Serializer for portfolio allocation data."""
    
    asset_symbol = serializers.CharField()
    asset_name = serializers.CharField()
    asset_type = serializers.CharField()
    sector = serializers.CharField()
    value = serializers.DecimalField(max_digits=20, decimal_places=2)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    quantity = serializers.DecimalField(max_digits=20, decimal_places=8)
    average_cost = serializers.DecimalField(max_digits=20, decimal_places=8)
    current_price = serializers.DecimalField(max_digits=20, decimal_places=8)
    unrealized_return = serializers.DecimalField(max_digits=20, decimal_places=2)
    unrealized_return_percentage = serializers.DecimalField(max_digits=10, decimal_places=4)