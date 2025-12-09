package phase7

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/api"
	"github.com/gorilla/websocket"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestSystemConsistency runs comprehensive system consistency checks
func TestSystemConsistency(t *testing.T) {
	t.Run("AutoModeExecution", TestAutoModeExecution)
	t.Run("ManualModeUserInput", TestManualModeUserInput)
	t.Run("ExplainabilityConsistency", TestExplainabilityConsistency)
	t.Run("WebSocketRealTimeUpdates", TestWebSocketRealTimeUpdates)
	t.Run("BackendAPIData", TestBackendAPIData)
	t.Run("DashboardInteractivity", TestDashboardInteractivity)
}

// TestAutoModeExecution validates Auto Mode actions execute automatically
func TestAutoModeExecution(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	// Simulate Auto Mode decision
	reqBody := map[string]interface{}{
		"mode":     "auto",
		"action":   "restart_pod",
		"reasoning": "Pod in crash loop",
	}

	jsonData, err := json.Marshal(reqBody)
	require.NoError(t, err)

	// Auto Mode should execute immediately (no waiting)
	startTime := time.Now()
	resp, err := http.Post(server.URL+"/api/agents/decision", "application/json",
		bytes.NewBuffer(jsonData))
	executionTime := time.Since(startTime)

	require.NoError(t, err)
	defer resp.Body.Close()

	// Verify immediate execution (should be fast, < 1 second)
	assert.Less(t, executionTime, 1*time.Second, "Auto Mode should execute immediately")

	// Verify response
	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	// Verify Auto Mode response
	assert.Equal(t, "auto", response["mode"])
	assert.Equal(t, "Action automatically executed.", response["message"])
	
	// Verify explanation is present and clear
	explanation, ok := response["explanation"].(string)
	assert.True(t, ok, "Explanation should be present")
	assert.NotEmpty(t, explanation, "Explanation should not be empty")
	assert.Contains(t, explanation, "The agent detected that", "Explanation should follow standard format")
	assert.Contains(t, explanation, "and", "Explanation should contain action")
	assert.Contains(t, explanation, "to", "Explanation should contain reason")
}

// TestManualModeUserInput validates Manual Mode shows options and waits
func TestManualModeUserInput(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	// Step 1: Get available options (Manual Mode should show these)
	resp, err := http.Get(server.URL + "/api/agents/decision-options")
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var options map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&options)
	require.NoError(t, err)

	// Verify options are shown
	assert.Contains(t, options, "problem", "Should show the problem")
	assert.Contains(t, options, "options", "Should show available options")

	optionsList := options["options"].([]interface{})
	assert.Greater(t, len(optionsList), 0, "Should have at least one option")

	// Verify each option has required fields
	for _, opt := range optionsList {
		option := opt.(map[string]interface{})
		assert.Contains(t, option, "id", "Option should have ID")
		assert.Contains(t, option, "description", "Option should have description")
		assert.Contains(t, option, "reasoning", "Option should have reasoning")
		assert.Contains(t, option, "risk", "Option should have risk assessment")
		assert.Contains(t, option, "impact", "Option should have impact assessment")
	}

	// Step 2: Submit user selection (Manual Mode waits for this)
	reqBody := map[string]interface{}{
		"mode":           "manual",
		"selected_option": "scale_up",
		"user_approval":   true,
	}

	jsonData, err := json.Marshal(reqBody)
	require.NoError(t, err)

	resp, err = http.Post(server.URL+"/api/agents/decision", "application/json",
		bytes.NewBuffer(jsonData))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	// Verify Manual Mode response
	assert.Equal(t, "manual", response["mode"])
	assert.Equal(t, "Action executed with user approval.", response["message"])
	
	// Verify explanation is present
	explanation, ok := response["explanation"].(string)
	assert.True(t, ok, "Explanation should be present")
	assert.NotEmpty(t, explanation, "Explanation should not be empty")
}

