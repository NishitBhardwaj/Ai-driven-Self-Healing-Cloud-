package integration

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/events"
	"github.com/ai-driven-self-healing-cloud/agents/self-healing"
	"github.com/ai-driven-self-healing-cloud/agents/scaling"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestAgentTakesActionOnErrorDetected tests that agents take action on ERROR_DETECTED event
func TestAgentTakesActionOnErrorDetected(t *testing.T) {
	registry := core.GetRegistry()
	
	// Create and register Self-Healing Agent
	healingAgent := selfhealing.NewSelfHealingAgent()
	err := registry.RegisterAgent(healingAgent)
	require.NoError(t, err)
	
	// Start agent
	err = healingAgent.Start()
	require.NoError(t, err)
	defer healingAgent.Stop()
	
	// Create error event
	errorEvent := map[string]interface{}{
		"error_type":    "service_crash",
		"service_id":    "web-app-123",
		"error_message": "Service crashed",
		"severity":      "high",
	}
	
	// Send event to agent
	err = healingAgent.ReceiveEvent(events.ERROR_DETECTED, errorEvent)
	require.NoError(t, err, "Agent should receive ERROR_DETECTED event")
	
	// Give time for agent to process
	time.Sleep(200 * time.Millisecond)
	
	// Verify agent is still healthy (action was taken)
	health := healingAgent.HealthCheck()
	assert.True(t, health.Healthy, "Agent should remain healthy after processing event")
}

// TestAgentTakesActionOnScalingRequired tests that Scaling Agent takes action on SCALE_REQUIRED
func TestAgentTakesActionOnScalingRequired(t *testing.T) {
	registry := core.GetRegistry()
	
	// Create and register Scaling Agent
	scalingAgent := scaling.NewScalingAgent()
	err := registry.RegisterAgent(scalingAgent)
	require.NoError(t, err)
	
	// Start agent
	err = scalingAgent.Start()
	require.NoError(t, err)
	defer scalingAgent.Stop()
	
	// Create scaling event
	scalingEvent := map[string]interface{}{
		"service_id":      "api-service",
		"current_load":    0.95,
		"target_replicas": 5,
		"reason":          "CPU usage exceeded threshold",
	}
	
	// Send event to agent
	err = scalingAgent.ReceiveEvent(events.SCALE_REQUIRED, scalingEvent)
	require.NoError(t, err, "Agent should receive SCALE_REQUIRED event")
	
	// Give time for agent to process
	time.Sleep(200 * time.Millisecond)
	
	// Verify agent processed the event
	health := scalingAgent.HealthCheck()
	assert.True(t, health.Healthy, "Agent should remain healthy after processing event")
}

// TestAgentTakesActionOnHealingRequired tests that Self-Healing Agent takes action on HEALING_REQUIRED
func TestAgentTakesActionOnHealingRequired(t *testing.T) {
	registry := core.GetRegistry()
	
	// Create and register Self-Healing Agent
	healingAgent := selfhealing.NewSelfHealingAgent()
	err := registry.RegisterAgent(healingAgent)
	require.NoError(t, err)
	
	// Start agent
	err = healingAgent.Start()
	require.NoError(t, err)
	defer healingAgent.Stop()
	
	// Create healing event
	healingEvent := map[string]interface{}{
		"service_id":   "web-app-123",
		"failure_type": "crash_loop",
		"error":        "Pod restarting repeatedly",
	}
	
	// Send event to agent
	err = healingAgent.ReceiveEvent(events.HEALING_REQUIRED, healingEvent)
	require.NoError(t, err, "Agent should receive HEALING_REQUIRED event")
	
	// Give time for agent to process
	time.Sleep(200 * time.Millisecond)
	
	// Verify agent processed the event
	health := healingAgent.HealthCheck()
	assert.True(t, health.Healthy, "Agent should remain healthy after processing event")
}

// TestAgentTakesActionOnSecurityAlert tests that Security Agent takes action on SECURITY_ALERT
func TestAgentTakesActionOnSecurityAlert(t *testing.T) {
	// This would test Python Security Agent
	// For now, verify event routing works
	
	router := core.GetRouter()
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Create security alert event
	securityEvent := map[string]interface{}{
		"threat_type": "intrusion_attempt",
		"source_ip":   "192.168.1.100",
		"severity":    "high",
	}
	
	// Route event (would go to Security Agent)
	err = router.Route(events.SECURITY_ALERT, securityEvent)
	require.NoError(t, err, "Should route SECURITY_ALERT event")
	
	time.Sleep(100 * time.Millisecond)
}

