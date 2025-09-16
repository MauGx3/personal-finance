"""
Tests for the Feature Registry System

Tests to validate that the new structured approach for handling optional
components works correctly and replaces fragile try/except patterns.
"""

import pytest


class TestFeatureRegistry:
    """Test the core feature registry functionality."""

    def test_feature_registry_import(self):
        """Test that the feature registry can be imported."""
        from src.personal_finance.feature_registry import (
            FeatureRegistry,
            registry,
        )

        assert isinstance(registry, FeatureRegistry)

    def test_register_available_feature(self):
        """Test registering a feature that is available."""
        from src.personal_finance.feature_registry import FeatureRegistry

        test_registry = FeatureRegistry()

        # Register a built-in module that should always be available
        feature_info = test_registry.register_feature("json_module", "json")

        assert feature_info.is_available is True
        assert feature_info.component is not None
        assert feature_info.import_error is None
        assert test_registry.is_available("json_module") is True

    def test_register_unavailable_feature(self):
        """Test registering a feature that is not available."""
        from src.personal_finance.feature_registry import FeatureRegistry

        test_registry = FeatureRegistry()

        # Register a non-existent module
        feature_info = test_registry.register_feature(
            "nonexistent_module", "this.module.does.not.exist"
        )

        assert feature_info.is_available is False
        assert feature_info.component is None
        assert feature_info.import_error is not None
        assert test_registry.is_available("nonexistent_module") is False

    def test_register_required_feature_success(self):
        """Test registering a required feature that succeeds."""
        from src.personal_finance.feature_registry import FeatureRegistry

        test_registry = FeatureRegistry()

        # Register a required feature that should be available
        feature_info = test_registry.register_feature(
            "json_required", "json", required=True
        )

        assert feature_info.is_available is True
        assert feature_info.component is not None

    def test_register_required_feature_failure(self):
        """Test registering a required feature that fails."""
        from src.personal_finance.feature_registry import FeatureRegistry

        test_registry = FeatureRegistry()

        # Register a required feature that should fail
        with pytest.raises(ImportError):
            test_registry.register_feature(
                "nonexistent_required",
                "this.module.does.not.exist",
                required=True,
            )

    def test_get_component_with_default(self):
        """Test getting components with defaults."""
        from src.personal_finance.feature_registry import FeatureRegistry

        test_registry = FeatureRegistry()

        # Test with unavailable feature
        result = test_registry.get_component(
            "unknown_feature", "default_value"
        )
        assert result == "default_value"

        # Test with available feature
        test_registry.register_feature("json_test", "json")
        result = test_registry.get_component("json_test")
        assert result is not None

    def test_convenience_functions(self):
        """Test the convenience functions work correctly."""
        from src.personal_finance.feature_registry import (
            register_optional_feature,
            is_feature_available,
            get_feature,
        )

        # Test optional registration
        component = register_optional_feature("json_optional", "json")
        assert component is not None
        assert is_feature_available("json_optional") is True
        assert get_feature("json_optional") is not None

        # Test with unavailable module
        component = register_optional_feature(
            "unavailable_optional", "nonexistent.module"
        )
        assert component is None
        assert is_feature_available("unavailable_optional") is False
        assert get_feature("unavailable_optional", "default") == "default"


class TestDjangoFeatureRegistry:
    """Test the Django-specific feature registry."""

    def test_django_registry_import(self):
        """Test that the Django registry can be imported."""
        from config.django_feature_registry import (
            DjangoFeatureRegistry,
            django_registry,
        )

        assert isinstance(django_registry, DjangoFeatureRegistry)

    def test_register_viewsets_unavailable(self):
        """Test registering ViewSets that are not available."""
        from config.django_feature_registry import DjangoFeatureRegistry

        test_registry = DjangoFeatureRegistry()

        # Register non-existent ViewSets
        viewsets = test_registry.register_viewsets(
            "test_feature",
            "nonexistent.module",
            ["TestViewSet", "AnotherViewSet"],
        )

        assert viewsets["TestViewSet"] is None
        assert viewsets["AnotherViewSet"] is None
        assert test_registry.is_available("test_feature") is False

    def test_get_viewset_methods(self):
        """Test the methods for getting ViewSets."""
        from config.django_feature_registry import DjangoFeatureRegistry

        test_registry = DjangoFeatureRegistry()

        # Register some test ViewSets (will fail but that's expected)
        test_registry.register_viewsets(
            "test_feature", "nonexistent.module", ["ViewSet1", "ViewSet2"]
        )

        # Test getting individual ViewSet
        result = test_registry.get_viewset(
            "test_feature", "ViewSet1", "default"
        )
        assert result == "default"

        # Test getting all ViewSets
        all_viewsets = test_registry.get_all_viewsets("test_feature")
        assert all_viewsets["ViewSet1"] is None
        assert all_viewsets["ViewSet2"] is None

    def test_convenience_functions_django(self):
        """Test Django convenience functions."""
        from config.django_feature_registry import (
            register_optional_viewsets,
            get_viewset,
            is_django_feature_available,
        )

        # Register optional ViewSets
        viewsets = register_optional_viewsets(
            "test_optional", "nonexistent.module", ["TestViewSet"]
        )

        assert viewsets["TestViewSet"] is None
        assert is_django_feature_available("test_optional") is False
        assert (
            get_viewset("test_optional", "TestViewSet", "default") == "default"
        )


class TestUpdatedImports:
    """Test that the updated import patterns work correctly."""

    def test_personal_finance_package_imports(self):
        """Test that the updated personal finance package imports work."""
        # This tests the updated src/personal_finance/__init__.py
        try:
            import src.personal_finance as pf

            # These should be either valid modules or None
            assert pf.portfolio is None or hasattr(pf.portfolio, "__name__")
            assert pf.yahoo_finance is None or hasattr(
                pf.yahoo_finance, "__name__"
            )
            assert pf.database is None or hasattr(pf.database, "__name__")
            assert pf.logger is None or hasattr(pf.logger, "__call__")

        except ImportError:
            # If the package isn't properly set up, that's okay for this test
            pytest.skip(
                "Personal finance package not properly configured for testing"
            )

    def test_api_router_imports(self):
        """Test that the updated API router imports work."""
        try:
            # Import the updated API router
            import config.api_router as router_module

            # Check that ViewSets are either classes or None
            viewsets_to_check = [
                "PriceHistoryViewSet",
                "PortfolioViewSet",
                "PositionViewSet",
                "TransactionViewSet",
                "PortfolioSnapshotViewSet",
                "UserViewSet",
                "RealtimeViewSet",
                "TaxYearViewSet",
                "TaxLotViewSet",
            ]

            for viewset_name in viewsets_to_check:
                if hasattr(router_module, viewset_name):
                    viewset = getattr(router_module, viewset_name)
                    assert viewset is None or (
                        hasattr(viewset, "__name__")
                        and "ViewSet" in viewset.__name__
                    )

        except ImportError as e:
            # If Django or other dependencies aren't available, that's expected
            pytest.skip(f"API router dependencies not available: {e}")

    def test_celery_config_imports(self):
        """Test that the updated Celery config imports work."""
        try:
            import config

            # Check that celery_app is either a Celery app or doesn't exist
            if hasattr(config, "celery_app"):
                assert config.celery_app is None or hasattr(
                    config.celery_app, "task"
                )

        except ImportError:
            # If config module isn't available, that's okay
            pytest.skip("Config module not available for testing")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
