"""Compatibility shim: re-export desktop GUI from `personal_finance.gui`.

The implementation now lives in `personal_finance.gui.desktop_gui`.
"""

from .gui.desktop_gui import *  # re-export for backward compatibility

__all__ = ["App"]
