# Real-time WebSocket Implementation - Usage Guide

This document provides comprehensive guidance on using the real-time WebSocket system for live market data updates and portfolio tracking.

## Overview

The real-time WebSocket system provides:
- **Live Price Feeds**: Real-time asset price updates from multiple data sources
- **Portfolio Tracking**: Live portfolio value calculations with position updates
- **WebSocket Management**: Connection handling, authentication, and message routing
- **Scalable Architecture**: Designed for high-frequency updates and multiple concurrent users
- **Production Ready**: Comprehensive error handling, logging, and monitoring capabilities

## Quick Start

### 1. Start the Price Feed Service

```bash
# Start the real-time price feed service
python manage.py start_price_feed

# With custom settings
python manage.py start_price_feed --interval 15 --batch-size 100 --verbose
```

### 2. Access the Real-time Dashboard

Navigate to `/realtime/dashboard/` to access the interactive WebSocket dashboard.

### 3. Test WebSocket Connection

Use the test interface at `/realtime/test/` to verify WebSocket connectivity.

## WebSocket API

### Connection

Connect to the WebSocket endpoint:
```javascript
const wsUrl = 'ws://localhost:8000/ws/realtime/';
const socket = new WebSocket(wsUrl);
```

### Message Format

All messages follow this JSON structure:
```json
{
    "type": "message_type",
    "data": {
        // Message-specific data
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Supported Message Types

#### Client to Server

**Ping/Pong**
```json
{
    "type": "ping",
    "data": {}
}
```

**Asset Subscription**
```json
{
    "type": "subscribe_asset",
    "data": {
        "symbol": "AAPL"
    }
}
```

**Portfolio Subscription**
```json
{
    "type": "subscribe_portfolio", 
    "data": {
        "portfolio_id": 123
    }
}
```

**Unsubscription**
```json
{
    "type": "unsubscribe_asset",
    "data": {
        "symbol": "AAPL"
    }
}
```

#### Server to Client

**Connection Established**
```json
{
    "type": "connection",
    "data": {
        "status": "connected",
        "connection_id": "uuid-string",
        "authenticated": true,
        "user_id": 123
    }
}
```

**Asset Price Update**
```json
{
    "type": "asset_update",
    "data": {
        "symbol": "AAPL",
        "price": 150.25,
        "change": 2.50,
        "change_percent": 1.69,
        "volume": 50000000,
        "high": 151.00,
        "low": 148.50
    }
}
```

**Portfolio Value Update**
```json
{
    "type": "portfolio_update",
    "data": {
        "portfolio_id": 123,
        "name": "Growth Portfolio",
        "total_value": 50000.00,
        "daily_change": 125.50,
        "daily_change_percent": 0.25
    }
}
```

## JavaScript Client Usage

### Basic WebSocket Client

```javascript
class SimpleWebSocketClient {
    constructor(url) {
        this.url = url;
        this.socket = null;
    }
    
    connect() {
        this.socket = new WebSocket(this.url);
        
        this.socket.onopen = (event) => {
            console.log('Connected to WebSocket');
            this.sendMessage('ping', {});
        };
        
        this.socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
        
        this.socket.onclose = (event) => {
            console.log('WebSocket connection closed');
        };
    }
    
    sendMessage(type, data) {
        const message = {
            type: type,
            data: data,
            timestamp: new Date().toISOString()
        };
        this.socket.send(JSON.stringify(message));
    }
    
    handleMessage(message) {
        switch(message.type) {
            case 'asset_update':
                this.updateAssetPrice(message.data);
                break;
            case 'portfolio_update':
                this.updatePortfolioValue(message.data);
                break;
            default:
                console.log('Received:', message);
        }
    }
    
    subscribeToAsset(symbol) {
        this.sendMessage('subscribe_asset', { symbol: symbol });
    }
    
    subscribeToPortfolio(portfolioId) {
        this.sendMessage('subscribe_portfolio', { portfolio_id: portfolioId });
    }
}

// Usage
const client = new SimpleWebSocketClient('ws://localhost:8000/ws/realtime/');
client.connect();

// Subscribe to updates
client.subscribeToAsset('AAPL');
client.subscribeToPortfolio(123);
```

### Advanced Usage with React/Vue

```javascript
// React Hook for WebSocket
import { useState, useEffect, useRef } from 'react';

function useWebSocket(url) {
    const [isConnected, setIsConnected] = useState(false);
    const [messages, setMessages] = useState([]);
    const socket = useRef(null);
    
    useEffect(() => {
        socket.current = new WebSocket(url);
        
        socket.current.onopen = () => setIsConnected(true);
        socket.current.onclose = () => setIsConnected(false);
        socket.current.onmessage = (event) => {
            const message = JSON.parse(event.data);
            setMessages(prev => [...prev, message]);
        };
        
        return () => socket.current.close();
    }, [url]);
    
    const sendMessage = (type, data) => {
        if (socket.current && socket.current.readyState === WebSocket.OPEN) {
            const message = { type, data, timestamp: new Date().toISOString() };
            socket.current.send(JSON.stringify(message));
        }
    };
    
    return { isConnected, messages, sendMessage };
}

