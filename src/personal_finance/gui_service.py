"""Simple service adapter used by GUI frontends.

This lives on top of DatabaseManager and exposes a small, stable API
that both a web frontend and a local desktop GUI can call.

Pass an explicit database_url to use a local DB for development (e.g. sqlite)
or omit to use environment `DATABASE_URL` (production).

Compatibility shim: re-export GUIService from `personal_finance.gui`.

After the refactor the implementation resides at
`personal_finance.gui.gui_service.GUIService`.
"""

from .gui.gui_service import GUIService

__all__ = ["GUIService"]
