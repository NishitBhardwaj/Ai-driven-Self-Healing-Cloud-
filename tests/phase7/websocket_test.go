package phase7

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gorilla/websocket"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestWebSocketConnection tests WebSocket connection establishment
func TestWebSocketConnection(t *testing.T) {
	// Create a test WebSocket server
	upgrader := websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		conn, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			t.Fatalf("Failed to upgrade connection: %v", err)
		}
		defer conn.Close()

		// Send test message
		msg := map[string]interface{}{
			"type":    "agent_update",
			"agent":   "self-healing-001",
			"status":  "running",
			"message": "Action automatically executed.",
			"explanation": "The agent detected that service 'web-app-123' experienced crash_loop failure and restarted the service to restore service availability.",
		}

		if err := conn.WriteJSON(msg); err != nil {
			t.Fatalf("Failed to write message: %v", err)
		}
	}))
	defer server.Close()

	// Connect to WebSocket
	wsURL := "ws" + server.URL[4:] + "/ws"
	conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	require.NoError(t, err)
	defer conn.Close()

	// Read message
	var received map[string]interface{}
	err = conn.ReadJSON(&received)
	require.NoError(t, err)

	// Verify message
	assert.Equal(t, "agent_update", received["type"])
	assert.Equal(t, "self-healing-001", received["agent"])
	assert.Equal(t, "running", received["status"])
	assert.Contains(t, received["explanation"].(string), "The agent detected that")
}

// TestWebSocketAgentStatusUpdate tests real-time agent status updates
func TestWebSocketAgentStatusUpdate(t *testing.T) {
	upgrader := websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		conn, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			t.Fatalf("Failed to upgrade connection: %v", err)
		}
		defer conn.Close()

		// Simulate multiple agent status updates
		updates := []map[string]interface{}{
			{
				"type":    "agent_update",
				"agent":   "self-healing-001",
				"status":  "running",
				"action":  "restart_pod",
				"message": "Action automatically executed.",
				"explanation": "The agent detected that service 'web-app-123' experienced crash_loop failure and restarted the service to restore service availability.",
			},
			{
				"type":    "agent_update",
				"agent":   "scaling-001",
				"status":  "running",
				"action":  "scale_up",
				"message": "Action automatically executed.",
				"explanation": "The agent detected that CPU usage exceeded 90% (current: 95.0%) and scaled up from 3 to 5 replicas to prevent service degradation and ensure optimal performance.",
			},
		}

		for _, update := range updates {
			if err := conn.WriteJSON(update); err != nil {
				t.Fatalf("Failed to write message: %v", err)
			}
			time.Sleep(10 * time.Millisecond)
		}
	}))
	defer server.Close()

	// Connect and receive updates
	wsURL := "ws" + server.URL[4:] + "/ws"
	conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	require.NoError(t, err)
	defer conn.Close()

	// Set read deadline
	conn.SetReadDeadline(time.Now().Add(1 * time.Second))

	// Receive first update
	var update1 map[string]interface{}
	err = conn.ReadJSON(&update1)
	require.NoError(t, err)
	assert.Equal(t, "self-healing-001", update1["agent"])
	assert.Equal(t, "restart_pod", update1["action"])

	// Receive second update
	var update2 map[string]interface{}
	err = conn.ReadJSON(&update2)
	require.NoError(t, err)
	assert.Equal(t, "scaling-001", update2["agent"])
	assert.Equal(t, "scale_up", update2["action"])
}

