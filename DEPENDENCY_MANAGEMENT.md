# Dependency Management System

This document explains the new structured dependency management system that replaces the fragile try/except import patterns previously used throughout the codebase.

## Problem Statement

The original code had multiple scattered try/except blocks for imports like this:

```python
# OLD: Fragile approach
try:
    from . import portfolio
except Exception:
    portfolio = None

try:
    import stockdex as sd
except ImportError:
    sd = None
```

This approach was problematic because:
- Error messages were unclear or missing
- No centralized dependency management
- Difficult to understand what dependencies are optional vs required
- Silent failures made debugging difficult
- No fallback strategies documented

## New Solution

The new system provides:

### 1. Centralized Dependency Management (`dependencies.py`)

A `DependencyManager` class that:
- Registers dependencies with proper metadata
- Provides clear error messages with installation instructions
- Supports feature flags for optional functionality
- Logs dependency status appropriately

### 2. Configuration-Driven Approach (`dependency_config.py`)

All dependencies are configured in one place with:
- Import paths
- Required vs optional status
- Fallback strategies
- Installation instructions
- Feature flag associations

### 3. Structured Error Handling

Instead of silent failures, the system provides:
- Clear error messages
- Installation instructions
- Fallback strategy information
- Proper logging levels (INFO for optional, ERROR for required)

## Usage Examples

### Basic Dependency Registration

```python
from .dependencies import dependency_manager

# Register a dependency
dep_info = dependency_manager.register_dependency(
    name="stockdex",
    import_path="stockdex",
    required=False,
    fallback_available=True
)

# Get the module if available
stockdex = dependency_manager.get_dependency("stockdex")
if stockdex:
    # Use the module
    ticker = stockdex.Ticker("AAPL")
```

### Feature Flags

```python
# Enable/disable features based on available dependencies
dependency_manager.enable_feature("advanced_analytics")

if dependency_manager.is_feature_enabled("advanced_analytics"):
    # Provide advanced features
    pass
```

### Requiring Dependencies

```python
from .dependencies import require_dependency

# This will raise a clear error if the dependency is missing
pymongo = require_dependency("pymongo", "MongoDB support")
MongoClient = pymongo.MongoClient
```

## Migration Guide

### Before (Fragile)

```python
try:
    import stockdex as sd
except ImportError:
    sd = None

# Later in code...
if sd is not None:
    ticker = sd.Ticker("AAPL")
```

### After (Structured)

```python
from .dependencies import dependency_manager, get_module

# Register the dependency (usually done in setup)
dependency_manager.register_dependency(
    name="stockdex",
    import_path="stockdex",
    required=False,
    fallback_available=True
)

# Get the module
sd = get_module("stockdex")

# Use it the same way
if sd is not None:
    ticker = sd.Ticker("AAPL")
```

## Benefits

1. **Clear Error Messages**: Users get helpful error messages with installation instructions
2. **Centralized Configuration**: All dependency information in one place
3. **Better Debugging**: Proper logging instead of silent failures
4. **Feature Flags**: Can enable/disable features based on available dependencies
5. **Fallback Strategies**: Clear documentation of what happens when dependencies are missing
6. **Maintainability**: Easier to understand and modify dependency requirements

## Configuration

Dependencies are configured in `dependency_config.py`:

```python
DEPENDENCY_CONFIG = {
    "stockdx": {
        "import_path": "stockdx",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Use alternative price fetching APIs",
        "description": "Stock data and financial information API",
        "install_command": "pip install stockdx"
    }
}
```

## Testing

The system includes comprehensive tests in `test_dependency_management.py` that validate:
- Dependency registration and retrieval
- Error handling for missing dependencies
- Feature flag functionality
- Backward compatibility

## Backward Compatibility

The new system maintains backward compatibility:
- Existing module attributes (`personal_finance.portfolio`, etc.) still work
- Import behavior is preserved
- Only error handling and logging are improved

## Future Enhancements

Possible future improvements:
- Automatic dependency installation prompts
- Version checking for dependencies
- Dependency graph visualization
- Integration with package managers