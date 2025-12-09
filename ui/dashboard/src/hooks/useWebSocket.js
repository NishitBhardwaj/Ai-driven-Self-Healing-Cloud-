import { useState, useEffect, useRef } from 'react';

/**
 * Custom hook for WebSocket connection
 * Provides real-time data updates from the backend
 */
export function useWebSocket(url) {
  const [connected, setConnected] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    const connect = () => {
      try {
        const ws = new WebSocket(url);

        ws.onopen = () => {
          if (isMounted) {
            setConnected(true);
            setError(null);
            console.log('WebSocket connected');
          }
        };

        ws.onmessage = (event) => {
          if (isMounted) {
            try {
              const message = JSON.parse(event.data);
              setData(message);
            } catch (err) {
              console.error('Error parsing WebSocket message:', err);
            }
          }
        };

        ws.onerror = (err) => {
          if (isMounted) {
            setError(err);
            console.error('WebSocket error:', err);
          }
        };

        ws.onclose = () => {
          if (isMounted) {
            setConnected(false);
            // Attempt to reconnect after 3 seconds
            reconnectTimeoutRef.current = setTimeout(() => {
              if (isMounted) {
                connect();
              }
            }, 3000);
          }
        };

        wsRef.current = ws;
      } catch (err) {
        if (isMounted) {
          setError(err);
          setConnected(false);
        }
      }
    };

    connect();

    return () => {
      isMounted = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url]);

  const sendMessage = (message) => {
    if (wsRef.current && connected) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  return { connected, data, error, sendMessage };
}

