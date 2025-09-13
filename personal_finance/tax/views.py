"""API views for tax functionality."""

import logging
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Graceful import handling for missing models
try:
    from personal_finance.portfolios.models import Portfolio
except ImportError:
    Portfolio = None
    
from .models import (
    TaxYear, TaxLot, CapitalGainLoss, DividendIncome,
    TaxLossHarvestingOpportunity, TaxOptimizationRecommendation, TaxReport
)
from .serializers import (
    TaxYearSerializer, TaxLotSerializer, CapitalGainLossSerializer,
    DividendIncomeSerializer, TaxLossHarvestingOpportunitySerializer,
    TaxOptimizationRecommendationSerializer, TaxReportSerializer,
    TaxSummarySerializer, TaxCalculationRequestSerializer,
    LossHarvestingAnalysisSerializer
)
from .services import TaxCalculationService, TaxLossHarvestingService, TaxOptimizationService
from .report_service import TaxReportService

User = get_user_model()
logger = logging.getLogger(__name__)


class TaxYearViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for TaxYear model - read-only."""
    
    serializer_class = TaxYearSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TaxYear.objects.all().order_by('-year')


class TaxLotViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for TaxLot model - read-only."""
    
    serializer_class = TaxLotSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['position__portfolio', 'position__asset', 'acquisition_date']
    
    def get_queryset(self):
        """Filter tax lots to user's positions only."""
        return TaxLot.objects.filter(
            position__portfolio__user=self.request.user
        ).select_related(
            'position__asset', 'position__portfolio', 'transaction'
        ).order_by('-acquisition_date')


class CapitalGainLossViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CapitalGainLoss model - read-only."""
    
    serializer_class = CapitalGainLossSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['tax_year', 'term', 'position__portfolio', 'position__asset', 'sale_date']
    
    def get_queryset(self):
        """Filter capital gains/losses to user's transactions only."""
        return CapitalGainLoss.objects.filter(
            user=self.request.user
        ).select_related(
            'tax_year', 'position__asset', 'position__portfolio', 'transaction', 'tax_lot'
        ).order_by('-sale_date')


class DividendIncomeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for DividendIncome model - read-only."""
    
    serializer_class = DividendIncomeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['tax_year', 'dividend_type', 'position__portfolio', 'position__asset', 'payment_date']
    
    def get_queryset(self):
        """Filter dividend income to user's positions only."""
        return DividendIncome.objects.filter(
            user=self.request.user
        ).select_related(
            'tax_year', 'position__asset', 'position__portfolio'
        ).order_by('-payment_date')


class TaxLossHarvestingOpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for TaxLossHarvestingOpportunity model - read-only."""
    
    serializer_class = TaxLossHarvestingOpportunitySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'tax_year', 'position__portfolio', 'position__asset']
    
    def get_queryset(self):
        """Filter opportunities to user's positions only."""
        return TaxLossHarvestingOpportunity.objects.filter(
            user=self.request.user
        ).select_related(
            'position__asset', 'position__portfolio', 'tax_year'
        ).order_by('-potential_loss_amount')
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Analyze portfolios for tax loss harvesting opportunities."""
        serializer = LossHarvestingAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        minimum_loss = serializer.validated_data['minimum_loss_threshold']
        generate_recommendations = serializer.validated_data['generate_recommendations']
        
        try:
            loss_service = TaxLossHarvestingService()
            opportunities = loss_service.identify_loss_harvesting_opportunities(
                request.user, minimum_loss
            )
            
            if generate_recommendations and opportunities:
                loss_service.generate_loss_harvesting_recommendations(opportunities)
            
            # Serialize and return opportunities
            opportunity_serializer = TaxLossHarvestingOpportunitySerializer(
                opportunities, many=True
            )
            
            return Response({
                'opportunities_count': len(opportunities),
                'total_potential_loss': sum(opp.potential_loss_amount for opp in opportunities),
                'total_estimated_benefit': sum(
                    opp.tax_benefit_estimate or Decimal('0') for opp in opportunities
                ),
                'opportunities': opportunity_serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error analyzing loss harvesting opportunities: {str(e)}")
            return Response(
                {'error': 'Failed to analyze opportunities'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaxOptimizationRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for TaxOptimizationRecommendation model."""
    
    serializer_class = TaxOptimizationRecommendationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['recommendation_type', 'priority', 'is_implemented', 'tax_year']
    
    def get_queryset(self):
        """Filter recommendations to user only."""
        return TaxOptimizationRecommendation.objects.filter(
            user=self.request.user
        ).select_related(
            'tax_year', 'portfolio'
        ).order_by('-estimated_tax_savings', '-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_implemented(self, request, pk=None):
        """Mark a recommendation as implemented."""
        recommendation = self.get_object()
        recommendation.is_implemented = True
        recommendation.implementation_date = timezone.now().date()
        recommendation.implementation_notes = request.data.get('notes', '')
        recommendation.save()
        
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate tax optimization recommendations."""
        year = request.data.get('year')
        tax_year = None
        
        if year:
            try:
                tax_year = TaxYear.objects.get(year=year)
            except TaxYear.DoesNotExist:
                return Response(
                    {'error': f'Tax year {year} not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            optimization_service = TaxOptimizationService()
            recommendations = optimization_service.generate_tax_optimization_recommendations(
                request.user, tax_year
            )
            
            # Save recommendations to database
            for rec in recommendations:
                rec.save()
            
            serializer = TaxOptimizationRecommendationSerializer(recommendations, many=True)
            
            return Response({
                'recommendations_count': len(recommendations),
                'total_potential_savings': sum(
                    rec.estimated_tax_savings or Decimal('0') for rec in recommendations
                ),
                'recommendations': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {str(e)}")
            return Response(
                {'error': 'Failed to generate recommendations'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaxReportViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for TaxReport model."""
    
    serializer_class = TaxReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['report_type', 'tax_year', 'generated_date']
    
    def get_queryset(self):
        """Filter reports to user only."""
        return TaxReport.objects.filter(
            user=self.request.user
        ).select_related('tax_year').order_by('-generated_date')
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate tax reports."""
        year = request.data.get('year', timezone.now().year)
        report_type = request.data.get('report_type', 'all')
        
        try:
            # Get or create tax year
            tax_year, created = TaxYear.objects.get_or_create(
                year=year,
                defaults={
                    'filing_deadline': f"{year + 1}-04-15",
                    'standard_deduction_single': 13850,
                    'standard_deduction_married': 27700,
                    'long_term_capital_gains_thresholds': {
                        '0': {'min': 0, 'max': 44625, 'rate': 0.0},
                        '15': {'min': 44626, 'max': 492300, 'rate': 0.15},
                        '20': {'min': 492301, 'max': None, 'rate': 0.20}
                    }
                }
            )
            
            report_service = TaxReportService()
            
            if report_type == 'all':
                reports = report_service.generate_all_tax_reports(request.user, tax_year)
            elif report_type == 'schedule_d':
                reports = {'schedule_d': report_service.generate_schedule_d_report(request.user, tax_year)}
            elif report_type == 'form_1099_div':
                reports = {'form_1099_div': report_service.generate_dividend_report(request.user, tax_year)}
            elif report_type == 'form_8949':
                reports = {'form_8949': report_service.generate_form_8949_report(request.user, tax_year)}
            elif report_type == 'tax_summary':
                reports = {'tax_summary': report_service.generate_tax_summary_report(request.user, tax_year)}
            elif report_type == 'loss_carryforward':
                reports = {'loss_carryforward': report_service.generate_loss_carryforward_report(request.user, tax_year)}
            else:
                return Response(
                    {'error': 'Invalid report type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Serialize reports
            report_data = {}
            for report_type_key, report in reports.items():
                serializer = TaxReportSerializer(report)
                report_data[report_type_key] = serializer.data
            
            return Response({
                'tax_year': year,
                'reports_generated': len(reports),
                'reports': report_data
            })
            
        except Exception as e:
            logger.error(f"Error generating tax reports: {str(e)}")
            return Response(
                {'error': 'Failed to generate reports'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaxAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for tax analytics and calculations."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get comprehensive tax summary for user."""
        year = request.query_params.get('year', timezone.now().year)
        portfolio_id = request.query_params.get('portfolio_id')
        
        try:
            # Get or create tax year
            tax_year, _ = TaxYear.objects.get_or_create(
                year=year,
                defaults={
                    'filing_deadline': f"{year + 1}-04-15",
                    'standard_deduction_single': 13850,
                    'standard_deduction_married': 27700,
                    'long_term_capital_gains_thresholds': {}
                }
            )
            
            portfolio = None
            if portfolio_id:
                try:
                    portfolio = Portfolio.objects.get(
                        id=portfolio_id, user=request.user
                    )
                except Portfolio.DoesNotExist:
                    return Response(
                        {'error': 'Portfolio not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            tax_service = TaxCalculationService()
            
            # Calculate capital gains/losses
            capital_gains = tax_service.calculate_capital_gains_losses(
                request.user, tax_year, portfolio
            )
            
            # Calculate dividend income
            dividends = tax_service.calculate_dividend_income(
                request.user, tax_year, portfolio
            )
            
            # Get tax optimization data
            loss_opportunities = TaxLossHarvestingOpportunity.objects.filter(
                user=request.user,
                tax_year=tax_year
            ).count()
            
            recommendations = TaxOptimizationRecommendation.objects.filter(
                user=request.user,
                tax_year=tax_year,
                is_implemented=False
            ).count()
            
            # Calculate estimated tax liability
            net_gains = capital_gains['totals']['net_capital_gain_loss']
            total_dividends = dividends['total_dividends']
            
            estimated_tax = max(net_gains * Decimal('0.15'), Decimal('0'))
            estimated_dividend_tax = total_dividends * Decimal('0.15')
            
            summary_data = {
                'tax_year': year,
                'portfolio': portfolio.name if portfolio else 'All Portfolios',
                'capital_gains': capital_gains,
                'dividends': dividends,
                'tax_estimates': {
                    'capital_gains_tax': estimated_tax,
                    'dividend_tax': estimated_dividend_tax,
                    'total_estimated_tax': estimated_tax + estimated_dividend_tax
                },
                'optimization': {
                    'loss_opportunities': loss_opportunities,
                    'pending_recommendations': recommendations
                },
                'summary_metrics': {
                    'total_investment_income': net_gains + total_dividends,
                    'taxable_events': capital_gains['transactions_count'] + dividends['payment_count']
                }
            }
            
            serializer = TaxSummarySerializer(data=summary_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error generating tax summary: {str(e)}")
            return Response(
                {'error': 'Failed to generate tax summary'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Trigger tax calculations for user transactions."""
        serializer = TaxCalculationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        year = serializer.validated_data.get('year')
        portfolio_id = serializer.validated_data.get('portfolio_id')
        reprocess = serializer.validated_data.get('reprocess', False)
        
        try:
            # Import here to avoid circular imports
            from personal_finance.portfolios.models import Transaction
        except ImportError:
            # Handle case where portfolios models are not available
            return Response({
                'error': 'Portfolio models are not available. Please ensure portfolios app is properly migrated.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        # Build query for transactions
        queryset = Transaction.objects.filter(
            position__portfolio__user=request.user
        ).select_related('position__asset', 'position__portfolio')
            
        if year:
            queryset = queryset.filter(date__year=year)
            
        if portfolio_id:
            try:
                portfolio = Portfolio.objects.get(
                    id=portfolio_id, user=request.user
                )
                queryset = queryset.filter(position__portfolio=portfolio)
            except Portfolio.DoesNotExist:
                return Response(
                    {'error': 'Portfolio not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        # Process transactions
        tax_service = TaxCalculationService()
        processed_count = 0
        error_count = 0
        
        for transaction in queryset:
            try:
                # Skip if already processed and not reprocessing
                if not reprocess and self._is_transaction_processed(transaction):
                    continue
                
                tax_service.process_transaction_for_taxes(transaction)
                processed_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing transaction {transaction.id}: {str(e)}")
        
        return Response({
            'processed_transactions': processed_count,
            'errors': error_count,
            'total_transactions': queryset.count(),
            'reprocessed': reprocess
        })
    
    def _is_transaction_processed(self, transaction):
        """Check if a transaction has already been processed for taxes."""
        if transaction.transaction_type == 'buy':
            return TaxLot.objects.filter(transaction=transaction).exists()
        elif transaction.transaction_type == 'sell':
            return CapitalGainLoss.objects.filter(transaction=transaction).exists()
        elif transaction.transaction_type == 'dividend':
            return DividendIncome.objects.filter(
                position=transaction.position,
                payment_date=transaction.date,
                total_amount=transaction.quantity * transaction.price
            ).exists()
        return False