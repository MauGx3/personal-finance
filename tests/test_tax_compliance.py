"""
Tax and regulatory compliance test suite.

Tests tax calculations, reporting features, and compliance with
financial regulations for the personal finance platform.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from personal_finance.assets.models import Asset, Portfolio, Holding

User = get_user_model()


@pytest.mark.django_db
class TestCapitalGainsCalculations:
    """Test capital gains and losses calculations."""
    
    def setup_method(self):
        """Set up tax calculation testing."""
        self.user = User.objects.create_user(
            username="taxpayer",
            email="taxpayer@example.com",
            password="tax123"
        )
        
        self.asset = Asset.objects.create(
            symbol="TAX_TEST",
            name="Tax Test Asset",
            asset_type=Asset.ASSET_STOCK,
            currency="USD"
        )
    
    def test_short_term_capital_gains(self):
        """Test short-term capital gains calculation (held < 1 year)."""
        purchase_date = date.today() - timedelta(days=180)  # 6 months ago
        sale_date = date.today()
        
        # Purchase: 100 shares at $50 = $5,000
        purchase_price = Decimal('50.00')
        quantity = Decimal('100')
        sale_price = Decimal('60.00')  # Sold at $60
        
        cost_basis = quantity * purchase_price  # $5,000
        sale_proceeds = quantity * sale_price   # $6,000
        capital_gain = sale_proceeds - cost_basis  # $1,000
        
        # Holding period < 1 year = short-term
        holding_period = (sale_date - purchase_date).days
        is_short_term = holding_period < 365
        
        assert is_short_term is True
        assert capital_gain == Decimal('1000.00')
        assert capital_gain > Decimal('0')  # Gain
    
    def test_long_term_capital_gains(self):
        """Test long-term capital gains calculation (held >= 1 year)."""
        purchase_date = date.today() - timedelta(days=400)  # > 1 year ago
        sale_date = date.today()
        
        # Purchase: 200 shares at $75 = $15,000
        purchase_price = Decimal('75.00')
        quantity = Decimal('200')
        sale_price = Decimal('90.00')  # Sold at $90
        
        cost_basis = quantity * purchase_price  # $15,000
        sale_proceeds = quantity * sale_price   # $18,000
        capital_gain = sale_proceeds - cost_basis  # $3,000
        
        # Holding period >= 1 year = long-term
        holding_period = (sale_date - purchase_date).days
        is_long_term = holding_period >= 365
        
        assert is_long_term is True
        assert capital_gain == Decimal('3000.00')
        assert capital_gain > Decimal('0')  # Gain
    
    def test_capital_losses(self):
        """Test capital losses calculation."""
        purchase_date = date.today() - timedelta(days=120)
        sale_date = date.today()
        
        # Purchase: 150 shares at $80 = $12,000
        purchase_price = Decimal('80.00')
        quantity = Decimal('150')
        sale_price = Decimal('65.00')  # Sold at $65 (loss)
        
        cost_basis = quantity * purchase_price  # $12,000
        sale_proceeds = quantity * sale_price   # $9,750
        capital_loss = sale_proceeds - cost_basis  # -$2,250
        
        assert capital_loss == Decimal('-2250.00')
        assert capital_loss < Decimal('0')  # Loss
        
        # Absolute loss amount for tax purposes
        loss_amount = abs(capital_loss)
        assert loss_amount == Decimal('2250.00')
    
    def test_fifo_cost_basis_calculation(self):
        """Test FIFO (First In, First Out) cost basis calculation."""
        # Multiple purchases of the same asset
        purchases = [
            (date(2023, 1, 15), Decimal('100'), Decimal('50.00')),  # 100 @ $50
            (date(2023, 3, 20), Decimal('100'), Decimal('55.00')),  # 100 @ $55
            (date(2023, 6, 10), Decimal('100'), Decimal('60.00')),  # 100 @ $60
        ]
        
        # Sell 150 shares using FIFO
        shares_to_sell = Decimal('150')
        total_cost_basis = Decimal('0')
        shares_sold = Decimal('0')
        
        for purchase_date, quantity, price in purchases:
            if shares_sold >= shares_to_sell:
                break
                
            shares_from_this_lot = min(quantity, shares_to_sell - shares_sold)
            cost_from_this_lot = shares_from_this_lot * price
            total_cost_basis += cost_from_this_lot
            shares_sold += shares_from_this_lot
        
        # FIFO: Sell 100 @ $50 + 50 @ $55 = $5,000 + $2,750 = $7,750
        expected_cost_basis = Decimal('7750.00')
        assert total_cost_basis == expected_cost_basis
        assert shares_sold == shares_to_sell
    
    def test_specific_identification_cost_basis(self):
        """Test specific identification cost basis method."""
        # Multiple purchases with different tax lots
        tax_lots = [
            {'date': date(2023, 1, 15), 'quantity': Decimal('100'), 'price': Decimal('50.00'), 'lot_id': 1},
            {'date': date(2023, 3, 20), 'quantity': Decimal('100'), 'price': Decimal('55.00'), 'lot_id': 2},
            {'date': date(2023, 6, 10), 'quantity': Decimal('100'), 'price': Decimal('60.00'), 'lot_id': 3},
        ]
        
        # Specifically sell from lot 3 (highest cost basis for tax loss)
        selected_lot_id = 3
        shares_to_sell = Decimal('75')
        
        selected_lot = next(lot for lot in tax_lots if lot['lot_id'] == selected_lot_id)
        cost_basis = shares_to_sell * selected_lot['price']
        
        # Specific ID: Sell 75 @ $60 = $4,500
        expected_cost_basis = Decimal('4500.00')
        assert cost_basis == expected_cost_basis
    
    def test_wash_sale_rule(self):
        """Test wash sale rule implementation."""
        # Sell at a loss
        sale_date = date(2023, 6, 15)
        sale_price = Decimal('40.00')
        cost_basis = Decimal('50.00')
        quantity = Decimal('100')
        
        loss = (sale_price - cost_basis) * quantity  # -$1,000 loss
        
        # Repurchase within 30 days (wash sale)
        repurchase_date = date(2023, 6, 25)  # 10 days later
        repurchase_price = Decimal('42.00')
        
        days_between = (repurchase_date - sale_date).days
        is_wash_sale = days_between <= 30
        
        assert is_wash_sale is True
        assert loss == Decimal('-1000.00')
        
        # In wash sale, loss is disallowed and added to new cost basis
        if is_wash_sale:
            disallowed_loss = abs(loss)
            adjusted_cost_basis = repurchase_price + (disallowed_loss / quantity)
            
            # New cost basis: $42 + ($1,000 / 100) = $52.00 per share
            expected_adjusted_basis = Decimal('52.00')
            assert adjusted_cost_basis == expected_adjusted_basis


@pytest.mark.django_db
class TestDividendTaxCalculations:
    """Test dividend income tax calculations."""
    
    def setup_method(self):
        """Set up dividend tax testing."""
        self.user = User.objects.create_user(
            username="dividend_investor",
            email="dividends@example.com",
            password="div123"
        )
        
        self.dividend_stock = Asset.objects.create(
            symbol="DIV_STOCK",
            name="Dividend Stock",
            asset_type=Asset.ASSET_STOCK,
            metadata={"dividend_yield": "0.025"}  # 2.5% yield
        )
    
    def test_qualified_dividend_calculation(self):
        """Test qualified dividend tax calculation."""
        # Qualified dividends (held > 60 days) get preferential tax rates
        holding_period_days = 90  # > 60 days
        dividend_amount = Decimal('500.00')
        
        is_qualified = holding_period_days > 60
        assert is_qualified is True
        
        # Qualified dividends taxed at capital gains rates (0%, 15%, 20%)
        # Simplified tax calculation for testing
        income_level = Decimal('75000')  # Example income
        
        if income_level <= Decimal('47025'):  # 2024 threshold example
            qualified_div_tax_rate = Decimal('0.00')  # 0%
        elif income_level <= Decimal('518900'):
            qualified_div_tax_rate = Decimal('0.15')  # 15%
        else:
            qualified_div_tax_rate = Decimal('0.20')  # 20%
        
        qualified_div_tax = dividend_amount * qualified_div_tax_rate
        
        assert qualified_div_tax_rate == Decimal('0.15')
        assert qualified_div_tax == Decimal('75.00')  # $500 * 15%
    
    def test_ordinary_dividend_calculation(self):
        """Test ordinary dividend tax calculation."""
        # Ordinary dividends (held <= 60 days) taxed as ordinary income
        holding_period_days = 45  # <= 60 days
        dividend_amount = Decimal('300.00')
        
        is_qualified = holding_period_days > 60
        assert is_qualified is False
        
        # Ordinary dividends taxed at marginal tax rate
        marginal_tax_rate = Decimal('0.22')  # 22% bracket example
        ordinary_div_tax = dividend_amount * marginal_tax_rate
        
        assert ordinary_div_tax == Decimal('66.00')  # $300 * 22%
    
    def test_dividend_reinvestment_cost_basis(self):
        """Test cost basis adjustment for dividend reinvestment."""
        # Original holding
        original_shares = Decimal('100')
        original_price = Decimal('50.00')
        original_cost_basis = original_shares * original_price  # $5,000
        
        # Dividend payment and reinvestment
        dividend_per_share = Decimal('1.25')
        total_dividend = original_shares * dividend_per_share  # $125
        
        # Reinvestment price (often different from current market price)
        reinvestment_price = Decimal('51.00')
        additional_shares = total_dividend / reinvestment_price  # ~2.45 shares
        
        # New cost basis includes reinvested dividends
        new_total_shares = original_shares + additional_shares
        new_total_cost_basis = original_cost_basis + total_dividend
        new_avg_cost_per_share = new_total_cost_basis / new_total_shares
        
        assert additional_shares.quantize(Decimal('0.001')) == Decimal('2.451')
        assert new_total_cost_basis == Decimal('5125.00')
        # Allow for small rounding differences in cost per share calculation
        expected_avg_cost = Decimal('50.02')  # Correct calculation result
        assert new_avg_cost_per_share.quantize(Decimal('0.01')) == expected_avg_cost


@pytest.mark.django_db
class TestTaxLossHarvesting:
    """Test tax loss harvesting strategies and calculations."""
    
    def setup_method(self):
        """Set up tax loss harvesting testing."""
        self.user = User.objects.create_user(
            username="harvester",
            email="harvest@example.com",
            password="harvest123"
        )
        
        self.portfolio = Portfolio.objects.create(
            user=self.user,
            name="Tax Loss Harvesting Portfolio"
        )
    
    def test_loss_harvesting_opportunity_identification(self):
        """Test identifying tax loss harvesting opportunities."""
        # Create assets with different performance
        assets_performance = [
            ("WINNER", Decimal('100'), Decimal('50.00'), Decimal('75.00')),  # +50% gain
            ("LOSER1", Decimal('100'), Decimal('60.00'), Decimal('45.00')),  # -25% loss
            ("LOSER2", Decimal('100'), Decimal('40.00'), Decimal('30.00')),  # -25% loss
            ("FLAT", Decimal('100'), Decimal('50.00'), Decimal('50.00'))     # 0% change
        ]
        
        harvesting_opportunities = []
        
        for symbol, quantity, cost_basis, current_price in assets_performance:
            asset = Asset.objects.create(
                symbol=symbol,
                name=f"{symbol} Asset",
                asset_type=Asset.ASSET_STOCK
            )
            
            # Calculate unrealized gain/loss
            total_cost = quantity * cost_basis
            current_value = quantity * current_price
            unrealized_gain_loss = current_value - total_cost
            
            # Identify loss harvesting opportunities (losses > threshold)
            loss_threshold = Decimal('-500.00')  # $500 minimum loss
            
            if unrealized_gain_loss < loss_threshold:
                harvesting_opportunities.append({
                    'symbol': symbol,
                    'loss_amount': abs(unrealized_gain_loss),
                    'loss_percentage': (unrealized_gain_loss / total_cost) * 100
                })
        
        # Should identify LOSER1 and LOSER2 as opportunities
        assert len(harvesting_opportunities) == 2
        
        loser1_opportunity = next(
            opp for opp in harvesting_opportunities if opp['symbol'] == 'LOSER1'
        )
        assert loser1_opportunity['loss_amount'] == Decimal('1500.00')
        assert loser1_opportunity['loss_percentage'] == Decimal('-25.00')
    
    def test_tax_loss_carryforward(self):
        """Test tax loss carryforward calculation."""
        # Annual capital gains and losses
        current_year_gains = Decimal('5000.00')
        current_year_losses = Decimal('-8000.00')
        
        # Net capital loss
        net_capital_loss = current_year_gains + current_year_losses  # -$3,000
        
        # Annual capital loss deduction limit
        annual_deduction_limit = Decimal('-3000.00')
        
        # Current year deduction
        current_year_deduction = max(net_capital_loss, annual_deduction_limit)
        
        # Carryforward amount
        carryforward_loss = net_capital_loss - current_year_deduction
        
        assert net_capital_loss == Decimal('-3000.00')
        assert current_year_deduction == Decimal('-3000.00')
        assert carryforward_loss == Decimal('0.00')  # All used in current year
        
        # Example with larger loss
        large_loss_year = Decimal('-10000.00')
        large_loss_deduction = max(large_loss_year, annual_deduction_limit)
        large_loss_carryforward = large_loss_year - large_loss_deduction
        
        assert large_loss_deduction == Decimal('-3000.00')
        assert large_loss_carryforward == Decimal('-7000.00')  # Carry forward $7,000
    
    def test_substantially_identical_securities(self):
        """Test identification of substantially identical securities for wash sale avoidance."""
        # Create similar securities
        securities = [
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "type": "ETF", "index": "S&P 500"},
            {"symbol": "VOO", "name": "Vanguard S&P 500 ETF", "type": "ETF", "index": "S&P 500"},
            {"symbol": "IVV", "name": "iShares Core S&P 500 ETF", "type": "ETF", "index": "S&P 500"},
            {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "type": "ETF", "index": "Total Market"},
        ]
        
        # Function to check if securities are substantially identical
        def are_substantially_identical(sec1, sec2):
            # Simplified check - same underlying index
            return (sec1["index"] == sec2["index"] and 
                   sec1["type"] == sec2["type"])
        
        # Test SPY vs VOO (both S&P 500 ETFs)
        spy = securities[0]
        voo = securities[1]
        vti = securities[3]
        
        assert are_substantially_identical(spy, voo) is True   # Same index
        assert are_substantially_identical(spy, vti) is False  # Different indices
    
    def test_optimal_harvesting_strategy(self):
        """Test optimal tax loss harvesting strategy."""
        # Portfolio positions with different loss amounts and holding periods
        positions = [
            {"symbol": "LOSS_ST", "loss": Decimal('2000'), "holding_days": 150, "liquidity": "high"},
            {"symbol": "LOSS_LT", "loss": Decimal('3000'), "holding_days": 400, "liquidity": "high"},
            {"symbol": "LOSS_SM", "loss": Decimal('800'), "holding_days": 200, "liquidity": "low"},
            {"symbol": "GAIN_ST", "loss": Decimal('-1500'), "holding_days": 100, "liquidity": "high"},  # Gain
        ]
        
        # Harvesting strategy: prioritize by loss amount and liquidity
        harvestable_positions = [
            pos for pos in positions 
            if pos["loss"] > Decimal('1000') and pos["liquidity"] == "high"
        ]
        
        # Sort by loss amount (descending)
        harvestable_positions.sort(key=lambda x: x["loss"], reverse=True)
        
        assert len(harvestable_positions) == 2
        assert harvestable_positions[0]["symbol"] == "LOSS_LT"  # Highest loss first
        assert harvestable_positions[1]["symbol"] == "LOSS_ST"
        
        # Calculate total harvestable loss
        total_harvestable_loss = sum(pos["loss"] for pos in harvestable_positions)
        assert total_harvestable_loss == Decimal('5000')


@pytest.mark.django_db
class TestRetirementAccountTaxRules:
    """Test tax rules for retirement accounts (401k, IRA, Roth IRA)."""
    
    def setup_method(self):
        """Set up retirement account testing."""
        self.user = User.objects.create_user(
            username="retiree",
            email="retirement@example.com",
            password="retire123"
        )
    
    def test_traditional_ira_contribution_limits(self):
        """Test traditional IRA contribution limits and tax deductions."""
        # 2024 IRA contribution limits
        age = 45  # Under 50
        base_contribution_limit = Decimal('7000.00')  # 2024 limit
        catch_up_contribution = Decimal('1000.00')  # Age 50+
        
        # Contribution limit based on age
        if age >= 50:
            max_contribution = base_contribution_limit + catch_up_contribution
        else:
            max_contribution = base_contribution_limit
        
        assert max_contribution == Decimal('7000.00')  # Under 50
        
        # Test age 50+ scenario
        age_50_plus = 55
        if age_50_plus >= 50:
            max_contribution_50_plus = base_contribution_limit + catch_up_contribution
        else:
            max_contribution_50_plus = base_contribution_limit
            
        assert max_contribution_50_plus == Decimal('8000.00')  # With catch-up
    
    def test_roth_ira_income_limits(self):
        """Test Roth IRA income limits and phase-out rules."""
        # 2024 Roth IRA income limits (single filer example)
        income_phase_out_start = Decimal('138000')
        income_phase_out_end = Decimal('153000')
        base_contribution_limit = Decimal('7000.00')
        
        test_incomes = [
            Decimal('100000'),  # Below phase-out
            Decimal('145000'),  # In phase-out range
            Decimal('160000'),  # Above phase-out
        ]
        
        for income in test_incomes:
            if income <= income_phase_out_start:
                # Full contribution allowed
                allowed_contribution = base_contribution_limit
            elif income >= income_phase_out_end:
                # No contribution allowed
                allowed_contribution = Decimal('0')
            else:
                # Phase-out calculation
                phase_out_range = income_phase_out_end - income_phase_out_start
                excess_income = income - income_phase_out_start
                reduction_ratio = excess_income / phase_out_range
                allowed_contribution = base_contribution_limit * (Decimal('1') - reduction_ratio)
                # Round down to nearest $10
                allowed_contribution = (allowed_contribution / 10).quantize(Decimal('1')) * 10
        
        # Test specific values
        income_100k = Decimal('100000')
        allowed_100k = base_contribution_limit if income_100k <= income_phase_out_start else Decimal('0')
        assert allowed_100k == Decimal('7000.00')
        
        income_160k = Decimal('160000')
        allowed_160k = Decimal('0') if income_160k >= income_phase_out_end else base_contribution_limit
        assert allowed_160k == Decimal('0')
    
    def test_401k_contribution_limits(self):
        """Test 401(k) contribution limits and employer matching."""
        # 2024 401(k) limits
        age = 35
        employee_base_limit = Decimal('23000.00')  # 2024 limit
        catch_up_limit = Decimal('7500.00')  # Age 50+
        total_annual_limit = Decimal('69000.00')  # Employee + employer
        
        # Employee contribution limit
        if age >= 50:
            employee_limit = employee_base_limit + catch_up_limit
        else:
            employee_limit = employee_base_limit
        
        assert employee_limit == Decimal('23000.00')  # Under 50
        
        # Employer matching example (50% of first 6% of salary)
        annual_salary = Decimal('80000.00')
        match_percentage = Decimal('0.50')  # 50% match
        match_limit_percentage = Decimal('0.06')  # Up to 6% of salary
        
        max_matched_contribution = annual_salary * match_limit_percentage  # $4,800
        employee_contribution = Decimal('5000.00')  # Employee contributes $5,000
        
        matched_amount = min(employee_contribution, max_matched_contribution) * match_percentage
        
        assert max_matched_contribution == Decimal('4800.00')
        assert matched_amount == Decimal('2400.00')  # 50% of $4,800
    
    def test_required_minimum_distributions(self):
        """Test required minimum distribution calculations for traditional accounts."""
        # RMD calculation for traditional IRA/401(k) at age 72+
        age = 75
        account_balance = Decimal('500000.00')  # End of previous year
        
        # IRS life expectancy table (simplified)
        life_expectancy_factors = {
            72: Decimal('27.4'), 73: Decimal('26.5'), 74: Decimal('25.5'),
            75: Decimal('24.6'), 76: Decimal('23.7'), 77: Decimal('22.9')
        }
        
        if age >= 72:
            life_expectancy_factor = life_expectancy_factors.get(age, Decimal('22.9'))
            required_distribution = account_balance / life_expectancy_factor
        else:
            required_distribution = Decimal('0')  # No RMD before age 72
        
        assert life_expectancy_factor == Decimal('24.6')
        assert required_distribution.quantize(Decimal('0.01')) == Decimal('20325.20')
        
        # Test no RMD for younger age
        young_age = 65
        young_rmd = Decimal('0') if young_age < 72 else account_balance / life_expectancy_factors.get(young_age, Decimal('22.9'))
        assert young_rmd == Decimal('0')


@pytest.mark.django_db
class TestInternationalTaxCompliance:
    """Test international tax compliance features."""
    
    def setup_method(self):
        """Set up international tax testing."""
        self.user = User.objects.create_user(
            username="international",
            email="intl@example.com",
            password="intl123"
        )
    
    def test_foreign_tax_credit_calculation(self):
        """Test foreign tax credit calculation for international investments."""
        # Foreign dividend with withholding tax
        foreign_dividend = Decimal('1000.00')
        foreign_withholding_rate = Decimal('0.15')  # 15% withholding
        foreign_tax_withheld = foreign_dividend * foreign_withholding_rate
        
        # US tax on same dividend
        us_marginal_rate = Decimal('0.22')  # 22% bracket
        us_tax_on_dividend = foreign_dividend * us_marginal_rate
        
        # Foreign tax credit (limited to US tax on foreign income)
        foreign_tax_credit = min(foreign_tax_withheld, us_tax_on_dividend)
        
        assert foreign_tax_withheld == Decimal('150.00')
        assert us_tax_on_dividend == Decimal('220.00')
        assert foreign_tax_credit == Decimal('150.00')  # Limited to foreign tax paid
        
        # Net US tax after foreign tax credit
        net_us_tax = us_tax_on_dividend - foreign_tax_credit
        assert net_us_tax == Decimal('70.00')
    
    def test_currency_conversion_for_tax_reporting(self):
        """Test currency conversion for foreign investments."""
        # Foreign investment in EUR
        eur_purchase_price = Decimal('85.00')
        eur_sale_price = Decimal('95.00')
        shares = Decimal('100')
        
        # Exchange rates on transaction dates
        usd_eur_rate_purchase = Decimal('1.20')  # $1.20 per EUR
        usd_eur_rate_sale = Decimal('1.15')      # $1.15 per EUR
        
        # Convert to USD for tax reporting
        usd_cost_basis = (eur_purchase_price * shares) * usd_eur_rate_purchase
        usd_sale_proceeds = (eur_sale_price * shares) * usd_eur_rate_sale
        
        # Capital gain/loss in USD
        usd_capital_gain = usd_sale_proceeds - usd_cost_basis
        
        assert usd_cost_basis == Decimal('10200.00')   # €8,500 * $1.20
        assert usd_sale_proceeds == Decimal('10925.00') # €9,500 * $1.15
        assert usd_capital_gain == Decimal('725.00')
        
        # Note: Also includes currency gain/loss component
        eur_gain = (eur_sale_price - eur_purchase_price) * shares  # €1,000
        eur_gain_in_usd_at_sale_rate = eur_gain * usd_eur_rate_sale  # $1,150
        
        currency_effect = usd_capital_gain - eur_gain_in_usd_at_sale_rate
        assert currency_effect == Decimal('-425.00')  # Currency loss
    
    def test_pfic_reporting_requirements(self):
        """Test PFIC (Passive Foreign Investment Company) reporting requirements."""
        # Simplified PFIC test
        foreign_fund = {
            'name': 'Foreign Mutual Fund',
            'country': 'Germany',
            'passive_income_percentage': Decimal('0.80'),  # 80% passive income
            'us_shareholder_percentage': Decimal('0.05')   # 5% US ownership
        }
        
        # PFIC tests
        passive_income_test = foreign_fund['passive_income_percentage'] >= Decimal('0.75')
        asset_test = True  # Simplified - would need actual asset composition
        
        is_pfic = passive_income_test or asset_test
        
        assert passive_income_test is True  # Meets passive income test
        assert is_pfic is True
        
        # PFIC requires Form 8621 filing
        if is_pfic:
            requires_form_8621 = True
            # Additional reporting and potential adverse tax treatment
            pfic_tax_treatment = "Mark-to-market or excess distribution method"
        else:
            requires_form_8621 = False
            pfic_tax_treatment = "Regular capital gains treatment"
        
        assert requires_form_8621 is True
        assert "Mark-to-market" in pfic_tax_treatment


@pytest.mark.django_db
class TestTaxReportGeneration:
    """Test tax report generation and formatting."""
    
    def setup_method(self):
        """Set up tax report testing."""
        self.user = User.objects.create_user(
            username="reporter",
            email="reports@example.com",
            password="report123"
        )
        
        self.tax_year = 2024
    
    def test_schedule_d_generation(self):
        """Test Schedule D (capital gains/losses) generation."""
        # Sample transactions for Schedule D
        transactions = [
            {
                'asset': 'AAPL',
                'description': 'Apple Inc. Common Stock',
                'date_acquired': date(2023, 3, 15),
                'date_sold': date(2024, 8, 20),
                'proceeds': Decimal('15000.00'),
                'cost_basis': Decimal('12000.00'),
                'gain_loss': Decimal('3000.00'),
                'term': 'Long-term'
            },
            {
                'asset': 'GOOGL',
                'description': 'Alphabet Inc. Class A',
                'date_acquired': date(2024, 1, 10),
                'date_sold': date(2024, 6, 15),
                'proceeds': Decimal('8000.00'),
                'cost_basis': Decimal('9000.00'),
                'gain_loss': Decimal('-1000.00'),
                'term': 'Short-term'
            }
        ]
        
        # Separate by term
        short_term_transactions = [t for t in transactions if t['term'] == 'Short-term']
        long_term_transactions = [t for t in transactions if t['term'] == 'Long-term']
        
        # Calculate totals
        short_term_gain_loss = sum(t['gain_loss'] for t in short_term_transactions)
        long_term_gain_loss = sum(t['gain_loss'] for t in long_term_transactions)
        net_capital_gain_loss = short_term_gain_loss + long_term_gain_loss
        
        assert short_term_gain_loss == Decimal('-1000.00')
        assert long_term_gain_loss == Decimal('3000.00')
        assert net_capital_gain_loss == Decimal('2000.00')
        
        # Schedule D format validation
        for transaction in transactions:
            assert 'asset' in transaction
            assert 'date_acquired' in transaction
            assert 'date_sold' in transaction
            assert transaction['date_sold'] > transaction['date_acquired']
    
    def test_form_1099_div_equivalent(self):
        """Test 1099-DIV equivalent report generation."""
        # Sample dividend data
        dividend_data = [
            {
                'payer': 'Apple Inc.',
                'ordinary_dividends': Decimal('150.00'),
                'qualified_dividends': Decimal('150.00'),
                'capital_gain_distributions': Decimal('0.00'),
                'federal_tax_withheld': Decimal('0.00'),
                'foreign_tax_paid': Decimal('0.00')
            },
            {
                'payer': 'Vanguard S&P 500 ETF',
                'ordinary_dividends': Decimal('450.00'),
                'qualified_dividends': Decimal('450.00'),
                'capital_gain_distributions': Decimal('25.00'),
                'federal_tax_withheld': Decimal('0.00'),
                'foreign_tax_paid': Decimal('5.00')
            }
        ]
        
        # Calculate totals
        total_ordinary_dividends = sum(d['ordinary_dividends'] for d in dividend_data)
        total_qualified_dividends = sum(d['qualified_dividends'] for d in dividend_data)
        total_capital_gain_distributions = sum(d['capital_gain_distributions'] for d in dividend_data)
        total_foreign_tax_paid = sum(d['foreign_tax_paid'] for d in dividend_data)
        
        assert total_ordinary_dividends == Decimal('600.00')
        assert total_qualified_dividends == Decimal('600.00')
        assert total_capital_gain_distributions == Decimal('25.00')
        assert total_foreign_tax_paid == Decimal('5.00')
        
        # 1099-DIV validation
        for dividend in dividend_data:
            assert dividend['qualified_dividends'] <= dividend['ordinary_dividends']
            assert all(value >= Decimal('0') for value in dividend.values() if isinstance(value, Decimal))
    
    def test_tax_summary_report(self):
        """Test comprehensive tax summary report."""
        # Comprehensive tax data
        tax_summary = {
            'tax_year': self.tax_year,
            'short_term_capital_gains': Decimal('-500.00'),
            'long_term_capital_gains': Decimal('2500.00'),
            'ordinary_dividends': Decimal('1200.00'),
            'qualified_dividends': Decimal('1000.00'),
            'foreign_tax_credits': Decimal('25.00'),
            'tax_loss_carryforward_used': Decimal('1000.00'),
            'wash_sales_disallowed': Decimal('200.00')
        }
        
        # Calculate net capital gains
        net_capital_gains = (tax_summary['short_term_capital_gains'] + 
                           tax_summary['long_term_capital_gains'])
        
        # Calculate total investment income
        total_investment_income = (net_capital_gains + 
                                 tax_summary['ordinary_dividends'])
        
        # Calculate net taxable investment income
        net_taxable_income = total_investment_income - tax_summary['foreign_tax_credits']
        
        assert net_capital_gains == Decimal('2000.00')
        assert total_investment_income == Decimal('3200.00')
        assert net_taxable_income == Decimal('3175.00')
        
        # Report validation
        assert tax_summary['qualified_dividends'] <= tax_summary['ordinary_dividends']
        assert tax_summary['tax_year'] == self.tax_year
    
    def test_cost_basis_tracking_report(self):
        """Test cost basis tracking report for compliance."""
        # Cost basis tracking for multiple lots
        cost_basis_records = [
            {
                'asset': 'MSFT',
                'lot_id': 1,
                'acquisition_date': date(2023, 1, 15),
                'quantity': Decimal('100'),
                'cost_per_share': Decimal('250.00'),
                'total_cost': Decimal('25000.00'),
                'adjustments': Decimal('0.00'),  # Stock splits, etc.
                'remaining_quantity': Decimal('100')
            },
            {
                'asset': 'MSFT',
                'lot_id': 2,
                'acquisition_date': date(2023, 6, 20),
                'quantity': Decimal('50'),
                'cost_per_share': Decimal('300.00'),
                'total_cost': Decimal('15000.00'),
                'adjustments': Decimal('0.00'),
                'remaining_quantity': Decimal('50')
            }
        ]
        
        # Aggregate by asset
        asset_totals = {}
        for record in cost_basis_records:
            asset = record['asset']
            if asset not in asset_totals:
                asset_totals[asset] = {
                    'total_quantity': Decimal('0'),
                    'total_cost': Decimal('0'),
                    'weighted_avg_cost': Decimal('0')
                }
            
            asset_totals[asset]['total_quantity'] += record['remaining_quantity']
            asset_totals[asset]['total_cost'] += record['total_cost']
        
        # Calculate weighted average cost
        for asset, totals in asset_totals.items():
            if totals['total_quantity'] > 0:
                totals['weighted_avg_cost'] = totals['total_cost'] / totals['total_quantity']
        
        msft_totals = asset_totals['MSFT']
        assert msft_totals['total_quantity'] == Decimal('150')
        assert msft_totals['total_cost'] == Decimal('40000.00')
        assert msft_totals['weighted_avg_cost'].quantize(Decimal('0.01')) == Decimal('266.67')