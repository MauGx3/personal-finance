"""
Django Feature Registry for API Components

This module provides a Django-specific feature registry for managing
optional API components like ViewSets, replacing fragile try/except
import patterns with structured feature management.
"""

import logging
from typing import Any, Dict, Optional, List, Type
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DjangoFeatureInfo:
    """Information about a registered Django feature."""

    name: str
    module_path: str
    component_names: List[str]
    is_available: bool
    import_error: Optional[str] = None
    components: Dict[str, Any] = None


class DjangoFeatureRegistry:
    """
    Registry for optional Django components like ViewSets.

    Provides structured management of optional Django API components,
    replacing fragile try/except patterns with explicit feature management.
    """

    def __init__(self):
        self._features: Dict[str, DjangoFeatureInfo] = {}
        self._logger = logging.getLogger(__name__)

    def register_viewsets(
        self,
        feature_name: str,
        module_path: str,
        viewset_names: List[str],
        required: bool = False,
    ) -> Dict[str, Any]:
        """
        Register Django ViewSets from a module.

        Args:
            feature_name: Name of the feature for lookup
            module_path: Python module path containing ViewSets
            viewset_names: List of ViewSet class names to import
            required: Whether these ViewSets are required

        Returns:
            Dictionary mapping ViewSet names to classes (or None if unavailable)
        """
        feature_info = DjangoFeatureInfo(
            name=feature_name,
            module_path=module_path,
            component_names=viewset_names,
            is_available=False,
            components={},
        )

        try:
            # Import the module
            import importlib

            module = importlib.import_module(module_path)

            # Get each ViewSet
            for viewset_name in viewset_names:
                viewset_class = getattr(module, viewset_name)
                feature_info.components[viewset_name] = viewset_class

            feature_info.is_available = True
            self._logger.debug(
                f"Django feature '{feature_name}' registered successfully"
            )

        except (ImportError, AttributeError, Exception) as e:
            feature_info.import_error = str(e)
            self._logger.debug(
                f"Django feature '{feature_name}' unavailable: {e}"
            )

            # Set all components to None
            for viewset_name in viewset_names:
                feature_info.components[viewset_name] = None

            if required:
                self._logger.error(
                    f"Required Django feature '{feature_name}' is unavailable: {e}"
                )
                raise ImportError(
                    f"Required Django feature '{feature_name}' cannot be imported: {e}"
                )

        self._features[feature_name] = feature_info
        return feature_info.components

    def is_available(self, feature_name: str) -> bool:
        """Check if a Django feature is available."""
        return self._features.get(
            feature_name, DjangoFeatureInfo("", "", [], False)
        ).is_available

    def get_viewset(
        self, feature_name: str, viewset_name: str, default: Any = None
    ) -> Any:
        """Get a specific ViewSet from a feature."""
        feature = self._features.get(feature_name)
        if feature and feature.is_available and feature.components:
            return feature.components.get(viewset_name, default)
        return default

    def get_all_viewsets(self, feature_name: str) -> Dict[str, Any]:
        """Get all ViewSets from a feature."""
        feature = self._features.get(feature_name)
        if feature and feature.components:
            return feature.components.copy()
        return {}

    def list_features(self) -> Dict[str, DjangoFeatureInfo]:
        """Get all registered Django features."""
        return self._features.copy()


# Global Django registry instance
django_registry = DjangoFeatureRegistry()


def register_optional_viewsets(
    feature_name: str, module_path: str, viewset_names: List[str]
) -> Dict[str, Any]:
    """
    Convenience function to register optional ViewSets.

    Returns dictionary with ViewSet classes or None for each name.
    """
    return django_registry.register_viewsets(
        feature_name, module_path, viewset_names, required=False
    )


def register_required_viewsets(
    feature_name: str, module_path: str, viewset_names: List[str]
) -> Dict[str, Any]:
    """
    Convenience function to register required ViewSets.

    Raises ImportError if any ViewSet is not available.
    """
    return django_registry.register_viewsets(
        feature_name, module_path, viewset_names, required=True
    )


def get_viewset(
    feature_name: str, viewset_name: str, default: Any = None
) -> Any:
    """Get a specific ViewSet, or default if unavailable."""
    return django_registry.get_viewset(feature_name, viewset_name, default)


def is_django_feature_available(feature_name: str) -> bool:
    """Check if a Django feature is available."""
    return django_registry.is_available(feature_name)
