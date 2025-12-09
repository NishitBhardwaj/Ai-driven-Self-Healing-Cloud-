package agents

import (
	"testing"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/self-healing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestSelfHealingAgentHealthCheck verifies that the health check endpoint works
func TestSelfHealingAgentHealthCheck(t *testing.T) {
	agent := selfhealing.NewSelfHealingAgent()
	
	// Initialize agent
	err := agent.Init()
	require.NoError(t, err)
	
	// Start agent
	err = agent.Start()
	require.NoError(t, err)
	
	// Check health
	health := agent.HealthCheck()
	
	// Verify health status
	assert.True(t, health.Healthy, "Agent should be healthy when running")
	assert.Equal(t, string(core.StatusRunning), health.Status, "Status should be 'running'")
	assert.NotZero(t, health.Timestamp, "Timestamp should be set")
}

// TestSelfHealingAgentHealthCheckStopped verifies health check when agent is stopped
func TestSelfHealingAgentHealthCheckStopped(t *testing.T) {
	agent := selfhealing.NewSelfHealingAgent()
	
	// Stop agent
	err := agent.Stop()
	require.NoError(t, err)
	
	// Check health
	health := agent.HealthCheck()
	
	// Verify health status
	assert.False(t, health.Healthy, "Agent should not be healthy when stopped")
	assert.Equal(t, string(core.StatusStopped), health.Status, "Status should be 'stopped'")
}

// TestSelfHealingAction triggers self-healing action on failure
func TestSelfHealingAction(t *testing.T) {
	agent := selfhealing.NewSelfHealingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Simulate a failure scenario
	healingRequest := &selfhealing.HealingRequest{
		ServiceID:   "web-app-123",
		FailureType: "crash_loop",
		Error:       "Pod restarting repeatedly",
		Metadata:    map[string]interface{}{"pod_name": "web-app-123"},
	}
	
	// Perform healing action
	result, err := agent.Healer.Heal(healingRequest)
	require.NoError(t, err, "Healing action should succeed")
	
	// Verify result
	assert.NotNil(t, result, "Result should not be nil")
	assert.Equal(t, "web-app-123", result.ServiceID, "Service ID should match")
	assert.True(t, result.Success, "Healing action should be successful")
	assert.NotEmpty(t, result.Action, "Action should be specified")
	assert.NotEmpty(t, result.Reasoning, "Reasoning should be provided")
}

// TestSelfHealingAgentRestartService simulates failure and ensures agent restarts service
func TestSelfHealingAgentRestartService(t *testing.T) {
	agent := selfhealing.NewSelfHealingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Simulate service crash
	healingRequest := &selfhealing.HealingRequest{
		ServiceID:   "api-service-456",
		FailureType: "service_crash",
		Error:       "Service crashed unexpectedly",
		Metadata: map[string]interface{}{
			"service_name": "api-service",
			"restart_count": 3,
		},
	}
	
	// Perform healing
	result, err := agent.Healer.Heal(healingRequest)
	require.NoError(t, err)
	
	// Verify that restart action was taken
	assert.True(t, result.Success, "Healing should succeed")
	assert.Contains(t, result.Action, "restart", "Action should involve restarting")
	
	// Verify explanation is generated
	explanation := agent.ExplainAction(healingRequest, result)
	assert.NotEmpty(t, explanation, "Explanation should be provided")
	assert.Contains(t, explanation, "The agent detected that", "Explanation should follow standard format")
}

// TestSelfHealingAgentErrorHandling tests error handling
func TestSelfHealingAgentErrorHandling(t *testing.T) {
	agent := selfhealing.NewSelfHealingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	// Test with invalid request
	invalidRequest := &selfhealing.HealingRequest{
		ServiceID:   "",
		FailureType: "",
		Error:       "",
	}
	
	// Should handle gracefully
	result, err := agent.Healer.Heal(invalidRequest)
	// Even with invalid input, should return a result (may use fallback strategy)
	assert.NotNil(t, result, "Should return a result even with invalid input")
}

// TestSelfHealingAgentInit tests agent initialization
func TestSelfHealingAgentInit(t *testing.T) {
	agent := selfhealing.NewSelfHealingAgent()
	
	// Verify initial state
	assert.NotNil(t, agent, "Agent should be created")
	assert.Equal(t, "Self-Healing Agent", agent.GetName(), "Agent name should be correct")
	assert.Equal(t, "self-healing-agent", agent.GetID(), "Agent ID should be correct")
	
	// Initialize
	err := agent.Init()
	require.NoError(t, err, "Initialization should succeed")
}

// TestSelfHealingAgentStartStop tests agent start and stop
func TestSelfHealingAgentStartStop(t *testing.T) {
	agent := selfhealing.NewSelfHealingAgent()
	
	// Start agent
	err := agent.Start()
	require.NoError(t, err)
	
	// Verify status
	assert.Equal(t, core.StatusRunning, agent.Status, "Status should be running")
	assert.False(t, agent.StartedAt.IsZero(), "StartedAt should be set")
	
	// Stop agent
	err = agent.Stop()
	require.NoError(t, err)
	
	// Verify status
	assert.Equal(t, core.StatusStopped, agent.Status, "Status should be stopped")
	assert.False(t, agent.StoppedAt.IsZero(), "StoppedAt should be set")
}

// TestSelfHealingAgentExplainAction tests explanation generation
func TestSelfHealingAgentExplainAction(t *testing.T) {
	agent := selfhealing.NewSelfHealingAgent()
	
	input := map[string]interface{}{
		"service_id":   "test-service",
		"failure_type": "crash_loop",
		"error":        "Pod restarting",
	}
	
	output := map[string]interface{}{
		"action":  "restart_pod",
		"success": true,
	}
	
	explanation := agent.ExplainAction(input, output)
	
	// Verify explanation format
	assert.NotEmpty(t, explanation, "Explanation should not be empty")
	assert.Contains(t, explanation, "The agent detected that", "Should follow standard format")
}

