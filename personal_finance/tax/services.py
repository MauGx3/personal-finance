"""Tax calculation and optimization services."""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone

# Graceful import handling for missing models
try:
    from personal_finance.portfolios.models import Portfolio, Position, Transaction
except ImportError:
    Portfolio = Position = Transaction = None
    
from .models import (
    TaxYear, TaxLot, CapitalGainLoss, DividendIncome,
    TaxLossHarvestingOpportunity, TaxOptimizationRecommendation, TaxReport
)

User = get_user_model()
logger = logging.getLogger(__name__)


class TaxCalculationService:
    """Comprehensive tax calculation service.
    
    Handles capital gains/losses, dividend income, and tax optimization
    calculations for personal finance portfolios.
    """
    
    def __init__(self):
        """Initialize tax calculation service."""
        self.current_date = timezone.now().date()
        
    def calculate_capital_gains_losses(
        self, 
        user: User, 
        tax_year: TaxYear,
        portfolio: Optional[Portfolio] = None
    ) -> Dict[str, Any]:
        """Calculate all capital gains and losses for a tax year.
        
        Args:
            user: User to calculate for
            tax_year: Tax year for calculations
            portfolio: Optional specific portfolio (all portfolios if None)
            
        Returns:
            Dict containing capital gains/losses breakdown
        """
        logger.info(f"Calculating capital gains/losses for {user.username} - {tax_year.year}")
        
        # Get all capital gains/losses for the tax year
        gains_losses = CapitalGainLoss.objects.filter(
            user=user,
            tax_year=tax_year
        )
        
        if portfolio:
            gains_losses = gains_losses.filter(position__portfolio=portfolio)
        
        # Aggregate by term
        short_term_gains = gains_losses.filter(
            term='short', gain_loss_amount__gt=0
        ).aggregate(total=Sum('gain_loss_amount'))['total'] or Decimal('0')
        
        short_term_losses = gains_losses.filter(
            term='short', gain_loss_amount__lt=0
        ).aggregate(total=Sum('gain_loss_amount'))['total'] or Decimal('0')
        
        long_term_gains = gains_losses.filter(
            term='long', gain_loss_amount__gt=0
        ).aggregate(total=Sum('gain_loss_amount'))['total'] or Decimal('0')
        
        long_term_losses = gains_losses.filter(
            term='long', gain_loss_amount__lt=0
        ).aggregate(total=Sum('gain_loss_amount'))['total'] or Decimal('0')
        
        # Calculate net amounts
        net_short_term = short_term_gains + short_term_losses  # losses are negative
        net_long_term = long_term_gains + long_term_losses
        
        # Calculate overall net capital gain/loss
        net_capital_gain_loss = net_short_term + net_long_term
        
        return {
            'short_term': {
                'gains': short_term_gains,
                'losses': abs(short_term_losses),
                'net': net_short_term
            },
            'long_term': {
                'gains': long_term_gains,
                'losses': abs(long_term_losses),
                'net': net_long_term
            },
            'totals': {
                'total_gains': short_term_gains + long_term_gains,
                'total_losses': abs(short_term_losses) + abs(long_term_losses),
                'net_capital_gain_loss': net_capital_gain_loss
            },
            'transactions_count': gains_losses.count()
        }
    
    def calculate_dividend_income(
        self, 
        user: User, 
        tax_year: TaxYear,
        portfolio: Optional[Portfolio] = None
    ) -> Dict[str, Any]:
        """Calculate dividend income for tax reporting.
        
        Args:
            user: User to calculate for
            tax_year: Tax year for calculations
            portfolio: Optional specific portfolio
            
        Returns:
            Dict containing dividend income breakdown
        """
        logger.info(f"Calculating dividend income for {user.username} - {tax_year.year}")
        
        dividends = DividendIncome.objects.filter(
            user=user,
            tax_year=tax_year
        )
        
        if portfolio:
            dividends = dividends.filter(position__portfolio=portfolio)
        
        # Calculate by dividend type
        qualified_dividends = dividends.filter(
            dividend_type='qualified'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        ordinary_dividends = dividends.filter(
            dividend_type='ordinary'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        capital_gain_distributions = dividends.filter(
            dividend_type='capital_gain'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        return_of_capital = dividends.filter(
            dividend_type='return_of_capital'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        total_dividends = qualified_dividends + ordinary_dividends
        total_distributions = capital_gain_distributions + return_of_capital
        
        return {
            'qualified_dividends': qualified_dividends,
            'ordinary_dividends': ordinary_dividends,
            'capital_gain_distributions': capital_gain_distributions,
            'return_of_capital': return_of_capital,
            'total_dividends': total_dividends,
            'total_distributions': total_distributions,
            'grand_total': total_dividends + total_distributions,
            'payment_count': dividends.count()
        }
    
    def process_transaction_for_taxes(self, transaction: Transaction) -> None:
        """Process a transaction for tax implications.
        
        Args:
            transaction: Transaction to process
        """
        if transaction.transaction_type == 'buy':
            self._create_tax_lot(transaction)
        elif transaction.transaction_type == 'sell':
            self._process_sale_transaction(transaction)
        elif transaction.transaction_type == 'dividend':
            self._process_dividend_transaction(transaction)
    
    def _create_tax_lot(self, transaction: Transaction) -> TaxLot:
        """Create a tax lot for a buy transaction.
        
        Args:
            transaction: Buy transaction
            
        Returns:
            Created TaxLot instance
        """
        # Calculate cost basis including fees
        cost_basis_per_share = transaction.price
        if transaction.fees:
            # Distribute fees across shares
            cost_basis_per_share += transaction.fees / transaction.quantity
        
        total_cost_basis = cost_basis_per_share * transaction.quantity
        
        tax_lot = TaxLot.objects.create(
            position=transaction.position,
            acquisition_date=transaction.date,
            original_quantity=transaction.quantity,
            remaining_quantity=transaction.quantity,
            cost_basis_per_share=cost_basis_per_share,
            total_cost_basis=total_cost_basis,
            transaction=transaction
        )
        
        logger.info(f"Created tax lot for {transaction.position.asset.symbol}: {transaction.quantity} shares @ ${cost_basis_per_share}")
        return tax_lot
    
    def _process_sale_transaction(self, transaction: Transaction) -> List[CapitalGainLoss]:
        """Process a sale transaction and create capital gains/losses.
        
        Args:
            transaction: Sale transaction
            
        Returns:
            List of created CapitalGainLoss instances
        """
        gains_losses = []
        remaining_to_sell = transaction.quantity
        
        # Get tax lots for this position in FIFO order
        tax_lots = TaxLot.objects.filter(
            position=transaction.position,
            remaining_quantity__gt=0
        ).order_by('acquisition_date', 'id')
        
        for tax_lot in tax_lots:
            if remaining_to_sell <= 0:
                break
                
            # Determine how many shares to sell from this lot
            shares_to_sell = min(remaining_to_sell, tax_lot.remaining_quantity)
            
            # Calculate gain/loss
            gross_proceeds = shares_to_sell * transaction.price
            cost_basis = shares_to_sell * tax_lot.cost_basis_per_share
            
            # Allocate fees proportionally
            fee_allocation = Decimal('0')
            if transaction.fees:
                fee_proportion = shares_to_sell / transaction.quantity
                fee_allocation = transaction.fees * fee_proportion
                gross_proceeds -= fee_allocation
            
            gain_loss_amount = gross_proceeds - cost_basis
            
            # Determine if long-term or short-term
            holding_period = transaction.date - tax_lot.acquisition_date
            term = 'long' if holding_period.days > 365 else 'short'
            
            # Get or create tax year
            tax_year, _ = TaxYear.objects.get_or_create(
                year=transaction.date.year,
                defaults={
                    'filing_deadline': date(transaction.date.year + 1, 4, 15),
                    'standard_deduction_single': Decimal('13850'),
                    'standard_deduction_married': Decimal('27700'),
                    'long_term_capital_gains_thresholds': {
                        '0': {'min': 0, 'max': 44625, 'rate': 0.0},
                        '15': {'min': 44626, 'max': 492300, 'rate': 0.15},
                        '20': {'min': 492301, 'max': None, 'rate': 0.20}
                    }
                }
            )
            
            # Create capital gain/loss record
            capital_gain_loss = CapitalGainLoss.objects.create(
                user=transaction.position.portfolio.user,
                tax_year=tax_year,
                position=transaction.position,
                transaction=transaction,
                tax_lot=tax_lot,
                sale_date=transaction.date,
                sale_price_per_share=transaction.price,
                quantity_sold=shares_to_sell,
                gross_proceeds=gross_proceeds + fee_allocation,  # Before fees for reporting
                cost_basis_per_share=tax_lot.cost_basis_per_share,
                total_cost_basis=cost_basis,
                gain_loss_amount=gain_loss_amount,
                term=term
            )
            
            gains_losses.append(capital_gain_loss)
            
            # Update tax lot
            tax_lot.remaining_quantity -= shares_to_sell
            tax_lot.save()
            
            remaining_to_sell -= shares_to_sell
            
            logger.info(f"Processed sale: {shares_to_sell} shares of {transaction.position.asset.symbol}, "
                       f"{term} {gain_loss_amount:+.2f}")
        
        return gains_losses
    
    def _process_dividend_transaction(self, transaction: Transaction) -> Optional[DividendIncome]:
        """Process a dividend transaction.
        
        Args:
            transaction: Dividend transaction
            
        Returns:
            Created DividendIncome instance or None
        """
        if transaction.transaction_type != 'dividend':
            return None
        
        # Get or create tax year
        tax_year, _ = TaxYear.objects.get_or_create(
            year=transaction.date.year,
            defaults={
                'filing_deadline': date(transaction.date.year + 1, 4, 15),
                'standard_deduction_single': Decimal('13850'),
                'standard_deduction_married': Decimal('27700'),
                'long_term_capital_gains_thresholds': {}
            }
        )
        
        # Assume qualified dividend unless specified otherwise
        dividend_type = 'qualified'
        
        dividend_income = DividendIncome.objects.create(
            user=transaction.position.portfolio.user,
            tax_year=tax_year,
            position=transaction.position,
            payment_date=transaction.date,
            ex_dividend_date=transaction.date,  # Simplified - in reality this would be tracked separately
            dividend_type=dividend_type,
            amount_per_share=transaction.price,  # Price field used for dividend amount
            shares_held=transaction.quantity,
            total_amount=transaction.quantity * transaction.price,
            tax_withheld=Decimal('0')
        )
        
        logger.info(f"Processed dividend: {transaction.position.asset.symbol} ${dividend_income.total_amount}")
        return dividend_income


class TaxLossHarvestingService:
    """Tax loss harvesting identification and recommendation service."""
    
    def __init__(self):
        """Initialize tax loss harvesting service."""
        self.current_date = timezone.now().date()
        
    def identify_loss_harvesting_opportunities(
        self, 
        user: User,
        minimum_loss_threshold: Decimal = Decimal('100')
    ) -> List[TaxLossHarvestingOpportunity]:
        """Identify tax loss harvesting opportunities.
        
        Args:
            user: User to analyze
            minimum_loss_threshold: Minimum loss amount to consider
            
        Returns:
            List of tax loss harvesting opportunities
        """
        logger.info(f"Identifying tax loss harvesting opportunities for {user.username}")
        
        opportunities = []
        
        # Get current tax year
        current_year = self.current_date.year
        tax_year, _ = TaxYear.objects.get_or_create(
            year=current_year,
            defaults={
                'filing_deadline': date(current_year + 1, 4, 15),
                'standard_deduction_single': Decimal('13850'),
                'standard_deduction_married': Decimal('27700'),
                'long_term_capital_gains_thresholds': {}
            }
        )
        
        # Get all positions with current unrealized losses
        portfolios = Portfolio.objects.filter(user=user)
        for portfolio in portfolios:
            positions = Position.objects.filter(portfolio=portfolio)
            
            for position in positions:
                if not position.asset.current_price:
                    continue
                    
                # Calculate unrealized loss
                current_value = position.quantity * position.asset.current_price
                cost_basis = position.average_cost * position.quantity
                unrealized_loss = current_value - cost_basis
                
                if unrealized_loss < -minimum_loss_threshold:
                    # Check for wash sale risk
                    wash_sale_end_date = self._check_wash_sale_risk(position)
                    
                    # Create opportunity record
                    opportunity, created = TaxLossHarvestingOpportunity.objects.get_or_create(
                        user=user,
                        position=position,
                        tax_year=tax_year,
                        defaults={
                            'potential_loss_amount': abs(unrealized_loss),
                            'current_unrealized_loss': unrealized_loss,
                            'wash_sale_end_date': wash_sale_end_date,
                            'status': 'wash_sale_risk' if wash_sale_end_date else 'identified'
                        }
                    )
                    
                    if not created:
                        # Update existing opportunity
                        opportunity.current_unrealized_loss = unrealized_loss
                        opportunity.potential_loss_amount = abs(unrealized_loss)
                        opportunity.wash_sale_end_date = wash_sale_end_date
                        opportunity.status = 'wash_sale_risk' if wash_sale_end_date else 'identified'
                        opportunity.save()
                    
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _check_wash_sale_risk(self, position: Position) -> Optional[date]:
        """Check if selling a position would trigger wash sale rules.
        
        Args:
            position: Position to check
            
        Returns:
            Date when wash sale period ends, or None if no risk
        """
        # Check for purchases of the same security in the last 30 days
        thirty_days_ago = self.current_date - timedelta(days=30)
        
        recent_purchases = Transaction.objects.filter(
            position__asset=position.asset,
            position__portfolio__user=position.portfolio.user,
            transaction_type='buy',
            date__gte=thirty_days_ago,
            date__lte=self.current_date
        ).order_by('-date')
        
        if recent_purchases.exists():
            # Wash sale risk exists - return date 30 days after last purchase
            last_purchase = recent_purchases.first()
            return last_purchase.date + timedelta(days=30)
        
        return None
    
    def generate_loss_harvesting_recommendations(
        self, 
        opportunities: List[TaxLossHarvestingOpportunity]
    ) -> None:
        """Generate specific recommendations for loss harvesting opportunities.
        
        Args:
            opportunities: List of opportunities to analyze
        """
        for opportunity in opportunities:
            if opportunity.status == 'wash_sale_risk':
                # Recommend waiting until wash sale period ends
                opportunity.recommended_sale_date = opportunity.wash_sale_end_date
                opportunity.alternative_investments = self._suggest_alternative_investments(
                    opportunity.position.asset
                )
            else:
                # Recommend immediate sale
                opportunity.recommended_sale_date = self.current_date
                opportunity.status = 'recommended'
            
            # Estimate tax benefit (simplified calculation)
            opportunity.tax_benefit_estimate = self._estimate_tax_benefit(
                opportunity.potential_loss_amount
            )
            
            opportunity.save()
    
    def _suggest_alternative_investments(self, asset) -> List[str]:
        """Suggest alternative investments to avoid wash sale rules.
        
        Args:
            asset: Asset being sold
            
        Returns:
            List of alternative investment suggestions
        """
        alternatives = []
        
        # For individual stocks, suggest ETFs in same sector
        if asset.asset_type == 'stock':
            if asset.symbol == 'AAPL':
                alternatives = ['VGT', 'XLK', 'FTEC']  # Technology ETFs
            elif asset.symbol == 'MSFT':
                alternatives = ['VGT', 'XLK', 'FTEC']
            else:
                alternatives = ['VTI', 'ITOT', 'SWTSX']  # Broad market ETFs
        
        # For ETFs, suggest similar but different ETFs
        elif asset.asset_type == 'etf':
            if asset.symbol == 'SPY':
                alternatives = ['VOO', 'IVV', 'VTI']
            elif asset.symbol == 'QQQ':
                alternatives = ['VGT', 'XLK', 'FTEC']
            else:
                alternatives = ['VTI', 'ITOT', 'SWTSX']
        
        return alternatives
    
    def _estimate_tax_benefit(self, loss_amount: Decimal) -> Decimal:
        """Estimate tax benefit from realizing a loss.
        
        Args:
            loss_amount: Amount of loss to realize
            
        Returns:
            Estimated tax benefit
        """
        # Simplified calculation assuming 22% marginal tax rate
        # In reality, this would consider user's tax bracket and other factors
        marginal_tax_rate = Decimal('0.22')
        return loss_amount * marginal_tax_rate


class TaxOptimizationService:
    """Tax optimization recommendations and strategies service."""
    
    def __init__(self):
        """Initialize tax optimization service."""
        self.current_date = timezone.now().date()
        
    def generate_tax_optimization_recommendations(
        self, 
        user: User,
        tax_year: Optional[TaxYear] = None
    ) -> List[TaxOptimizationRecommendation]:
        """Generate comprehensive tax optimization recommendations.
        
        Args:
            user: User to analyze
            tax_year: Tax year for analysis (current year if None)
            
        Returns:
            List of tax optimization recommendations
        """
        if not tax_year:
            tax_year, _ = TaxYear.objects.get_or_create(
                year=self.current_date.year,
                defaults={
                    'filing_deadline': date(self.current_date.year + 1, 4, 15),
                    'standard_deduction_single': Decimal('13850'),
                    'standard_deduction_married': Decimal('27700'),
                    'long_term_capital_gains_thresholds': {}
                }
            )
        
        recommendations = []
        
        # Analyze portfolios for optimization opportunities
        portfolios = Portfolio.objects.filter(user=user)
        
        for portfolio in portfolios:
            recommendations.extend(self._analyze_asset_location(user, portfolio, tax_year))
            recommendations.extend(self._analyze_rebalancing_opportunities(user, portfolio, tax_year))
            recommendations.extend(self._analyze_holding_periods(user, portfolio, tax_year))
        
        # General tax recommendations
        recommendations.extend(self._generate_general_tax_recommendations(user, tax_year))
        
        return recommendations
    
    def _analyze_asset_location(
        self, 
        user: User, 
        portfolio: Portfolio, 
        tax_year: TaxYear
    ) -> List[TaxOptimizationRecommendation]:
        """Analyze asset location optimization opportunities.
        
        Args:
            user: User to analyze
            portfolio: Portfolio to analyze
            tax_year: Tax year for analysis
            
        Returns:
            List of asset location recommendations
        """
        recommendations = []
        
        # Simplified asset location analysis
        # In a real implementation, this would analyze taxable vs tax-advantaged accounts
        
        if portfolio.name and 'taxable' in portfolio.name.lower():
            recommendation = TaxOptimizationRecommendation(
                user=user,
                tax_year=tax_year,
                portfolio=portfolio,
                recommendation_type='asset_location',
                priority='medium',
                title='Optimize Asset Location for Tax Efficiency',
                description=(
                    'Consider moving tax-inefficient investments to tax-advantaged accounts. '
                    'High-dividend stocks and bonds generate regular taxable income and may be '
                    'better suited for IRAs or 401(k)s, while tax-efficient index funds can '
                    'remain in taxable accounts.'
                ),
                estimated_tax_savings=Decimal('500'),
                action_required=(
                    '1. Review high-dividend positions in taxable account\n'
                    '2. Consider moving to IRA/401(k) if contribution room available\n'
                    '3. Replace with tax-efficient index funds in taxable account'
                ),
                deadline=date(tax_year.year, 12, 31)
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_rebalancing_opportunities(
        self, 
        user: User, 
        portfolio: Portfolio, 
        tax_year: TaxYear
    ) -> List[TaxOptimizationRecommendation]:
        """Analyze tax-efficient rebalancing opportunities.
        
        Args:
            user: User to analyze
            portfolio: Portfolio to analyze
            tax_year: Tax year for analysis
            
        Returns:
            List of rebalancing recommendations
        """
        recommendations = []
        
        # Check if portfolio needs rebalancing and has tax implications
        positions = Position.objects.filter(portfolio=portfolio)
        total_value = sum(p.quantity * (p.asset.current_price or p.average_cost) for p in positions)
        
        if total_value > 10000:  # Only for significant portfolios
            recommendation = TaxOptimizationRecommendation(
                user=user,
                tax_year=tax_year,
                portfolio=portfolio,
                recommendation_type='rebalancing',
                priority='low',
                title='Consider Tax-Efficient Rebalancing',
                description=(
                    'Rebalance your portfolio using new contributions and dividends first, '
                    'then consider tax-loss harvesting to offset any necessary sales of '
                    'appreciated assets. This minimizes the tax impact of rebalancing.'
                ),
                estimated_tax_savings=Decimal('200'),
                action_required=(
                    '1. Use new contributions to buy underweight assets\n'
                    '2. Reinvest dividends in underweight positions\n'
                    '3. Harvest losses before selling appreciated assets\n'
                    '4. Consider holding period for long-term capital gains'
                ),
                deadline=date(tax_year.year, 12, 31)
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_holding_periods(
        self, 
        user: User, 
        portfolio: Portfolio, 
        tax_year: TaxYear
    ) -> List[TaxOptimizationRecommendation]:
        """Analyze holding period optimization opportunities.
        
        Args:
            user: User to analyze
            portfolio: Portfolio to analyze
            tax_year: Tax year for analysis
            
        Returns:
            List of holding period recommendations
        """
        recommendations = []
        
        # Find positions close to long-term status
        tax_lots = TaxLot.objects.filter(
            position__portfolio=portfolio,
            remaining_quantity__gt=0
        )
        
        near_long_term_lots = []
        for lot in tax_lots:
            days_held = (self.current_date - lot.acquisition_date).days
            if 330 <= days_held <= 365:  # Within 35 days of long-term status
                if lot.unrealized_gain_loss > 0:  # Only for gains
                    near_long_term_lots.append(lot)
        
        if near_long_term_lots:
            total_potential_savings = sum(
                lot.unrealized_gain_loss * Decimal('0.15')  # Assume 15% LTCG rate vs 22% ordinary
                for lot in near_long_term_lots
            )
            
            recommendation = TaxOptimizationRecommendation(
                user=user,
                tax_year=tax_year,
                portfolio=portfolio,
                recommendation_type='holding_period',
                priority='high',
                title='Optimize Holding Periods for Long-Term Capital Gains',
                description=(
                    f'You have {len(near_long_term_lots)} positions that will qualify for '
                    'long-term capital gains treatment within the next 35 days. Consider '
                    'delaying sales until after the one-year holding period to benefit from '
                    'preferential tax treatment.'
                ),
                estimated_tax_savings=total_potential_savings,
                action_required=(
                    '1. Review positions approaching one-year holding period\n'
                    '2. Delay any planned sales until long-term status achieved\n'
                    '3. Mark calendar for earliest sale dates\n'
                    '4. Consider partial sales if liquidity needed'
                ),
                deadline=min(lot.acquisition_date + timedelta(days=366) for lot in near_long_term_lots)
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_general_tax_recommendations(
        self, 
        user: User, 
        tax_year: TaxYear
    ) -> List[TaxOptimizationRecommendation]:
        """Generate general tax optimization recommendations.
        
        Args:
            user: User to analyze
            tax_year: Tax year for analysis
            
        Returns:
            List of general tax recommendations
        """
        recommendations = []
        
        # Year-end tax planning recommendation
        if self.current_date.month >= 10:  # Q4
            recommendation = TaxOptimizationRecommendation(
                user=user,
                tax_year=tax_year,
                recommendation_type='loss_harvesting',
                priority='high',
                title='Year-End Tax Loss Harvesting Review',
                description=(
                    'Review your portfolio for tax loss harvesting opportunities before '
                    'year-end. Realizing losses can offset capital gains and up to $3,000 '
                    'of ordinary income, with additional losses carried forward to future years.'
                ),
                estimated_tax_savings=Decimal('750'),
                action_required=(
                    '1. Identify positions with unrealized losses\n'
                    '2. Check for wash sale rule violations\n'
                    '3. Execute sales by December 31st\n'
                    '4. Consider alternative investments to maintain exposure'
                ),
                deadline=date(tax_year.year, 12, 31)
            )
            recommendations.append(recommendation)
        
        return recommendations