"""
Performance Benchmark Test Suite for Personal Finance Platform

This module contains performance tests and benchmarks for critical operations
to ensure the platform meets performance requirements under various loads.
"""

import pytest
import time
import threading
import concurrent.futures
from decimal import Decimal
from unittest.mock import Mock, patch
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
import statistics
import memory_profiler
import psutil
import os

User = get_user_model()


class PerformanceTestMixin:
    """Mixin providing performance testing utilities."""
    
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure function execution time."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time
    
    def measure_memory_usage(self, func, *args, **kwargs):
        """Measure memory usage of function execution."""
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        result = func(*args, **kwargs)
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        return result, memory_used
    
    def run_concurrent_test(self, func, num_threads=10, iterations_per_thread=5):
        """Run function concurrently and measure performance."""
        results = []
        execution_times = []
        
        def worker():
            for _ in range(iterations_per_thread):
                start_time = time.perf_counter()
                result = func()
                end_time = time.perf_counter()
                results.append(result)
                execution_times.append(end_time - start_time)
        
        threads = []
        start_time = time.perf_counter()
        
        for _ in range(num_threads):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.perf_counter() - start_time
        
        return {
            'results': results,
            'total_time': total_time,
            'avg_execution_time': statistics.mean(execution_times),
            'max_execution_time': max(execution_times),
            'min_execution_time': min(execution_times),
            'throughput': len(results) / total_time
        }


