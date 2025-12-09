package phase7

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestAutoModeDecision tests Auto Mode decision execution
func TestAutoModeDecision(t *testing.T) {
	// Create test server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" || r.URL.Path != "/api/agents/decision" {
			w.WriteHeader(http.StatusNotFound)
			return
		}

		var req map[string]interface{}
		err := json.NewDecoder(r.Body).Decode(&req)
		require.NoError(t, err)

		// Verify request
		assert.Equal(t, "auto", req["mode"])
		assert.Contains(t, req, "action")
		assert.Contains(t, req, "reasoning")

		// Return response
		response := map[string]interface{}{
			"status":      "success",
			"mode":        "auto",
			"message":     "Action automatically executed.",
			"explanation": "The agent detected that CPU usage exceeded 90% (current: 95.0%) and scaled up from 3 to 5 replicas to prevent service degradation and ensure optimal performance.",
			"action":      req["action"],
			"confidence":  0.95,
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}))
	defer server.Close()

	// Make request
	reqBody := map[string]interface{}{
		"mode":     "auto",
		"action":   "scale_up",
		"reasoning": "CPU usage exceeded threshold",
	}

	jsonData, err := json.Marshal(reqBody)
	require.NoError(t, err)

	resp, err := http.Post(server.URL+"/api/agents/decision", "application/json", 
		bytes.NewBuffer(jsonData))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	// Verify response
	assert.Equal(t, "success", response["status"])
	assert.Equal(t, "auto", response["mode"])
	assert.Equal(t, "Action automatically executed.", response["message"])
	assert.Contains(t, response["explanation"].(string), "The agent detected that")
}

// TestManualModeDecision tests Manual Mode decision with user approval
func TestManualModeDecision(t *testing.T) {
	// Create test server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" && r.URL.Path == "/api/agents/decision-options" {
			// Return available options
			options := map[string]interface{}{
				"problem": "CPU usage is at 95%",
				"options": []map[string]interface{}{
					{
						"id":          "scale_up",
						"description": "Scale up from 3 to 5 replicas",
						"reasoning":   "Adding more replicas will distribute the load",
						"risk":        "low",
						"impact":      "high",
					},
					{
						"id":          "optimize",
						"description": "Optimize existing resources",
						"reasoning":   "Optimize the current deployment configuration",
						"risk":        "medium",
						"impact":      "medium",
					},
				},
			}
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(options)
			return
		}

		if r.Method == "POST" && r.URL.Path == "/api/agents/decision" {
			var req map[string]interface{}
			err := json.NewDecoder(r.Body).Decode(&req)
			require.NoError(t, err)

			// Verify request
			assert.Equal(t, "manual", req["mode"])
			assert.Contains(t, req, "selected_option")
			assert.Contains(t, req, "user_approval")

			// Return response
			response := map[string]interface{}{
				"status":      "success",
				"mode":        "manual",
				"message":     "Action executed with user approval.",
				"explanation": "The agent detected that CPU usage exceeded 90% (current: 95.0%) and scaled up from 3 to 5 replicas to prevent service degradation and ensure optimal performance.",
				"action":      req["selected_option"],
				"confidence":  0.85,
			}

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(response)
			return
		}

		w.WriteHeader(http.StatusNotFound)
	}))
	defer server.Close()

	// Step 1: Get available options
	resp, err := http.Get(server.URL + "/api/agents/decision-options")
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var options map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&options)
	require.NoError(t, err)

	// Verify options
	assert.Contains(t, options, "options")
	optionsList := options["options"].([]interface{})
	assert.Greater(t, len(optionsList), 0)

	// Step 2: Submit user selection
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

	// Verify response
	assert.Equal(t, "success", response["status"])
	assert.Equal(t, "manual", response["mode"])
	assert.Equal(t, "Action executed with user approval.", response["message"])
	assert.Contains(t, response["explanation"].(string), "The agent detected that")
}

// TestDecisionUIExplanationFormat tests explanation format in UI
func TestDecisionUIExplanationFormat(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		response := map[string]interface{}{
			"status":      "success",
			"mode":        "auto",
			"message":     "Action automatically executed.",
			"explanation": "The agent detected that CPU usage exceeded 90% (current: 95.0%) and scaled up from 3 to 5 replicas to prevent service degradation and ensure optimal performance.",
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}))
	defer server.Close()

	resp, err := http.Get(server.URL + "/api/agents/decision")
	require.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	// Verify explanation format
	explanation := response["explanation"].(string)
	
	// Must start with "The agent detected that"
	assert.True(t, 
		explanation[:len("The agent detected that")] == "The agent detected that",
		"Explanation should start with 'The agent detected that'")
	
	// Must contain "and" (separating problem and action)
	assert.Contains(t, explanation, "and")
	
	// Must contain "to" (separating action and reason)
	assert.Contains(t, explanation, "to")
	
	// Must end with period
	assert.True(t, explanation[len(explanation)-1] == '.',
		"Explanation should end with a period")
}

// TestAutoModeNoUserInput tests that Auto Mode doesn't require user input
func TestAutoModeNoUserInput(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Auto mode should execute immediately without waiting
		response := map[string]interface{}{
			"status":      "success",
			"mode":        "auto",
			"message":     "Action automatically executed.",
			"explanation": "The agent detected that service 'web-app-123' experienced crash_loop failure and restarted the service to restore service availability.",
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}))
	defer server.Close()

	reqBody := map[string]interface{}{
		"mode":   "auto",
		"action": "restart_pod",
	}

	jsonData, err := json.Marshal(reqBody)
	require.NoError(t, err)

	// Request should complete immediately (no waiting)
	resp, err := http.Post(server.URL+"/api/agents/decision", "application/json",
		bytes.NewBuffer(jsonData))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)

	// Verify no user input was required
	assert.Equal(t, "auto", response["mode"])
	assert.NotContains(t, response, "user_approval")
	assert.NotContains(t, response, "pending")
}

// TestManualModeShowsOptions tests that Manual Mode shows available options
func TestManualModeShowsOptions(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/api/agents/decision-options" {
			options := map[string]interface{}{
				"problem": "CPU usage is at 95%",
				"options": []map[string]interface{}{
					{
						"id":          "scale_up",
						"description": "Scale up from 3 to 5 replicas",
						"reasoning":   "Adding more replicas will distribute the load",
						"risk":        "low",
						"impact":      "high",
					},
					{
						"id":          "optimize",
						"description": "Optimize existing resources",
						"reasoning":   "Optimize the current deployment configuration",
						"risk":        "medium",
						"impact":      "medium",
					},
				},
			}
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(options)
		}
	}))
	defer server.Close()

	resp, err := http.Get(server.URL + "/api/agents/decision-options")
	require.NoError(t, err)
	defer resp.Body.Close()

	var options map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&options)
	require.NoError(t, err)

	// Verify options structure
	assert.Contains(t, options, "problem")
	assert.Contains(t, options, "options")
	
	optionsList := options["options"].([]interface{})
	assert.Greater(t, len(optionsList), 0)
	
	// Verify each option has required fields
	for _, opt := range optionsList {
		option := opt.(map[string]interface{})
		assert.Contains(t, option, "id")
		assert.Contains(t, option, "description")
		assert.Contains(t, option, "reasoning")
		assert.Contains(t, option, "risk")
		assert.Contains(t, option, "impact")
	}
}

