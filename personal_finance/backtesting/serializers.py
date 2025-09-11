"""Django REST Framework serializers for backtesting models."""

from rest_framework import serializers
from decimal import Decimal
from typing import Dict, Any

from personal_finance.assets.serializers import AssetSerializer
from ..models import Strategy, Backtest, BacktestResult, BacktestPortfolioSnapshot, BacktestTrade


class StrategySerializer(serializers.ModelSerializer):
    """Serializer for Strategy model."""
    
    asset_universe = AssetSerializer(many=True, read_only=True)
    asset_symbols = serializers.ListField(
        child=serializers.CharField(max_length=20),
        write_only=True,
        required=False,
        help_text="List of asset symbols to include in strategy universe"
    )
    backtest_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Strategy
        fields = [
            'id', 'name', 'description', 'strategy_type', 'parameters',
            'initial_capital', 'rebalance_frequency', 'max_position_size',
            'stop_loss_percentage', 'take_profit_percentage', 'asset_universe',
            'asset_symbols', 'backtest_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_backtest_count(self, obj) -> int:
        """Get number of backtests for this strategy."""
        return obj.backtests.count()
    
    def create(self, validated_data):
        """Create strategy with asset universe."""
        asset_symbols = validated_data.pop('asset_symbols', [])
        
        # Set user from request
        validated_data['user'] = self.context['request'].user
        
        strategy = super().create(validated_data)
        
        # Add assets to universe
        if asset_symbols:
            from personal_finance.assets.models import Asset
            assets = Asset.objects.filter(symbol__in=asset_symbols)
            strategy.asset_universe.add(*assets)
        
        return strategy
    
    def update(self, instance, validated_data):
        """Update strategy with asset universe."""
        asset_symbols = validated_data.pop('asset_symbols', None)
        
        strategy = super().update(instance, validated_data)
        
        # Update asset universe if provided
        if asset_symbols is not None:
            from personal_finance.assets.models import Asset
            assets = Asset.objects.filter(symbol__in=asset_symbols)
            strategy.asset_universe.set(assets)
        
        return strategy


class BacktestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new backtests."""
    
    benchmark_symbol = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text="Benchmark asset symbol (e.g., SPY)"
    )
    
    class Meta:
        model = Backtest
        fields = [
            'strategy', 'name', 'description', 'start_date', 'end_date',
            'benchmark_symbol', 'transaction_costs', 'slippage'
        ]
    
    def create(self, validated_data):
        """Create backtest with benchmark asset."""
        benchmark_symbol = validated_data.pop('benchmark_symbol', None)
        
        backtest = super().create(validated_data)
        
        # Set benchmark asset if provided
        if benchmark_symbol:
            from personal_finance.assets.models import Asset
            try:
                benchmark_asset = Asset.objects.get(symbol=benchmark_symbol)
                backtest.benchmark_asset = benchmark_asset
                backtest.save()
            except Asset.DoesNotExist:
                pass  # Silently ignore invalid benchmark symbol
        
        return backtest


class BacktestResultSerializer(serializers.ModelSerializer):
    """Serializer for BacktestResult model."""
    
    profit_factor = serializers.SerializerMethodField()
    expectancy = serializers.SerializerMethodField()
    
    class Meta:
        model = BacktestResult
        fields = [
            'id', 'total_return', 'annualized_return', 'volatility', 'sharpe_ratio',
            'max_drawdown', 'var_95', 'calmar_ratio', 'total_trades', 'winning_trades',
            'losing_trades', 'win_rate', 'average_win', 'average_loss', 'benchmark_return',
            'alpha', 'beta', 'information_ratio', 'final_portfolio_value', 'cash_balance',
            'total_transaction_costs', 'profit_factor', 'expectancy', 'daily_returns',
            'portfolio_values', 'trade_history', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_profit_factor(self, obj) -> float:
        """Get calculated profit factor."""
        return float(obj.profit_factor) if obj.profit_factor else None
    
    def get_expectancy(self, obj) -> float:
        """Get calculated expectancy."""
        return float(obj.expectancy) if obj.expectancy else None


class BacktestSerializer(serializers.ModelSerializer):
    """Serializer for Backtest model with results."""
    
    strategy = StrategySerializer(read_only=True)
    benchmark_asset = AssetSerializer(read_only=True)
    result = BacktestResultSerializer(read_only=True)
    duration_days = serializers.SerializerMethodField()
    execution_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Backtest
        fields = [
            'id', 'strategy', 'name', 'description', 'start_date', 'end_date',
            'benchmark_asset', 'transaction_costs', 'slippage', 'status',
            'progress_percentage', 'error_message', 'started_at', 'completed_at',
            'duration_days', 'execution_time', 'result', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'progress_percentage', 'error_message', 'started_at',
            'completed_at', 'created_at', 'updated_at'
        ]
    
    def get_duration_days(self, obj) -> int:
        """Get backtest duration in days."""
        return obj.duration_days
    
    def get_execution_time(self, obj) -> float:
        """Get execution time in seconds."""
        return obj.execution_time


class BacktestPortfolioSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for portfolio snapshots."""
    
    cash_percentage = serializers.SerializerMethodField()
    invested_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = BacktestPortfolioSnapshot
        fields = [
            'id', 'date', 'total_value', 'cash_balance', 'invested_value',
            'cash_percentage', 'invested_percentage', 'daily_return',
            'cumulative_return', 'positions', 'benchmark_value', 'benchmark_return'
        ]
        read_only_fields = ['id']
    
    def get_cash_percentage(self, obj) -> float:
        """Get cash as percentage of total portfolio."""
        return float(obj.cash_percentage)
    
    def get_invested_percentage(self, obj) -> float:
        """Get invested amount as percentage of total portfolio."""
        return float(obj.invested_percentage)


class BacktestTradeSerializer(serializers.ModelSerializer):
    """Serializer for individual trades."""
    
    asset = AssetSerializer(read_only=True)
    total_cost = serializers.SerializerMethodField()
    is_opening_trade = serializers.SerializerMethodField()
    is_closing_trade = serializers.SerializerMethodField()
    
    class Meta:
        model = BacktestTrade
        fields = [
            'id', 'asset', 'trade_type', 'date', 'quantity', 'price',
            'transaction_cost', 'slippage_cost', 'total_cost', 'gross_value',
            'net_value', 'signal_strength', 'reason', 'portfolio_value_before',
            'portfolio_value_after', 'position_size_percentage', 'is_opening_trade',
            'is_closing_trade'
        ]
        read_only_fields = ['id']
    
    def get_total_cost(self, obj) -> float:
        """Get total trade cost."""
        return float(obj.total_cost)
    
    def get_is_opening_trade(self, obj) -> bool:
        """Check if this is an opening trade."""
        return obj.is_opening_trade
    
    def get_is_closing_trade(self, obj) -> bool:
        """Check if this is a closing trade."""
        return obj.is_closing_trade


class BacktestPerformanceChartSerializer(serializers.Serializer):
    """Serializer for backtest performance chart data."""
    
    dates = serializers.ListField(child=serializers.DateField())
    portfolio_values = serializers.ListField(child=serializers.FloatField())
    benchmark_values = serializers.ListField(child=serializers.FloatField(), required=False)
    daily_returns = serializers.ListField(child=serializers.FloatField())
    cumulative_returns = serializers.ListField(child=serializers.FloatField())
    drawdowns = serializers.ListField(child=serializers.FloatField())


class BacktestSummarySerializer(serializers.Serializer):
    """Serializer for backtest summary statistics."""
    
    total_backtests = serializers.IntegerField()
    completed_backtests = serializers.IntegerField()
    running_backtests = serializers.IntegerField()
    failed_backtests = serializers.IntegerField()
    best_performing_backtest = serializers.DictField(required=False)
    worst_performing_backtest = serializers.DictField(required=False)
    average_return = serializers.FloatField(required=False)
    average_sharpe_ratio = serializers.FloatField(required=False)