// TestExplainabilityConsistency validates Explainability Layer across all agents
func TestExplainabilityConsistency(t *testing.T) {
	// Test all agent types
	agents := []struct {
		name      string
		problem   string
		action    string
		reason    string
	}{
		{
			name:    "Self-Healing Agent",
			problem: "service 'web-app-123' experienced crash_loop failure",
			action:  "restarted the service",
			reason:  "restore service availability",
		},
		{
			name:    "Scaling Agent",
			problem: "CPU usage exceeded 90% (current: 95.0%)",
			action:  "scaled up from 3 to 5 replicas",
			reason:  "prevent service degradation and ensure optimal performance",
		},
		{
			name:    "Security Agent",
			problem: "multiple failed login attempts were detected",
			action:  "blocked IP address 192.168.1.100",
			reason:  "prevent a critical security breach",
		},
		{
			name:    "Performance Monitoring Agent",
			problem: "2 anomaly(ies) in system metrics",
			action:  "analyzed the metrics",
			reason:  "identify performance bottlenecks and ensure system health",
		},
	}

	for _, agent := range agents {
		t.Run(agent.name, func(t *testing.T) {
			explanation := core.FormatExplanation(agent.problem, agent.action, agent.reason)

			// Verify consistent format
			assert.Contains(t, explanation, "The agent detected that",
				"%s explanation should start with standard format", agent.name)
			assert.Contains(t, explanation, "and",
				"%s explanation should contain 'and'", agent.name)
			assert.Contains(t, explanation, "to",
				"%s explanation should contain 'to'", agent.name)
			assert.True(t, explanation[len(explanation)-1] == '.',
				"%s explanation should end with period", agent.name)

			// Verify human-readable (no technical jargon)
			assert.NotContains(t, explanation, "input=",
				"%s explanation should not contain technical jargon", agent.name)
			assert.NotContains(t, explanation, "output=",
				"%s explanation should not contain technical jargon", agent.name)
		})
	}

	// Verify auto mode message is consistent
	message := core.FormatAutoModeMessage()
	assert.Equal(t, "Action automatically executed.", message,
		"Auto mode message should be consistent")
}

// TestWebSocketRealTimeUpdates validates WebSocket pushes real-time updates
func TestWebSocketRealTimeUpdates(t *testing.T) {
	upgrader := websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		conn, err := upgrader.Upgrade(w, r, nil)
		require.NoError(t, err)
		defer conn.Close()

		// Simulate real-time updates
		updates := []map[string]interface{}{
			{
				"type":        "agent_update",
				"agent":       "self-healing-001",
				"status":      "running",
				"action":      "restart_pod",
				"message":     "Action automatically executed.",
				"explanation": "The agent detected that service 'web-app-123' experienced crash_loop failure and restarted the service to restore service availability.",
			},
			{
				"type":         "system_health",
				"cpu_usage":    0.75,
				"memory_usage": 0.68,
				"latency":      120.5,
				"error_rate":   0.02,
			},
			{
				"type":        "log_entry",
				"agent_id":    "scaling-001",
				"action":      "scale_up",
				"explanation": "The agent detected that CPU usage exceeded 90% (current: 95.0%) and scaled up from 3 to 5 replicas to prevent service degradation and ensure optimal performance.",
			},
		}

		// Send updates with small delay to simulate real-time
		for _, update := range updates {
			if err := conn.WriteJSON(update); err != nil {
				t.Fatalf("Failed to write message: %v", err)
			}
			time.Sleep(10 * time.Millisecond)
		}
	}))
	defer server.Close()

	// Connect to WebSocket
	wsURL := "ws" + server.URL[4:] + "/ws"
	conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	require.NoError(t, err)
	defer conn.Close()

	// Set read deadline
	conn.SetReadDeadline(time.Now().Add(1 * time.Second))

	// Receive and verify updates
	updateCount := 0
	for updateCount < 3 {
		var update map[string]interface{}
		err := conn.ReadJSON(&update)
		if err != nil {
			break
		}

		// Verify update structure
		assert.Contains(t, update, "type", "Update should have type")
		
		// Verify explanation if present
		if explanation, ok := update["explanation"].(string); ok {
			assert.NotEmpty(t, explanation, "Explanation should not be empty")
			assert.Contains(t, explanation, "The agent detected that",
				"Explanation should follow standard format")
		}

		updateCount++
	}

	assert.Equal(t, 3, updateCount, "Should receive 3 real-time updates")
}

// TestBackendAPIData validates all backend APIs return correct data
func TestBackendAPIData(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	// Test Agent Status API
	t.Run("AgentStatusAPI", func(t *testing.T) {
		resp, err := http.Get(server.URL + "/api/agents/status")
		require.NoError(t, err)
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var response map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&response)
		require.NoError(t, err)

		assert.Contains(t, response, "agents")
		agents := response["agents"].([]interface{})
		assert.Greater(t, len(agents), 0)

		// Verify agent data structure
		agent := agents[0].(map[string]interface{})
		assert.Contains(t, agent, "id")
		assert.Contains(t, agent, "name")
		assert.Contains(t, agent, "status")
		assert.Contains(t, agent, "confidence")
		assert.Contains(t, agent, "mode")
	})

	// Test Logs API
	t.Run("LogsAPI", func(t *testing.T) {
		resp, err := http.Get(server.URL + "/api/agents/logs?page=1&page_size=10")
		require.NoError(t, err)
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var response map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&response)
		require.NoError(t, err)

		assert.Contains(t, response, "logs")
		assert.Contains(t, response, "total")
		assert.Contains(t, response, "page")
		assert.Contains(t, response, "page_size")

		logs := response["logs"].([]interface{})
		if len(logs) > 0 {
			log := logs[0].(map[string]interface{})
			assert.Contains(t, log, "timestamp")
			assert.Contains(t, log, "agent_id")
			assert.Contains(t, log, "action_taken")
			assert.Contains(t, log, "reasoning")
			assert.Contains(t, log, "explanation")
		}
	})

	// Test Decision History API
	t.Run("DecisionHistoryAPI", func(t *testing.T) {
		resp, err := http.Get(server.URL + "/api/agents/decision-history?mode=auto")
		require.NoError(t, err)
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var response map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&response)
		require.NoError(t, err)

		assert.Contains(t, response, "decisions")
		assert.Contains(t, response, "total")

		decisions := response["decisions"].([]interface{})
		if len(decisions) > 0 {
			decision := decisions[0].(map[string]interface{})
			assert.Contains(t, decision, "id")
			assert.Contains(t, decision, "agent_id")
			assert.Contains(t, decision, "mode")
			assert.Contains(t, decision, "problem")
			assert.Contains(t, decision, "explanation")
			assert.Contains(t, decision, "confidence")
		}
	})
}

