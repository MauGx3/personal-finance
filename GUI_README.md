Personal Finance - Minimal GUI

This adds a tiny GUI layer to exercise CRUD operations against the database.

Files added:
- src/personal_finance/gui_service.py  # service adapter
- src/personal_finance/web_gui.py     # FastAPI app
- src/personal_finance/desktop_gui.py # Tkinter desktop app

Quickstart (web):
1. Ensure you have a DATABASE_URL env var for PostgreSQL (production). For local testing you can edit `web_gui.py` to instantiate `GUIService(database_url='sqlite:///./test.db')`.
2. Run the FastAPI app:

   PYTHONPATH=src uvicorn personal_finance.web_gui:app --reload

Quickstart (desktop):

1. Run the Tkinter app (ensure PYTHONPATH includes `src`):

   PYTHONPATH=src python -m personal_finance.desktop_gui

Notes:
- The production codebase enforces PostgreSQL for production use; the GUIService accepts an explicit `database_url` for local testing.
- If you prefer I can convert the desktop GUI to PySide/PyQt or wire the web GUI to a simple JavaScript frontend.