// Component usage
function PortfolioTracker({ portfolioId }) {
    const { isConnected, messages, sendMessage } = useWebSocket('ws://localhost:8000/ws/realtime/');
    const [portfolioValue, setPortfolioValue] = useState(0);
    
    useEffect(() => {
        if (isConnected) {
            sendMessage('subscribe_portfolio', { portfolio_id: portfolioId });
        }
    }, [isConnected, portfolioId]);
    
    useEffect(() => {
        const portfolioUpdates = messages.filter(m => m.type === 'portfolio_update');
        const latestUpdate = portfolioUpdates[portfolioUpdates.length - 1];
        if (latestUpdate) {
            setPortfolioValue(latestUpdate.data.total_value);
        }
    }, [messages]);
    
    return (
        <div>
            <h3>Portfolio Value: ${portfolioValue.toFixed(2)}</h3>
            <div>Status: {isConnected ? 'Connected' : 'Disconnected'}</div>
        </div>
    );
}
```

## REST API Integration

### Get WebSocket Information

```bash
GET /realtime/websocket-info/
```

Response:
```json
{
    "websocket_url": "ws://localhost:8000/ws/realtime/",
    "connection_info": {
        "protocol": "ws",
        "host": "localhost:8000",
        "path": "/ws/realtime/",
        "authentication": "session-based"
    },
    "message_types": {
        "ping": "Health check message",
        "subscribe_asset": "Subscribe to asset price updates"
    }
}
```

### Service Status

```bash
GET /realtime/status/
```

Response:
```json
{
    "service_status": "running",
    "global_stats": {
        "total_connections": 15,
        "authenticated_users": 8,
        "portfolio_subscriptions": 12,
        "asset_subscriptions": 25
    },
    "user_stats": {
        "connection_count": 2,
        "subscriptions": {
            "portfolios": [123, 456],
            "assets": ["AAPL", "GOOGL", "MSFT"]
        }
    }
}
```

### Force Price Update

```bash
POST /api/realtime/force_price_update/
Content-Type: application/json

{
    "symbols": ["AAPL", "GOOGL", "MSFT"]
}
```

## Management Commands

### Start Price Feed Service

```bash
# Basic usage
python manage.py start_price_feed

# With custom parameters
python manage.py start_price_feed \
    --interval 15 \
    --batch-size 100 \
    --verbose

# Production deployment
python manage.py start_price_feed \
    --interval 30 \
    --batch-size 50 \
    > /var/log/price_feed.log 2>&1 &
```

### Update Asset Prices (One-time)

```bash
# Update all assets
python manage.py update_asset_prices

# Update specific symbols
python manage.py update_asset_prices --symbols AAPL MSFT GOOGL

# Historical data update
python manage.py update_asset_prices --historical --days 30
```

## Configuration

### Settings

Add to your Django settings:

```python
# Real-time WebSocket Settings
REALTIME_UPDATE_INTERVAL = 30  # seconds
REALTIME_BATCH_SIZE = 50  # assets per batch
REALTIME_CACHE_TIMEOUT = 300  # 5 minutes
WEBSOCKET_TIMEOUT = 300  # 5 minutes
```

### Environment Variables

```bash
# .env file
REALTIME_UPDATE_INTERVAL=30
REALTIME_BATCH_SIZE=50
REALTIME_CACHE_TIMEOUT=300
WEBSOCKET_TIMEOUT=300
```

## Production Deployment

### Docker Configuration

```dockerfile
# Dockerfile additions for WebSocket support
EXPOSE 8000
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx Configuration

```nginx
# nginx.conf - WebSocket proxy
location /ws/ {
    proxy_pass http://django_app;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 86400;
}
```

### Systemd Service

```ini
# /etc/systemd/system/price-feed.service
[Unit]
Description=Personal Finance Price Feed Service
After=network.target

[Service]
Type=simple
User=finance
WorkingDirectory=/opt/personal-finance
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=/opt/personal-finance/venv/bin/python manage.py start_price_feed
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Monitoring and Logging

### Health Checks

```python
# views.py - Health check endpoint
@login_required
def health_check(request):
    return JsonResponse({
        'price_feed_running': price_feed_service.is_running,
        'active_connections': connection_manager.get_connection_count(),
        'timestamp': timezone.now().isoformat()
    })
```

### Logging Configuration

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'realtime_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/realtime.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'personal_finance.realtime': {
            'handlers': ['realtime_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Troubleshooting

### Common Issues

**WebSocket Connection Fails**
- Check if the price feed service is running
- Verify WebSocket URL and protocol (ws:// vs wss://)
- Check firewall and proxy settings

**No Price Updates**
- Verify data source availability
- Check API rate limits
- Review service logs for errors

**High Memory Usage**
- Reduce batch size and update frequency
- Implement connection limits
- Monitor subscription counts

### Debug Mode

```bash
# Enable verbose logging
python manage.py start_price_feed --verbose

# Check WebSocket connections
curl http://localhost:8000/realtime/status/

# Test specific assets
python manage.py update_asset_prices --symbols AAPL --dry-run
```

## Performance Optimization

### Caching Strategy

```python
# Implement Redis caching for price data
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Database Optimization

```python
# Optimize queries for real-time updates
# Use select_related and prefetch_related
positions = Position.objects.select_related('asset', 'portfolio').filter(
    portfolio__user=user,
    quantity__gt=0
)

# Index optimization
class Asset(models.Model):
    symbol = models.CharField(max_length=20, db_index=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
```

## Security Considerations

### Authentication

- WebSocket connections use Django session authentication
- User must be logged in to access portfolio data
- Portfolio access is restricted to owners only

### Rate Limiting

```python
# Implement connection limits per user
MAX_CONNECTIONS_PER_USER = 5
MAX_SUBSCRIPTIONS_PER_CONNECTION = 50
```

### Data Validation

- All incoming messages are validated
- Asset symbols are verified against database
- Portfolio ownership is checked for subscriptions

This implementation provides a solid foundation for real-time market data streaming with room for customization and scaling based on specific requirements.