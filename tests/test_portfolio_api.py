import os
import importlib
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def tmp_db_path(tmp_path):
    dbfile = tmp_path / "test_pf.db"
    return f"sqlite:///{dbfile}"


def test_create_and_list_position(tmp_db_path, monkeypatch):
    # Ensure DATABASE_URL is set before importing the web app (it creates a service at import)
    monkeypatch.setenv('DATABASE_URL', tmp_db_path)

    # Import web_gui after setting env so it constructs GUIService with our test DB
    web_gui = importlib.import_module('personal_finance.web_gui')

    # Create tables directly (tests don't run alembic)
    web_gui.service.db.create_tables()

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
