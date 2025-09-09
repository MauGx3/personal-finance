"""
Test Suite Runner and Configuration Manager

This module provides utilities to run the comprehensive test suite with
different configurations and generate detailed reports.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path


class TestSuiteRunner:
    """Comprehensive test suite runner with reporting capabilities."""
    
    def __init__(self, project_root=None):
        """Initialize test runner."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.test_dir = self.project_root / 'tests'
        self.reports_dir = self.project_root / 'test_reports'
        self.reports_dir.mkdir(exist_ok=True)
        
    def run_comprehensive_suite(self):
        """Run the complete comprehensive test suite."""
        print("🚀 Running Comprehensive Personal Finance Test Suite")
        print("=" * 60)
        
        # Test categories and their configurations
        test_categories = [
            {
                'name': 'Unit Tests',
                'marker': 'unit',
                'file': 'test_suite_comprehensive.py',
                'description': 'Core function unit tests'
            },
            {
                'name': 'Integration Tests', 
                'marker': 'integration',
                'file': 'test_integration_mocking.py',
                'description': 'Component integration tests'
            },
            {
                'name': 'Performance Tests',
                'marker': 'performance', 
                'file': 'test_performance_benchmarks.py',
                'description': 'Performance and benchmark tests'
            },
            {
                'name': 'Security Tests',
                'marker': 'security',
                'file': 'test_security_edge_cases.py', 
                'description': 'Security vulnerability tests'
            },
            {
                'name': 'Regression Tests',
                'marker': 'regression',
                'file': 'test_regression_suite.py',
                'description': 'Regression and compatibility tests'
            }
        ]
        
        results = {}
        start_time = time.time()
        
        for category in test_categories:
            print(f"\n📋 Running {category['name']}")
            print(f"   {category['description']}")
            print("-" * 40)
            
            result = self._run_test_category(category)
            results[category['name']] = result
            
            # Print summary
            if result['success']:
                print(f"✅ {category['name']}: {result['tests_passed']}/{result['tests_total']} passed")
            else:
                print(f"❌ {category['name']}: {result['tests_failed']} failed")
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        self._generate_comprehensive_report(results, total_time)
        
        # Print final summary
        self._print_final_summary(results, total_time)
        
        return results
    
    def run_quick_suite(self):
        """Run quick subset of tests for rapid feedback."""
        print("⚡ Running Quick Test Suite")
        print("=" * 30)
        
        # Quick test configuration
        quick_tests = [
            'tests/test_suite_comprehensive.py::TestCoreFinancialCalculations',
            'tests/test_integration_mocking.py::TestComponentIntegration::test_portfolio_transaction_position_integration',
            'tests/test_security_edge_cases.py::TestSecurityVulnerabilities::test_authentication_required'
        ]
        
        for test in quick_tests:
            print(f"Running {test.split('::')[-1]}...")
            result = subprocess.run(
                ['pytest', test, '-v'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print("✅ Passed")
            else:
                print("❌ Failed")
                print(result.stdout)
                print(result.stderr)
    
    def run_performance_benchmark(self):
        """Run performance benchmark suite."""
        print("📊 Running Performance Benchmark Suite")
        print("=" * 40)
        
        benchmark_cmd = [
            'pytest',
            'tests/test_performance_benchmarks.py',
            '--benchmark-only',
            '--benchmark-json=test_reports/benchmark_results.json',
            '-v'
        ]
        
        result = subprocess.run(
            benchmark_cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Performance benchmarks completed")
            self._analyze_benchmark_results()
        else:
            print("❌ Performance benchmarks failed")
            print(result.stdout)
            print(result.stderr)
    
    def run_security_audit(self):
        """Run comprehensive security audit."""
        print("🔒 Running Security Audit")
        print("=" * 25)
        
        security_tests = [
            'tests/test_security_edge_cases.py::TestSecurityVulnerabilities',
            'tests/test_security_edge_cases.py::TestFinancialEdgeCases',
        ]
        
        for test in security_tests:
            print(f"\n🔍 {test.split('::')[-1]}")
            result = subprocess.run(
                ['pytest', test, '-v', '--tb=short'],
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print("✅ Security tests passed")
            else:
                print("❌ Security vulnerabilities detected")
    
    def generate_coverage_report(self):
        """Generate comprehensive coverage report."""
        print("📈 Generating Coverage Report")
        print("=" * 30)
        
        coverage_cmd = [
            'pytest',
            'tests/',
            '--cov=personal_finance',
            '--cov-report=html:test_reports/coverage_html',
            '--cov-report=json:test_reports/coverage.json',
            '--cov-report=term-missing'
        ]
        
        result = subprocess.run(coverage_cmd, cwd=self.project_root)
        
        if result.returncode == 0:
            print("✅ Coverage report generated")
            print(f"📁 HTML report: {self.reports_dir}/coverage_html/index.html")
        else:
            print("❌ Coverage report generation failed")
    
    def _run_test_category(self, category):
        """Run a specific test category."""
        if category.get('file'):
            test_path = f"tests/{category['file']}"
        else:
            test_path = f"tests/ -m {category['marker']}"
        
        cmd = [
            'pytest',
            test_path,
            '--json-report',
            f'--json-report-file=test_reports/{category["name"].lower().replace(" ", "_")}_report.json',
            '-v'
        ]
        
        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        # Parse results
        try:
            report_file = self.reports_dir / f'{category["name"].lower().replace(" ", "_")}_report.json'
            if report_file.exists():
                with open(report_file) as f:
                    report_data = json.load(f)
                
                return {
                    'success': result.returncode == 0,
                    'tests_total': report_data.get('summary', {}).get('total', 0),
                    'tests_passed': report_data.get('summary', {}).get('passed', 0),
                    'tests_failed': report_data.get('summary', {}).get('failed', 0),
                    'tests_skipped': report_data.get('summary', {}).get('skipped', 0),
                    'duration': report_data.get('duration', 0),
                    'output': result.stdout
                }
        except:
            pass
        
        # Fallback result parsing
        return {
            'success': result.returncode == 0,
            'tests_total': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0,
            'duration': 0,
            'output': result.stdout + result.stderr
        }
    
    def _generate_comprehensive_report(self, results, total_time):
        """Generate comprehensive test report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_duration': total_time,
            'categories': results,
            'summary': {
                'total_tests': sum(r.get('tests_total', 0) for r in results.values()),
                'total_passed': sum(r.get('tests_passed', 0) for r in results.values()),
                'total_failed': sum(r.get('tests_failed', 0) for r in results.values()),
                'total_skipped': sum(r.get('tests_skipped', 0) for r in results.values()),
                'success_rate': 0
            }
        }
        
        # Calculate success rate
        total_tests = report['summary']['total_tests']
        if total_tests > 0:
            report['summary']['success_rate'] = (
                report['summary']['total_passed'] / total_tests * 100
            )
        
        # Save report
        report_file = self.reports_dir / 'comprehensive_test_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        self._generate_html_report(report)
    
    def _generate_html_report(self, report):
        """Generate HTML test report."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Personal Finance Platform Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .summary {{ background: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .category {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .success {{ background: #d5f4e6; }}
                .failure {{ background: #f8d7da; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: white; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏦 Personal Finance Platform Test Report</h1>
                <p>Generated: {report['timestamp']}</p>
                <p>Total Duration: {report['total_duration']:.2f} seconds</p>
            </div>
            
            <div class="summary">
                <h2>📊 Test Summary</h2>
                <div class="metric">
                    <strong>Total Tests:</strong> {report['summary']['total_tests']}
                </div>
                <div class="metric">
                    <strong>Passed:</strong> {report['summary']['total_passed']}
                </div>
                <div class="metric">
                    <strong>Failed:</strong> {report['summary']['total_failed']}
                </div>
                <div class="metric">
                    <strong>Success Rate:</strong> {report['summary']['success_rate']:.1f}%
                </div>
            </div>
            
            <h2>📋 Test Categories</h2>
        """
        
        for category, result in report['categories'].items():
            status_class = 'success' if result['success'] else 'failure'
            status_icon = '✅' if result['success'] else '❌'
            
            html_content += f"""
            <div class="category {status_class}">
                <h3>{status_icon} {category}</h3>
                <p><strong>Tests:</strong> {result['tests_passed']}/{result['tests_total']} passed</p>
                <p><strong>Duration:</strong> {result.get('duration', 0):.2f} seconds</p>
            </div>
            """
        
        html_content += """
            </body>
        </html>
        """
        
        report_file = self.reports_dir / 'test_report.html'
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        print(f"📄 HTML report generated: {report_file}")
    
    def _print_final_summary(self, results, total_time):
        """Print final test summary."""
        print("\n" + "=" * 60)
        print("🏁 FINAL TEST SUMMARY")
        print("=" * 60)
        
        total_tests = sum(r.get('tests_total', 0) for r in results.values())
        total_passed = sum(r.get('tests_passed', 0) for r in results.values())
        total_failed = sum(r.get('tests_failed', 0) for r in results.values())
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        
        if success_rate >= 95:
            print("\n🎉 EXCELLENT! Test suite passed with high success rate.")
        elif success_rate >= 80:
            print("\n👍 GOOD! Most tests passed, review failures.")
        else:
            print("\n⚠️  WARNING! Many tests failed, immediate attention required.")
        
        print(f"\n📁 Reports saved to: {self.reports_dir}")
    
    def _analyze_benchmark_results(self):
        """Analyze performance benchmark results."""
        benchmark_file = self.reports_dir / 'benchmark_results.json'
        
        if not benchmark_file.exists():
            print("❌ Benchmark results file not found")
            return
        
        try:
            with open(benchmark_file) as f:
                data = json.load(f)
            
            print("\n📊 Performance Analysis:")
            
            for benchmark in data.get('benchmarks', []):
                name = benchmark.get('name', 'Unknown')
                stats = benchmark.get('stats', {})
                mean_time = stats.get('mean', 0)
                
                if mean_time < 0.001:
                    status = "🟢 Excellent"
                elif mean_time < 0.01:
                    status = "🟡 Good"
                elif mean_time < 0.1:
                    status = "🟠 Acceptable"
                else:
                    status = "🔴 Needs Optimization"
                
                print(f"  {status} {name}: {mean_time:.4f}s")
        
        except Exception as e:
            print(f"❌ Error analyzing benchmark results: {e}")


def main():
    """Main test runner entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Personal Finance Platform Test Suite Runner')
    parser.add_argument('--suite', choices=['comprehensive', 'quick', 'performance', 'security', 'coverage'], 
                       default='comprehensive', help='Test suite to run')
    parser.add_argument('--project-root', help='Project root directory')
    
    args = parser.parse_args()
    
    runner = TestSuiteRunner(args.project_root)
    
    if args.suite == 'comprehensive':
        runner.run_comprehensive_suite()
    elif args.suite == 'quick':
        runner.run_quick_suite()
    elif args.suite == 'performance':
        runner.run_performance_benchmark()
    elif args.suite == 'security':
        runner.run_security_audit()
    elif args.suite == 'coverage':
        runner.generate_coverage_report()


if __name__ == '__main__':
    main()