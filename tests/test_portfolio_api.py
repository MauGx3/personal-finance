import importlib
import sys
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def tmp_db_path(tmp_path):
    dbfile = tmp_path / "test_pf.db"
    return f"sqlite:///{dbfile}"


def _bootstrap_app(tmp_db_path, monkeypatch):
    """Import (or reload) the web_gui module after setting DATABASE_URL.

    Tests set DATABASE_URL per-test to isolate sqlite files. Because the
    FastAPI app + GUIService are created at import time, we must reload the
    module if it was previously imported so the service binds to the new
    database URL instead of reusing a stale engine pointing at a different
    temporary DB (which led to UNIQUE constraint violations across tests).
    """
    monkeypatch.setenv("DATABASE_URL", tmp_db_path)
    if "personal_finance.web_gui" in sys.modules:
        web_gui = importlib.reload(sys.modules["personal_finance.web_gui"])
    else:
        web_gui = importlib.import_module("personal_finance.web_gui")
    web_gui.service.db.create_tables()
    return web_gui


def test_create_and_list_position(tmp_db_path, monkeypatch):
    web_gui = _bootstrap_app(tmp_db_path, monkeypatch)
    client = TestClient(web_gui.app)

    payload = {
        "symbol": "TEST",
        "name": "Test Corp",
        "quantity": 10.5,
        "buy_price": 12.34,
        "buy_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00")
    }

    # Create position
    resp = client.post("/positions", json=payload)
    assert resp.status_code == 200, resp.text

    # List positions and assert our position exists
    resp = client.get("/positions")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    symbols = [p.get('symbol') for p in data]
    assert any(s == 'TEST' for s in symbols), f"Positions returned: {data}"
