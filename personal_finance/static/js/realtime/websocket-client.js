/**
 * WebSocket client for real-time market data updates.
 * 
 * Handles WebSocket connections, message routing, and UI updates
 * for live portfolio and asset price feeds.
 */

class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.socket = null;
        this.connectionId = null;
        this.isConnected = false;
        this.messageCount = 0;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000; // 3 seconds
        
        // Subscription tracking
        this.portfolioSubscriptions = new Set();
        this.assetSubscriptions = new Set();
        
        // UI elements
        this.uiElements = {};
        
        // Message handlers
        this.messageHandlers = {
            'connection': this.handleConnection.bind(this),
            'asset_update': this.handleAssetUpdate.bind(this),
            'portfolio_update': this.handlePortfolioUpdate.bind(this),
            'subscription_confirmed': this.handleSubscriptionConfirmed.bind(this),
            'unsubscription_confirmed': this.handleUnsubscriptionConfirmed.bind(this),
            'error': this.handleError.bind(this),
            'pong': this.handlePong.bind(this)
        };
    }
    
    /**
     * Connect to the WebSocket server.
     */
    connect() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log('WebSocket already connected');
            return;
        }
        
        this.logMessage('Connecting to WebSocket...', 'info');
        
        try {
            this.socket = new WebSocket(this.url);
            
            this.socket.onopen = this.onOpen.bind(this);
            this.socket.onmessage = this.onMessage.bind(this);
            this.socket.onclose = this.onClose.bind(this);
            this.socket.onerror = this.onError.bind(this);
            
        } catch (error) {
            this.logMessage(`Connection error: ${error.message}`, 'error');
        }
    }
    
    /**
     * Disconnect from the WebSocket server.
     */
    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }
    
    /**
     * Handle WebSocket connection opened.
     */
    onOpen(event) {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.logMessage('WebSocket connected', 'success');
        this.updateConnectionStatus('Connected', 'success');
        
        // Send ping to verify connection
        this.sendMessage('ping', {});
    }
    
    /**
     * Handle incoming WebSocket messages.
     */
    onMessage(event) {
        try {
            const message = JSON.parse(event.data);
            this.messageCount++;
            
            this.logMessage(`Received: ${message.type}`, 'info');
            this.updateMessageCount();
            this.updateLastUpdate();
            
            // Route message to appropriate handler
            const handler = this.messageHandlers[message.type];
            if (handler) {
                handler(message.data);
            } else {
                console.warn('Unknown message type:', message.type);
            }
            
        } catch (error) {
            console.error('Error parsing message:', error);
            this.logMessage(`Parse error: ${error.message}`, 'error');
        }
    }
    
    /**
     * Handle WebSocket connection closed.
     */
    onClose(event) {
        this.isConnected = false;
        this.logMessage(`WebSocket disconnected: ${event.code}`, 'warning');
        this.updateConnectionStatus('Disconnected', 'secondary');
        
        // Attempt to reconnect if not intentional
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect();
        }
    }
    
    /**
     * Handle WebSocket errors.
     */
    onError(event) {
        console.error('WebSocket error:', event);
        this.logMessage('WebSocket error occurred', 'error');
    }
    
    /**
     * Attempt to reconnect to the WebSocket.
     */
    attemptReconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectInterval * this.reconnectAttempts;
        
        this.logMessage(`Reconnecting in ${delay/1000} seconds... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`, 'warning');
        
        setTimeout(() => {
            this.connect();
        }, delay);
    }
    
    /**
     * Send a message to the WebSocket server.
     */
    sendMessage(type, data) {
        if (!this.isConnected) {
            this.logMessage('Cannot send message: not connected', 'error');
            return false;
        }
        
        const message = {
            type: type,
            data: data,
            timestamp: new Date().toISOString()
        };
        
        try {
            this.socket.send(JSON.stringify(message));
            this.logMessage(`Sent: ${type}`, 'info');
            return true;
        } catch (error) {
            this.logMessage(`Send error: ${error.message}`, 'error');
            return false;
        }
    }
    
    /**
     * Subscribe to asset price updates.
     */
    subscribeToAsset(symbol) {
        if (this.sendMessage('subscribe_asset', { symbol: symbol })) {
            this.assetSubscriptions.add(symbol);
            this.updateAssetSubscriptions();
        }
    }
    
    /**
     * Unsubscribe from asset price updates.
     */
    unsubscribeFromAsset(symbol) {
        if (this.sendMessage('unsubscribe_asset', { symbol: symbol })) {
            this.assetSubscriptions.delete(symbol);
            this.updateAssetSubscriptions();
        }
    }
    
    /**
     * Subscribe to portfolio value updates.
     */
    subscribeToPortfolio(portfolioId) {
        if (this.sendMessage('subscribe_portfolio', { portfolio_id: portfolioId })) {
            this.portfolioSubscriptions.add(portfolioId);
            this.updatePortfolioSubscriptions();
        }
    }
    
    /**
     * Unsubscribe from portfolio value updates.
     */
    unsubscribeFromPortfolio(portfolioId) {
        if (this.sendMessage('unsubscribe_portfolio', { portfolio_id: portfolioId })) {
            this.portfolioSubscriptions.delete(portfolioId);
            this.updatePortfolioSubscriptions();
        }
    }
    
    // Message Handlers
    
    handleConnection(data) {
        this.connectionId = data.connection_id;
        this.updateConnectionId();
        this.logMessage(`Connection established: ${this.connectionId}`, 'success');
    }
    
    handleAssetUpdate(data) {
        this.updateAssetPrice(data);
        this.logMessage(`Asset update: ${data.symbol} = $${data.price}`, 'info');
    }
    
    handlePortfolioUpdate(data) {
        this.updatePortfolioValue(data);
        this.logMessage(`Portfolio update: ${data.name} = $${data.total_value}`, 'info');
    }
    
    handleSubscriptionConfirmed(data) {
        this.logMessage(`Subscription confirmed: ${data.type} - ${data.symbol || data.portfolio_id}`, 'success');
    }
    
    handleUnsubscriptionConfirmed(data) {
        this.logMessage(`Unsubscription confirmed: ${data.type} - ${data.symbol || data.portfolio_id}`, 'success');
    }
    
    handleError(data) {
        this.logMessage(`Server error: ${data.message}`, 'error');
    }
    
    handlePong(data) {
        this.logMessage('Pong received', 'info');
    }
    
    // UI Update Methods
    
    updateConnectionStatus(status, type) {
        const element = this.uiElements.connectionStatus;
        if (element) {
            element.textContent = status;
            element.className = `badge badge-${type}`;
        }
        
        // Update buttons
        const connectBtn = this.uiElements.connectBtn;
        const disconnectBtn = this.uiElements.disconnectBtn;
        
        if (this.isConnected) {
            if (connectBtn) connectBtn.style.display = 'none';
            if (disconnectBtn) disconnectBtn.style.display = 'inline-block';
        } else {
            if (connectBtn) connectBtn.style.display = 'inline-block';
            if (disconnectBtn) disconnectBtn.style.display = 'none';
        }
    }
    
    updateConnectionId() {
        const element = this.uiElements.connectionId;
        if (element) {
            element.textContent = this.connectionId || '-';
        }
    }
    
    updateMessageCount() {
        const element = this.uiElements.messageCount;
        if (element) {
            element.textContent = this.messageCount;
        }
    }
    
    updateLastUpdate() {
        const element = this.uiElements.lastUpdate;
        if (element) {
            element.textContent = new Date().toLocaleTimeString();
        }
    }
    
    updateAssetPrice(data) {
        const container = this.uiElements.assetPrices;
        if (!container) return;
        
        let assetElement = container.querySelector(`[data-symbol="${data.symbol}"]`);
        
        if (!assetElement) {
            assetElement = document.createElement('div');
            assetElement.className = 'asset-price-item border-bottom py-2';
            assetElement.setAttribute('data-symbol', data.symbol);
            container.appendChild(assetElement);
            
            // Remove "no data" message if it exists
            const noDataMsg = container.querySelector('.text-muted');
            if (noDataMsg) noDataMsg.remove();
        }
        
        const changeClass = data.change >= 0 ? 'text-success' : 'text-danger';
        const changeSymbol = data.change >= 0 ? '+' : '';
        
        assetElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <strong>${data.symbol}</strong>
                <div class="text-end">
                    <div class="h6 mb-0">$${parseFloat(data.price).toFixed(2)}</div>
                    <small class="${changeClass}">
                        ${changeSymbol}${(data.change || 0).toFixed(2)} 
                        (${changeSymbol}${(data.change_percent || 0).toFixed(2)}%)
                    </small>
                </div>
            </div>
        `;
    }
    
    updatePortfolioValue(data) {
        const container = this.uiElements.portfolioValues;
        if (!container) return;
        
        let portfolioElement = container.querySelector(`[data-portfolio-id="${data.portfolio_id}"]`);
        
        if (!portfolioElement) {
            portfolioElement = document.createElement('div');
            portfolioElement.className = 'portfolio-value-item border-bottom py-2';
            portfolioElement.setAttribute('data-portfolio-id', data.portfolio_id);
            container.appendChild(portfolioElement);
            
            // Remove "no data" message if it exists
            const noDataMsg = container.querySelector('.text-muted');
            if (noDataMsg) noDataMsg.remove();
        }
        
        const changeClass = data.daily_change >= 0 ? 'text-success' : 'text-danger';
        const changeSymbol = data.daily_change >= 0 ? '+' : '';
        
        portfolioElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <strong>${data.name}</strong>
                <div class="text-end">
                    <div class="h6 mb-0">$${parseFloat(data.total_value).toFixed(2)}</div>
                    <small class="${changeClass}">
                        ${changeSymbol}${(data.daily_change || 0).toFixed(2)} 
                        (${changeSymbol}${(data.daily_change_percent || 0).toFixed(2)}%)
                    </small>
                </div>
            </div>
        `;
    }
    
    updateAssetSubscriptions() {
        const container = this.uiElements.assetSubscriptions;
        if (!container) return;
        
        container.innerHTML = '';
        
        if (this.assetSubscriptions.size === 0) {
            container.innerHTML = '<li class="text-muted">No active subscriptions</li>';
            return;
        }
        
        this.assetSubscriptions.forEach(symbol => {
            const li = document.createElement('li');
            li.className = 'mb-1';
            li.innerHTML = `
                <span class="badge badge-primary me-2">${symbol}</span>
                <button class="btn btn-xs btn-outline-danger" onclick="wsClient.unsubscribeFromAsset('${symbol}')">×</button>
            `;
            container.appendChild(li);
        });
    }
    
    updatePortfolioSubscriptions() {
        const container = this.uiElements.portfolioSubscriptions;
        if (!container) return;
        
        container.innerHTML = '';
        
        if (this.portfolioSubscriptions.size === 0) {
            container.innerHTML = '<li class="text-muted">No active subscriptions</li>';
            return;
        }
        
        this.portfolioSubscriptions.forEach(portfolioId => {
            const li = document.createElement('li');
            li.className = 'mb-1';
            li.innerHTML = `
                <span class="badge badge-success me-2">Portfolio ${portfolioId}</span>
                <button class="btn btn-xs btn-outline-danger" onclick="wsClient.unsubscribeFromPortfolio(${portfolioId})">×</button>
            `;
            container.appendChild(li);
        });
    }
    
    logMessage(message, type = 'info') {
        const logContainer = this.uiElements.messageLog;
        if (!logContainer) {
            console.log(`[${type.toUpperCase()}] ${message}`);
            return;
        }
        
        const timestamp = new Date().toLocaleTimeString();
        const typeColors = {
            'info': 'text-info',
            'success': 'text-success',
            'warning': 'text-warning',
            'error': 'text-danger'
        };
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${typeColors[type] || 'text-dark'}`;
        logEntry.innerHTML = `[${timestamp}] ${message}`;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Limit log entries to prevent memory issues
        const entries = logContainer.querySelectorAll('.log-entry');
        if (entries.length > 100) {
            entries[0].remove();
        }
    }
    
    clearLog() {
        const logContainer = this.uiElements.messageLog;
        if (logContainer) {
            logContainer.innerHTML = '';
        }
    }
    
    /**
     * Bind WebSocket client to UI elements.
     */
    bindToUI() {
        // Cache UI elements
        this.uiElements = {
            connectionStatus: document.getElementById('connection-status'),
            connectionId: document.getElementById('connection-id'),
            messageCount: document.getElementById('message-count'),
            lastUpdate: document.getElementById('last-update'),
            connectBtn: document.getElementById('connect-btn'),
            disconnectBtn: document.getElementById('disconnect-btn'),
            portfolioSelect: document.getElementById('portfolio-select'),
            assetSymbol: document.getElementById('asset-symbol'),
            subscribePortfolioBtn: document.getElementById('subscribe-portfolio-btn'),
            unsubscribePortfolioBtn: document.getElementById('unsubscribe-portfolio-btn'),
            subscribeAssetBtn: document.getElementById('subscribe-asset-btn'),
            unsubscribeAssetBtn: document.getElementById('unsubscribe-asset-btn'),
            portfolioSubscriptions: document.getElementById('portfolio-subscriptions'),
            assetSubscriptions: document.getElementById('asset-subscriptions'),
            portfolioValues: document.getElementById('portfolio-values'),
            assetPrices: document.getElementById('asset-prices'),
            messageLog: document.getElementById('message-log'),
            clearLogBtn: document.getElementById('clear-log-btn')
        };
        
        // Bind events
        if (this.uiElements.connectBtn) {
            this.uiElements.connectBtn.addEventListener('click', () => this.connect());
        }
        
        if (this.uiElements.disconnectBtn) {
            this.uiElements.disconnectBtn.addEventListener('click', () => this.disconnect());
        }
        
        if (this.uiElements.subscribePortfolioBtn) {
            this.uiElements.subscribePortfolioBtn.addEventListener('click', () => {
                const portfolioId = this.uiElements.portfolioSelect.value;
                if (portfolioId) {
                    this.subscribeToPortfolio(parseInt(portfolioId));
                }
            });
        }
        
        if (this.uiElements.unsubscribePortfolioBtn) {
            this.uiElements.unsubscribePortfolioBtn.addEventListener('click', () => {
                const portfolioId = this.uiElements.portfolioSelect.value;
                if (portfolioId) {
                    this.unsubscribeFromPortfolio(parseInt(portfolioId));
                }
            });
        }
        
        if (this.uiElements.subscribeAssetBtn) {
            this.uiElements.subscribeAssetBtn.addEventListener('click', () => {
                const symbol = this.uiElements.assetSymbol.value.toUpperCase();
                if (symbol) {
                    this.subscribeToAsset(symbol);
                    this.uiElements.assetSymbol.value = '';
                }
            });
        }
        
        if (this.uiElements.unsubscribeAssetBtn) {
            this.uiElements.unsubscribeAssetBtn.addEventListener('click', () => {
                const symbol = this.uiElements.assetSymbol.value.toUpperCase();
                if (symbol) {
                    this.unsubscribeFromAsset(symbol);
                    this.uiElements.assetSymbol.value = '';
                }
            });
        }
        
        if (this.uiElements.clearLogBtn) {
            this.uiElements.clearLogBtn.addEventListener('click', () => this.clearLog());
        }
        
        // Enter key support for asset symbol input
        if (this.uiElements.assetSymbol) {
            this.uiElements.assetSymbol.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.uiElements.subscribeAssetBtn.click();
                }
            });
        }
        
        // Initialize subscriptions display
        this.updateAssetSubscriptions();
        this.updatePortfolioSubscriptions();
    }
}

// Make WebSocketClient available globally
window.WebSocketClient = WebSocketClient;