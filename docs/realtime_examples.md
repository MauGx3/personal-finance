# Realtime Price Service Usage Examples

This document provides examples of how to use the new `RealtimeService` for subscribing to near real-time price updates.

## Overview

The `RealtimeService` provides a simple publish/subscribe API for receiving price updates from financial data sources. It supports both polling mode (periodic HTTP queries) and WebSocket mode for pushing updates to clients.

## Basic Usage

### 1. Polling Mode (Simple Subscription)

```python
import asyncio
from decimal import Decimal
from personal_finance.realtime.services import RealtimeService, PricePoint

async def main():
    # Create service instance
    service = RealtimeService(
        mode="polling",           # Use polling mode
        update_interval=15,       # Update every 15 seconds
        max_batch_size=50        # Process up to 50 symbols per batch
    )
    
    # Define callback function
    def price_callback(price_point: PricePoint):
        print(f"Price update for {price_point.symbol}: "
              f"${price_point.price} "
              f"({price_point.change:+} / {price_point.change_percent:+.2f}%)")
    
    # Subscribe to symbols
    await service.subscribe(["AAPL", "GOOGL", "MSFT"], price_callback)
    
    # Start the service
    await service.start()
    
    # Let it run for a while
    print("Listening for price updates... Press Ctrl+C to stop")
    try:
        await asyncio.sleep(60)  # Run for 1 minute
    except KeyboardInterrupt:
        print("Stopping service...")
    
    # Stop the service gracefully
    await service.stop()

# Run the example
if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Using the Global Service Instance

```python
import asyncio
from personal_finance.realtime.services import (
    start_realtime_service, 
    stop_realtime_service,
    realtime_service
)

async def main():
    # Start the global service
    await start_realtime_service(mode="polling", update_interval=10)
    
    # Subscribe using the global instance
    def my_callback(price_point):
        print(f"{price_point.symbol}: ${price_point.price}")
    
    await realtime_service.subscribe(["AAPL"], my_callback)
    
    # Let it run
    await asyncio.sleep(30)
    
    # Stop the service
    await stop_realtime_service()

asyncio.run(main())
```

### 3. Multiple Callbacks for the Same Symbol

```python
import asyncio
from personal_finance.realtime.services import RealtimeService

async def main():
    service = RealtimeService(mode="polling", update_interval=5)
    
    # Log prices to console
    def console_logger(price_point):
        print(f"[CONSOLE] {price_point.symbol}: ${price_point.price}")
    
    # Save to file
    def file_logger(price_point):
        with open("price_log.txt", "a") as f:
            f.write(f"{price_point.timestamp}: {price_point.symbol} = ${price_point.price}\\n")
    
    # Alert on significant changes
    def alert_callback(price_point):
        if price_point.change_percent and abs(price_point.change_percent) > 5:
            print(f"🚨 ALERT: {price_point.symbol} moved {price_point.change_percent:.2f}%")
    
    # Subscribe all callbacks to the same symbol
    await service.subscribe(["AAPL"], console_logger)
    await service.subscribe(["AAPL"], file_logger) 
    await service.subscribe(["AAPL"], alert_callback)
    
    await service.start()
    await asyncio.sleep(60)
    await service.stop()

asyncio.run(main())
```

### 4. Async Callbacks

```python
import asyncio
from personal_finance.realtime.services import RealtimeService

async def main():
    service = RealtimeService(mode="polling")
    
    # Async callback that might do database operations, API calls, etc.
    async def async_callback(price_point):
        print(f"Processing {price_point.symbol}...")
        
        # Simulate async operation (database save, API call, etc.)
        await asyncio.sleep(0.1)
        
        print(f"Saved {price_point.symbol} price: ${price_point.price}")
    
    await service.subscribe(["AAPL", "GOOGL"], async_callback)
    await service.start()
    
    await asyncio.sleep(30)
    await service.stop()

asyncio.run(main())
```

## WebSocket Usage

### 1. Starting a WebSocket Server

```python
import asyncio
from personal_finance.realtime.ws import start_websocket_server

async def main():
    # Start WebSocket server
    server = await start_websocket_server(host="localhost", port=8765)
    
    if server:
        print("WebSocket server running on ws://localhost:8765")
        print("Connect with a WebSocket client to receive price updates")
        
        try:
            # Keep server running
            await server.wait_closed()
        except KeyboardInterrupt:
            print("Shutting down server...")

asyncio.run(main())
```

### 2. WebSocket Client Example (JavaScript)

```javascript
// Connect to the WebSocket server
const socket = new WebSocket('ws://localhost:8765');

