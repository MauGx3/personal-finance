"""Minimal FastAPI web GUI exposing CRUD endpoints for the finance DB.

Run with (from repo root):

PYTHONPATH=src uvicorn personal_finance.web_gui:app --reload

Ensure DATABASE_URL is exported for PostgreSQL in production. For local testing
you can pass a sqlite URL by instantiating GUIService(database_url=...) in code.
"""
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response, JSONResponse
from sqlalchemy import text
from pydantic import BaseModel

from .gui_service import GUIService

app = FastAPI(title="Personal Finance GUI")
service = GUIService()  # uses env DATABASE_URL by default


class TickerIn(BaseModel):
    symbol: str
    name: str
    price: Optional[float] = None


class PositionIn(BaseModel):
    symbol: str
    name: str
    quantity: float
    buy_price: float
    buy_date: datetime


class PriceIn(BaseModel):
    symbol: str
    date: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None


@app.get("/tickers")
def list_tickers():
    return service.list_tickers()


@app.get("/", include_in_schema=False)
def landing():
        """Serve a small landing page with links to the API docs and health check."""
        html = """
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width,initial-scale=1" />
            <title>Personal Finance</title>
            <style>
                body { font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; margin: 40px; color:#0f172a }
                a { color: #2563eb; text-decoration: none }
                .card { border: 1px solid #e6e9ef; padding: 18px; border-radius: 8px; max-width:720px }
            </style>
        </head>
        <body>
            <h1>Personal Finance</h1>
            <div class="card">
                <p>A minimal web GUI for your personal finance data.</p>
                <ul>
                    <li><a href="/docs">Interactive API docs (OpenAPI)</a></li>
                    <li><a href="/tickers">GET /tickers</a></li>
                    <li><a href="/positions">GET /positions</a></li>
                </ul>
                <p>Health: <a href="/health">/health</a></p>
            </div>
            <footer style="margin-top:18px;color:#6b7280">Deployed service</footer>
        </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=200)


@app.get('/favicon.ico', include_in_schema=False)
def favicon():
        """Return empty 204 so browsers don't hit a 404 for favicon requests."""
        return Response(status_code=204)


@app.post("/tickers")
def create_ticker(payload: TickerIn):
    t = service.add_ticker(payload.symbol.upper(), payload.name, payload.price)
    if not t:
        raise HTTPException(status_code=400, detail="Could not create ticker")
    return t


@app.get("/positions")
def list_positions():
    return service.list_positions()


@app.post("/positions")
def create_position(payload: PositionIn):
    p = service.add_position(payload.symbol.upper(), payload.name, payload.quantity, payload.buy_price, payload.buy_date)
    return p


@app.post("/prices")
def add_price(payload: PriceIn):
    p = service.add_price(payload.symbol.upper(), payload.date, payload.open, payload.high, payload.low, payload.close, payload.volume)
    return p


@app.get("/health")
def health():
    """Lightweight health check — verifies the app and DB connectivity.

    Returns 200 with {status: 'ok', db: 'ok'} when a simple SELECT 1 succeeds.
    Returns 503 with error details if the DB check fails.
    """
    try:
        # Perform a minimal DB round-trip to ensure connectivity and basic query ability.
        with service.db.get_session() as session:
            session.execute(text("SELECT 1"))
        return JSONResponse(status_code=200, content={"status": "ok", "db": "ok"})
    except Exception as exc:  # pragma: no cover - runtime failure path
        # Don't leak internal stack but include the exception message for diagnostics.
        return JSONResponse(status_code=503, content={"status": "fail", "db": "error", "detail": str(exc)})
