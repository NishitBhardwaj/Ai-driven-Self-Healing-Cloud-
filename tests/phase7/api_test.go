package phase7

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/api"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestAgentStatusAPI tests GET /api/agents/status endpoint
func TestAgentStatusAPI(t *testing.T) {
	// Create registry and setup routes
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	// Create test server
	server := httptest.NewServer(router)
	defer server.Close()

	// Make request
	resp, err := http.Get(server.URL + "/api/agents/status")
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)
	assert.Equal(t, "application/json", resp.Header.Get("Content-Type"))

	// Parse response
	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	// Verify response structure
	assert.Contains(t, response, "agents")
	agents := response["agents"].([]interface{})
	assert.Greater(t, len(agents), 0)

	// Verify agent structure
	if len(agents) > 0 {
		agent := agents[0].(map[string]interface{})
		assert.Contains(t, agent, "id")
		assert.Contains(t, agent, "name")
		assert.Contains(t, agent, "status")
		assert.Contains(t, agent, "confidence")
		assert.Contains(t, agent, "mode")
	}
}

// TestAgentStatusAPIWithExplanation tests that explanations are included
func TestAgentStatusAPIWithExplanation(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	resp, err := http.Get(server.URL + "/api/agents/status")
	require.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	agents := response["agents"].([]interface{})
	if len(agents) > 0 {
		agent := agents[0].(map[string]interface{})
		
		// Check if explanation exists (may be empty string)
		if explanation, ok := agent["explanation"].(string); ok {
			// If explanation exists, verify format
			if explanation != "" {
				assert.Contains(t, explanation, "The agent detected that")
			}
		}
	}
}

// TestLogsAPI tests GET /api/agents/logs endpoint
func TestLogsAPI(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	// Test without query parameters
	resp, err := http.Get(server.URL + "/api/agents/logs")
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	// Verify response structure
	assert.Contains(t, response, "logs")
	assert.Contains(t, response, "total")
	assert.Contains(t, response, "page")
	assert.Contains(t, response, "page_size")
	assert.Contains(t, response, "has_more")

	// Verify log structure
	logs := response["logs"].([]interface{})
	if len(logs) > 0 {
		log := logs[0].(map[string]interface{})
		assert.Contains(t, log, "id")
		assert.Contains(t, log, "timestamp")
		assert.Contains(t, log, "agent_id")
		assert.Contains(t, log, "action_taken")
		assert.Contains(t, log, "reasoning")
		assert.Contains(t, log, "explanation")
	}
}

// TestLogsAPIWithFilters tests logs API with query parameters
func TestLogsAPIWithFilters(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	// Test with agent_id filter
	resp, err := http.Get(server.URL + "/api/agents/logs?agent_id=self-healing-001&page=1&page_size=10")
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	assert.Contains(t, response, "logs")
	assert.Equal(t, float64(1), response["page"])
	assert.Equal(t, float64(10), response["page_size"])
}

// TestLogsAPIExplanationFormat tests explanation format in logs
func TestLogsAPIExplanationFormat(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	resp, err := http.Get(server.URL + "/api/agents/logs")
	require.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	logs := response["logs"].([]interface{})
	if len(logs) > 0 {
		log := logs[0].(map[string]interface{})
		
		if explanation, ok := log["explanation"].(string); ok && explanation != "" {
			// Verify explanation format
			assert.Contains(t, explanation, "The agent detected that")
			assert.Contains(t, explanation, "and")
			assert.Contains(t, explanation, "to")
		}
	}
}

// TestDecisionHistoryAPI tests GET /api/agents/decision-history endpoint
func TestDecisionHistoryAPI(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	resp, err := http.Get(server.URL + "/api/agents/decision-history")
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	// Verify response structure
	assert.Contains(t, response, "decisions")
	assert.Contains(t, response, "total")
	assert.Contains(t, response, "page")
	assert.Contains(t, response, "page_size")
	assert.Contains(t, response, "has_more")

	// Verify decision structure
	decisions := response["decisions"].([]interface{})
	if len(decisions) > 0 {
		decision := decisions[0].(map[string]interface{})
		assert.Contains(t, decision, "id")
		assert.Contains(t, decision, "agent_id")
		assert.Contains(t, decision, "mode")
		assert.Contains(t, decision, "problem")
		assert.Contains(t, decision, "reasoning")
		assert.Contains(t, decision, "explanation")
		assert.Contains(t, decision, "confidence")
	}
}

// TestDecisionHistoryAPIWithFilters tests decision history with filters
func TestDecisionHistoryAPIWithFilters(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	// Test with mode filter
	resp, err := http.Get(server.URL + "/api/agents/decision-history?mode=auto&page=1&page_size=20")
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	decisions := response["decisions"].([]interface{})
	// Verify all decisions are in auto mode
	for _, d := range decisions {
		decision := d.(map[string]interface{})
		assert.Equal(t, "auto", decision["mode"])
	}
}

// TestDecisionHistoryExplanationFormat tests explanation format in decision history
func TestDecisionHistoryExplanationFormat(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	resp, err := http.Get(server.URL + "/api/agents/decision-history")
	require.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	decisions := response["decisions"].([]interface{})
	if len(decisions) > 0 {
		decision := decisions[0].(map[string]interface{})
		
		if explanation, ok := decision["explanation"].(string); ok && explanation != "" {
			// Verify explanation format
			assert.Contains(t, explanation, "The agent detected that")
			assert.Contains(t, explanation, "and")
			assert.Contains(t, explanation, "to")
		}
	}
}

// TestAPICORS tests CORS headers
func TestAPICORS(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	// Test OPTIONS request
	req, err := http.NewRequest("OPTIONS", server.URL+"/api/agents/status", nil)
	require.NoError(t, err)

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	// Verify CORS headers
	assert.Equal(t, "*", resp.Header.Get("Access-Control-Allow-Origin"))
	assert.Contains(t, resp.Header.Get("Access-Control-Allow-Methods"), "GET")
}

// TestAPIHealthCheck tests health check endpoint
func TestAPIHealthCheck(t *testing.T) {
	registry := core.GetRegistry()
	logger := logrus.New()
	router := api.SetupRoutes(registry, logger)

	server := httptest.NewServer(router)
	defer server.Close()

	resp, err := http.Get(server.URL + "/health")
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, "ok", response["status"])
}

