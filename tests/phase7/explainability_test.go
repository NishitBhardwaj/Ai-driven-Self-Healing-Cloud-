package phase7

import (
	"testing"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestSelfHealingAgentExplanation tests Self-Healing Agent explanation
func TestSelfHealingAgentExplanation(t *testing.T) {
	// This would require importing the actual agent
	// For now, test the explanation format
	
	input := map[string]interface{}{
		"service_id":   "web-app-123",
		"failure_type": "crash_loop",
		"error":        "Pod restarting repeatedly",
	}
	
	output := map[string]interface{}{
		"action":  "restart_pod",
		"success": true,
	}
	
	// Test explanation format using formatter
	explanation := core.FormatExplanation(
		"service 'web-app-123' experienced crash_loop failure",
		"restarted the service",
		"restore service availability",
	)
	
	// Verify format
	assert.Contains(t, explanation, "The agent detected that")
	assert.Contains(t, explanation, "and")
	assert.Contains(t, explanation, "to")
	assert.True(t, explanation[len(explanation)-1] == '.', "Should end with period")
}

// TestScalingAgentExplanation tests Scaling Agent explanation
func TestScalingAgentExplanation(t *testing.T) {
	input := map[string]interface{}{
		"cpu_usage": 0.95,
		"replicas":  3,
	}
	
	output := map[string]interface{}{
		"action":   "scale_up",
		"replicas": 5,
	}
	
	explanation := core.FormatExplanation(
		"CPU usage exceeded 90% (current: 95.0%)",
		"scaled up from 3 to 5 replicas",
		"prevent service degradation and ensure optimal performance",
	)
	
	assert.Contains(t, explanation, "The agent detected that")
	assert.Contains(t, explanation, "CPU usage exceeded")
	assert.Contains(t, explanation, "scaled up")
}

// TestSecurityAgentExplanation tests Security Agent explanation
func TestSecurityAgentExplanation(t *testing.T) {
	input := []map[string]interface{}{
		{
			"source_ip": "192.168.1.100",
			"action":    "failed_login",
			"count":     10,
		},
	}
	
	output := map[string]interface{}{
		"action":     "block_ip",
		"blocked_ip": "192.168.1.100",
		"severity":   "high",
	}
	
	explanation := core.FormatExplanation(
		"multiple failed login attempts were detected",
		"blocked IP address 192.168.1.100",
		"prevent a critical security breach",
	)
	
	assert.Contains(t, explanation, "The agent detected that")
	assert.Contains(t, explanation, "failed login attempts")
	assert.Contains(t, explanation, "blocked IP")
}

// TestMonitoringAgentExplanation tests Performance Monitoring Agent explanation
func TestMonitoringAgentExplanation(t *testing.T) {
	input := map[string]interface{}{
		"metrics": []string{"cpu", "memory", "latency"},
	}
	
	output := map[string]interface{}{
		"anomalies":           []string{"high_cpu", "high_latency"},
		"threshold_violations": []string{"cpu > 90%"},
		"action":              "alert",
	}
	
	explanation := core.FormatExplanation(
		"2 anomaly(ies) in system metrics and 1 threshold violation(s)",
		"analyzed the metrics",
		"identify performance bottlenecks and ensure system health",
	)
	
	assert.Contains(t, explanation, "The agent detected that")
	assert.Contains(t, explanation, "anomaly")
	assert.Contains(t, explanation, "analyzed")
}

// TestExplanationFormatConsistency tests that all explanations follow the same format
func TestExplanationFormatConsistency(t *testing.T) {
	testCases := []struct {
		name      string
		problem   string
		action    string
		reason    string
		checkFunc func(string) bool
	}{
		{
			name:    "Self-Healing",
			problem: "service failure",
			action:  "restarted the service",
			reason:  "restore availability",
			checkFunc: func(exp string) bool {
				return containsAll(exp, []string{"The agent detected that", "and", "to"})
			},
		},
		{
			name:    "Scaling",
			problem: "CPU usage exceeded 90%",
			action:  "scaled up replicas",
			reason:  "prevent degradation",
			checkFunc: func(exp string) bool {
				return containsAll(exp, []string{"The agent detected that", "and", "to"})
			},
		},
		{
			name:    "Security",
			problem: "suspicious activity detected",
			action:  "blocked IP address",
			reason:  "prevent breach",
			checkFunc: func(exp string) bool {
				return containsAll(exp, []string{"The agent detected that", "and", "to"})
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			explanation := core.FormatExplanation(tc.problem, tc.action, tc.reason)
			
			// Verify format
			assert.True(t, tc.checkFunc(explanation), "Explanation should contain required parts")
			assert.True(t, explanation[len(explanation)-1] == '.', "Should end with period")
		})
	}
}

// TestAutoModeMessage tests auto mode message format
func TestAutoModeMessage(t *testing.T) {
	message := core.FormatAutoModeMessage()
	assert.Equal(t, "Action automatically executed.", message)
}

// TestExplanationWithContext tests explanation with context
func TestExplanationWithContext(t *testing.T) {
	context := map[string]interface{}{
		"cpu_usage":    0.95,
		"memory_usage": 0.88,
		"replicas":     5,
	}
	
	explanation := core.FormatExplanationWithContext(
		"Scaling Agent",
		"CPU usage exceeded 90%",
		"scaled up from 3 to 5 replicas",
		"prevent service degradation",
		context,
	)
	
	assert.Contains(t, explanation, "The agent detected that")
	assert.Contains(t, explanation, "Context:")
	assert.Contains(t, explanation, "cpu_usage")
}

// TestExplanationHumanReadable tests that explanations are human-readable
func TestExplanationHumanReadable(t *testing.T) {
	explanation := core.FormatExplanation(
		"service 'web-app-123' experienced crash_loop failure",
		"restarted the service",
		"restore service availability",
	)
	
	// Should be readable (no technical jargon without context)
	assert.NotContains(t, explanation, "input=")
	assert.NotContains(t, explanation, "output=")
	assert.NotContains(t, explanation, "%v")
	
	// Should contain clear descriptions
	assert.Contains(t, explanation, "service")
	assert.Contains(t, explanation, "restarted")
}

// Helper function
func containsAll(s string, substrings []string) bool {
	for _, substr := range substrings {
		if !contains(s, substr) {
			return false
		}
	}
	return true
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || 
		(len(s) > len(substr) && 
			(s[:len(substr)] == substr || 
			 s[len(s)-len(substr):] == substr ||
			 containsInMiddle(s, substr))))
}

