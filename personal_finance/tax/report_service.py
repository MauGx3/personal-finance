"""Tax report generation service."""

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, List, Any, Optional

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from .models import (
    TaxYear, CapitalGainLoss, DividendIncome, TaxReport,
    TaxLossHarvestingOpportunity, TaxOptimizationRecommendation
)
from .services import TaxCalculationService

User = get_user_model()
logger = logging.getLogger(__name__)


class TaxReportService:
    """Tax report generation and formatting service."""
    
    def __init__(self):
        """Initialize tax report service."""
        self.tax_calc_service = TaxCalculationService()
        
    def generate_schedule_d_report(
        self, 
        user: User, 
        tax_year: TaxYear
    ) -> TaxReport:
        """Generate Schedule D (Capital Gains and Losses) report.
        
        Args:
            user: User to generate report for
            tax_year: Tax year for the report
            
        Returns:
            Generated TaxReport instance
        """
        logger.info(f"Generating Schedule D report for {user.username} - {tax_year.year}")
        
        # Calculate capital gains/losses
        capital_gains_data = self.tax_calc_service.calculate_capital_gains_losses(
            user, tax_year
        )
        
        # Get detailed transaction data
        gains_losses = CapitalGainLoss.objects.filter(
            user=user,
            tax_year=tax_year
        ).select_related('position__asset', 'transaction').order_by(
            'term', 'sale_date', 'position__asset__symbol'
        )
        
        # Separate short-term and long-term transactions
        short_term_transactions = []
        long_term_transactions = []
        
        for gain_loss in gains_losses:
            transaction_data = {
                'symbol': gain_loss.position.asset.symbol,
                'description': f"{gain_loss.position.asset.name} ({gain_loss.position.asset.symbol})",
                'acquisition_date': gain_loss.tax_lot.acquisition_date,
                'sale_date': gain_loss.sale_date,
                'quantity': gain_loss.quantity_sold,
                'gross_proceeds': gain_loss.gross_proceeds,
                'cost_basis': gain_loss.total_cost_basis,
                'gain_loss': gain_loss.gain_loss_amount,
                'wash_sale_adjustment': gain_loss.wash_sale_adjustment
            }
            
            if gain_loss.term == 'short':
                short_term_transactions.append(transaction_data)
            else:
                long_term_transactions.append(transaction_data)
        
        # Prepare report data
        report_data = {
            'user': {
                'name': user.get_full_name() or user.username,
                'username': user.username
            },
            'tax_year': tax_year.year,
            'generation_date': date.today(),
            'summary': capital_gains_data,
            'short_term_transactions': short_term_transactions,
            'long_term_transactions': long_term_transactions,
            'form_totals': {
                'short_term_subtotal': capital_gains_data['short_term']['net'],
                'long_term_subtotal': capital_gains_data['long_term']['net'],
                'net_capital_gain_loss': capital_gains_data['totals']['net_capital_gain_loss']
            }
        }
        
        # Create or update tax report
        tax_report, created = TaxReport.objects.update_or_create(
            user=user,
            tax_year=tax_year,
            report_type='schedule_d',
            defaults={
                'report_data': report_data,
                'total_short_term_gains': capital_gains_data['short_term']['gains'],
                'total_short_term_losses': capital_gains_data['short_term']['losses'],
                'total_long_term_gains': capital_gains_data['long_term']['gains'],
                'total_long_term_losses': capital_gains_data['long_term']['losses'],
                'net_capital_gain_loss': capital_gains_data['totals']['net_capital_gain_loss']
            }
        )
        
        logger.info(f"Generated Schedule D report: {tax_report.id}")
        return tax_report
    
    def generate_dividend_report(
        self, 
        user: User, 
        tax_year: TaxYear
    ) -> TaxReport:
        """Generate Form 1099-DIV equivalent dividend report.
        
        Args:
            user: User to generate report for
            tax_year: Tax year for the report
            
        Returns:
            Generated TaxReport instance
        """
        logger.info(f"Generating dividend report for {user.username} - {tax_year.year}")
        
        # Calculate dividend income
        dividend_data = self.tax_calc_service.calculate_dividend_income(
            user, tax_year
        )
        
        # Get detailed dividend data by asset
        dividends = DividendIncome.objects.filter(
            user=user,
            tax_year=tax_year
        ).select_related('position__asset').order_by(
            'position__asset__symbol', 'payment_date'
        )
        
        # Group dividends by asset
        dividends_by_asset = {}
        for dividend in dividends:
            symbol = dividend.position.asset.symbol
            if symbol not in dividends_by_asset:
                dividends_by_asset[symbol] = {
                    'asset_name': dividend.position.asset.name,
                    'qualified_dividends': Decimal('0'),
                    'ordinary_dividends': Decimal('0'),
                    'capital_gain_distributions': Decimal('0'),
                    'return_of_capital': Decimal('0'),
                    'total_dividends': Decimal('0'),
                    'payments': []
                }
            
            asset_data = dividends_by_asset[symbol]
            asset_data['payments'].append({
                'payment_date': dividend.payment_date,
                'type': dividend.dividend_type,
                'amount': dividend.total_amount,
                'shares': dividend.shares_held,
                'per_share': dividend.amount_per_share
            })
            
            # Add to appropriate category
            if dividend.dividend_type == 'qualified':
                asset_data['qualified_dividends'] += dividend.total_amount
            elif dividend.dividend_type == 'ordinary':
                asset_data['ordinary_dividends'] += dividend.total_amount
            elif dividend.dividend_type == 'capital_gain':
                asset_data['capital_gain_distributions'] += dividend.total_amount
            elif dividend.dividend_type == 'return_of_capital':
                asset_data['return_of_capital'] += dividend.total_amount
            
            asset_data['total_dividends'] = (
                asset_data['qualified_dividends'] + 
                asset_data['ordinary_dividends']
            )
        
        # Prepare report data
        report_data = {
            'user': {
                'name': user.get_full_name() or user.username,
                'username': user.username
            },
            'tax_year': tax_year.year,
            'generation_date': date.today(),
            'summary': dividend_data,
            'dividends_by_asset': dividends_by_asset,
            'total_payments': dividends.count()
        }
        
        # Create or update tax report
        tax_report, created = TaxReport.objects.update_or_create(
            user=user,
            tax_year=tax_year,
            report_type='form_1099_div',
            defaults={
                'report_data': report_data,
                'total_dividend_income': dividend_data['grand_total']
            }
        )
        
        logger.info(f"Generated dividend report: {tax_report.id}")
        return tax_report
    
    def generate_form_8949_report(
        self, 
        user: User, 
        tax_year: TaxYear
    ) -> TaxReport:
        """Generate Form 8949 (Sales and Other Dispositions) report.
        
        Args:
            user: User to generate report for
            tax_year: Tax year for the report
            
        Returns:
            Generated TaxReport instance
        """
        logger.info(f"Generating Form 8949 report for {user.username} - {tax_year.year}")
        
        # Get all capital gains/losses with full detail
        gains_losses = CapitalGainLoss.objects.filter(
            user=user,
            tax_year=tax_year
        ).select_related(
            'position__asset', 'transaction', 'tax_lot'
        ).order_by('term', 'sale_date')
        
        # Prepare detailed transaction records for Form 8949
        transactions = []
        for gain_loss in gains_losses:
            transactions.append({
                'description': f"{gain_loss.quantity_sold} shares {gain_loss.position.asset.name}",
                'symbol': gain_loss.position.asset.symbol,
                'acquisition_date': gain_loss.tax_lot.acquisition_date.strftime('%m/%d/%Y'),
                'sale_date': gain_loss.sale_date.strftime('%m/%d/%Y'),
                'gross_proceeds': gain_loss.gross_proceeds,
                'cost_basis': gain_loss.total_cost_basis,
                'adjustment_code': 'W' if gain_loss.wash_sale_adjustment != 0 else '',
                'adjustment_amount': gain_loss.wash_sale_adjustment,
                'gain_loss': gain_loss.gain_loss_amount,
                'term': gain_loss.term,
                'quantity': gain_loss.quantity_sold,
                'price_per_share': gain_loss.sale_price_per_share
            })
        
        # Calculate totals
        short_term_total = sum(
            t['gain_loss'] for t in transactions if t['term'] == 'short'
        )
        long_term_total = sum(
            t['gain_loss'] for t in transactions if t['term'] == 'long'
        )
        
        report_data = {
            'user': {
                'name': user.get_full_name() or user.username,
                'username': user.username
            },
            'tax_year': tax_year.year,
            'generation_date': date.today(),
            'transactions': transactions,
            'summary': {
                'total_transactions': len(transactions),
                'short_term_total': short_term_total,
                'long_term_total': long_term_total,
                'net_total': short_term_total + long_term_total
            }
        }
        
        # Create or update tax report
        tax_report, created = TaxReport.objects.update_or_create(
            user=user,
            tax_year=tax_year,
            report_type='form_8949',
            defaults={
                'report_data': report_data,
                'net_capital_gain_loss': short_term_total + long_term_total
            }
        )
        
        logger.info(f"Generated Form 8949 report: {tax_report.id}")
        return tax_report
    
    def generate_tax_summary_report(
        self, 
        user: User, 
        tax_year: TaxYear
    ) -> TaxReport:
        """Generate comprehensive annual tax summary report.
        
        Args:
            user: User to generate report for
            tax_year: Tax year for the report
            
        Returns:
            Generated TaxReport instance
        """
        logger.info(f"Generating tax summary report for {user.username} - {tax_year.year}")
        
        # Get capital gains/losses data
        capital_gains_data = self.tax_calc_service.calculate_capital_gains_losses(
            user, tax_year
        )
        
        # Get dividend data
        dividend_data = self.tax_calc_service.calculate_dividend_income(
            user, tax_year
        )
        
        # Get tax optimization opportunities
        loss_opportunities = TaxLossHarvestingOpportunity.objects.filter(
            user=user,
            tax_year=tax_year
        ).order_by('-potential_loss_amount')
        
        optimization_recommendations = TaxOptimizationRecommendation.objects.filter(
            user=user,
            tax_year=tax_year,
            is_implemented=False
        ).order_by('-estimated_tax_savings')
        
        # Calculate estimated tax liability (simplified)
        net_capital_gains = capital_gains_data['totals']['net_capital_gain_loss']
        total_dividends = dividend_data['total_dividends']
        
        # Simplified tax calculation (would be more complex in reality)
        estimated_tax_on_gains = max(net_capital_gains * Decimal('0.15'), Decimal('0'))
        estimated_tax_on_dividends = total_dividends * Decimal('0.15')  # Assume qualified
        total_estimated_tax = estimated_tax_on_gains + estimated_tax_on_dividends
        
        report_data = {
            'user': {
                'name': user.get_full_name() or user.username,
                'username': user.username
            },
            'tax_year': tax_year.year,
            'generation_date': date.today(),
            'capital_gains': capital_gains_data,
            'dividends': dividend_data,
            'tax_estimates': {
                'capital_gains_tax': estimated_tax_on_gains,
                'dividend_tax': estimated_tax_on_dividends,
                'total_estimated_tax': total_estimated_tax
            },
            'optimization': {
                'loss_opportunities_count': loss_opportunities.count(),
                'total_potential_losses': sum(opp.potential_loss_amount for opp in loss_opportunities),
                'recommendations_count': optimization_recommendations.count(),
                'total_potential_savings': sum(
                    rec.estimated_tax_savings or Decimal('0') 
                    for rec in optimization_recommendations
                )
            },
            'summary_metrics': {
                'total_investment_income': net_capital_gains + total_dividends,
                'net_investment_income_tax': max(
                    (net_capital_gains + total_dividends - Decimal('200000')) * Decimal('0.038'),
                    Decimal('0')
                )  # Simplified NIIT calculation
            }
        }
        
        # Create or update tax report
        tax_report, created = TaxReport.objects.update_or_create(
            user=user,
            tax_year=tax_year,
            report_type='tax_summary',
            defaults={
                'report_data': report_data,
                'total_short_term_gains': capital_gains_data['short_term']['gains'],
                'total_short_term_losses': capital_gains_data['short_term']['losses'],
                'total_long_term_gains': capital_gains_data['long_term']['gains'],
                'total_long_term_losses': capital_gains_data['long_term']['losses'],
                'net_capital_gain_loss': capital_gains_data['totals']['net_capital_gain_loss'],
                'total_dividend_income': dividend_data['total_dividends']
            }
        )
        
        logger.info(f"Generated tax summary report: {tax_report.id}")
        return tax_report
    
    def generate_loss_carryforward_report(
        self, 
        user: User, 
        tax_year: TaxYear
    ) -> TaxReport:
        """Generate loss carryforward tracking report.
        
        Args:
            user: User to generate report for
            tax_year: Tax year for the report
            
        Returns:
            Generated TaxReport instance
        """
        logger.info(f"Generating loss carryforward report for {user.username} - {tax_year.year}")
        
        # Get capital losses from previous years
        previous_years_losses = []
        current_year = tax_year.year
        
        for year in range(current_year - 8, current_year):  # Look back 8 years
            try:
                prev_tax_year = TaxYear.objects.get(year=year)
                prev_report = TaxReport.objects.filter(
                    user=user,
                    tax_year=prev_tax_year,
                    report_type='schedule_d'
                ).first()
                
                if prev_report and prev_report.net_capital_gain_loss < 0:
                    # Calculate unused losses (simplified - would track actual usage)
                    net_loss = abs(prev_report.net_capital_gain_loss)
                    ordinary_income_offset = min(net_loss, Decimal('3000'))
                    carryforward = net_loss - ordinary_income_offset
                    
                    if carryforward > 0:
                        previous_years_losses.append({
                            'year': year,
                            'net_loss': net_loss,
                            'ordinary_offset': ordinary_income_offset,
                            'carryforward': carryforward
                        })
                        
            except TaxYear.DoesNotExist:
                continue
        
        # Current year capital gains/losses
        current_year_data = self.tax_calc_service.calculate_capital_gains_losses(
            user, tax_year
        )
        
        current_net_loss = current_year_data['totals']['net_capital_gain_loss']
        
        # Calculate available carryforward
        total_carryforward = sum(loss['carryforward'] for loss in previous_years_losses)
        
        if current_net_loss < 0:
            total_carryforward += abs(current_net_loss) - min(abs(current_net_loss), Decimal('3000'))
        
        report_data = {
            'user': {
                'name': user.get_full_name() or user.username,
                'username': user.username
            },
            'tax_year': tax_year.year,
            'generation_date': date.today(),
            'current_year': {
                'net_capital_gain_loss': current_net_loss,
                'ordinary_income_offset': min(abs(current_net_loss), Decimal('3000')) if current_net_loss < 0 else Decimal('0'),
                'new_carryforward': max(abs(current_net_loss) - Decimal('3000'), Decimal('0')) if current_net_loss < 0 else Decimal('0')
            },
            'previous_years_losses': previous_years_losses,
            'total_carryforward_available': total_carryforward,
            'expiration_schedule': [
                {
                    'year': loss['year'],
                    'amount': loss['carryforward'],
                    'expires': loss['year'] + 8  # Capital losses carry forward indefinitely (post-1997)
                }
                for loss in previous_years_losses
            ]
        }
        
        # Create or update tax report
        tax_report, created = TaxReport.objects.update_or_create(
            user=user,
            tax_year=tax_year,
            report_type='loss_carryforward',
            defaults={
                'report_data': report_data,
                'net_capital_gain_loss': current_net_loss
            }
        )
        
        logger.info(f"Generated loss carryforward report: {tax_report.id}")
        return tax_report
    
    def generate_all_tax_reports(
        self, 
        user: User, 
        tax_year: TaxYear
    ) -> Dict[str, TaxReport]:
        """Generate all available tax reports for a user and tax year.
        
        Args:
            user: User to generate reports for
            tax_year: Tax year for the reports
            
        Returns:
            Dictionary of report type to TaxReport instance
        """
        logger.info(f"Generating all tax reports for {user.username} - {tax_year.year}")
        
        reports = {}
        
        try:
            reports['schedule_d'] = self.generate_schedule_d_report(user, tax_year)
            reports['form_1099_div'] = self.generate_dividend_report(user, tax_year)
            reports['form_8949'] = self.generate_form_8949_report(user, tax_year)
            reports['tax_summary'] = self.generate_tax_summary_report(user, tax_year)
            reports['loss_carryforward'] = self.generate_loss_carryforward_report(user, tax_year)
            
            logger.info(f"Generated {len(reports)} tax reports successfully")
            
        except Exception as e:
            logger.error(f"Error generating tax reports: {str(e)}")
            raise
        
        return reports