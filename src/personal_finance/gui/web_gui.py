"""Minimal web GUI used by tests.

Exports an `app` FastAPI instance and a module-global `service` (GUIService).
This file is deliberately minimal and avoids complex templates that can
confuse parsing when edited programmatically.
"""

from typing import Any, Dict
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from personal_finance.gui.gui_service import GUIService

app = FastAPI()
service = GUIService()


def _pos_to_dict(p) -> Dict[str, Any]:
    return {
        "symbol": getattr(p, "symbol", None),
        "name": getattr(p, "name", None),
        "quantity": getattr(p, "quantity", None),
        "buy_price": getattr(p, "buy_price", None),
        "buy_date": getattr(p, "buy_date", None).strftime("%Y-%m-%dT%H:%M:%S") if getattr(p, "buy_date", None) else None,
    }


@app.get("/positions")
def list_positions():
    try:
        positions = service.list_positions()
        return [_pos_to_dict(p) for p in positions]
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}")


@app.post("/positions")
def create_position(payload: Dict[str, Any]):
    sym = payload.get("symbol")
    if not sym:
        raise HTTPException(status_code=400, detail="symbol required")
    name = payload.get("name")
    qty = payload.get("quantity", 0)
    buy_price = payload.get("buy_price", 0)
    buy_date_raw = payload.get("buy_date")

    buy_date = buy_date_raw
    if isinstance(buy_date_raw, str):
        try:
            buy_date = datetime.fromisoformat(buy_date_raw)
        except Exception:
            buy_date = buy_date_raw

    created = service.add_position(sym, name, qty, buy_price, buy_date)
    if created is None:
        raise HTTPException(status_code=400, detail="Could not create position")
    if isinstance(created, dict):
        return created
    return _pos_to_dict(created)


@app.get("/portfolio", response_class=HTMLResponse)
def portfolio_page():
    html = """
    <html>
      <head><meta charset="utf-8"><title>Portfolio</title></head>
      <body>
        <h1>Portfolio</h1>
        <pre id="positions">loading...</pre>
        <script>
          async function load(){
            const r = await fetch('/positions');
            const j = await r.json();
            document.getElementById('positions').innerText = JSON.stringify(j, null, 2);
          }
          load();
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/asset/{symbol}", response_class=HTMLResponse)
def asset_page(symbol: str):
    tpl = """
    <html>
      <head><meta charset="utf-8"><title>Asset __SYMBOL__</title></head>
      <body>
        <h1 id="title">Asset</h1>
        <pre id="summary">loading...</pre>
        <script>
          async function load(sym){
            const r = await fetch('/asset_summary/' + encodeURIComponent(sym));
            const j = await r.json();
            document.getElementById('title').textContent = j.symbol;
            document.getElementById('summary').innerText = JSON.stringify(j, null, 2);
          }
          (function(){ const parts = location.pathname.split('/'); load(parts.pop()); })();
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=tpl.replace('__SYMBOL__', symbol))


@app.get('/asset_summary/{symbol}')
def asset_summary(symbol: str):
    symbol = symbol.upper()
    try:
        ticker = service.get_ticker(symbol)
        position = service.db.get_portfolio_position(symbol)
        if not ticker and not position:
            raise HTTPException(status_code=404, detail='Symbol not found')
        return {
            'symbol': symbol,
            'name': getattr(ticker, 'name', None) or getattr(position, 'name', None),
            'price': getattr(ticker, 'price', None) if ticker else None,
            'quantity': getattr(position, 'quantity', None) if position else None,
            'buy_price': getattr(position, 'buy_price', None) if position else None,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}")
