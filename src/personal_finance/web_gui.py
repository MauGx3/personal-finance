"""Compatibility shim: keep imports working at personal_finance.web_gui.

The real implementation now lives in personal_finance.gui.web_gui. Importing
this module simply re-exports the FastAPI `app` and the module-global
`service` object so existing code and tests continue to work.
"""

from .gui.web_gui import app, service  # re-export concrete symbols

__all__ = ["app", "service"]
