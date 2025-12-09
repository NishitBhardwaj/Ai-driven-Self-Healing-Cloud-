/**
 * WebSocket Service
 * Handles real-time communication with backend for agent updates, system health, and events
 */

class WebSocketService {
  constructor(url = 'ws://localhost:8080/ws') {
    this.url = url;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 3000;
    this.listeners = new Map();
    this.isConnected = false;
    this.eventHistory = [];
    this.maxHistorySize = 1000;
  }

  /**
   * Connect to WebSocket server
   */
  connect() {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.emit('connection', { status: 'connected' });
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', { error });
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.emit('connection', { status: 'disconnected' });
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      this.attemptReconnect();
    }
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(message) {
    const { type, payload, timestamp } = message;

    // Add to event history
    const event = {
      id: `event-${Date.now()}-${Math.random()}`,
      type,
      payload,
      timestamp: timestamp || new Date().toISOString(),
      receivedAt: new Date().toISOString(),
    };

    this.addToHistory(event);

    // Emit to listeners
    this.emit(type, event);
    this.emit('*', event); // Emit to all listeners
  }

  /**
   * Add event to history
   */
  addToHistory(event) {
    this.eventHistory.unshift(event);
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory = this.eventHistory.slice(0, this.maxHistorySize);
    }
  }

  /**
   * Attempt to reconnect to WebSocket
   */
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay);
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('connection', { status: 'failed' });
    }
  }

  /**
   * Send message to WebSocket server
   */
  send(message) {
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, message not sent:', message);
    }
  }

  /**
   * Subscribe to event type
   */
  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(eventType);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  /**
   * Unsubscribe from event type
   */
  off(eventType, callback) {
    const callbacks = this.listeners.get(eventType);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Emit event to listeners
   */
  emit(eventType, data) {
    // Emit to specific listeners
    const callbacks = this.listeners.get(eventType);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in event callback:', error);
        }
      });
    }
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.listeners.clear();
  }

  /**
   * Get connection status
   */
  getConnectionStatus() {
    return {
      connected: this.isConnected,
      url: this.url,
      reconnectAttempts: this.reconnectAttempts,
    };
  }

  /**
   * Get event history
   */
  getEventHistory(filter = {}) {
    let history = [...this.eventHistory];

    // Filter by type
    if (filter.type) {
      history = history.filter(event => event.type === filter.type);
    }

    // Filter by agent
    if (filter.agentId) {
      history = history.filter(event => 
        event.payload?.agent_id === filter.agentId ||
        event.payload?.agentId === filter.agentId
      );
    }

    // Filter by date range
    if (filter.startDate) {
      history = history.filter(event => 
        new Date(event.timestamp) >= new Date(filter.startDate)
      );
    }
    if (filter.endDate) {
      history = history.filter(event => 
        new Date(event.timestamp) <= new Date(filter.endDate)
      );
    }

    // Limit results
    if (filter.limit) {
      history = history.slice(0, filter.limit);
    }

    return history;
  }

  /**
   * Clear event history
   */
  clearHistory() {
    this.eventHistory = [];
  }
}

// Create singleton instance
let wsServiceInstance = null;

export const getWebSocketService = (url) => {
  if (!wsServiceInstance) {
    wsServiceInstance = new WebSocketService(url);
  }
  return wsServiceInstance;
};

export default WebSocketService;

