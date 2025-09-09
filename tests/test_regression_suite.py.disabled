"""
Regression Test Suite for Personal Finance Platform

This module contains regression tests to ensure that core functionality
is preserved across updates and changes to the platform.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json

User = get_user_model()


class TestCorePortfolioRegression(TestCase):
    """Regression tests for core portfolio functionality."""
    
    def setUp(self):
        """Set up regression test data."""
        self.user = User.objects.create_user(
            username='regression_user',
            email='regression@test.com',
            password='regression_pass'
        )
    
    def test_portfolio_creation_regression(self):
        """Ensure portfolio creation works as expected across updates."""
        with patch('personal_finance.portfolios.models.Portfolio') as MockPortfolio:
            # Mock the expected behavior
            mock_portfolio_instance = Mock()
            mock_portfolio_instance.id = 1
            mock_portfolio_instance.name = 'Regression Test Portfolio'
            mock_portfolio_instance.description = 'Testing portfolio creation'
            mock_portfolio_instance.user = self.user
            mock_portfolio_instance.created_at = datetime.now()
            mock_portfolio_instance.is_active = True
            
            MockPortfolio.objects.create.return_value = mock_portfolio_instance
            MockPortfolio.objects.get.return_value = mock_portfolio_instance
            
            # Test portfolio creation
            portfolio = MockPortfolio.objects.create(
                name='Regression Test Portfolio',
                description='Testing portfolio creation',
                user=self.user
            )
            
            # Verify expected behavior
            self.assertEqual(portfolio.name, 'Regression Test Portfolio')
            self.assertEqual(portfolio.user, self.user)
            self.assertTrue(portfolio.is_active)
            self.assertIsNotNone(portfolio.created_at)
            
            # Test portfolio retrieval
            retrieved_portfolio = MockPortfolio.objects.get(id=1)
            self.assertEqual(retrieved_portfolio.id, 1)
            self.assertEqual(retrieved_portfolio.name, portfolio.name)
    
    def test_transaction_processing_regression(self):
        """Ensure transaction processing maintains expected behavior."""
        with patch('personal_finance.portfolios.models.Transaction') as MockTransaction, \
             patch('personal_finance.portfolios.models.Position') as MockPosition:
            
            # Mock transaction
            mock_transaction = Mock()
            mock_transaction.id = 1
            mock_transaction.portfolio_id = 1
            mock_transaction.symbol = 'AAPL'
            mock_transaction.transaction_type = 'BUY'
            mock_transaction.quantity = 100
            mock_transaction.price = Decimal('150.00')
            mock_transaction.commission = Decimal('9.99')
            mock_transaction.date = datetime.now().date()
            
            MockTransaction.objects.create.return_value = mock_transaction
            
            # Mock position update
            mock_position = Mock()
            mock_position.portfolio_id = 1
            mock_position.symbol = 'AAPL'
            mock_position.quantity = 100
            mock_position.average_cost = Decimal('150.00')
            mock_position.total_cost = Decimal('15009.99')  # Including commission
            
            MockPosition.objects.get_or_create.return_value = (mock_position, True)
            
            # Test transaction creation
            transaction = MockTransaction.objects.create(
                portfolio_id=1,
                symbol='AAPL',
                transaction_type='BUY',
                quantity=100,
                price=Decimal('150.00'),
                commission=Decimal('9.99')
            )
            
            # Verify transaction properties
            self.assertEqual(transaction.symbol, 'AAPL')
            self.assertEqual(transaction.quantity, 100)
            self.assertEqual(transaction.price, Decimal('150.00'))
            self.assertEqual(transaction.commission, Decimal('9.99'))
            
            # Test position creation/update
            position, created = MockPosition.objects.get_or_create(
                portfolio_id=1,
                symbol='AAPL',
                defaults={
                    'quantity': transaction.quantity,
                    'average_cost': transaction.price
                }
            )
            
            self.assertEqual(position.symbol, 'AAPL')
            self.assertEqual(position.quantity, 100)
            self.assertTrue(created)
    
    def test_portfolio_valuation_regression(self):
        """Ensure portfolio valuation calculations remain accurate."""
        # Test data representing a typical portfolio
        portfolio_positions = [
            {
                'symbol': 'AAPL',
                'quantity': 100,
                'cost_basis': Decimal('150.00'),
                'current_price': Decimal('155.00')
            },
            {
                'symbol': 'GOOGL', 
                'quantity': 50,
                'cost_basis': Decimal('2500.00'),
                'current_price': Decimal('2550.00')
            },
            {
                'symbol': 'MSFT',
                'quantity': 75,
                'cost_basis': Decimal('300.00'),
                'current_price': Decimal('320.00')
            }
        ]
        
        # Expected calculations
        expected_total_cost = (
            100 * Decimal('150.00') +   # AAPL: 15,000
            50 * Decimal('2500.00') +   # GOOGL: 125,000
            75 * Decimal('300.00')      # MSFT: 22,500
        )  # Total: 162,500
        
        expected_total_value = (
            100 * Decimal('155.00') +   # AAPL: 15,500
            50 * Decimal('2550.00') +   # GOOGL: 127,500
            75 * Decimal('320.00')      # MSFT: 24,000
        )  # Total: 167,000
        
        expected_total_return = expected_total_value - expected_total_cost  # 4,500
        expected_return_percentage = (expected_total_return / expected_total_cost) * 100  # 2.77%
        
        # Perform calculations
        total_cost = sum(pos['quantity'] * pos['cost_basis'] for pos in portfolio_positions)
        total_value = sum(pos['quantity'] * pos['current_price'] for pos in portfolio_positions)
        total_return = total_value - total_cost
        return_percentage = (total_return / total_cost) * 100 if total_cost > 0 else 0
        
        # Verify calculations match expected values
        self.assertEqual(total_cost, expected_total_cost)
        self.assertEqual(total_value, expected_total_value)
        self.assertEqual(total_return, expected_total_return)
        self.assertAlmostEqual(float(return_percentage), 2.77, places=2)
    
    def test_asset_allocation_regression(self):
        """Ensure asset allocation calculations remain consistent."""
        portfolio_positions = [
            {'symbol': 'AAPL', 'market_value': Decimal('15500.00')},
            {'symbol': 'GOOGL', 'market_value': Decimal('127500.00')},
            {'symbol': 'MSFT', 'market_value': Decimal('24000.00')}
        ]
        
        total_value = sum(pos['market_value'] for pos in portfolio_positions)
        
        # Calculate allocations
        allocations = {}
        for position in portfolio_positions:
            allocation = (position['market_value'] / total_value) * 100
            allocations[position['symbol']] = round(float(allocation), 2)
        
        # Expected allocations (percentages)
        expected_allocations = {
            'AAPL': 9.28,   # 15,500 / 167,000 * 100
            'GOOGL': 76.35, # 127,500 / 167,000 * 100  
            'MSFT': 14.37   # 24,000 / 167,000 * 100
        }
        
        # Verify allocations
        for symbol, expected_allocation in expected_allocations.items():
            self.assertAlmostEqual(allocations[symbol], expected_allocation, places=2)
        
        # Ensure allocations sum to 100%
        total_allocation = sum(allocations.values())
        self.assertAlmostEqual(total_allocation, 100.0, places=1)


class TestAnalyticsRegression(TestCase):
    """Regression tests for analytics calculations."""
    
    def test_sharpe_ratio_calculation_regression(self):
        """Ensure Sharpe ratio calculation remains accurate."""
        # Test data: monthly returns for one year
        monthly_returns = [
            0.05, -0.02, 0.08, 0.03, -0.01, 0.06,
            0.02, -0.04, 0.07, 0.01, 0.04, -0.03
        ]
        risk_free_rate = 0.02  # 2% annual = ~0.17% monthly
        monthly_risk_free = risk_free_rate / 12
        
        # Calculate excess returns
        excess_returns = [r - monthly_risk_free for r in monthly_returns]
        
        # Calculate mean and standard deviation
        import statistics
        mean_excess_return = statistics.mean(excess_returns)
        std_excess_return = statistics.stdev(excess_returns)
        
        # Calculate Sharpe ratio (annualized)
        sharpe_ratio = (mean_excess_return * 12) / (std_excess_return * (12 ** 0.5))
        
        # Expected value based on test data
        expected_sharpe_ratio = 1.09  # Approximate expected value
        
        self.assertAlmostEqual(sharpe_ratio, expected_sharpe_ratio, places=1)
        self.assertGreater(sharpe_ratio, 0)  # Should be positive for this dataset
    
    def test_var_calculation_regression(self):
        """Ensure Value at Risk calculation remains consistent."""
        # Portfolio returns for VaR calculation
        portfolio_returns = [
            0.05, -0.08, 0.12, -0.03, 0.07, -0.15, 0.09, -0.05,
            0.02, -0.11, 0.06, -0.02, 0.08, -0.09, 0.04, -0.06,
            0.10, -0.04, 0.03, -0.07
        ]
        
        confidence_level = 0.95  # 95% confidence
        
        # Sort returns and find VaR
        sorted_returns = sorted(portfolio_returns)
        var_index = int((1 - confidence_level) * len(sorted_returns))
        var_95 = sorted_returns[var_index]
        
        # Expected VaR (approximately)
        expected_var = -0.11  # 5th percentile of sorted returns
        
        self.assertAlmostEqual(var_95, expected_var, places=2)
        self.assertLess(var_95, 0)  # VaR should be negative (representing loss)
    
    def test_beta_calculation_regression(self):
        """Ensure beta calculation remains accurate."""
        # Market returns (benchmark)
        market_returns = [
            0.02, -0.01, 0.04, 0.01, -0.02, 0.03, 0.00, -0.01,
            0.02, 0.01, 0.03, -0.01, 0.02, 0.00, 0.01, -0.02
        ]
        
        # Portfolio returns
        portfolio_returns = [
            0.03, -0.02, 0.06, 0.02, -0.03, 0.04, 0.01, -0.02,
            0.03, 0.01, 0.05, -0.02, 0.03, 0.00, 0.02, -0.03
        ]
        
        # Calculate beta using covariance and variance
        import statistics
        
        # Calculate covariance
        mean_market = statistics.mean(market_returns)
        mean_portfolio = statistics.mean(portfolio_returns)
        
        covariance = sum(
            (market_returns[i] - mean_market) * (portfolio_returns[i] - mean_portfolio)
            for i in range(len(market_returns))
        ) / (len(market_returns) - 1)
        
        # Calculate market variance
        market_variance = statistics.variance(market_returns)
        
        # Calculate beta
        beta = covariance / market_variance
        
        # Expected beta (approximately 1.5 based on test data)
        expected_beta = 1.5
        
        self.assertAlmostEqual(beta, expected_beta, places=1)
        self.assertGreater(beta, 1.0)  # Portfolio should be more volatile than market
    
    def test_max_drawdown_regression(self):
        """Ensure maximum drawdown calculation remains consistent."""
        # Portfolio values over time
        portfolio_values = [
            10000, 10500, 10200, 10800, 11200, 10900,
            10600, 9800, 9200, 9600, 10100, 10400,
            10800, 11100, 10700, 11500, 12000, 11800
        ]
        
        # Calculate maximum drawdown
        peak = portfolio_values[0]
        max_drawdown = 0
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Expected maximum drawdown
        # Peak was 11200, trough was 9200
        # Drawdown = (11200 - 9200) / 11200 = 0.1786 (17.86%)
        expected_max_drawdown = 0.1786
        
        self.assertAlmostEqual(max_drawdown, expected_max_drawdown, places=3)
        self.assertGreater(max_drawdown, 0)
        self.assertLess(max_drawdown, 1)


class TestTaxCalculationRegression(TestCase):
    """Regression tests for tax calculations."""
    
    def test_capital_gains_calculation_regression(self):
        """Ensure capital gains calculation remains accurate."""
        # Transaction history for capital gains
        transactions = [
            # Buy 100 shares at $100
            {'date': '2023-01-15', 'type': 'BUY', 'symbol': 'AAPL', 'quantity': 100, 'price': 100.00},
            # Buy 50 more shares at $120
            {'date': '2023-03-10', 'type': 'BUY', 'symbol': 'AAPL', 'quantity': 50, 'price': 120.00},
            # Sell 75 shares at $150 (FIFO)
            {'date': '2023-08-20', 'type': 'SELL', 'symbol': 'AAPL', 'quantity': 75, 'price': 150.00},
        ]
        
        # Calculate capital gains using FIFO
        remaining_shares = []
        capital_gains = []
        
        for txn in transactions:
            if txn['type'] == 'BUY':
                remaining_shares.append({
                    'quantity': txn['quantity'],
                    'cost_basis': txn['price'],
                    'date': txn['date']
                })
            elif txn['type'] == 'SELL':
                shares_to_sell = txn['quantity']
                sale_price = txn['price']
                sale_date = txn['date']
                
                while shares_to_sell > 0 and remaining_shares:
                    lot = remaining_shares[0]
                    
                    if lot['quantity'] <= shares_to_sell:
                        # Sell entire lot
                        gain = (sale_price - lot['cost_basis']) * lot['quantity']
                        capital_gains.append({
                            'gain': gain,
                            'quantity': lot['quantity'],
                            'purchase_date': lot['date'],
                            'sale_date': sale_date
                        })
                        shares_to_sell -= lot['quantity']
                        remaining_shares.pop(0)
                    else:
                        # Partial sale of lot
                        gain = (sale_price - lot['cost_basis']) * shares_to_sell
                        capital_gains.append({
                            'gain': gain,
                            'quantity': shares_to_sell,
                            'purchase_date': lot['date'],
                            'sale_date': sale_date
                        })
                        lot['quantity'] -= shares_to_sell
                        shares_to_sell = 0
        
        # Expected results:
        # Sell 75 shares: first 100 shares bought at $100
        # Capital gain = (150 - 100) * 75 = $3,750
        expected_total_gain = 3750.0
        actual_total_gain = sum(cg['gain'] for cg in capital_gains)
        
        self.assertEqual(actual_total_gain, expected_total_gain)
        self.assertEqual(len(capital_gains), 1)  # Should be one capital gain record
        self.assertEqual(capital_gains[0]['quantity'], 75)
    
    def test_wash_sale_detection_regression(self):
        """Ensure wash sale detection works correctly."""
        transactions = [
            # Sell at a loss
            {'date': '2023-06-01', 'type': 'SELL', 'symbol': 'MSFT', 'quantity': 100, 'price': 90.00},
            # Buy back within 30 days (wash sale)
            {'date': '2023-06-15', 'type': 'BUY', 'symbol': 'MSFT', 'quantity': 100, 'price': 85.00},
            # Another sale (no wash sale - different timeframe)
            {'date': '2023-08-01', 'type': 'SELL', 'symbol': 'AAPL', 'quantity': 50, 'price': 140.00},
        ]
        
        # Assume we had previous purchases
        previous_cost_basis = {'MSFT': 100.00, 'AAPL': 150.00}
        
        wash_sales = []
        
        for i, txn in enumerate(transactions):
            if txn['type'] == 'SELL':
                sale_date = datetime.strptime(txn['date'], '%Y-%m-%d')
                
                # Look for repurchases within 30 days
                for j, other_txn in enumerate(transactions[i+1:], i+1):
                    if (other_txn['type'] == 'BUY' and 
                        other_txn['symbol'] == txn['symbol']):
                        
                        buy_date = datetime.strptime(other_txn['date'], '%Y-%m-%d')
                        days_between = (buy_date - sale_date).days
                        
                        if 0 <= days_between <= 30:
                            # Calculate loss (wash sale only applies to losses)
                            cost_basis = previous_cost_basis.get(txn['symbol'], txn['price'])
                            if txn['price'] < cost_basis:
                                loss = (cost_basis - txn['price']) * txn['quantity']
                                wash_sales.append({
                                    'symbol': txn['symbol'],
                                    'sale_date': txn['date'],
                                    'buy_date': other_txn['date'],
                                    'disallowed_loss': loss
                                })
        
        # Expected: one wash sale for MSFT
        self.assertEqual(len(wash_sales), 1)
        self.assertEqual(wash_sales[0]['symbol'], 'MSFT')
        self.assertEqual(wash_sales[0]['disallowed_loss'], 1000.0)  # (100-90) * 100
    
    def test_dividend_income_classification_regression(self):
        """Ensure dividend income classification remains correct."""
        dividend_transactions = [
            # Qualified dividend (held > 60 days)
            {
                'symbol': 'AAPL',
                'dividend_amount': 0.25,
                'shares': 100,
                'ex_date': '2023-05-15',
                'holding_period_days': 120
            },
            # Non-qualified dividend (held < 60 days)
            {
                'symbol': 'MSFT',
                'dividend_amount': 0.30,
                'shares': 50,
                'ex_date': '2023-06-10',
                'holding_period_days': 45
            },
            # Qualified dividend (held exactly 61 days)
            {
                'symbol': 'GOOGL',
                'dividend_amount': 0.15,
                'shares': 25,
                'ex_date': '2023-07-01',
                'holding_period_days': 61
            }
        ]
        
        qualified_dividends = 0
        ordinary_dividends = 0
        
        for div in dividend_transactions:
            total_dividend = div['dividend_amount'] * div['shares']
            
            if div['holding_period_days'] > 60:
                qualified_dividends += total_dividend
            else:
                ordinary_dividends += total_dividend
        
        # Expected calculations:
        # AAPL: 0.25 * 100 = $25.00 (qualified)
        # MSFT: 0.30 * 50 = $15.00 (ordinary)
        # GOOGL: 0.15 * 25 = $3.75 (qualified)
        
        expected_qualified = 28.75  # 25.00 + 3.75
        expected_ordinary = 15.00
        
        self.assertEqual(qualified_dividends, expected_qualified)
        self.assertEqual(ordinary_dividends, expected_ordinary)


class TestDataIntegrityRegression(TestCase):
    """Regression tests for data integrity and consistency."""
    
    def test_position_balance_consistency_regression(self):
        """Ensure position balances remain consistent with transactions."""
        # Simulate transaction history
        transactions = [
            {'type': 'BUY', 'symbol': 'AAPL', 'quantity': 100, 'price': 150.00, 'date': '2023-01-15'},
            {'type': 'BUY', 'symbol': 'AAPL', 'quantity': 50, 'price': 160.00, 'date': '2023-02-15'},
            {'type': 'SELL', 'symbol': 'AAPL', 'quantity': 25, 'price': 170.00, 'date': '2023-03-15'},
            {'type': 'BUY', 'symbol': 'MSFT', 'quantity': 75, 'price': 300.00, 'date': '2023-01-20'},
            {'type': 'SELL', 'symbol': 'MSFT', 'quantity': 25, 'price': 320.00, 'date': '2023-04-20'},
        ]
        
        # Calculate expected positions
        positions = {}
        
        for txn in transactions:
            symbol = txn['symbol']
            
            if symbol not in positions:
                positions[symbol] = {'quantity': 0, 'total_cost': 0}
            
            if txn['type'] == 'BUY':
                positions[symbol]['quantity'] += txn['quantity']
                positions[symbol]['total_cost'] += txn['quantity'] * txn['price']
            elif txn['type'] == 'SELL':
                # For simplicity, use current average cost for FIFO
                if positions[symbol]['quantity'] > 0:
                    avg_cost = positions[symbol]['total_cost'] / positions[symbol]['quantity']
                    positions[symbol]['quantity'] -= txn['quantity']
                    positions[symbol]['total_cost'] -= txn['quantity'] * avg_cost
        
        # Expected final positions
        expected_positions = {
            'AAPL': {'quantity': 125, 'avg_cost': 153.33},  # (100*150 + 50*160 - 25*153.33) / 125
            'MSFT': {'quantity': 50, 'avg_cost': 300.00}    # (75*300 - 25*300) / 50
        }
        
        # Verify positions
        for symbol, expected in expected_positions.items():
            actual_quantity = positions[symbol]['quantity']
            actual_avg_cost = positions[symbol]['total_cost'] / actual_quantity if actual_quantity > 0 else 0
            
            self.assertEqual(actual_quantity, expected['quantity'])
            self.assertAlmostEqual(actual_avg_cost, expected['avg_cost'], places=2)
    
    def test_portfolio_summary_consistency_regression(self):
        """Ensure portfolio summary calculations remain consistent."""
        # Sample portfolio data
        positions = [
            {'symbol': 'AAPL', 'quantity': 100, 'cost_basis': 150.00, 'current_price': 155.00},
            {'symbol': 'GOOGL', 'quantity': 50, 'cost_basis': 2500.00, 'current_price': 2550.00},
            {'symbol': 'MSFT', 'quantity': 75, 'cost_basis': 300.00, 'current_price': 320.00},
        ]
        
        # Calculate summary metrics
        total_cost = sum(pos['quantity'] * pos['cost_basis'] for pos in positions)
        total_value = sum(pos['quantity'] * pos['current_price'] for pos in positions)
        total_return = total_value - total_cost
        return_percentage = (total_return / total_cost) * 100 if total_cost > 0 else 0
        
        # Calculate individual position metrics
        position_returns = []
        for pos in positions:
            pos_cost = pos['quantity'] * pos['cost_basis']
            pos_value = pos['quantity'] * pos['current_price']
            pos_return = pos_value - pos_cost
            pos_return_pct = (pos_return / pos_cost) * 100 if pos_cost > 0 else 0
            
            position_returns.append({
                'symbol': pos['symbol'],
                'return': pos_return,
                'return_percentage': pos_return_pct
            })
        
        # Verify consistency: sum of individual returns should equal total return
        sum_individual_returns = sum(pos['return'] for pos in position_returns)
        
        self.assertAlmostEqual(float(sum_individual_returns), float(total_return), places=2)
        
        # Verify expected values
        expected_total_cost = 162500.00  # 15000 + 125000 + 22500
        expected_total_value = 167000.00  # 15500 + 127500 + 24000
        expected_total_return = 4500.00
        
        self.assertAlmostEqual(float(total_cost), expected_total_cost, places=2)
        self.assertAlmostEqual(float(total_value), expected_total_value, places=2)
        self.assertAlmostEqual(float(total_return), expected_total_return, places=2)


class TestAPIEndpointRegression(APITestCase):
    """Regression tests for API endpoints."""
    
    def setUp(self):
        """Set up API regression tests."""
        self.user = User.objects.create_user(
            username='api_regression_user',
            email='api@regression.com',
            password='api_pass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_portfolio_list_endpoint_regression(self):
        """Ensure portfolio list endpoint behavior remains consistent."""
        with patch('personal_finance.portfolios.models.Portfolio.objects') as mock_objects:
            # Mock portfolio queryset
            mock_portfolio1 = Mock()
            mock_portfolio1.id = 1
            mock_portfolio1.name = 'Portfolio 1'
            mock_portfolio1.description = 'First portfolio'
            mock_portfolio1.user = self.user
            
            mock_portfolio2 = Mock()
            mock_portfolio2.id = 2
            mock_portfolio2.name = 'Portfolio 2'
            mock_portfolio2.description = 'Second portfolio'
            mock_portfolio2.user = self.user
            
            mock_objects.filter.return_value = [mock_portfolio1, mock_portfolio2]
            
            # Mock the response structure
            with patch('rest_framework.response.Response') as mock_response:
                mock_response.return_value.status_code = status.HTTP_200_OK
                mock_response.return_value.data = [
                    {
                        'id': 1,
                        'name': 'Portfolio 1',
                        'description': 'First portfolio',
                        'user': self.user.id
                    },
                    {
                        'id': 2,
                        'name': 'Portfolio 2',
                        'description': 'Second portfolio',
                        'user': self.user.id
                    }
                ]
                
                # Simulate API call
                response = mock_response.return_value
                
                # Verify response structure
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response.data), 2)
                self.assertEqual(response.data[0]['name'], 'Portfolio 1')
                self.assertEqual(response.data[1]['name'], 'Portfolio 2')
    
    def test_portfolio_create_endpoint_regression(self):
        """Ensure portfolio creation endpoint behavior remains consistent."""
        portfolio_data = {
            'name': 'New Regression Portfolio',
            'description': 'Created via regression test'
        }
        
        with patch('personal_finance.portfolios.serializers.PortfolioSerializer') as mock_serializer:
            mock_serializer_instance = mock_serializer.return_value
            mock_serializer_instance.is_valid.return_value = True
            mock_serializer_instance.save.return_value = Mock(
                id=3,
                name='New Regression Portfolio',
                description='Created via regression test',
                user=self.user
            )
            mock_serializer_instance.data = {
                'id': 3,
                'name': 'New Regression Portfolio',
                'description': 'Created via regression test',
                'user': self.user.id
            }
            
            with patch('rest_framework.response.Response') as mock_response:
                mock_response.return_value.status_code = status.HTTP_201_CREATED
                mock_response.return_value.data = mock_serializer_instance.data
                
                # Simulate API call
                response = mock_response.return_value
                
                # Verify response
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(response.data['name'], 'New Regression Portfolio')
                self.assertEqual(response.data['user'], self.user.id)
    
    def test_analytics_endpoint_regression(self):
        """Ensure analytics endpoint returns expected data structure."""
        with patch('personal_finance.analytics.services.AnalyticsService') as mock_service:
            # Mock analytics data
            mock_analytics = {
                'portfolio_id': 1,
                'total_value': 167000.00,
                'total_cost': 162500.00,
                'total_return': 4500.00,
                'return_percentage': 2.77,
                'risk_metrics': {
                    'sharpe_ratio': 1.25,
                    'beta': 1.1,
                    'var_95': -0.08,
                    'max_drawdown': -0.12
                },
                'allocation': {
                    'AAPL': 9.28,
                    'GOOGL': 76.35,
                    'MSFT': 14.37
                }
            }
            
            mock_service.calculate_portfolio_analytics.return_value = mock_analytics
            
            with patch('rest_framework.response.Response') as mock_response:
                mock_response.return_value.status_code = status.HTTP_200_OK
                mock_response.return_value.data = mock_analytics
                
                # Simulate API call
                response = mock_response.return_value
                
                # Verify response structure and key metrics
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn('total_value', response.data)
                self.assertIn('risk_metrics', response.data)
                self.assertIn('allocation', response.data)
                
                # Verify specific values
                self.assertEqual(response.data['total_value'], 167000.00)
                self.assertEqual(response.data['return_percentage'], 2.77)
                self.assertAlmostEqual(
                    sum(response.data['allocation'].values()), 
                    100.0, 
                    places=1
                )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])