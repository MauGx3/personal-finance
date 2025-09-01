"""Minimal FastAPI web GUI exposing CRUD endpoints for the finance DB.

Run with (from repo root):

PYTHONPATH=src uvicorn personal_finance.web_gui:app --reload

Ensure DATABASE_URL is exported for PostgreSQL in production. For local testing
you can pass a sqlite URL by instantiating GUIService(database_url=...) in code.
"""
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
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
