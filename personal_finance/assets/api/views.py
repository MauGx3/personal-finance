"""API views for asset management."""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Any

from django.db.models import Q, Avg
from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..models import Asset, PriceHistory, Holding, Portfolio as LegacyPortfolio
from ..serializers import (
    AssetListSerializer, AssetDetailSerializer, AssetCreateUpdateSerializer,
    PriceHistorySerializer, AssetPerformanceSerializer, TechnicalIndicatorsSerializer,
    AssetSearchSerializer, AssetSerializer, PortfolioSerializer, HoldingSerializer
)
from personal_finance.analytics.services import PerformanceAnalytics, TechnicalIndicators
from personal_finance.data_sources.services import data_source_manager


class AssetViewSet(viewsets.ModelViewSet):
    """ViewSet for asset management with comprehensive market data."""
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Return active assets with optional filtering."""
        queryset = Asset.objects.filter(is_active=True)
        
        # Filter by asset type
        asset_type = self.request.query_params.get('asset_type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        
        # Filter by exchange
        exchange = self.request.query_params.get('exchange')
        if exchange:
            queryset = queryset.filter(exchange=exchange)
        
        # Filter by sector
        sector = self.request.query_params.get('sector')
        if sector:
            queryset = queryset.filter(sector=sector)
        
        # Search by symbol or name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(symbol__icontains=search) | Q(name__icontains=search)
            )
        
        return queryset.order_by('symbol')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return AssetListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AssetCreateUpdateSerializer
        else:
            return AssetDetailSerializer
    
    @extend_schema(
        summary="Search for assets",
        description="Search assets by symbol, name, or other criteria.",
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query (symbol, name, ISIN, etc.)',
                required=True
            ),
            OpenApiParameter(
                name='asset_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by asset type',
                required=False
            ),
            OpenApiParameter(
                name='exchange',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by exchange',
                required=False
            ),
            OpenApiParameter(
                name='limit',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum number of results (default: 50)',
                required=False
            ),
        ],
        responses={200: AssetSearchSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def search(self, request: Request):
        """Search for assets with comprehensive filtering."""
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Search query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start with basic search
        queryset = Asset.objects.filter(is_active=True)
        
        # Apply search filters
        search_filters = (
            Q(symbol__icontains=query) |
            Q(name__icontains=query) |
            Q(isin__icontains=query) |
            Q(cusip__icontains=query)
        )
        queryset = queryset.filter(search_filters)
        
        # Apply additional filters
        asset_type = request.query_params.get('asset_type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        
        exchange = request.query_params.get('exchange')
        if exchange:
            queryset = queryset.filter(exchange=exchange)
        
        # Limit results
        limit = int(request.query_params.get('limit', 50))
        queryset = queryset[:limit]
        
        # Prepare search results
        results = []
        for asset in queryset:
            results.append({
                'symbol': asset.symbol,
                'name': asset.name or '',
                'asset_type': asset.asset_type,
                'exchange': asset.exchange or '',
                'currency': asset.currency,
                'current_price': asset.current_price or Decimal('0'),
                'market_cap': asset.market_cap or Decimal('0'),
                'sector': asset.sector or ''
            })
        
        serializer = AssetSearchSerializer(results, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get asset performance metrics",
        description="Calculate comprehensive performance metrics for an asset.",
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
        responses={200: AssetPerformanceSerializer}
    )
    @action(detail=True, methods=['get'])
    def performance_metrics(self, request: Request, pk=None):
        """Get comprehensive performance metrics for an asset."""
        asset = self.get_object()
        
        # Parse date parameters
        end_date = self._parse_date_param(request, 'end_date', timezone.now().date())
        start_date = self._parse_date_param(
            request, 'start_date', end_date - timedelta(days=365)
        )
        benchmark_symbol = request.query_params.get('benchmark')
        
        try:
            analytics = PerformanceAnalytics()
            metrics = analytics.calculate_asset_metrics(asset, start_date, end_date)
            
            # Add benchmark comparison if requested
            if benchmark_symbol:
                try:
                    benchmark_asset = Asset.objects.get(symbol=benchmark_symbol)
                    benchmark_metrics = analytics.calculate_asset_metrics(
                        benchmark_asset, start_date, end_date
                    )
                    metrics['beta'] = analytics.calculate_beta(asset, benchmark_asset, start_date, end_date)
                except Asset.DoesNotExist:
                    metrics['beta'] = None
            
            # Add time period information
            metrics.update({
                'start_date': start_date,
                'end_date': end_date,
                'days_analyzed': (end_date - start_date).days
            })
            
            serializer = AssetPerformanceSerializer(data=metrics)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to calculate metrics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get technical indicators",
        description="Calculate technical indicators for an asset.",
        parameters=[
            OpenApiParameter(
                name='period',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of days for calculation (default: 200)',
                required=False
            ),
        ],
        responses={200: TechnicalIndicatorsSerializer}
    )
    @action(detail=True, methods=['get'])
    def technical_indicators(self, request: Request, pk=None):
        """Get technical indicators for an asset."""
        asset = self.get_object()
        period = int(request.query_params.get('period', 200))
        
        try:
            indicators = TechnicalIndicators()
            data = indicators.calculate_indicators(asset, period)
            
            serializer = TechnicalIndicatorsSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to calculate indicators: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get price history",
        description="Get historical price data for an asset.",
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date for price data (default: 1 year ago)',
                required=False
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date for price data (default: today)',
                required=False
            ),
            OpenApiParameter(
                name='frequency',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Data frequency: daily, weekly, monthly (default: daily)',
                required=False
            ),
        ],
        responses={200: PriceHistorySerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def price_history(self, request: Request, pk=None):
        """Get historical price data for an asset."""
        asset = self.get_object()
        
        # Parse parameters
        end_date = self._parse_date_param(request, 'end_date', timezone.now().date())
        start_date = self._parse_date_param(
            request, 'start_date', end_date - timedelta(days=365)
        )
        frequency = request.query_params.get('frequency', 'daily')
        
        # Get price history
        queryset = PriceHistory.objects.filter(
            asset=asset,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # Apply frequency filtering if needed
        if frequency == 'weekly':
            # Get weekly data (every 7th day)
            queryset = queryset.filter(date__week_day=1)  # Mondays
        elif frequency == 'monthly':
            # Get monthly data (first trading day of each month)
            monthly_data = []
            current_month = None
            for price in queryset:
                if current_month != price.date.month:
                    monthly_data.append(price)
                    current_month = price.date.month
            queryset = monthly_data
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PriceHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PriceHistorySerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Update asset price",
        description="Manually update the current price for an asset.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'price': {'type': 'number', 'format': 'decimal'},
                    'volume': {'type': 'integer', 'minimum': 0},
                    'source': {'type': 'string', 'default': 'manual'}
                },
                'required': ['price']
            }
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def update_price(self, request: Request, pk=None):
        """Manually update the current price for an asset."""
        asset = self.get_object()
        
        try:
            price = Decimal(str(request.data.get('price')))
            volume = request.data.get('volume')
            source = request.data.get('source', 'manual')
            
            asset.update_price_data(
                price=price,
                volume=volume,
                source=source
            )
            
            serializer = AssetDetailSerializer(asset)
            return Response(serializer.data)
            
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Invalid price data: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to update price: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Refresh asset data",
        description="Refresh asset data from external data sources.",
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def refresh_data(self, request: Request, pk=None):
        """Refresh asset data from external data sources."""
        asset = self.get_object()
        
        try:
            # Get fresh data from data sources
            price_data = data_source_manager.get_current_price(asset.symbol)
            
            if price_data:
                asset.update_price_data(
                    price=price_data.current_price,
                    volume=price_data.volume,
                    day_high=price_data.day_high,
                    day_low=price_data.day_low,
                    source=price_data.source
                )
                
                # Also refresh basic asset info if available
                asset_info = data_source_manager.get_asset_info(asset.symbol)
                if asset_info:
                    if asset_info.get('name'):
                        asset.name = asset_info['name']
                    if asset_info.get('sector'):
                        asset.sector = asset_info['sector']
                    if asset_info.get('industry'):
                        asset.industry = asset_info['industry']
                    if asset_info.get('market_cap'):
                        asset.market_cap = asset_info['market_cap']
                    asset.save()
                
                serializer = AssetDetailSerializer(asset)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': 'Unable to fetch data from external sources'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
                
        except Exception as e:
            return Response(
                {'error': f'Failed to refresh data: {str(e)}'},
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


class PriceHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing price history data."""
    
    serializer_class = PriceHistorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Return price history with optional filtering."""
        queryset = PriceHistory.objects.all().select_related('asset')
        
        # Filter by asset
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        
        # Filter by asset symbol
        symbol = self.request.query_params.get('symbol')
        if symbol:
            queryset = queryset.filter(asset__symbol=symbol)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        if start_date:
            try:
                start_date = date.fromisoformat(start_date)
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            try:
                end_date = date.fromisoformat(end_date)
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        
        return queryset.order_by('-date')


# Legacy ViewSets for backward compatibility
class LegacyPortfolioViewSet(viewsets.ModelViewSet):
    """Legacy portfolio ViewSet for backward compatibility."""
    
    queryset = LegacyPortfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not serializer.validated_data.get("user"):
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class LegacyHoldingViewSet(viewsets.ModelViewSet):
    """Legacy holding ViewSet for backward compatibility."""
    
    queryset = Holding.objects.all()
    serializer_class = HoldingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not serializer.validated_data.get("user"):
            serializer.save(user=self.request.user)
        else:
            serializer.save()


# Maintain backward compatibility by aliasing legacy ViewSets
PortfolioViewSet = LegacyPortfolioViewSet
HoldingViewSet = LegacyHoldingViewSet