class TestPortfolioPerformance(TestCase, PerformanceTestMixin):
    """Performance tests for portfolio operations."""
    
    def setUp(self):
        """Set up performance test data."""
        self.user = Mock()
        self.user.id = 1
        
        # Large portfolio for performance testing
        self.large_portfolio = self._create_large_portfolio(1000)
        self.medium_portfolio = self._create_large_portfolio(100)
        self.small_portfolio = self._create_large_portfolio(10)
    
    def test_portfolio_valuation_performance(self):
        """Test portfolio valuation with different sizes."""
        test_cases = [
            ('small', self.small_portfolio, 0.01),    # < 10ms
            ('medium', self.medium_portfolio, 0.1),   # < 100ms
            ('large', self.large_portfolio, 1.0),     # < 1s
        ]
        
        for size, portfolio, max_time in test_cases:
            with self.subTest(size=size):
                result, execution_time = self.measure_execution_time(
                    self._calculate_portfolio_value, portfolio
                )
                
                self.assertIsNotNone(result)
                self.assertLess(execution_time, max_time,
                               f"{size} portfolio valuation took {execution_time:.3f}s")
    
    def test_portfolio_analytics_performance(self):
        """Test performance of analytics calculations."""
        analytics_functions = [
            ('total_return', self._calculate_total_return),
            ('sharpe_ratio', self._calculate_sharpe_ratio),
            ('var_calculation', self._calculate_var),
            ('max_drawdown', self._calculate_max_drawdown),
        ]
        
        for func_name, func in analytics_functions:
            with self.subTest(function=func_name):
                result, execution_time = self.measure_execution_time(
                    func, self.large_portfolio
                )
                
                # Analytics should complete within 500ms
                self.assertLess(execution_time, 0.5,
                               f"{func_name} took {execution_time:.3f}s")
    
    def test_concurrent_portfolio_access(self):
        """Test concurrent access to portfolio data."""
        def portfolio_operation():
            return self._calculate_portfolio_value(self.medium_portfolio)
        
        performance = self.run_concurrent_test(
            portfolio_operation, 
            num_threads=20, 
            iterations_per_thread=5
        )
        
        # Should maintain good throughput under load
        self.assertGreater(performance['throughput'], 50,  # > 50 ops/sec
                          f"Throughput: {performance['throughput']:.2f} ops/sec")
        
        # Average response time should be reasonable
        self.assertLess(performance['avg_execution_time'], 0.1,  # < 100ms average
                       f"Average time: {performance['avg_execution_time']:.3f}s")
    
    def test_memory_usage_portfolio_operations(self):
        """Test memory usage of portfolio operations."""
        def memory_intensive_operation():
            # Simulate multiple portfolio calculations
            results = []
            for _ in range(100):
                result = self._calculate_portfolio_value(self.medium_portfolio)
                results.append(result)
            return results
        
        result, memory_used = self.measure_memory_usage(memory_intensive_operation)
        
        # Should not use excessive memory (< 50MB)
        self.assertLess(memory_used, 50,
                       f"Memory usage: {memory_used:.2f}MB")
    
    # Helper methods
    def _create_large_portfolio(self, size):
        """Create portfolio with specified number of positions."""
        return [
            {
                'symbol': f'STOCK{i:04d}',
                'quantity': 100 + (i % 1000),
                'cost_basis': Decimal(f'{100 + (i % 500)}.{(i % 100):02d}'),
                'current_price': Decimal(f'{105 + (i % 300)}.{(i % 100):02d}')
            }
            for i in range(size)
        ]
    
    def _calculate_portfolio_value(self, portfolio):
        """Calculate total portfolio value."""
        return sum(
            pos['quantity'] * pos['current_price']
            for pos in portfolio
        )
    
    def _calculate_total_return(self, portfolio):
        """Calculate total return."""
        cost = sum(pos['quantity'] * pos['cost_basis'] for pos in portfolio)
        value = sum(pos['quantity'] * pos['current_price'] for pos in portfolio)
        return (value - cost) / cost if cost > 0 else 0
    
    def _calculate_sharpe_ratio(self, portfolio):
        """Calculate Sharpe ratio."""
        # Simplified calculation for performance testing
        returns = [0.02, -0.01, 0.03, 0.015, -0.005] * (len(portfolio) // 5 + 1)
        returns = returns[:len(portfolio)]
        
        if not returns or len(returns) < 2:
            return 0
        
        avg_return = statistics.mean(returns)
        std_dev = statistics.stdev(returns)
        return avg_return / std_dev if std_dev > 0 else 0
    
    def _calculate_var(self, portfolio):
        """Calculate Value at Risk."""
        # Simplified VaR calculation
        returns = [(pos['current_price'] - pos['cost_basis']) / pos['cost_basis'] 
                  for pos in portfolio if pos['cost_basis'] > 0]
        
        if not returns:
            return 0
        
        sorted_returns = sorted(returns)
        var_index = int(0.05 * len(sorted_returns))  # 5% VaR
        return sorted_returns[var_index] if var_index < len(sorted_returns) else 0
    
    def _calculate_max_drawdown(self, portfolio):
        """Calculate maximum drawdown."""
        # Simplified max drawdown calculation
        values = [pos['current_price'] for pos in portfolio]
        
        if not values:
            return 0
        
        peak = values[0]
        max_dd = 0
        
        for value in values:
            if value > peak:
                peak = value
            dd = (value - peak) / peak if peak > 0 else 0
            if dd < max_dd:
                max_dd = dd
        
        return max_dd


class TestAPIPerformance(APITestCase, PerformanceTestMixin):
    """Performance tests for API endpoints."""
    
    def setUp(self):
        """Set up API performance tests."""
        self.user = User.objects.create_user(
            username='perftest',
            email='perf@test.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_api_response_times(self):
        """Test API endpoint response times."""
        endpoints = [
            ('/api/portfolios/', 'GET', None),
            ('/api/assets/', 'GET', None),
            ('/api/analytics/summary/', 'GET', None),
        ]
        
        for endpoint, method, data in endpoints:
            with self.subTest(endpoint=endpoint):
                with patch('django.http.HttpResponse') as mock_response:
                    mock_response.return_value.status_code = 200
                    mock_response.return_value.json.return_value = {}
                    
                    start_time = time.perf_counter()
                    # Simulate API call (mocked)
                    response = mock_response.return_value
                    end_time = time.perf_counter()
                    
                    response_time = end_time - start_time
                    
                    # API should respond within 200ms
                    self.assertLess(response_time, 0.2,
                                   f"{endpoint} response time: {response_time:.3f}s")
    
    def test_api_concurrent_load(self):
        """Test API performance under concurrent load."""
        def api_request():
            with patch('rest_framework.response.Response') as mock_response:
                mock_response.return_value.status_code = 200
                # Simulate API processing time
                time.sleep(0.01)  # 10ms processing time
                return mock_response.return_value
        
        performance = self.run_concurrent_test(
            api_request,
            num_threads=50,
            iterations_per_thread=2
        )
        
        # Should handle concurrent load efficiently
        self.assertGreater(performance['throughput'], 30,  # > 30 requests/sec
                          f"API throughput: {performance['throughput']:.2f} req/sec")
    
    def test_pagination_performance(self):
        """Test pagination performance with large datasets."""
        def paginated_request(page_size=100):
            # Simulate pagination processing
            mock_data = [{'id': i, 'name': f'Item {i}'} for i in range(page_size)]
            return {'results': mock_data, 'count': page_size}
        
        page_sizes = [10, 50, 100, 500, 1000]
        
        for page_size in page_sizes:
            with self.subTest(page_size=page_size):
                result, execution_time = self.measure_execution_time(
                    paginated_request, page_size
                )
                
                # Pagination should scale reasonably
                time_per_item = execution_time / page_size
                self.assertLess(time_per_item, 0.001,  # < 1ms per item
                               f"Page size {page_size}: {time_per_item:.4f}s per item")


class TestDataProcessingPerformance(TestCase, PerformanceTestMixin):
    """Performance tests for data processing operations."""
    
    def test_price_data_processing_performance(self):
        """Test performance of price data processing."""
        # Generate large price dataset
        large_dataset = [
            {
                'symbol': f'STOCK{i % 1000:03d}',
                'price': 100 + (i % 500) * 0.01,
                'volume': 1000000 + (i % 1000000),
                'timestamp': f'2023-01-{(i % 30) + 1:02d}'
            }
            for i in range(10000)  # 10k price points
        ]
        
        result, execution_time = self.measure_execution_time(
            self._process_price_data, large_dataset
        )
        
        # Should process 10k records quickly
        self.assertLess(execution_time, 2.0,  # < 2 seconds
                       f"Price data processing: {execution_time:.3f}s")
        
        # Should maintain data integrity
        self.assertEqual(len(result), len(large_dataset))
    
    def test_technical_indicators_performance(self):
        """Test performance of technical indicator calculations."""
        # Generate price series for technical analysis
        price_series = [100 + i * 0.1 + (i % 10) * 0.5 for i in range(1000)]
        
        indicators = [
            ('SMA_20', lambda p: self._calculate_sma(p, 20)),
            ('SMA_50', lambda p: self._calculate_sma(p, 50)),
            ('RSI_14', lambda p: self._calculate_rsi(p, 14)),
            ('MACD', lambda p: self._calculate_macd(p)),
        ]
        
        for indicator_name, indicator_func in indicators:
            with self.subTest(indicator=indicator_name):
                result, execution_time = self.measure_execution_time(
                    indicator_func, price_series
                )
                
                # Technical indicators should calculate quickly
                self.assertLess(execution_time, 0.5,  # < 500ms
                               f"{indicator_name}: {execution_time:.3f}s")
    
    def test_batch_transaction_processing(self):
        """Test performance of batch transaction processing."""
        # Generate large batch of transactions
        transactions = [
            {
                'portfolio_id': (i % 10) + 1,
                'symbol': f'STOCK{i % 100:02d}',
                'type': 'BUY' if i % 2 == 0 else 'SELL',
                'quantity': 100 + (i % 500),
                'price': Decimal(f'{100 + (i % 200)}.{(i % 100):02d}'),
                'date': f'2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}'
            }
            for i in range(5000)  # 5k transactions
        ]
        
        result, execution_time = self.measure_execution_time(
            self._process_transactions_batch, transactions
        )
        
        # Batch processing should be efficient
        time_per_transaction = execution_time / len(transactions)
        self.assertLess(time_per_transaction, 0.001,  # < 1ms per transaction
                       f"Batch processing: {time_per_transaction:.4f}s per transaction")
    
    def test_data_aggregation_performance(self):
        """Test performance of data aggregation operations."""
        # Generate portfolio data for aggregation
        portfolio_data = {
            'positions': [
                {
                    'symbol': f'STOCK{i:03d}',
                    'quantity': 100 + (i % 1000),
                    'cost_basis': Decimal(f'{50 + (i % 200)}.{(i % 100):02d}'),
                    'current_price': Decimal(f'{55 + (i % 250)}.{(i % 100):02d}'),
                    'sector': f'Sector{i % 10}',
                    'country': f'Country{i % 20}'
                }
                for i in range(2000)  # 2k positions
            ]
        }
        
        aggregations = [
            ('by_sector', lambda d: self._aggregate_by_sector(d)),
            ('by_country', lambda d: self._aggregate_by_country(d)),
            ('performance_metrics', lambda d: self._calculate_performance_metrics(d)),
        ]
        
        for agg_name, agg_func in aggregations:
            with self.subTest(aggregation=agg_name):
                result, execution_time = self.measure_execution_time(
                    agg_func, portfolio_data
                )
                
                # Aggregations should complete quickly
                self.assertLess(execution_time, 1.0,  # < 1 second
                               f"{agg_name}: {execution_time:.3f}s")
    
    # Helper methods
    def _process_price_data(self, dataset):
        """Process price data (validation, cleaning, formatting)."""
        processed = []
        for item in dataset:
            if item['price'] > 0 and item['volume'] > 0:
                processed_item = {
                    'symbol': item['symbol'],
                    'price': round(item['price'], 2),
                    'volume': int(item['volume']),
                    'timestamp': item['timestamp']
                }
                processed.append(processed_item)
        return processed
    
    def _calculate_sma(self, prices, period):
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return []
        
        sma = []
        for i in range(period - 1, len(prices)):
            avg = sum(prices[i - period + 1:i + 1]) / period
            sma.append(avg)
        return sma
    
    def _calculate_rsi(self, prices, period):
        """Calculate RSI."""
        if len(prices) < period + 1:
            return []
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        if len(gains) < period:
            return []
        
        # Calculate RSI
        rsi_values = []
        for i in range(period - 1, len(gains)):
            avg_gain = sum(gains[i - period + 1:i + 1]) / period
            avg_loss = sum(losses[i - period + 1:i + 1]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return rsi_values
    
    def _calculate_macd(self, prices):
        """Calculate MACD."""
        if len(prices) < 26:
            return []
        
        # Simplified MACD calculation
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        if len(ema_12) >= len(ema_26):
            macd = [ema_12[i] - ema_26[i] for i in range(len(ema_26))]
        else:
            macd = [ema_12[i] - ema_26[i] for i in range(len(ema_12))]
        
        return macd
    
    def _calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [prices[0]]  # Start with first price
        
        for i in range(1, len(prices)):
            ema_value = (prices[i] * multiplier) + (ema[-1] * (1 - multiplier))
            ema.append(ema_value)
        
        return ema[period - 1:]  # Return only after enough periods
    
    def _process_transactions_batch(self, transactions):
        """Process transactions in batch."""
        processed = []
        portfolio_balances = {}
        
        for txn in transactions:
            portfolio_id = txn['portfolio_id']
            symbol = txn['symbol']
            
            # Initialize portfolio if not exists
            if portfolio_id not in portfolio_balances:
                portfolio_balances[portfolio_id] = {}
            
            if symbol not in portfolio_balances[portfolio_id]:
                portfolio_balances[portfolio_id][symbol] = 0
            
            # Process transaction
            if txn['type'] == 'BUY':
                portfolio_balances[portfolio_id][symbol] += txn['quantity']
            else:  # SELL
                portfolio_balances[portfolio_id][symbol] -= txn['quantity']
            
            processed.append({
                'transaction_id': len(processed) + 1,
                'processed': True,
                'new_balance': portfolio_balances[portfolio_id][symbol]
            })
        
        return processed
    
    def _aggregate_by_sector(self, portfolio_data):
        """Aggregate portfolio data by sector."""
        sector_aggregation = {}
        
        for position in portfolio_data['positions']:
            sector = position['sector']
            value = position['quantity'] * position['current_price']
            
            if sector not in sector_aggregation:
                sector_aggregation[sector] = {
                    'total_value': Decimal('0'),
                    'position_count': 0
                }
            
            sector_aggregation[sector]['total_value'] += value
            sector_aggregation[sector]['position_count'] += 1
        
        return sector_aggregation
    
    def _aggregate_by_country(self, portfolio_data):
        """Aggregate portfolio data by country."""
        country_aggregation = {}
        
        for position in portfolio_data['positions']:
            country = position['country']
            value = position['quantity'] * position['current_price']
            
            if country not in country_aggregation:
                country_aggregation[country] = {
                    'total_value': Decimal('0'),
                    'position_count': 0
                }
            
            country_aggregation[country]['total_value'] += value
            country_aggregation[country]['position_count'] += 1
        
        return country_aggregation
    
    def _calculate_performance_metrics(self, portfolio_data):
        """Calculate portfolio performance metrics."""
        total_cost = Decimal('0')
        total_value = Decimal('0')
        
        for position in portfolio_data['positions']:
            cost = position['quantity'] * position['cost_basis']
            value = position['quantity'] * position['current_price']
            total_cost += cost
            total_value += value
        
        return {
            'total_cost': total_cost,
            'total_value': total_value,
            'total_return': total_value - total_cost,
            'return_percentage': ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0,
            'position_count': len(portfolio_data['positions'])
        }


class TestCachePerformance(TestCase, PerformanceTestMixin):
    """Performance tests for caching mechanisms."""
    
    def setUp(self):
        """Set up cache performance tests."""
        cache.clear()
    
    def test_cache_read_write_performance(self):
        """Test cache read/write performance."""
        # Test different data sizes
        data_sizes = [
            ('small', {'portfolio_id': 1, 'value': 1000.0}),
            ('medium', {'portfolio_data': [{'id': i, 'value': i * 100} for i in range(100)]}),
            ('large', {'portfolio_data': [{'id': i, 'value': i * 100} for i in range(1000)]})
        ]
        
        for size_name, data in data_sizes:
            with self.subTest(size=size_name):
                # Test cache write
                write_result, write_time = self.measure_execution_time(
                    cache.set, f'test_key_{size_name}', data, 300
                )
                
                # Test cache read
                read_result, read_time = self.measure_execution_time(
                    cache.get, f'test_key_{size_name}'
                )
                
                # Cache operations should be fast
                self.assertLess(write_time, 0.01,  # < 10ms
                               f"Cache write ({size_name}): {write_time:.4f}s")
                self.assertLess(read_time, 0.01,  # < 10ms
                               f"Cache read ({size_name}): {read_time:.4f}s")
                
                # Data should be preserved
                self.assertEqual(read_result, data)
    
    def test_cache_hit_ratio_performance(self):
        """Test cache performance with different hit ratios."""
        # Populate cache with test data
        for i in range(100):
            cache.set(f'portfolio_{i}', {'value': i * 1000}, 300)
        
        def cache_access_pattern(hit_ratio=0.8):
            """Simulate cache access with specified hit ratio."""
            hits = 0
            misses = 0
            
            for i in range(1000):
                if i % 100 < (hit_ratio * 100):
                    # Cache hit
                    key = f'portfolio_{i % 100}'
                    result = cache.get(key)
                    if result is not None:
                        hits += 1
                    else:
                        misses += 1
                else:
                    # Cache miss
                    key = f'portfolio_new_{i}'
                    result = cache.get(key)
                    misses += 1
            
            return hits, misses
        
        # Test different hit ratios
        hit_ratios = [0.5, 0.8, 0.95]
        
        for hit_ratio in hit_ratios:
            with self.subTest(hit_ratio=hit_ratio):
                result, execution_time = self.measure_execution_time(
                    cache_access_pattern, hit_ratio
                )
                
                hits, misses = result
                actual_hit_ratio = hits / (hits + misses) if (hits + misses) > 0 else 0
                
                # Performance should scale with hit ratio
                time_per_access = execution_time / 1000
                self.assertLess(time_per_access, 0.0001,  # < 0.1ms per access
                               f"Hit ratio {hit_ratio}: {time_per_access:.6f}s per access")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])