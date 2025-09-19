"""
Test that the copilot setup steps install all required dependencies.

This test validates that the expanded copilot-setup-steps.yml workflow
provides comprehensive coverage of all packages needed for the entire project.
"""
import importlib
import subprocess
import sys
from pathlib import Path

import pytest


class TestCopilotSetupCompleteness:
    """Test copilot setup dependency completeness."""

    def test_core_django_packages_available(self):
        """Test that core Django and related packages are available."""
        required_django_packages = [
            "django",
            "environ",  # django-environ imports as 'environ'
            "allauth",  # django-allauth imports as 'allauth'
            "crispy_forms",  # django-crispy-forms imports as 'crispy_forms'
            "compressor",  # django-compressor imports as 'compressor'
            "django_redis",
            "rest_framework",  # djangorestframework imports as 'rest_framework'
            "corsheaders",  # django-cors-headers imports as 'corsheaders'
        ]
        
        for package in required_django_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                pytest.fail(f"Required Django package '{package}' not available")

    def test_finance_libraries_available(self):
        """Test that finance-specific libraries are available."""
        required_finance_packages = [
            "yfinance",
            "pandas", 
            "numpy",
            "matplotlib",
            "plotly",
            "quantstats",
            "stockdex",
            "bs4",  # beautifulsoup4 imports as 'bs4'
            "requests",
        ]
        
        for package in required_finance_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                pytest.fail(f"Required finance package '{package}' not available")

    def test_development_tools_available(self):
        """Test that development tools are available."""
        required_dev_tools = [
            "pytest",
            "ruff", 
            "mypy",
            "coverage",
            "sphinx",
        ]
        
        for tool in required_dev_tools:
            try:
                # Test if the tool is available as a module
                result = subprocess.run(
                    [sys.executable, "-c", f"import {tool}"],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    # Some tools might be available as CLI commands but not modules
                    result = subprocess.run(
                        [tool, "--version"], 
                        capture_output=True, 
                        text=True
                    )
                    if result.returncode != 0:
                        pytest.fail(f"Required development tool '{tool}' not available")
            except (ImportError, FileNotFoundError):
                pytest.fail(f"Required development tool '{tool}' not available")

    def test_web_server_packages_available(self):
        """Test that web server and async packages are available."""
        required_web_packages = [
            "uvicorn",
            "celery",
            "redis",
        ]
        
        for package in required_web_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                pytest.fail(f"Required web package '{package}' not available")

    def test_database_packages_available(self):
        """Test that database-related packages are available."""
        required_db_packages = [
            "sqlalchemy",
            "alembic",
            "psycopg2",  # psycopg2-binary provides psycopg2
        ]
        
        for package in required_db_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                pytest.fail(f"Required database package '{package}' not available")

    def test_minimum_package_count(self):
        """Test that we have a reasonable number of packages installed."""
        try:
            result = subprocess.run(
                ["uv", "pip", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            package_count = len(result.stdout.strip().split('\n')) - 2  # Subtract header lines
            
            # The expanded setup should install significantly more packages than the minimal setup
            assert package_count >= 200, (
                f"Expected at least 200 packages to be installed, found {package_count}. "
                "This suggests the copilot setup might not be installing all required dependencies."
            )
        except subprocess.CalledProcessError:
            pytest.fail("Could not determine installed package count")

    def test_project_can_be_imported(self):
        """Test that the personal_finance project can be imported."""
        try:
            # Add src to path for testing
            src_path = Path(__file__).parent.parent / "src"
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
            
            # Test importing the main project
            import personal_finance
            assert personal_finance is not None
            
        except ImportError as e:
            pytest.fail(f"Could not import personal_finance project: {e}")

    def test_constraints_are_respected(self):
        """Test that installed packages respect the constraints file."""
        constraints_file = Path(__file__).parent.parent / "constraints.txt"
        if not constraints_file.exists():
            pytest.skip("No constraints.txt file found")
            
        # Read constraints
        with open(constraints_file) as f:
            constraints = {}
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '==' in line:
                    package, version = line.split('==', 1)
                    constraints[package.lower()] = version
        
        if not constraints:
            pytest.skip("No version constraints found in constraints.txt")
            
        # Check some key constrained packages
        try:
            result = subprocess.run(
                ["uv", "pip", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            
            installed = {}
            for line in result.stdout.strip().split('\n')[2:]:  # Skip headers
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        package = parts[0].lower()
                        version = parts[1]
                        installed[package] = version
            
            # Check that key constrained packages are installed with compatible versions
            key_packages = ['pandas', 'numpy', 'requests']  # Skip django as it may get security updates
            for package in key_packages:
                if package in constraints and package in installed:
                    expected_version = constraints[package]
                    actual_version = installed[package]
                    # For constraints, we mainly check that the major.minor versions match
                    expected_major_minor = '.'.join(expected_version.split('.')[:2])
                    actual_major_minor = '.'.join(actual_version.split('.')[:2])
                    assert actual_major_minor == expected_major_minor, (
                        f"Package {package} major.minor version mismatch: "
                        f"expected {expected_major_minor}.x, got {actual_version}"
                    )
                    
        except subprocess.CalledProcessError:
            pytest.fail("Could not check installed package versions")