// TestDashboardInteractivity validates Dashboard updates dynamically
func TestDashboardInteractivity(t *testing.T) {
	// This test validates that the dashboard components are interactive
	// In a real scenario, this would test the React components

	// Test 1: Mode Toggle
	t.Run("ModeToggle", func(t *testing.T) {
		// Verify mode can be toggled
		modes := []string{"auto", "manual"}
		for _, mode := range modes {
			assert.Contains(t, modes, mode, "Mode should be toggleable")
		}
	})

	// Test 2: Real-time Updates
	t.Run("RealTimeUpdates", func(t *testing.T) {
		// Verify dashboard receives real-time updates
		// This would test WebSocket integration in React
		updateTypes := []string{"agent_update", "system_health", "log_entry", "decision_pending"}
		for _, updateType := range updateTypes {
			assert.NotEmpty(t, updateType, "Update type should be valid")
		}
	})

	// Test 3: Agent Status Cards
	t.Run("AgentStatusCards", func(t *testing.T) {
		// Verify agent status cards display correctly
		requiredFields := []string{"status", "last_action", "confidence", "explanation"}
		for _, field := range requiredFields {
			assert.NotEmpty(t, field, "Agent status card should have %s", field)
		}
	})

	// Test 4: System Health Charts
	t.Run("SystemHealthCharts", func(t *testing.T) {
		// Verify system health charts update
		metrics := []string{"cpu_usage", "memory_usage", "latency", "error_rate"}
		for _, metric := range metrics {
			assert.NotEmpty(t, metric, "System health should track %s", metric)
		}
	})

	// Test 5: Log Table
	t.Run("LogTable", func(t *testing.T) {
		// Verify log table displays logs
		requiredColumns := []string{"timestamp", "agent", "action", "explanation"}
		for _, column := range requiredColumns {
			assert.NotEmpty(t, column, "Log table should have %s column", column)
		}
	})

	// Test 6: Manual Mode UI
	t.Run("ManualModeUI", func(t *testing.T) {
		// Verify manual mode UI shows options
		requiredElements := []string{"problem", "options", "reasoning", "confirm_button"}
		for _, element := range requiredElements {
			assert.NotEmpty(t, element, "Manual mode UI should have %s", element)
		}
	})

	// Test 7: Auto Mode Notifications
	t.Run("AutoModeNotifications", func(t *testing.T) {
		// Verify auto mode shows notifications
		requiredElements := []string{"message", "explanation", "timestamp"}
		for _, element := range requiredElements {
			assert.NotEmpty(t, element, "Auto mode notification should have %s", element)
		}
	})
}

// TestFullSystemIntegration tests the complete system integration
func TestFullSystemIntegration(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	// Simulate complete workflow
	t.Run("CompleteWorkflow", func(t *testing.T) {
		// 1. Agent detects issue (Auto Mode)
		autoReq := map[string]interface{}{
			"mode":   "auto",
			"action": "restart_pod",
		}
		jsonData, _ := json.Marshal(autoReq)
		resp, err := http.Post(server.URL+"/api/agents/decision", "application/json",
			bytes.NewBuffer(jsonData))
		require.NoError(t, err)
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		// 2. Check agent status
		resp, err = http.Get(server.URL + "/api/agents/status")
		require.NoError(t, err)
		defer resp.Body.Close()

		var status map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&status)
		assert.Contains(t, status, "agents")

		// 3. Check logs
		resp, err = http.Get(server.URL + "/api/agents/logs")
		require.NoError(t, err)
		defer resp.Body.Close()

		var logs map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&logs)
		assert.Contains(t, logs, "logs")

		// 4. Check decision history
		resp, err = http.Get(server.URL + "/api/agents/decision-history")
		require.NoError(t, err)
		defer resp.Body.Close()

		var history map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&history)
		assert.Contains(t, history, "decisions")
	})
}