socket.onopen = function(event) {
    console.log('Connected to price feed');
    
    // Subscribe to price updates
    socket.send(JSON.stringify({
        type: 'subscribe',
        data: {
            symbols: ['AAPL', 'GOOGL', 'MSFT']
        }
    }));
};

socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    
    switch(message.type) {
        case 'subscribed':
            console.log('Subscribed to:', message.symbols);
            break;
            
        case 'price_update':
            const price = message.data;
            console.log(`${price.symbol}: $${price.price} (${price.change_percent}%)`);
            
            // Update UI with new price
            updatePriceDisplay(price);
            break;
            
        case 'error':
            console.error('WebSocket error:', message.error);
            break;
    }
};

function updatePriceDisplay(price) {
    const element = document.getElementById(`price-${price.symbol}`);
    if (element) {
        element.textContent = `$${price.price}`;
        element.className = price.change >= 0 ? 'price-up' : 'price-down';
    }
}
```

### 3. WebSocket Client Example (Python)

```python
import asyncio
import websockets
import json

async def client():
    uri = "ws://localhost:8765"
    
    async with websockets.connect(uri) as websocket:
        # Subscribe to updates
        subscribe_message = {
            "type": "subscribe",
            "data": {"symbols": ["AAPL", "GOOGL"]}
        }
        await websocket.send(json.dumps(subscribe_message))
        
        # Listen for updates
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data["type"] == "price_update":
                    price = data["data"]
                    print(f"Received: {price['symbol']} = ${price['price']}")
                elif data["type"] == "subscribed":
                    print(f"Subscribed to: {data['symbols']}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")

asyncio.run(client())
```

## Configuration

### Environment Variables

You can configure the service using environment variables:

```bash
# Set update interval (seconds)
export REALTIME_UPDATE_INTERVAL=15

# Set batch size for processing symbols
export REALTIME_BATCH_SIZE=50

# Set cache timeout (seconds)  
export REALTIME_CACHE_TIMEOUT=300
```

### Django Settings

If using with Django, add these settings:

```python
# settings.py

# Real-time service configuration
REALTIME_UPDATE_INTERVAL = 15  # seconds between price updates
REALTIME_BATCH_SIZE = 50       # max symbols per batch
REALTIME_CACHE_TIMEOUT = 300   # cache timeout in seconds
```

## Error Handling

```python
import asyncio
from personal_finance.realtime.services import RealtimeService

async def main():
    service = RealtimeService(mode="polling")
    
    def robust_callback(price_point):
        try:
            # Your price processing logic here
            process_price_update(price_point)
        except Exception as e:
            print(f"Error processing {price_point.symbol}: {e}")
            # Log error, send alert, etc.
    
    await service.subscribe(["AAPL"], robust_callback)
    
    try:
        await service.start()
        await asyncio.sleep(60)
    except Exception as e:
        print(f"Service error: {e}")
    finally:
        await service.stop()

def process_price_update(price_point):
    # Your processing logic
    pass

asyncio.run(main())
```

## Integration with Django Views

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from personal_finance.realtime.services import realtime_service

@csrf_exempt
async def subscribe_to_prices(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        symbols = data.get('symbols', [])
        
        # Define callback to store in session or database
        def price_callback(price_point):
            # Store price update for this user/session
            # You could use Django channels, WebSocket, or polling
            pass
        
        await realtime_service.subscribe(symbols, price_callback)
        
        return JsonResponse({
            'status': 'subscribed',
            'symbols': symbols
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
```

## Testing

```python
import asyncio
from unittest.mock import Mock
from personal_finance.realtime.services import RealtimeService, PricePoint
from decimal import Decimal

async def test_subscription():
    service = RealtimeService(mode="polling")
    
    # Track callback calls
    callback_calls = []
    
    def test_callback(price_point):
        callback_calls.append(price_point)
    
    # Subscribe
    await service.subscribe(["AAPL"], test_callback)
    
    # Simulate price update
    price_point = PricePoint(symbol="AAPL", price=Decimal("150.00"))
    await service._notify_subscribers("AAPL", price_point)
    
    # Verify callback was called
    assert len(callback_calls) == 1
    assert callback_calls[0].symbol == "AAPL"
    
    print("Test passed!")

asyncio.run(test_subscription())
```

This completes the basic usage examples for the Realtime Price Service. The service provides a flexible, easy-to-use API for real-time financial data streaming with support for both polling and WebSocket modes.