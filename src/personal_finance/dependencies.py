"""
Dependency Management System

Provides a structured approach to handle optional dependencies with proper
error handling and fallback mechanisms. This replaces the fragile try/except
blocks scattered throughout the codebase.
"""

import logging
from typing import Any, Dict, Optional, Type, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DependencyStatus(Enum):
    """Status of dependency availability."""
    AVAILABLE = "available"
    MISSING = "missing"
    ERROR = "error"


@dataclass
class DependencyInfo:
    """Information about a dependency."""
    name: str
    module: Optional[Any] = None
    status: DependencyStatus = DependencyStatus.MISSING
    error_message: Optional[str] = None
    fallback_available: bool = False


class DependencyManager:
    """
    Manages optional dependencies with structured error handling.
    
    This class provides a centralized way to manage optional dependencies,
    check their availability, and provide fallback mechanisms.
    """
    
    def __init__(self):
        self._dependencies: Dict[str, DependencyInfo] = {}
        self._feature_flags: Dict[str, bool] = {}
    
    def register_dependency(
        self,
        name: str,
        import_path: str,
        required: bool = False,
        fallback_available: bool = False
    ) -> DependencyInfo:
        """
        Register and attempt to import a dependency.
        
        Args:
            name: Human-readable name for the dependency
            import_path: Python import path (e.g., 'stockdex')
            required: Whether this dependency is required for core functionality
            fallback_available: Whether fallback mechanisms exist
            
        Returns:
            DependencyInfo object with import status
        """
        try:
            module = self._import_module(import_path)
            dep_info = DependencyInfo(
                name=name,
                module=module,
                status=DependencyStatus.AVAILABLE,
                fallback_available=fallback_available
            )
            logger.debug(f"Successfully imported {name} from {import_path}")
            
        except ImportError as e:
            error_msg = f"Failed to import {name} from {import_path}: {e}"
            if required:
                logger.error(error_msg)
            else:
                logger.info(f"Optional dependency {name} not available: {e}")
            
            dep_info = DependencyInfo(
                name=name,
                module=None,
                status=DependencyStatus.MISSING,
                error_message=error_msg,
                fallback_available=fallback_available
            )
            
        except Exception as e:
            error_msg = f"Unexpected error importing {name}: {e}"
            logger.warning(error_msg)
            
            dep_info = DependencyInfo(
                name=name,
                module=None,
                status=DependencyStatus.ERROR,
                error_message=error_msg,
                fallback_available=fallback_available
            )
        
        self._dependencies[name] = dep_info
        return dep_info
    
    def get_dependency(self, name: str) -> Optional[Any]:
        """
        Get a dependency module if available.
        
        Args:
            name: Name of the dependency
            
        Returns:
            The imported module or None if not available
        """
        dep_info = self._dependencies.get(name)
        if dep_info and dep_info.status == DependencyStatus.AVAILABLE:
            return dep_info.module
        return None
    
    def is_available(self, name: str) -> bool:
        """Check if a dependency is available."""
        dep_info = self._dependencies.get(name)
        return dep_info is not None and dep_info.status == DependencyStatus.AVAILABLE
    
    def get_status(self, name: str) -> Optional[DependencyInfo]:
        """Get detailed status information for a dependency."""
        return self._dependencies.get(name)
    
    def list_dependencies(self) -> Dict[str, DependencyInfo]:
        """Get all registered dependencies."""
        return self._dependencies.copy()
    
    def enable_feature(self, feature_name: str) -> None:
        """Enable a feature flag."""
        self._feature_flags[feature_name] = True
    
    def disable_feature(self, feature_name: str) -> None:
        """Disable a feature flag."""
        self._feature_flags[feature_name] = False
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature flag is enabled."""
        return self._feature_flags.get(feature_name, False)
    
    def _import_module(self, import_path: str) -> Any:
        """Import a module by path."""
        if '.' in import_path:
            # Handle relative imports like '.database'
            if import_path.startswith('.'):
                # This would need to be called from within the package
                from importlib import import_module
                return import_module(import_path, package='personal_finance')
            else:
                # Handle absolute imports like 'stockdex'
                from importlib import import_module
                return import_module(import_path)
        else:
            # Simple import
            return __import__(import_path)


# Global dependency manager instance
dependency_manager = DependencyManager()


def setup_core_dependencies() -> None:
    """
    Setup core dependencies for the personal finance package.
    
    This function registers all known dependencies with proper fallback
    information and feature flags.
    """
    # External finance libraries
    dependency_manager.register_dependency(
        name="stockdex",
        import_path="stockdex",
        required=False,
        fallback_available=True
    )
    
    dependency_manager.register_dependency(
        name="yfinance", 
        import_path="yfinance",
        required=False,
        fallback_available=True
    )
    
    # Database dependencies
    dependency_manager.register_dependency(
        name="pymongo",
        import_path="pymongo",
        required=False,
        fallback_available=True
    )
    
    dependency_manager.register_dependency(
        name="alembic",
        import_path="alembic",
        required=False,
        fallback_available=False
    )
    
    # Enable default features
    dependency_manager.enable_feature("portfolio_management")
    dependency_manager.enable_feature("price_fetching")


def get_module(name: str) -> Optional[Any]:
    """
    Convenience function to get a dependency module.
    
    Args:
        name: Name of the dependency
        
    Returns:
        The module if available, None otherwise
    """
    return dependency_manager.get_dependency(name)


def require_dependency(name: str, feature_name: str = None) -> Any:
    """
    Require a dependency, raising an error if not available.
    
    Args:
        name: Name of the dependency
        feature_name: Optional feature name for better error messages
        
    Returns:
        The dependency module
        
    Raises:
        ImportError: If the dependency is not available
    """
    module = dependency_manager.get_dependency(name)
    if module is None:
        dep_info = dependency_manager.get_status(name)
        feature_msg = f" for {feature_name}" if feature_name else ""
        
        if dep_info and dep_info.fallback_available:
            raise ImportError(
                f"Dependency '{name}' is required{feature_msg} but not available. "
                f"Please install it with: pip install {name}"
            )
        else:
            raise ImportError(
                f"Critical dependency '{name}' is not available{feature_msg}. "
                f"Error: {dep_info.error_message if dep_info else 'Unknown error'}"
            )
    
    return module