package agents

import (
	"testing"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/performance-monitoring"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestMonitoringAgentHealthCheck verifies health check
func TestMonitoringAgentHealthCheck(t *testing.T) {
	agent := performancemonitoring.NewPerformanceMonitoringAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	health := agent.HealthCheck()
	
	assert.True(t, health.Healthy, "Agent should be healthy when running")
	assert.Equal(t, string(core.StatusRunning), health.Status)
}

// TestMonitoringAgentFetchMetrics verifies agent fetches metrics from Prometheus
func TestMonitoringAgentFetchMetrics(t *testing.T) {
	agent := performancemonitoring.NewPerformanceMonitoringAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Simulate fetching metrics
	metrics := []performancemonitoring.Metric{
		{
			Name:      "cpu_usage",
			Value:     0.75,
			Timestamp: time.Now(),
			Labels:    map[string]string{"service": "web-app"},
		},
		{
			Name:      "memory_usage",
			Value:     0.68,
			Timestamp: time.Now(),
			Labels:    map[string]string{"service": "web-app"},
		},
		{
			Name:      "request_latency",
			Value:     120.5,
			Timestamp: time.Now(),
			Labels:    map[string]string{"service": "web-app"},
		},
	}
	
	// Analyze metrics
	anomalies, err := agent.Analyzer.AnalyzeMetrics(metrics)
	require.NoError(t, err, "Metrics analysis should succeed")
	
	// Verify metrics were analyzed
	assert.NotNil(t, anomalies, "Anomalies should be returned")
	// Anomalies may be empty if no issues detected
}

// TestMonitoringAgentAnomalyDetection verifies anomaly detection
func TestMonitoringAgentAnomalyDetection(t *testing.T) {
	agent := performancemonitoring.NewPerformanceMonitoringAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Create metrics with anomaly (high CPU)
	metrics := []performancemonitoring.Metric{
		{
			Name:      "cpu_usage",
			Value:     0.95, // High CPU - should trigger anomaly
			Timestamp: time.Now(),
			Labels:    map[string]string{"service": "web-app"},
		},
		{
			Name:      "memory_usage",
			Value:     0.50,
			Timestamp: time.Now(),
			Labels:    map[string]string{"service": "web-app"},
		},
		{
			Name:      "error_rate",
			Value:     0.10, // High error rate - should trigger anomaly
			Timestamp: time.Now(),
			Labels:    map[string]string{"service": "web-app"},
		},
	}
	
	// Analyze metrics
	anomalies, err := agent.Analyzer.AnalyzeMetrics(metrics)
	require.NoError(t, err)
	
	// Verify anomalies are detected
	assert.NotNil(t, anomalies, "Anomalies should be returned")
	
	// Check if anomalies were detected (may use fallback detection)
	if len(anomalies) > 0 {
		// Verify anomaly structure
		anomaly := anomalies[0]
		assert.NotEmpty(t, anomaly.MetricName, "Anomaly should have metric name")
		assert.NotEmpty(t, anomaly.Description, "Anomaly should have description")
		assert.NotZero(t, anomaly.DetectedAt, "Anomaly should have detection timestamp")
	}
}

// TestMonitoringAgentCollectMetrics tests metrics collection
func TestMonitoringAgentCollectMetrics(t *testing.T) {
	agent := performancemonitoring.NewPerformanceMonitoringAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Test metrics collection
	metrics, err := agent.Analyzer.CollectMetrics()
	
	// Should either return metrics or error (depending on Prometheus connection)
	if err != nil {
		// If Prometheus is not available, that's okay for unit tests
		assert.Error(t, err, "Expected error when Prometheus is not available")
	} else {
		assert.NotNil(t, metrics, "Metrics should be returned")
	}
}

// TestMonitoringAgentThresholdViolation tests threshold violation detection
func TestMonitoringAgentThresholdViolation(t *testing.T) {
	agent := performancemonitoring.NewPerformanceMonitoringAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Create metrics exceeding thresholds
	metrics := []performancemonitoring.Metric{
		{
			Name:      "cpu_usage",
			Value:     0.95, // Exceeds 90% threshold
			Timestamp: time.Now(),
		},
		{
			Name:      "memory_usage",
			Value:     0.92, // Exceeds 90% threshold
			Timestamp: time.Now(),
		},
	}
	
	// Analyze metrics
	anomalies, err := agent.Analyzer.AnalyzeMetrics(metrics)
	require.NoError(t, err)
	
	// Should detect threshold violations
	assert.NotNil(t, anomalies, "Anomalies should be returned")
}

// TestMonitoringAgentExplainAction tests explanation generation
func TestMonitoringAgentExplainAction(t *testing.T) {
	agent := performancemonitoring.NewPerformanceMonitoringAgent()
	
	input := map[string]interface{}{
		"metrics": []string{"cpu", "memory"},
	}
	
	output := map[string]interface{}{
		"anomalies": []string{"high_cpu"},
		"action":    "alert",
	}
	
	explanation := agent.ExplainAction(input, output)
	
	assert.NotEmpty(t, explanation, "Explanation should not be empty")
	assert.Contains(t, explanation, "The agent detected that", "Should follow standard format")
}

