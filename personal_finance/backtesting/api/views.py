"""API views for backtesting functionality."""

import logging
from datetime import date, timedelta
from typing import Dict, Any

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from personal_finance.assets.models import Asset
from ..models import Strategy, Backtest, BacktestResult, BacktestPortfolioSnapshot, BacktestTrade
from ..services import BacktestEngine, get_available_strategies
from ..serializers import (
    StrategySerializer, BacktestSerializer, BacktestCreateSerializer,
    BacktestResultSerializer, BacktestPortfolioSnapshotSerializer,
    BacktestTradeSerializer, BacktestPerformanceChartSerializer,
    BacktestSummarySerializer
)

logger = logging.getLogger(__name__)


class StrategyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing trading strategies."""
    
    serializer_class = StrategySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return strategies for current user."""
        return Strategy.objects.filter(user=self.request.user).prefetch_related('asset_universe')
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get available strategy types."""
        strategy_types = get_available_strategies()
        return Response({
            'strategy_types': [
                {'value': value, 'label': label}
                for value, label in strategy_types
            ]
        })
    
    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """Clone an existing strategy."""
        strategy = self.get_object()
        
        # Create clone with new name
        cloned_strategy = Strategy.objects.create(
            user=request.user,
            name=f"{strategy.name} (Copy)",
            description=strategy.description,
            strategy_type=strategy.strategy_type,
            parameters=strategy.parameters.copy(),
            initial_capital=strategy.initial_capital,
            rebalance_frequency=strategy.rebalance_frequency,
            max_position_size=strategy.max_position_size,
            stop_loss_percentage=strategy.stop_loss_percentage,
            take_profit_percentage=strategy.take_profit_percentage
        )
        
        # Copy asset universe
        cloned_strategy.asset_universe.set(strategy.asset_universe.all())
        
        serializer = self.get_serializer(cloned_strategy)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def performance_summary(self, request, pk=None):
        """Get performance summary for all backtests of this strategy."""
        strategy = self.get_object()
        
        completed_backtests = strategy.backtests.filter(
            status='completed',
            result__isnull=False
        )
        
        if not completed_backtests.exists():
            return Response({
                'total_backtests': 0,
                'completed_backtests': 0,
                'average_return': None,
                'average_sharpe_ratio': None,
                'best_backtest': None,
                'worst_backtest': None
            })
        
        # Calculate averages
        results = completed_backtests.select_related('result')
        avg_data = results.aggregate(
            avg_return=Avg('result__total_return'),
            avg_sharpe=Avg('result__sharpe_ratio')
        )
        
        # Find best and worst
        best_result = results.order_by('-result__total_return').first()
        worst_result = results.order_by('result__total_return').first()
        
        return Response({
            'total_backtests': strategy.backtests.count(),
            'completed_backtests': completed_backtests.count(),
            'average_return': float(avg_data['avg_return']) if avg_data['avg_return'] else None,
            'average_sharpe_ratio': float(avg_data['avg_sharpe']) if avg_data['avg_sharpe'] else None,
            'best_backtest': {
                'id': best_result.id,
                'name': best_result.name,
                'total_return': float(best_result.result.total_return),
                'sharpe_ratio': float(best_result.result.sharpe_ratio) if best_result.result.sharpe_ratio else None
            } if best_result else None,
            'worst_backtest': {
                'id': worst_result.id,
                'name': worst_result.name,
                'total_return': float(worst_result.result.total_return),
                'sharpe_ratio': float(worst_result.result.sharpe_ratio) if worst_result.result.sharpe_ratio else None
            } if worst_result else None
        })


class BacktestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing backtests."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return backtests for current user's strategies."""
        return Backtest.objects.filter(
            strategy__user=self.request.user
        ).select_related('strategy', 'benchmark_asset', 'result')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return BacktestCreateSerializer
        return BacktestSerializer
    
    def perform_create(self, serializer):
        """Validate strategy ownership before creating backtest."""
        strategy = serializer.validated_data['strategy']
        if strategy.user != self.request.user:
            raise ValidationError("Cannot create backtest for strategy owned by another user")
        
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """Run or re-run a backtest."""
        backtest = self.get_object()
        
        # Check if backtest is already running
        if backtest.status == 'running':
            return Response(
                {'error': 'Backtest is already running'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate strategy has assets
        if not backtest.strategy.asset_universe.exists():
            return Response(
                {'error': 'Strategy has no assets in universe'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Run backtest asynchronously in production, synchronously for demo
            engine = BacktestEngine()
            result = engine.run_backtest(backtest)
            
            # Return updated backtest with results
            backtest.refresh_from_db()
            serializer = self.get_serializer(backtest)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Backtest execution failed: {str(e)}")
            return Response(
                {'error': f'Backtest execution failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def performance_chart(self, request, pk=None):
        """Get performance chart data for backtest."""
        backtest = self.get_object()
        
        if not backtest.is_completed():
            return Response(
                {'error': 'Backtest not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get portfolio snapshots
        snapshots = backtest.portfolio_snapshots.order_by('date')
        
        if not snapshots.exists():
            return Response(
                {'error': 'No portfolio data available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare chart data
        dates = [snapshot.date for snapshot in snapshots]
        portfolio_values = [float(snapshot.total_value) for snapshot in snapshots]
        daily_returns = [float(snapshot.daily_return) if snapshot.daily_return else 0.0 for snapshot in snapshots]
        cumulative_returns = [float(snapshot.cumulative_return) for snapshot in snapshots]
        
        # Calculate drawdowns
        portfolio_series = portfolio_values
        running_max = []
        current_max = portfolio_series[0]
        
        for value in portfolio_series:
            if value > current_max:
                current_max = value
            running_max.append(current_max)
        
        drawdowns = [(value - max_val) / max_val * 100 for value, max_val in zip(portfolio_series, running_max)]
        
        chart_data = {
            'dates': dates,
            'portfolio_values': portfolio_values,
            'daily_returns': daily_returns,
            'cumulative_returns': cumulative_returns,
            'drawdowns': drawdowns
        }
        
        # Add benchmark data if available
        benchmark_values = [float(snapshot.benchmark_value) for snapshot in snapshots if snapshot.benchmark_value]
        if benchmark_values and len(benchmark_values) == len(portfolio_values):
            chart_data['benchmark_values'] = benchmark_values
        
        serializer = BacktestPerformanceChartSerializer(chart_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def trades(self, request, pk=None):
        """Get trades for this backtest."""
        backtest = self.get_object()
        trades = backtest.trades.select_related('asset').order_by('date', 'created_at')
        
        # Apply pagination
        page = self.paginate_queryset(trades)
        if page is not None:
            serializer = BacktestTradeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BacktestTradeSerializer(trades, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def snapshots(self, request, pk=None):
        """Get portfolio snapshots for this backtest."""
        backtest = self.get_object()
        snapshots = backtest.portfolio_snapshots.order_by('date')
        
        # Apply pagination
        page = self.paginate_queryset(snapshots)
        if page is not None:
            serializer = BacktestPortfolioSnapshotSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BacktestPortfolioSnapshotSerializer(snapshots, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for user's backtests."""
        user_backtests = self.get_queryset()
        
        # Basic counts
        total_backtests = user_backtests.count()
        status_counts = user_backtests.aggregate(
            completed=Count('id', filter=Q(status='completed')),
            running=Count('id', filter=Q(status='running')),
            failed=Count('id', filter=Q(status='failed'))
        )
        
        completed_backtests = user_backtests.filter(
            status='completed',
            result__isnull=False
        ).select_related('result')
        
        summary_data = {
            'total_backtests': total_backtests,
            'completed_backtests': status_counts['completed'],
            'running_backtests': status_counts['running'],
            'failed_backtests': status_counts['failed']
        }
        
        if completed_backtests.exists():
            # Calculate averages
            avg_data = completed_backtests.aggregate(
                avg_return=Avg('result__total_return'),
                avg_sharpe=Avg('result__sharpe_ratio')
            )
            
            summary_data.update({
                'average_return': float(avg_data['avg_return']) if avg_data['avg_return'] else None,
                'average_sharpe_ratio': float(avg_data['avg_sharpe']) if avg_data['avg_sharpe'] else None
            })
            
            # Find best and worst performing
            best_backtest = completed_backtests.order_by('-result__total_return').first()
            worst_backtest = completed_backtests.order_by('result__total_return').first()
            
            if best_backtest:
                summary_data['best_performing_backtest'] = {
                    'id': best_backtest.id,
                    'name': best_backtest.name,
                    'strategy_name': best_backtest.strategy.name,
                    'total_return': float(best_backtest.result.total_return),
                    'sharpe_ratio': float(best_backtest.result.sharpe_ratio) if best_backtest.result.sharpe_ratio else None
                }
            
            if worst_backtest:
                summary_data['worst_performing_backtest'] = {
                    'id': worst_backtest.id,
                    'name': worst_backtest.name,
                    'strategy_name': worst_backtest.strategy.name,
                    'total_return': float(worst_backtest.result.total_return),
                    'sharpe_ratio': float(worst_backtest.result.sharpe_ratio) if worst_backtest.result.sharpe_ratio else None
                }
        
        serializer = BacktestSummarySerializer(summary_data)
        return Response(serializer.data)


class BacktestResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing backtest results."""
    
    serializer_class = BacktestResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return results for current user's backtests."""
        return BacktestResult.objects.filter(
            backtest__strategy__user=self.request.user
        ).select_related('backtest', 'backtest__strategy')


class BacktestComparisonView(viewsets.GenericViewSet):
    """ViewSet for comparing multiple backtests."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def compare(self, request):
        """Compare multiple backtests."""
        backtest_ids = request.data.get('backtest_ids', [])
        
        if not backtest_ids or len(backtest_ids) < 2:
            return Response(
                {'error': 'At least 2 backtest IDs required for comparison'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(backtest_ids) > 10:
            return Response(
                {'error': 'Maximum 10 backtests can be compared at once'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get backtests
        backtests = Backtest.objects.filter(
            id__in=backtest_ids,
            strategy__user=request.user,
            status='completed',
            result__isnull=False
        ).select_related('strategy', 'result')
        
        if backtests.count() != len(backtest_ids):
            return Response(
                {'error': 'Some backtests not found or not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare comparison data
        comparison_data = {
            'backtests': [],
            'metrics_comparison': {}
        }
        
        metrics = [
            'total_return', 'annualized_return', 'volatility', 'sharpe_ratio',
            'max_drawdown', 'var_95', 'calmar_ratio', 'win_rate', 'total_trades'
        ]
        
        for backtest in backtests:
            backtest_data = {
                'id': backtest.id,
                'name': backtest.name,
                'strategy_name': backtest.strategy.name,
                'start_date': backtest.start_date,
                'end_date': backtest.end_date,
                'metrics': {}
            }
            
            # Extract metrics
            for metric in metrics:
                value = getattr(backtest.result, metric, None)
                if value is not None:
                    backtest_data['metrics'][metric] = float(value)
                else:
                    backtest_data['metrics'][metric] = None
            
            comparison_data['backtests'].append(backtest_data)
        
        # Calculate summary statistics for each metric
        for metric in metrics:
            values = [bt['metrics'][metric] for bt in comparison_data['backtests'] if bt['metrics'][metric] is not None]
            
            if values:
                comparison_data['metrics_comparison'][metric] = {
                    'min': min(values),
                    'max': max(values),
                    'average': sum(values) / len(values),
                    'best_backtest': max(comparison_data['backtests'], key=lambda x: x['metrics'][metric] if x['metrics'][metric] is not None else float('-inf'))['name'],
                    'worst_backtest': min(comparison_data['backtests'], key=lambda x: x['metrics'][metric] if x['metrics'][metric] is not None else float('inf'))['name']
                }
        
        return Response(comparison_data)


# Quick backtest creation endpoint
@action(detail=False, methods=['post'])
def quick_backtest(request):
    """Create and run a quick backtest with minimal configuration."""
    
    # Validate required parameters
    required_fields = ['strategy_type', 'asset_symbols', 'start_date', 'end_date']
    for field in required_fields:
        if field not in request.data:
            return Response(
                {'error': f'Field "{field}" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        # Create temporary strategy
        from ..services import create_strategy
        
        strategy = create_strategy(
            user=request.user,
            name=f"Quick {request.data['strategy_type']} - {timezone.now().strftime('%Y%m%d_%H%M%S')}",
            strategy_type=request.data['strategy_type'],
            parameters=request.data.get('parameters', {}),
            asset_symbols=request.data['asset_symbols'],
            initial_capital=request.data.get('initial_capital', 100000.0),
            max_position_size=request.data.get('max_position_size', 0.1)
        )
        
        # Create backtest
        benchmark_asset = None
        if request.data.get('benchmark_symbol'):
            try:
                benchmark_asset = Asset.objects.get(symbol=request.data['benchmark_symbol'])
            except Asset.DoesNotExist:
                pass
        
        backtest = Backtest.objects.create(
            strategy=strategy,
            name=f"Quick Backtest - {strategy.name}",
            start_date=request.data['start_date'],
            end_date=request.data['end_date'],
            benchmark_asset=benchmark_asset,
            transaction_costs=request.data.get('transaction_costs', 0.001),
            slippage=request.data.get('slippage', 0.0005)
        )
        
        # Run backtest
        engine = BacktestEngine()
        result = engine.run_backtest(backtest)
        
        # Return results
        backtest.refresh_from_db()
        serializer = BacktestSerializer(backtest)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Quick backtest failed: {str(e)}")
        return Response(
            {'error': f'Quick backtest failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )