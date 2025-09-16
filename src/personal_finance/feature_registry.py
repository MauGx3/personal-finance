"""
Feature Registry for Optional Components

This module provides a centralized registry system for managing optional
components and their availability, replacing fragile try/except import patterns
with a more structured approach.
"""

import logging
from typing import Any, Dict, Optional, Callable, Type
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FeatureInfo:
    """Information about a registered feature."""
    name: str
    module_path: str
    is_available: bool
    import_error: Optional[str] = None
    component: Optional[Any] = None


class FeatureRegistry:
    """
    Centralized registry for optional features and components.
    
    This registry provides a structured way to handle optional imports
    and component availability checking, replacing fragile try/except
    patterns with explicit feature management.
    """
    
    def __init__(self):
        self._features: Dict[str, FeatureInfo] = {}
        self._logger = logging.getLogger(__name__)
    
    def register_feature(
        self, 
        name: str, 
        module_path: str, 
        component_name: Optional[str] = None,
        required: bool = False
    ) -> FeatureInfo:
        """
        Register a feature and attempt to import it.
        
        Args:
            name: Feature name for lookup
            module_path: Python module path to import
            component_name: Specific component name within module (optional)
            required: Whether this feature is required (raises if unavailable)
            
        Returns:
            FeatureInfo with availability status
        """
        feature_info = FeatureInfo(
            name=name,
            module_path=module_path,
            is_available=False
        )
        
        try:
            # Import the module
            import importlib
            module = importlib.import_module(module_path)
            
            # Get specific component if specified
            if component_name:
                component = getattr(module, component_name)
                feature_info.component = component
            else:
                feature_info.component = module
            
            feature_info.is_available = True
            self._logger.debug(f"Feature '{name}' registered successfully")
            
        except (ImportError, AttributeError, Exception) as e:
            feature_info.import_error = str(e)
            self._logger.debug(f"Feature '{name}' unavailable: {e}")
            
            if required:
                self._logger.error(f"Required feature '{name}' is unavailable: {e}")
                raise ImportError(f"Required feature '{name}' cannot be imported: {e}")
        
        self._features[name] = feature_info
        return feature_info
    
    def is_available(self, name: str) -> bool:
        """Check if a feature is available."""
        return self._features.get(name, FeatureInfo("", "", False)).is_available
    
    def get_component(self, name: str, default: Any = None) -> Any:
        """Get the component for a feature, or return default if unavailable."""
        feature = self._features.get(name)
        if feature and feature.is_available:
            return feature.component
        return default
    
    def get_feature_info(self, name: str) -> Optional[FeatureInfo]:
        """Get detailed information about a feature."""
        return self._features.get(name)
    
    def list_features(self) -> Dict[str, FeatureInfo]:
        """Get all registered features."""
        return self._features.copy()
    
    def get_available_features(self) -> Dict[str, FeatureInfo]:
        """Get only available features."""
        return {
            name: info for name, info in self._features.items() 
            if info.is_available
        }
    
    def get_unavailable_features(self) -> Dict[str, FeatureInfo]:
        """Get only unavailable features."""
        return {
            name: info for name, info in self._features.items() 
            if not info.is_available
        }


# Global registry instance
registry = FeatureRegistry()


def register_optional_feature(
    name: str, 
    module_path: str, 
    component_name: Optional[str] = None
) -> Any:
    """
    Convenience function to register an optional feature.
    
    Returns the component if available, None otherwise.
    """
    feature_info = registry.register_feature(name, module_path, component_name, required=False)
    return feature_info.component if feature_info.is_available else None


def register_required_feature(
    name: str, 
    module_path: str, 
    component_name: Optional[str] = None
) -> Any:
    """
    Convenience function to register a required feature.
    
    Raises ImportError if the feature is not available.
    """
    feature_info = registry.register_feature(name, module_path, component_name, required=True)
    return feature_info.component


def is_feature_available(name: str) -> bool:
    """Check if a registered feature is available."""
    return registry.is_available(name)


def get_feature(name: str, default: Any = None) -> Any:
    """Get a registered feature component, or default if unavailable."""
    return registry.get_component(name, default)