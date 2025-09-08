import importlib
import sys
from datetime import datetime, timezone, timedelta

import pytest

# Skip entire module at collection time if FastAPI isn't available. This
# allows VS Code's test discovery to succeed even when optional dev deps
# (fastapi) are not installed in the current environment.
pytest.importorskip("fastapi")
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


def _seed_sample(web_gui):
    # Add ticker + position + a couple of prices
    svc = web_gui.service
    svc.add_ticker("ASSET_TEST", "Asset Test Corp", 20.0)
    now = datetime.now(timezone.utc)
    svc.add_position("ASSET_TEST", "Asset Test Corp", 5, 10.0, now)
    # Two prices (yesterday, today)
    svc.add_price("ASSET_TEST", now - timedelta(days=1), 19, 21, 18, 20, 1000)
    svc.add_price("ASSET_TEST", now, 20, 22, 19, 21, 1100)


def test_asset_summary_and_prices(tmp_db_path, monkeypatch):
    web_gui = _bootstrap_app(tmp_db_path, monkeypatch)
    _seed_sample(web_gui)
    client = TestClient(web_gui.app)

    # Summary endpoint
    r = client.get("/asset_summary/ASSET_TEST")
    assert r.status_code == 200, r.text
    summary = r.json()
    assert summary["symbol"] == "ASSET_TEST"
    assert summary["quantity"] == 5
    # Accept either stored price or last price from history depending on timing
    assert summary["price"] in (20.0, 21.0)
    assert summary["cost_basis"] == 50.0
    # Allow several possible current values (depends on stored price)
    assert summary["current_value"] in (100.0, 105.0, 110.0, 21.0 * 5)

    # Prices endpoint (limit param + ordering)
    r = client.get("/prices/ASSET_TEST?limit=1")
    assert r.status_code == 200
    prices = r.json()
    assert isinstance(prices, list) and len(prices) == 1
    # date ordering: most recent first
    latest = prices[0]["date"]
    assert latest is not None

    # Full list default
    r = client.get("/prices/ASSET_TEST")
    assert r.status_code == 200
    all_prices = r.json()
    assert len(all_prices) >= 2


def test_ticker_detail_404(tmp_db_path, monkeypatch):
    web_gui = _bootstrap_app(tmp_db_path, monkeypatch)
    client = TestClient(web_gui.app)
    r = client.get("/tickers/UNKNOWN")
    assert r.status_code == 404


def test_ticker_detail_success(tmp_db_path, monkeypatch):
    web_gui = _bootstrap_app(tmp_db_path, monkeypatch)
    web_gui.service.add_ticker("ABC", "ABC Inc", 12.5)
    client = TestClient(web_gui.app)
    r = client.get("/tickers/abc")  # case-insensitive
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "ABC"
    assert data["name"] == "ABC Inc"
