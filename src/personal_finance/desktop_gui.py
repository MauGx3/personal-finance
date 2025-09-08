"""Compatibility shim: re-export desktop GUI from `personal_finance.gui`.

The implementation now lives in `personal_finance.gui.desktop_gui`.
"""

try:  # pragma: no cover - optional GUI
    from .gui.desktop_gui import App
except Exception:  # pragma: no cover - fallback for packaging
    App = None

__all__ = ["App"]