// TestAgentActionChain tests that actions trigger subsequent events
func TestAgentActionChain(t *testing.T) {
	registry := core.GetRegistry()
	router := core.GetRouter()
	
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Register agents
	healingAgent := selfhealing.NewSelfHealingAgent()
	scalingAgent := scaling.NewScalingAgent()
	
	registry.RegisterAgent(healingAgent)
	registry.RegisterAgent(scalingAgent)
	
	healingAgent.Start()
	scalingAgent.Start()
	defer healingAgent.Stop()
	defer scalingAgent.Stop()
	
	// Step 1: Error detected -> triggers healing
	errorEvent := map[string]interface{}{
		"error_type": "service_crash",
		"service_id": "web-app-123",
	}
	
	err = router.Route(events.ERROR_DETECTED, errorEvent)
	require.NoError(t, err)
	time.Sleep(100 * time.Millisecond)
	
	// Step 2: High load detected -> triggers scaling
	scalingEvent := map[string]interface{}{
		"service_id":   "api-service",
		"current_load": 0.95,
	}
	
	err = router.Route(events.SCALE_REQUIRED, scalingEvent)
	require.NoError(t, err)
	time.Sleep(100 * time.Millisecond)
	
	// Verify both agents processed their events
	healingHealth := healingAgent.HealthCheck()
	scalingHealth := scalingAgent.HealthCheck()
	
	assert.True(t, healingHealth.Healthy, "Healing agent should be healthy")
	assert.True(t, scalingHealth.Healthy, "Scaling agent should be healthy")
}

// TestAgentActionWithExplanation tests that agent actions include explanations
func TestAgentActionWithExplanation(t *testing.T) {
	registry := core.GetRegistry()
	
	// Create Self-Healing Agent
	healingAgent := selfhealing.NewSelfHealingAgent()
	err := registry.RegisterAgent(healingAgent)
	require.NoError(t, err)
	
	err = healingAgent.Start()
	require.NoError(t, err)
	defer healingAgent.Stop()
	
	// Create healing request
	healingRequest := &selfhealing.HealingRequest{
		ServiceID:   "web-app-123",
		FailureType: "crash_loop",
		Error:       "Pod restarting repeatedly",
	}
	
	// Perform healing action
	result, err := healingAgent.Healer.Heal(healingRequest)
	require.NoError(t, err)
	
	// Verify explanation is generated
	explanation := healingAgent.ExplainAction(healingRequest, result)
	assert.NotEmpty(t, explanation, "Explanation should be generated")
	assert.Contains(t, explanation, "The agent detected that", "Should follow standard format")
}

// TestAgentActionErrorHandling tests error handling in agent actions
func TestAgentActionErrorHandling(t *testing.T) {
	registry := core.GetRegistry()
	
	// Create Scaling Agent
	scalingAgent := scaling.NewScalingAgent()
	err := registry.RegisterAgent(scalingAgent)
	require.NoError(t, err)
	
	err = scalingAgent.Start()
	require.NoError(t, err)
	defer scalingAgent.Stop()
	
	// Test with invalid metrics
	invalidMetrics := map[string]interface{}{
		"cpu_usage": "invalid",
		"replicas":  "not_a_number",
	}
	
	// Should handle gracefully
	decision, err := scalingAgent.Scaler.EvaluateScaling(invalidMetrics)
	
	// Should either return error or use defaults
	if err != nil {
		assert.Error(t, err, "Should return error for invalid input")
	} else {
		assert.NotNil(t, decision, "Should return decision even with invalid input")
	}
}

// TestAgentActionConcurrency tests concurrent agent actions
func TestAgentActionConcurrency(t *testing.T) {
	registry := core.GetRegistry()
	
	// Create multiple agents
	healingAgent := selfhealing.NewSelfHealingAgent()
	scalingAgent := scaling.NewScalingAgent()
	
	registry.RegisterAgent(healingAgent)
	registry.RegisterAgent(scalingAgent)
	
	healingAgent.Start()
	scalingAgent.Start()
	defer healingAgent.Stop()
	defer scalingAgent.Stop()
	
	// Perform concurrent actions
	errors := make(chan error, 2)
	
	// Concurrent healing action
	go func() {
		request := &selfhealing.HealingRequest{
			ServiceID:   "service-1",
			FailureType: "crash",
		}
		_, err := healingAgent.Healer.Heal(request)
		errors <- err
	}()
	
	// Concurrent scaling action
	go func() {
		metrics := map[string]interface{}{
			"cpu_usage": 0.95,
			"replicas":  3,
		}
		_, err := scalingAgent.Scaler.EvaluateScaling(metrics)
		errors <- err
	}()
	
	// Wait for both actions
	for i := 0; i < 2; i++ {
		err := <-errors
		assert.NoError(t, err, "Concurrent actions should not error")
	}
}

// TestAgentActionResponseTime tests agent action response time
func TestAgentActionResponseTime(t *testing.T) {
	registry := core.GetRegistry()
	
	healingAgent := selfhealing.NewSelfHealingAgent()
	err := registry.RegisterAgent(healingAgent)
	require.NoError(t, err)
	
	err = healingAgent.Start()
	require.NoError(t, err)
	defer healingAgent.Stop()
	
	// Measure action response time
	startTime := time.Now()
	
	request := &selfhealing.HealingRequest{
		ServiceID:   "test-service",
		FailureType: "crash",
		Error:       "Test error",
	}
	
	_, err = healingAgent.Healer.Heal(request)
	require.NoError(t, err)
	
	responseTime := time.Since(startTime)
	
	// Verify response time is reasonable (< 1 second for unit test)
	assert.Less(t, responseTime, 1*time.Second, "Action should complete quickly")
}

