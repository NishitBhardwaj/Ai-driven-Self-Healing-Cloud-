package integration

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/self-healing"
	"github.com/ai-driven-self-healing-cloud/agents/scaling"
	"github.com/gorilla/mux"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestRESTAPIAgentCommunication tests agent communication via REST API
func TestRESTAPIAgentCommunication(t *testing.T) {
	// Create test agents
	healingAgent := selfhealing.NewSelfHealingAgent()
	scalingAgent := scaling.NewScalingAgent()
	
	// Create router and register routes
	router := mux.NewRouter()
	
	// Register agent routes (simplified for testing)
	router.HandleFunc("/agents/self-healing/health", func(w http.ResponseWriter, r *http.Request) {
		health := healingAgent.HealthCheck()
		json.NewEncoder(w).Encode(health)
	}).Methods("GET")
	
	router.HandleFunc("/agents/scaling/health", func(w http.ResponseWriter, r *http.Request) {
		health := scalingAgent.HealthCheck()
		json.NewEncoder(w).Encode(health)
	}).Methods("GET")
	
	// Create test server
	server := httptest.NewServer(router)
	defer server.Close()
	
	// Test Self-Healing Agent health endpoint
	resp, err := http.Get(server.URL + "/agents/self-healing/health")
	require.NoError(t, err)
	defer resp.Body.Close()
	
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	
	// Test Scaling Agent health endpoint
	resp, err = http.Get(server.URL + "/agents/scaling/health")
	require.NoError(t, err)
	defer resp.Body.Close()
	
	assert.Equal(t, http.StatusOK, resp.StatusCode)
}

// TestRESTAPIAgentAction tests agent action via REST API
func TestRESTAPIAgentAction(t *testing.T) {
	healingAgent := selfhealing.NewSelfHealingAgent()
	healingAgent.Start()
	defer healingAgent.Stop()
	
	router := mux.NewRouter()
	
	// Register healing action endpoint
	router.HandleFunc("/agents/self-healing/heal", func(w http.ResponseWriter, r *http.Request) {
		var req map[string]interface{}
		json.NewDecoder(r.Body).Decode(&req)
		
		healingRequest := &selfhealing.HealingRequest{
			ServiceID:   req["service_id"].(string),
			FailureType: req["failure_type"].(string),
			Error:       req["error"].(string),
		}
		
		result, err := healingAgent.Healer.Heal(healingRequest)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		
		json.NewEncoder(w).Encode(result)
	}).Methods("POST")
	
	server := httptest.NewServer(router)
	defer server.Close()
	
	// Send healing request
	requestBody := map[string]interface{}{
		"service_id":   "web-app-123",
		"failure_type": "crash_loop",
		"error":        "Pod restarting",
	}
	
	jsonData, err := json.Marshal(requestBody)
	require.NoError(t, err)
	
	resp, err := http.Post(server.URL+"/agents/self-healing/heal", "application/json",
		bytes.NewBuffer(jsonData))
	require.NoError(t, err)
	defer resp.Body.Close()
	
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	
	// Verify response
	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	require.NoError(t, err)
	
	assert.Equal(t, "web-app-123", result["service_id"])
	assert.True(t, result["success"].(bool))
}

// TestRESTAPIAgentStatus tests agent status via REST API
func TestRESTAPIAgentStatus(t *testing.T) {
	registry := core.GetRegistry()
	
	healingAgent := selfhealing.NewSelfHealingAgent()
	registry.RegisterAgent(healingAgent)
	
	healingAgent.Start()
	defer healingAgent.Stop()
	
	router := mux.NewRouter()
	
	// Register status endpoint
	router.HandleFunc("/agents/{agent_id}/status", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		agentID := vars["agent_id"]
		
		agent, err := registry.GetAgentByName(agentID)
		if err != nil {
			http.Error(w, err.Error(), http.StatusNotFound)
			return
		}
		
		health := agent.HealthCheck()
		json.NewEncoder(w).Encode(health)
	}).Methods("GET")
	
	server := httptest.NewServer(router)
	defer server.Close()
	
	// Get agent status
	resp, err := http.Get(server.URL + "/agents/Self-Healing Agent/status")
	require.NoError(t, err)
	defer resp.Body.Close()
	
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	
	var health map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&health)
	require.NoError(t, err)
	
	assert.Contains(t, health, "healthy")
	assert.Contains(t, health, "status")
}

// TestRESTAPIAgentEvent tests sending event to agent via REST API
func TestRESTAPIAgentEvent(t *testing.T) {
	registry := core.GetRegistry()
	
	healingAgent := selfhealing.NewSelfHealingAgent()
	registry.RegisterAgent(healingAgent)
	
	healingAgent.Start()
	defer healingAgent.Stop()
	
	router := mux.NewRouter()
	
	// Register event endpoint
	router.HandleFunc("/agents/{agent_id}/event", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		agentID := vars["agent_id"]
		
		agent, err := registry.GetAgentByName(agentID)
		if err != nil {
			http.Error(w, err.Error(), http.StatusNotFound)
			return
		}
		
		var event map[string]interface{}
		json.NewDecoder(r.Body).Decode(&event)
		
		eventType := event["type"].(string)
		payload := event["payload"]
		
		err = agent.ReceiveEvent(eventType, payload)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]string{"status": "received"})
	}).Methods("POST")
	
	server := httptest.NewServer(router)
	defer server.Close()
	
	// Send event
	eventBody := map[string]interface{}{
		"type": "error.detected",
		"payload": map[string]interface{}{
			"error_type": "service_crash",
			"service_id": "web-app-123",
		},
	}
	
	jsonData, err := json.Marshal(eventBody)
	require.NoError(t, err)
	
	resp, err := http.Post(server.URL+"/agents/Self-Healing Agent/event", "application/json",
		bytes.NewBuffer(jsonData))
	require.NoError(t, err)
	defer resp.Body.Close()
	
	assert.Equal(t, http.StatusOK, resp.StatusCode)
}

// TestRESTAPIMultipleAgents tests communication with multiple agents via REST
func TestRESTAPIMultipleAgents(t *testing.T) {
	registry := core.GetRegistry()
	
	healingAgent := selfhealing.NewSelfHealingAgent()
	scalingAgent := scaling.NewScalingAgent()
	
	registry.RegisterAgent(healingAgent)
	registry.RegisterAgent(scalingAgent)
	
	healingAgent.Start()
	scalingAgent.Start()
	defer healingAgent.Stop()
	defer scalingAgent.Stop()
	
	router := mux.NewRouter()
	
	// Register multiple agent endpoints
	router.HandleFunc("/agents", func(w http.ResponseWriter, r *http.Request) {
		agents := registry.GetAllAgents()
		agentList := make([]map[string]string, 0)
		
		for name, agent := range agents {
			agentList = append(agentList, map[string]string{
				"id":   agent.GetID(),
				"name": name,
			})
		}
		
		json.NewEncoder(w).Encode(map[string]interface{}{
			"agents": agentList,
		})
	}).Methods("GET")
	
	server := httptest.NewServer(router)
	defer server.Close()
	
	// Get all agents
	resp, err := http.Get(server.URL + "/agents")
	require.NoError(t, err)
	defer resp.Body.Close()
	
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	
	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	require.NoError(t, err)
	
	agents := response["agents"].([]interface{})
	assert.Greater(t, len(agents), 0, "Should return multiple agents")
}

