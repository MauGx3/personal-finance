"""GUI subpackage: web and desktop frontends plus service adapter.

This package contains the original GUI modules moved from the package root
to keep the code organized. Top-level modules re-export from here to keep
backwards-compatibility.
"""

from .web_gui import app, service  # re-export for convenience

__all__ = ["app", "service"]
