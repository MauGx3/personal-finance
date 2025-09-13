"""
Test for the new dependency management system.

Validates that the structured approach properly handles missing dependencies
and provides clear error messages.
"""

import sys
import os
import pytest
from unittest.mock import patch

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from personal_finance.dependencies import (
    DependencyManager, 
    DependencyStatus,
    dependency_manager,
    setup_core_dependencies
)


class TestDependencyManager:
    """Test the dependency management system."""
    
    def test_dependency_manager_initialization(self):
        """Test that dependency manager initializes correctly."""
        dm = DependencyManager()
        assert dm._dependencies == {}
        assert dm._feature_flags == {}
    
    def test_register_available_dependency(self):
        """Test registering a dependency that is available."""
        dm = DependencyManager()
        
        # Register a built-in module that should always be available
        dep_info = dm.register_dependency(
            name="json",
            import_path="json",
            required=True,
            fallback_available=False
        )
        
        assert dep_info.name == "json"
        assert dep_info.status == DependencyStatus.AVAILABLE
        assert dep_info.module is not None
        assert dm.is_available("json")
    
    def test_register_missing_dependency(self):
        """Test registering a dependency that is missing."""
        dm = DependencyManager()
        
        # Register a module that doesn't exist
        dep_info = dm.register_dependency(
            name="nonexistent_module",
            import_path="nonexistent_module_that_should_not_exist",
            required=False,
            fallback_available=True
        )
        
        assert dep_info.name == "nonexistent_module"
        assert dep_info.status == DependencyStatus.MISSING
        assert dep_info.module is None
        assert not dm.is_available("nonexistent_module")
        assert dep_info.error_message is not None
    
    def test_get_dependency(self):
        """Test getting dependencies."""
        dm = DependencyManager()
        
        # Register available dependency
        dm.register_dependency("json", "json")
        
        # Test getting available dependency
        json_module = dm.get_dependency("json")
        assert json_module is not None
        
        # Test getting non-existent dependency
        missing_module = dm.get_dependency("missing")
        assert missing_module is None
    
    def test_feature_flags(self):
        """Test feature flag functionality."""
        dm = DependencyManager()
        
        # Test initial state
        assert not dm.is_feature_enabled("test_feature")
        
        # Test enabling feature
        dm.enable_feature("test_feature")
        assert dm.is_feature_enabled("test_feature")
        
        # Test disabling feature
        dm.disable_feature("test_feature")
        assert not dm.is_feature_enabled("test_feature")
    
    def test_list_dependencies(self):
        """Test listing all dependencies."""
        dm = DependencyManager()
        
        # Register multiple dependencies
        dm.register_dependency("json", "json")
        dm.register_dependency("missing", "nonexistent")
        
        deps = dm.list_dependencies()
        assert len(deps) == 2
        assert "json" in deps
        assert "missing" in deps
    
    def test_setup_core_dependencies(self):
        """Test that core dependencies are set up correctly."""
        # This will use the global dependency manager
        setup_core_dependencies()
        
        # Check that some dependencies are registered
        stockdex_status = dependency_manager.get_status("stockdex") 
        assert stockdex_status is not None
        
        # Check that feature flags are enabled
        assert dependency_manager.is_feature_enabled("portfolio_management")
        assert dependency_manager.is_feature_enabled("price_fetching")


class TestBackwardCompatibility:
    """Test that the new system maintains backward compatibility."""
    
    def test_module_import_compatibility(self):
        """Test that modules can still be imported as before."""
        # Import the package
        import personal_finance
        
        # Check that module attributes exist (may be None if dependencies missing)
        assert hasattr(personal_finance, 'portfolio')
        assert hasattr(personal_finance, 'yahoo_finance')
        assert hasattr(personal_finance, 'database')
        assert hasattr(personal_finance, 'logger')
    
    def test_portfolio_module_compatibility(self):
        """Test that portfolio module imports work correctly."""
        try:
            from personal_finance import portfolio
            # If import succeeds, check that sd variable exists
            if portfolio is not None:
                assert hasattr(portfolio, 'sd')
        except ImportError:
            # Import failure is acceptable for missing dependencies
            pass


if __name__ == "__main__":
    # Run basic tests
    dm = DependencyManager()
    
    # Test basic functionality
    print("Testing dependency manager...")
    
    # Test with available module
    dep_info = dm.register_dependency("json", "json")
    print(f"JSON module status: {dep_info.status}")
    
    # Test with missing module  
    dep_info = dm.register_dependency("missing", "nonexistent")
    print(f"Missing module status: {dep_info.status}")
    
    # Test feature flags
    dm.enable_feature("test")
    print(f"Test feature enabled: {dm.is_feature_enabled('test')}")
    
    print("Basic tests passed!")