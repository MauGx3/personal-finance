"""API views for portfolio management."""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Any

from django.db.models import Q, Prefetch
from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..models import Portfolio, Position, Transaction, PortfolioSnapshot
from ..serializers import (
    PortfolioListSerializer, PortfolioDetailSerializer, PortfolioCreateUpdateSerializer,
    PositionSerializer, PositionCreateUpdateSerializer,
    TransactionSerializer, TransactionCreateUpdateSerializer,
    PortfolioSnapshotSerializer, PerformanceMetricsSerializer, AllocationDataSerializer
)
from personal_finance.analytics.services import PerformanceAnalytics, TechnicalIndicators
from personal_finance.assets.models import Asset


class PortfolioViewSet(viewsets.ModelViewSet):
    """ViewSet for portfolio management with comprehensive analytics."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return portfolios owned by the current user."""
        return Portfolio.objects.filter(user=self.request.user).prefetch_related(
            'positions__asset'
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return PortfolioListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PortfolioCreateUpdateSerializer
        else:
            return PortfolioDetailSerializer
    
    def perform_create(self, serializer):
        """Create portfolio with current user as owner."""
        serializer.save(user=self.request.user)
    
    @extend_schema(
        summary="Get portfolio performance metrics",
        description="Calculate comprehensive performance metrics for a portfolio over a specified time period.",
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date for analysis (default: 1 year ago)',
                required=False
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date for analysis (default: today)',
                required=False
            ),
            OpenApiParameter(
                name='benchmark',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Benchmark symbol for comparison (e.g., SPY)',
                required=False
            ),
        ],
        responses={200: PerformanceMetricsSerializer}
    )
    @action(detail=True, methods=['get'])
    def performance_metrics(self, request: Request, pk=None):
        """Get comprehensive performance metrics for a portfolio."""
        portfolio = self.get_object()
        
        # Parse date parameters
        end_date = self._parse_date_param(request, 'end_date', timezone.now().date())
        start_date = self._parse_date_param(
            request, 'start_date', end_date - timedelta(days=365)
        )
        benchmark_symbol = request.query_params.get('benchmark', 'SPY')
        
        try:
            analytics = PerformanceAnalytics()
            metrics = analytics.calculate_portfolio_metrics(
                portfolio, start_date, end_date
            )
            
            # Add benchmark comparison if requested
            if benchmark_symbol:
                try:
                    benchmark_asset = Asset.objects.get(symbol=benchmark_symbol)
                    benchmark_metrics = analytics.calculate_asset_metrics(
                        benchmark_asset, start_date, end_date
                    )
                    metrics['benchmark'] = {
                        'symbol': benchmark_symbol,
                        'return': benchmark_metrics.get('total_return'),
                        'volatility': benchmark_metrics.get('volatility'),
                        'sharpe_ratio': benchmark_metrics.get('sharpe_ratio')
                    }
                except Asset.DoesNotExist:
                    metrics['benchmark'] = None
            
            # Add time period information
            metrics.update({
                'start_date': start_date,
                'end_date': end_date,
                'days_analyzed': (end_date - start_date).days
            })
            
            serializer = PerformanceMetricsSerializer(data=metrics)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to calculate metrics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get portfolio allocation data",
        description="Get detailed allocation data for portfolio visualization.",
        parameters=[
            OpenApiParameter(
                name='group_by',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Group allocation by: asset_type, sector, or individual',
                required=False
            ),
        ],
        responses={200: AllocationDataSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def allocation(self, request: Request, pk=None):
        """Get portfolio allocation data for visualization."""
        portfolio = self.get_object()
        group_by = request.query_params.get('group_by', 'individual')
        
        try:
            positions = portfolio.positions.filter(is_active=True).select_related('asset')
            total_value = portfolio.total_value
            
            allocation_data = []
            
            if group_by == 'individual':
                # Individual asset allocation
                for position in positions:
                    if position.current_value > 0:
                        allocation_data.append({
                            'asset_symbol': position.asset.symbol,
                            'asset_name': position.asset.name or position.asset.symbol,
                            'asset_type': position.asset.asset_type,
                            'sector': position.asset.sector or 'Unknown',
                            'value': position.current_value,
                            'percentage': (position.current_value / total_value * 100) if total_value > 0 else Decimal('0'),
                            'quantity': position.quantity,
                            'average_cost': position.average_cost,
                            'current_price': position.asset.current_price or Decimal('0'),
                            'unrealized_return': position.unrealized_gain_loss,
                            'unrealized_return_percentage': position.unrealized_return_percentage or Decimal('0')
                        })
            
            elif group_by == 'asset_type':
                # Group by asset type
                type_groups = {}
                for position in positions:
                    asset_type = position.asset.asset_type
                    if asset_type not in type_groups:
                        type_groups[asset_type] = {
                            'value': Decimal('0'),
                            'unrealized_return': Decimal('0'),
                            'count': 0
                        }
                    type_groups[asset_type]['value'] += position.current_value
                    type_groups[asset_type]['unrealized_return'] += position.unrealized_gain_loss
                    type_groups[asset_type]['count'] += 1
                
                for asset_type, data in type_groups.items():
                    allocation_data.append({
                        'asset_symbol': asset_type,
                        'asset_name': dict(Asset.ASSET_TYPE_CHOICES).get(asset_type, asset_type),
                        'asset_type': asset_type,
                        'sector': 'Multiple',
                        'value': data['value'],
                        'percentage': (data['value'] / total_value * 100) if total_value > 0 else Decimal('0'),
                        'quantity': data['count'],
                        'average_cost': Decimal('0'),
                        'current_price': Decimal('0'),
                        'unrealized_return': data['unrealized_return'],
                        'unrealized_return_percentage': Decimal('0')
                    })
            
            elif group_by == 'sector':
                # Group by sector
                sector_groups = {}
                for position in positions:
                    sector = position.asset.sector or 'Unknown'
                    if sector not in sector_groups:
                        sector_groups[sector] = {
                            'value': Decimal('0'),
                            'unrealized_return': Decimal('0'),
                            'count': 0
                        }
                    sector_groups[sector]['value'] += position.current_value
                    sector_groups[sector]['unrealized_return'] += position.unrealized_gain_loss
                    sector_groups[sector]['count'] += 1
                
                for sector, data in sector_groups.items():
                    allocation_data.append({
                        'asset_symbol': sector.upper().replace(' ', '_'),
                        'asset_name': sector,
                        'asset_type': 'SECTOR',
                        'sector': sector,
                        'value': data['value'],
                        'percentage': (data['value'] / total_value * 100) if total_value > 0 else Decimal('0'),
                        'quantity': data['count'],
                        'average_cost': Decimal('0'),
                        'current_price': Decimal('0'),
                        'unrealized_return': data['unrealized_return'],
                        'unrealized_return_percentage': Decimal('0')
                    })
            
            serializer = AllocationDataSerializer(allocation_data, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get allocation data: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get portfolio historical performance",
        description="Get historical performance data for portfolio charts.",
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date for data (default: 1 year ago)',
                required=False
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date for data (default: today)',
                required=False
            ),
            OpenApiParameter(
                name='frequency',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Data frequency: daily, weekly, monthly (default: daily)',
                required=False
            ),
        ]
    )
    @action(detail=True, methods=['get'])
    def historical_performance(self, request: Request, pk=None):
        """Get historical performance data for charts."""
        portfolio = self.get_object()
        
        # Parse parameters
        end_date = self._parse_date_param(request, 'end_date', timezone.now().date())
        start_date = self._parse_date_param(
            request, 'start_date', end_date - timedelta(days=365)
        )
        frequency = request.query_params.get('frequency', 'daily')
        
        try:
            # Get portfolio snapshots
            snapshots = PortfolioSnapshot.objects.filter(
                portfolio=portfolio,
                snapshot_date__gte=start_date,
                snapshot_date__lte=end_date
            ).order_by('snapshot_date')
            
            data = []
            for snapshot in snapshots:
                data.append({
                    'date': snapshot.snapshot_date,
                    'total_value': snapshot.total_value,
                    'total_cost_basis': snapshot.total_cost_basis,
                    'total_return': snapshot.total_return,
                    'return_percentage': snapshot.return_percentage,
                    'cash_balance': snapshot.cash_balance
                })
            
            return Response({
                'start_date': start_date,
                'end_date': end_date,
                'frequency': frequency,
                'data': data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get historical data: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _parse_date_param(self, request: Request, param_name: str, default: date) -> date:
        """Parse date parameter from request."""
        date_str = request.query_params.get(param_name)
        if date_str:
            try:
                return date.fromisoformat(date_str)
            except ValueError:
                pass
        return default


class PositionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing portfolio positions."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return positions from user's portfolios."""
        return Position.objects.filter(
            portfolio__user=self.request.user
        ).select_related('portfolio', 'asset').order_by('-modified')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return PositionCreateUpdateSerializer
        else:
            return PositionSerializer
    
    @extend_schema(
        summary="Get positions by portfolio",
        description="Filter positions by portfolio ID.",
        parameters=[
            OpenApiParameter(
                name='portfolio_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Portfolio ID to filter positions',
                required=False
            ),
            OpenApiParameter(
                name='active_only',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Show only active positions (default: true)',
                required=False
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs):
        """List positions with optional filtering."""
        queryset = self.get_queryset()
        
        # Filter by portfolio
        portfolio_id = request.query_params.get('portfolio_id')
        if portfolio_id:
            queryset = queryset.filter(portfolio_id=portfolio_id)
        
        # Filter by active status
        active_only = request.query_params.get('active_only', 'true').lower() == 'true'
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing investment transactions."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return transactions from user's positions."""
        return Transaction.objects.filter(
            position__portfolio__user=self.request.user
        ).select_related('position__portfolio', 'position__asset').order_by('-transaction_date', '-created')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return TransactionCreateUpdateSerializer
        else:
            return TransactionSerializer
    
    @extend_schema(
        summary="Get transactions by position or portfolio",
        description="Filter transactions by position or portfolio ID.",
        parameters=[
            OpenApiParameter(
                name='position_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Position ID to filter transactions',
                required=False
            ),
            OpenApiParameter(
                name='portfolio_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Portfolio ID to filter transactions',
                required=False
            ),
            OpenApiParameter(
                name='transaction_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Transaction type to filter (BUY, SELL, DIV, etc.)',
                required=False
            ),
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date for transaction range',
                required=False
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date for transaction range',
                required=False
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs):
        """List transactions with optional filtering."""
        queryset = self.get_queryset()
        
        # Filter by position
        position_id = request.query_params.get('position_id')
        if position_id:
            queryset = queryset.filter(position_id=position_id)
        
        # Filter by portfolio
        portfolio_id = request.query_params.get('portfolio_id')
        if portfolio_id:
            queryset = queryset.filter(position__portfolio_id=portfolio_id)
        
        # Filter by transaction type
        transaction_type = request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type.upper())
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        if start_date:
            try:
                start_date = date.fromisoformat(start_date)
                queryset = queryset.filter(transaction_date__gte=start_date)
            except ValueError:
                pass
        
        end_date = request.query_params.get('end_date')
        if end_date:
            try:
                end_date = date.fromisoformat(end_date)
                queryset = queryset.filter(transaction_date__lte=end_date)
            except ValueError:
                pass
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PortfolioSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing portfolio performance snapshots."""
    
    serializer_class = PortfolioSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return snapshots from user's portfolios."""
        return PortfolioSnapshot.objects.filter(
            portfolio__user=self.request.user
        ).select_related('portfolio').order_by('-snapshot_date')
    
    @extend_schema(
        summary="Get snapshots by portfolio",
        description="Filter snapshots by portfolio ID and date range.",
        parameters=[
            OpenApiParameter(
                name='portfolio_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Portfolio ID to filter snapshots',
                required=False
            ),
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date for snapshot range',
                required=False
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date for snapshot range',
                required=False
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs):
        """List snapshots with optional filtering."""
        queryset = self.get_queryset()
        
        # Filter by portfolio
        portfolio_id = request.query_params.get('portfolio_id')
        if portfolio_id:
            queryset = queryset.filter(portfolio_id=portfolio_id)
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        if start_date:
            try:
                start_date = date.fromisoformat(start_date)
                queryset = queryset.filter(snapshot_date__gte=start_date)
            except ValueError:
                pass
        
        end_date = request.query_params.get('end_date')
        if end_date:
            try:
                end_date = date.fromisoformat(end_date)
                queryset = queryset.filter(snapshot_date__lte=end_date)
            except ValueError:
                pass
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)