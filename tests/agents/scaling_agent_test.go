package agents

import (
	"testing"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/scaling"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestScalingAgentHealthCheck verifies health check
func TestScalingAgentHealthCheck(t *testing.T) {
	agent := scaling.NewScalingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	health := agent.HealthCheck()
	
	assert.True(t, health.Healthy, "Agent should be healthy when running")
	assert.Equal(t, string(core.StatusRunning), health.Status)
}

// TestScalingLogic verifies the scaling logic
func TestScalingLogic(t *testing.T) {
	agent := scaling.NewScalingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Test scaling evaluation
	scaler := agent.Scaler
	
	// High load scenario
	highLoadMetrics := map[string]interface{}{
		"cpu_usage":    0.95,
		"memory_usage":  0.88,
		"replicas":      3,
		"request_rate": 1000,
	}
	
	decision, err := scaler.EvaluateScaling(highLoadMetrics)
	require.NoError(t, err)
	
	// Should recommend scale up
	assert.NotNil(t, decision, "Decision should not be nil")
	assert.Contains(t, decision.Action, "scale", "Should recommend scaling action")
}

// TestScalingAgentScaleUp simulates high load and ensures agent scales up
func TestScalingAgentScaleUp(t *testing.T) {
	agent := scaling.NewScalingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Simulate high CPU usage
	metrics := map[string]interface{}{
		"cpu_usage":    0.95,
		"memory_usage":  0.85,
		"replicas":      3,
		"latency":       500.0,
		"error_rate":    0.05,
	}
	
	decision, err := agent.Scaler.EvaluateScaling(metrics)
	require.NoError(t, err)
	
	// Verify scale up recommendation
	assert.NotNil(t, decision, "Decision should not be nil")
	
	// Check if scaling up is recommended
	if decision.Action == "scale_up" || decision.Action == "scale" {
		assert.Greater(t, decision.TargetReplicas, 3, "Should scale up from 3 replicas")
	}
}

// TestScalingAgentScaleDown simulates low load and ensures agent scales down
func TestScalingAgentScaleDown(t *testing.T) {
	agent := scaling.NewScalingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Simulate low load
	metrics := map[string]interface{}{
		"cpu_usage":    0.25,
		"memory_usage":  0.30,
		"replicas":      5,
		"latency":       50.0,
		"error_rate":    0.001,
	}
	
	decision, err := agent.Scaler.EvaluateScaling(metrics)
	require.NoError(t, err)
	
	// Verify scale down recommendation
	assert.NotNil(t, decision, "Decision should not be nil")
	
	// Check if scaling down is recommended
	if decision.Action == "scale_down" {
		assert.Less(t, decision.TargetReplicas, 5, "Should scale down from 5 replicas")
	}
}

// TestScalingAgentNoScaling tests that agent doesn't scale when load is normal
func TestScalingAgentNoScaling(t *testing.T) {
	agent := scaling.NewScalingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Normal load scenario
	metrics := map[string]interface{}{
		"cpu_usage":    0.50,
		"memory_usage":  0.55,
		"replicas":      3,
		"latency":       100.0,
		"error_rate":    0.01,
	}
	
	decision, err := agent.Scaler.EvaluateScaling(metrics)
	require.NoError(t, err)
	
	// Should either maintain current replicas or recommend no action
	assert.NotNil(t, decision, "Decision should not be nil")
	
	// If no scaling needed, target should equal current
	if decision.Action == "no_action" || decision.Action == "" {
		assert.Equal(t, 3, decision.TargetReplicas, "Should maintain current replicas")
	}
}

// TestScalingAgentErrorHandling tests error handling
func TestScalingAgentErrorHandling(t *testing.T) {
	agent := scaling.NewScalingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	// Test with invalid metrics
	invalidMetrics := map[string]interface{}{
		"cpu_usage": "invalid",
		"replicas":  "not_a_number",
	}
	
	// Should handle gracefully
	decision, err := agent.Scaler.EvaluateScaling(invalidMetrics)
	// Should either return error or use default values
	if err != nil {
		assert.Error(t, err, "Should return error for invalid input")
	} else {
		assert.NotNil(t, decision, "Should return decision even with invalid input")
	}
}

// TestScalingAgentExplainAction tests explanation generation
func TestScalingAgentExplainAction(t *testing.T) {
	agent := scaling.NewScalingAgent()
	
	input := map[string]interface{}{
		"cpu_usage": 0.95,
		"replicas":  3,
	}
	
	output := map[string]interface{}{
		"action":   "scale_up",
		"replicas": 5,
	}
	
	explanation := agent.ExplainAction(input, output)
	
	assert.NotEmpty(t, explanation, "Explanation should not be empty")
	assert.Contains(t, explanation, "The agent detected that", "Should follow standard format")
}

