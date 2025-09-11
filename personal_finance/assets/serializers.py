"""Serializers for asset API endpoints."""

from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, Any
from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Asset
from .models import Holding  # Legacy model
from .models import Portfolio as LegacyPortfolio  # Legacy model

# Graceful import for PriceHistory
try:
    from .models import PriceHistory
except ImportError:
    PriceHistory = None

UserModel = get_user_model()


class AssetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for asset list views."""
    
    price_change = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    price_change_percentage = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'symbol', 'name', 'asset_type', 'current_price', 
            'previous_close', 'price_change', 'price_change_percentage',
            'currency', 'exchange', 'last_price_update', 'is_tradeable'
        ]


class AssetDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for asset detail views."""
    
    price_change = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    price_change_percentage = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    is_stock_like = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'symbol', 'name', 'asset_type', 'currency', 'exchange', 
            'primary_exchange', 'isin', 'cusip', 'figi', 'current_price',
            'previous_close', 'day_high', 'day_low', 'volume', 'market_cap',
            'sector', 'industry', 'last_price_update', 'data_source',
            'is_tradeable', 'is_active', 'metadata', 'created', 'modified',
            'price_change', 'price_change_percentage', 'is_stock_like'
        ]
        read_only_fields = ['created', 'modified', 'last_price_update', 'data_source']


class AssetCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating assets."""
    
    class Meta:
        model = Asset
        fields = [
            'symbol', 'name', 'asset_type', 'currency', 'exchange',
            'primary_exchange', 'isin', 'cusip', 'figi', 'sector',
            'industry', 'is_tradeable', 'is_active', 'metadata'
        ]
    
    def validate_symbol(self, value):
        """Validate symbol is unique within exchange."""
        exchange = self.initial_data.get('exchange', '')
        asset = self.instance
        
        queryset = Asset.objects.filter(symbol=value, exchange=exchange)
        if asset:
            queryset = queryset.exclude(pk=asset.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                f"Asset with symbol '{value}' already exists on exchange '{exchange}'"
            )
        return value.upper()


if PriceHistory:
    class PriceHistorySerializer(serializers.ModelSerializer):
        """Serializer for asset price history."""
        
        daily_return = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
        
        class Meta:
            model = PriceHistory
            fields = [
                'id', 'asset', 'date', 'open_price', 'high_price', 'low_price',
                'close_price', 'adjusted_close', 'volume', 'dividend_amount',
                'split_ratio', 'data_source', 'created', 'modified', 'daily_return'
            ]
            read_only_fields = ['created', 'modified']
else:
    # Mock serializer if PriceHistory is not available
    class PriceHistorySerializer(serializers.Serializer):
        """Mock serializer for price history when model is unavailable."""
        pass


class AssetPerformanceSerializer(serializers.Serializer):
    """Serializer for asset performance metrics."""
    
    # Price data
    current_price = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    price_change = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    price_change_percentage = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    # Returns
    daily_return = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    weekly_return = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    monthly_return = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    ytd_return = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    annual_return = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    # Risk metrics
    volatility = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    beta = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    sharpe_ratio = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    max_drawdown = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    # Market data
    market_cap = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    volume = serializers.IntegerField(read_only=True)
    avg_volume = serializers.IntegerField(read_only=True)
    
    # Period info
    start_date = serializers.DateField(read_only=True)
    end_date = serializers.DateField(read_only=True)
    days_analyzed = serializers.IntegerField(read_only=True)


class TechnicalIndicatorsSerializer(serializers.Serializer):
    """Serializer for technical indicator data."""
    
    # Moving averages
    sma_20 = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    sma_50 = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    sma_200 = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    ema_12 = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    ema_26 = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    
    # Oscillators
    rsi_14 = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    macd = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    macd_signal = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    macd_histogram = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    
    # Bollinger Bands
    bb_upper = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    bb_middle = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    bb_lower = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    bb_width = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    # Additional indicators
    stochastic_k = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    stochastic_d = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    williams_r = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    # Calculation date
    calculation_date = serializers.DateField(read_only=True)


class AssetSearchSerializer(serializers.Serializer):
    """Serializer for asset search results."""
    
    symbol = serializers.CharField()
    name = serializers.CharField()
    asset_type = serializers.CharField()
    exchange = serializers.CharField()
    currency = serializers.CharField()
    current_price = serializers.DecimalField(max_digits=20, decimal_places=8)
    market_cap = serializers.DecimalField(max_digits=20, decimal_places=2)
    sector = serializers.CharField()


# Legacy serializers for backward compatibility
class AssetSerializer(serializers.ModelSerializer):
    """Legacy asset serializer for backward compatibility."""
    
    class Meta:
        model = Asset
        fields = [
            "id",
            "symbol",
            "name",
            "asset_type",
            "currency",
            "exchange",
            "isin",
            "cusip",
            "metadata",
            "is_active",
            "created",
            "modified",
        ]
        read_only_fields = ["id", "created", "modified"]


class PortfolioSerializer(serializers.ModelSerializer):
    """Legacy portfolio serializer for backward compatibility."""
    
    user = serializers.PrimaryKeyRelatedField(
        queryset=UserModel.objects.all(),
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = LegacyPortfolio
        fields = [
            "id",
            "user",
            "name",
            "description",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HoldingSerializer(serializers.ModelSerializer):
    """Legacy holding serializer for backward compatibility."""
    
    user = serializers.PrimaryKeyRelatedField(
        queryset=UserModel.objects.all(),
        default=serializers.CurrentUserDefault(),
    )
    asset = serializers.PrimaryKeyRelatedField(queryset=Asset.objects.all())
    portfolio = serializers.PrimaryKeyRelatedField(
        queryset=LegacyPortfolio.objects.all(),
        allow_null=True,
        required=False,
        default=None,
    )

    class Meta:
        model = Holding
        fields = [
            "id",
            "user",
            "asset",
            "portfolio",
            "quantity",
            "average_price",
            "currency",
            "acquired_at",
            "in_portfolio",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
