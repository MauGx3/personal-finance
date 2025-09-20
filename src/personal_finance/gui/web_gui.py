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
from personal_finance.assets.yahoo_finance import get_comprehensive_stock_info
import html

app = FastAPI()
service = GUIService()


def _pos_to_dict(p) -> Dict[str, Any]:
    return {
        "symbol": getattr(p, "symbol", None),
        "name": getattr(p, "name", None),
        "quantity": getattr(p, "quantity", None),
        "buy_price": getattr(p, "buy_price", None),
        "buy_date": getattr(p, "buy_date", None).strftime("%Y-%m-%dT%H:%M:%S")
        if getattr(p, "buy_date", None)
        else None,
    }


@app.get("/positions")
def list_positions():
    try:
        positions = service.list_positions()
        return [_pos_to_dict(p) for p in positions]
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Database unavailable: {exc}"
        )


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
        raise HTTPException(
            status_code=400, detail="Could not create position"
        )
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


@app.get("/stock/{symbol}", response_class=HTMLResponse)
def us_stock_page(symbol: str):
    """Dedicated US stock view page with comprehensive information"""
    symbol = symbol.upper()

    stock_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{symbol} - US Stock Information</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .stock-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
            .price-positive {{ color: #28a745; }}
            .price-negative {{ color: #dc3545; }}
            .metric-card {{ border-left: 4px solid #007bff; }}
            .loading {{ text-align: center; padding: 50px; }}
            .error {{ text-align: center; padding: 50px; color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="stock-header p-4 mb-4">
                <div class="row align-items-center">
                    <div class="col">
                        <h1 class="mb-0" id="stock-name">Loading {symbol}...</h1>
                        <p class="mb-0 opacity-75" id="stock-symbol">{symbol}</p>
                    </div>
                    <div class="col-auto">
                        <h2 class="mb-0" id="current-price">$--</h2>
                        <p class="mb-0" id="price-change">--</p>
                    </div>
                </div>
            </div>
            
            <div id="loading" class="loading">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p>Fetching stock information...</p>
            </div>
            
            <div id="error" class="error d-none">
                <h3>Stock Not Found</h3>
                <p>Could not retrieve information for symbol <strong>{symbol}</strong></p>
                <p>Please check the symbol and try again.</p>
                <a href="/" class="btn btn-primary">Back to Home</a>
            </div>
            
            <div id="stock-content" class="d-none">
                <div class="row">
                    <!-- Key Metrics -->
                    <div class="col-lg-8">
                        <div class="card metric-card mb-4">
                            <div class="card-header">
                                <h5 class="mb-0">Price Information</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="row mb-2">
                                            <div class="col-6"><strong>Previous Close:</strong></div>
                                            <div class="col-6" id="previous-close">$--</div>
                                        </div>
                                        <div class="row mb-2">
                                            <div class="col-6"><strong>Day Range:</strong></div>
                                            <div class="col-6" id="day-range">$-- - $--</div>
                                        </div>
                                        <div class="row mb-2">
                                            <div class="col-6"><strong>52 Week Range:</strong></div>
                                            <div class="col-6" id="week-range">$-- - $--</div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="row mb-2">
                                            <div class="col-6"><strong>Volume:</strong></div>
                                            <div class="col-6" id="volume">--</div>
                                        </div>
                                        <div class="row mb-2">
                                            <div class="col-6"><strong>Avg Volume:</strong></div>
                                            <div class="col-6" id="avg-volume">--</div>
                                        </div>
                                        <div class="row mb-2">
                                            <div class="col-6"><strong>Market Cap:</strong></div>
                                            <div class="col-6" id="market-cap">--</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card metric-card mb-4">
                            <div class="card-header">
                                <h5 class="mb-0">Company Information</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="row mb-2">
                                            <div class="col-4"><strong>Sector:</strong></div>
                                            <div class="col-8" id="sector">--</div>
                                        </div>
                                        <div class="row mb-2">
                                            <div class="col-4"><strong>Industry:</strong></div>
                                            <div class="col-8" id="industry">--</div>
                                        </div>
                                        <div class="row mb-2">
                                            <div class="col-4"><strong>Exchange:</strong></div>
                                            <div class="col-8" id="exchange">--</div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="row mb-2">
                                            <div class="col-4"><strong>P/E Ratio:</strong></div>
                                            <div class="col-8" id="pe-ratio">--</div>
                                        </div>
                                        <div class="row mb-2">
                                            <div class="col-4"><strong>Dividend Yield:</strong></div>
                                            <div class="col-8" id="dividend-yield">--</div>
                                        </div>
                                        <div class="row mb-2">
                                            <div class="col-4"><strong>Currency:</strong></div>
                                            <div class="col-8" id="currency">--</div>
                                        </div>
                                    </div>
                                </div>
                                <div class="mt-3" id="summary-section" style="display: none;">
                                    <h6>Business Summary:</h6>
                                    <p class="text-muted" id="business-summary">--</p>
                                </div>
                                <div class="mt-3" id="website-section" style="display: none;">
                                    <a href="#" target="_blank" id="company-website" class="btn btn-outline-primary btn-sm">Visit Company Website</a>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Quick Actions -->
                    <div class="col-lg-4">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Quick Actions</h5>
                            </div>
                            <div class="card-body">
                                <div class="d-grid gap-2">
                                    <button class="btn btn-primary" onclick="refreshData()">Refresh Data</button>
                                    <button class="btn btn-outline-secondary" onclick="viewHistoricalData()">View Historical Data</button>
                                    <button class="btn btn-outline-info" onclick="addToPortfolio()">Add to Portfolio</button>
                                </div>
                                <hr>
                                <small class="text-muted">
                                    <strong>Last Updated:</strong><br>
                                    <span id="last-updated">--</span>
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            async function loadStockData() {{
                try {{
                    const response = await fetch('/api/stock/{symbol}');
                    if (!response.ok) {{
                        throw new Error('Stock not found');
                    }}
                    
                    const data = await response.json();
                    
                    // Update header
                    document.getElementById('stock-name').textContent = data.name || '{symbol}';
                    document.getElementById('stock-symbol').textContent = data.symbol;
                    document.getElementById('current-price').textContent = '$' + data.current_price;
                    
                    // Update price change
                    const changeElement = document.getElementById('price-change');
                    const change = data.price_change;
                    const changePercent = data.price_change_percent;
                    const changeText = (change >= 0 ? '+' : '') + change.toFixed(2) + ' (' + (changePercent >= 0 ? '+' : '') + changePercent.toFixed(2) + '%)';
                    changeElement.textContent = changeText;
                    changeElement.className = change >= 0 ? 'price-positive mb-0' : 'price-negative mb-0';
                    
                    // Update price information
                    document.getElementById('previous-close').textContent = '$' + data.previous_close;
                    document.getElementById('day-range').textContent = '$' + data.day_low + ' - $' + data.day_high;
                    document.getElementById('week-range').textContent = data.fifty_two_week_low && data.fifty_two_week_high ? 
                        '$' + data.fifty_two_week_low + ' - $' + data.fifty_two_week_high : 'N/A';
                    document.getElementById('volume').textContent = data.volume_formatted;
                    document.getElementById('avg-volume').textContent = data.avg_volume ? (data.avg_volume / 1000000).toFixed(2) + 'M' : 'N/A';
                    document.getElementById('market-cap').textContent = data.market_cap_formatted;
                    
                    // Update company information
                    document.getElementById('sector').textContent = data.sector || 'N/A';
                    document.getElementById('industry').textContent = data.industry || 'N/A';
                    document.getElementById('exchange').textContent = data.exchange || 'N/A';
                    document.getElementById('pe-ratio').textContent = data.pe_ratio ? data.pe_ratio.toFixed(2) : 'N/A';
                    document.getElementById('dividend-yield').textContent = data.dividend_yield ? (data.dividend_yield * 100).toFixed(2) + '%' : 'N/A';
                    document.getElementById('currency').textContent = data.currency || 'USD';
                    
                    // Update business summary
                    if (data.summary) {{
                        document.getElementById('business-summary').textContent = data.summary;
                        document.getElementById('summary-section').style.display = 'block';
                    }}
                    
                    // Update website link
                    if (data.website) {{
                        document.getElementById('company-website').href = data.website;
                        document.getElementById('website-section').style.display = 'block';
                    }}
                    
                    // Update timestamp
                    document.getElementById('last-updated').textContent = data.last_updated;
                    
                    // Show content, hide loading
                    document.getElementById('loading').classList.add('d-none');
                    document.getElementById('stock-content').classList.remove('d-none');
                    
                }} catch (error) {{
                    console.error('Error loading stock data:', error);
                    document.getElementById('loading').classList.add('d-none');
                    document.getElementById('error').classList.remove('d-none');
                }}
            }}
            
            function refreshData() {{
                document.getElementById('stock-content').classList.add('d-none');
                document.getElementById('error').classList.add('d-none');
                document.getElementById('loading').classList.remove('d-none');
                loadStockData();
            }}
            
            function viewHistoricalData() {{
                window.open('/prices/{symbol}', '_blank');
            }}
            
            function addToPortfolio() {{
                alert('Add to Portfolio functionality coming soon!');
            }}
            
            // Load data when page loads
            loadStockData();
        </script>
    </body>
    </html>
    """

    return HTMLResponse(
        content=stock_template.format(symbol=html.escape(symbol))
    )


@app.get("/asset/{symbol}", response_class=HTMLResponse)
def asset_page(symbol: str):
    """Legacy asset page - redirect to new stock page for better experience"""
    # For US stocks, redirect to the new comprehensive view
    return us_stock_page(symbol)


@app.get("/api/stock/{symbol}")
def get_stock_info(symbol: str):
    """API endpoint to get comprehensive stock information"""
    symbol = symbol.upper()
    try:
        stock_data = get_comprehensive_stock_info(symbol)
        if not stock_data:
            raise HTTPException(
                status_code=404,
                detail=f"Stock information not found for symbol {symbol}",
            )
        return stock_data
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Unable to fetch stock data: {str(exc)}"
        )


@app.get("/asset_summary/{symbol}")
def asset_summary(symbol: str):
    symbol = symbol.upper()
    try:
        ticker = service.get_ticker(symbol)
        position = service.db.get_portfolio_position(symbol)
        if not ticker and not position:
            raise HTTPException(status_code=404, detail="Symbol not found")

        # Calculate cost_basis and current_value
        cost_basis = None
        current_value = None
        if position:
            cost_basis = position.quantity * position.buy_price
            current_price = ticker.price if ticker else position.buy_price
            current_value = position.quantity * current_price

        return {
            "symbol": symbol,
            "name": getattr(ticker, "name", None)
            or getattr(position, "name", None),
            "price": getattr(ticker, "price", None) if ticker else None,
            "quantity": getattr(position, "quantity", None)
            if position
            else None,
            "buy_price": getattr(position, "buy_price", None)
            if position
            else None,
            "cost_basis": cost_basis,
            "current_value": current_value,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Database unavailable: {exc}"
        )


@app.get("/prices/{symbol}")
def get_prices(symbol: str, limit: int = None):
    symbol = symbol.upper()
    try:
        prices = service.list_prices(symbol)
        if not prices:
            raise HTTPException(
                status_code=404, detail="No prices found for symbol"
            )

        # Convert to dict format and sort by date (most recent first)
        price_dicts = []
        for price in prices:
            price_dict = {
                "date": price.date.isoformat() if price.date else None,
                "open": price.open_price,
                "high": price.high_price,
                "low": price.low_price,
                "close": price.close_price,
                "volume": price.volume,
            }
            price_dicts.append(price_dict)

        # Sort by date descending (most recent first)
        price_dicts.sort(key=lambda x: x["date"] or "", reverse=True)

        # Apply limit if specified
        if limit is not None and limit > 0:
            price_dicts = price_dicts[:limit]

        return price_dicts
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Database unavailable: {exc}"
        )


@app.get("/tickers/{symbol}")
def get_ticker(symbol: str):
    symbol = symbol.upper()
    try:
        ticker = service.get_ticker(symbol)
        if not ticker:
            raise HTTPException(status_code=404, detail="Ticker not found")

        return {
            "symbol": ticker.symbol,
            "name": ticker.name,
            "price": ticker.price,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Database unavailable: {exc}"
        )