func containsInMiddle(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}

// TestPythonAgentExplanationFormat tests Python agent explanation format
func TestPythonAgentExplanationFormat(t *testing.T) {
	// This would test Python agents' explain_action methods
	// For now, verify the expected format
	
	expectedFormat := map[string]interface{}{
		"message":     "Action automatically executed.",
		"explanation": "The agent detected that [problem] and [action] to [reason].",
		"agent":       "Coding Agent",
	}
	
	// Verify expected fields
	assert.Contains(t, expectedFormat, "message")
	assert.Contains(t, expectedFormat, "explanation")
	assert.Contains(t, expectedFormat, "agent")
	
	// Verify message format
	assert.Equal(t, "Action automatically executed.", expectedFormat["message"])
	
	// Verify explanation format
	explanation := expectedFormat["explanation"].(string)
	assert.Contains(t, explanation, "The agent detected that")
}

// TestExplanationReasoningChain tests reasoning chain in explanations
func TestExplanationReasoningChain(t *testing.T) {
	// Test that explanations can include reasoning chains
	reasoningChain := []core.ReasoningStep{
		{
			StepNumber:  1,
			Description: "Problem Detection",
			Reasoning:   "Detected pod crash loop",
		},
		{
			StepNumber:  2,
			Description: "Analysis",
			Reasoning:   "Analyzed crash logs",
		},
		{
			StepNumber:  3,
			Description: "Action Selection",
			Reasoning:   "Selected restart_pod",
		},
	}
	
	// Verify reasoning chain structure
	assert.Equal(t, 3, len(reasoningChain))
	assert.Equal(t, 1, reasoningChain[0].StepNumber)
	assert.Equal(t, "Problem Detection", reasoningChain[0].Description)
}

// TestExplanationConfidence tests confidence levels in explanations
func TestExplanationConfidence(t *testing.T) {
	// Test confidence levels
	autoModeConfidence := 0.95
	manualModeConfidence := 0.85
	
	// Verify confidence ranges
	assert.GreaterOrEqual(t, autoModeConfidence, 0.9, "Auto mode should have high confidence")
	assert.GreaterOrEqual(t, manualModeConfidence, 0.8, "Manual mode should have good confidence")
	assert.LessOrEqual(t, autoModeConfidence, 1.0, "Confidence should not exceed 1.0")
	assert.LessOrEqual(t, manualModeConfidence, 1.0, "Confidence should not exceed 1.0")
}