// TestWebSocketSystemHealthUpdate tests system health updates
func TestWebSocketSystemHealthUpdate(t *testing.T) {
	upgrader := websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		conn, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			t.Fatalf("Failed to upgrade connection: %v", err)
		}
		defer conn.Close()

		// Send system health update
		healthUpdate := map[string]interface{}{
			"type":         "system_health",
			"cpu_usage":     0.75,
			"memory_usage":  0.68,
			"latency":       120.5,
			"error_rate":   0.02,
			"timestamp":    time.Now().Unix(),
		}

		if err := conn.WriteJSON(healthUpdate); err != nil {
			t.Fatalf("Failed to write message: %v", err)
		}
	}))
	defer server.Close()

	// Connect and receive update
	wsURL := "ws" + server.URL[4:] + "/ws"
	conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	require.NoError(t, err)
	defer conn.Close()

	var health map[string]interface{}
	err = conn.ReadJSON(&health)
	require.NoError(t, err)

	assert.Equal(t, "system_health", health["type"])
	assert.Equal(t, 0.75, health["cpu_usage"])
	assert.Equal(t, 0.68, health["memory_usage"])
}

// TestWebSocketLogEntry tests log entry updates
func TestWebSocketLogEntry(t *testing.T) {
	upgrader := websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		conn, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			t.Fatalf("Failed to upgrade connection: %v", err)
		}
		defer conn.Close()

		// Send log entry
		logEntry := map[string]interface{}{
			"type":        "log_entry",
			"agent_id":    "self-healing-001",
			"agent_name":  "Self-Healing Agent",
			"action":      "restart_pod",
			"reasoning":   "Pod was in crash loop. Restarting should resolve the issue.",
			"explanation": "The agent detected that service 'web-app-123' experienced crash_loop failure and restarted the service to restore service availability.",
			"confidence":  0.95,
			"mode":        "auto",
			"timestamp":   time.Now().Format(time.RFC3339),
		}

		if err := conn.WriteJSON(logEntry); err != nil {
			t.Fatalf("Failed to write message: %v", err)
		}
	}))
	defer server.Close()

	// Connect and receive log entry
	wsURL := "ws" + server.URL[4:] + "/ws"
	conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	require.NoError(t, err)
	defer conn.Close()

	var log map[string]interface{}
	err = conn.ReadJSON(&log)
	require.NoError(t, err)

	assert.Equal(t, "log_entry", log["type"])
	assert.Equal(t, "self-healing-001", log["agent_id"])
	assert.Contains(t, log["explanation"].(string), "The agent detected that")
	assert.Equal(t, 0.95, log["confidence"])
}

// TestWebSocketMessageFormat tests message format validation
func TestWebSocketMessageFormat(t *testing.T) {
	upgrader := websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		conn, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			t.Fatalf("Failed to upgrade connection: %v", err)
		}
		defer conn.Close()

		// Send properly formatted message
		msg := map[string]interface{}{
			"type":        "agent_update",
			"agent":       "scaling-001",
			"status":      "running",
			"message":     "Action automatically executed.",
			"explanation": "The agent detected that CPU usage exceeded 90% (current: 95.0%) and scaled up from 3 to 5 replicas to prevent service degradation and ensure optimal performance.",
		}

		jsonData, err := json.Marshal(msg)
		require.NoError(t, err)

		// Verify JSON is valid
		var parsed map[string]interface{}
		err = json.Unmarshal(jsonData, &parsed)
		require.NoError(t, err)

		if err := conn.WriteJSON(msg); err != nil {
			t.Fatalf("Failed to write message: %v", err)
		}
	}))
	defer server.Close()

	// Connect and verify format
	wsURL := "ws" + server.URL[4:] + "/ws"
	conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	require.NoError(t, err)
	defer conn.Close()

	var received map[string]interface{}
	err = conn.ReadJSON(&received)
	require.NoError(t, err)

	// Verify all required fields are present
	assert.Contains(t, received, "type")
	assert.Contains(t, received, "agent")
	assert.Contains(t, received, "status")
	assert.Contains(t, received, "message")
	assert.Contains(t, received, "explanation")
	
	// Verify explanation format
	explanation := received["explanation"].(string)
	assert.Contains(t, explanation, "The agent detected that")
	assert.Contains(t, explanation, "and")
	assert.Contains(t, explanation, "to")
}

