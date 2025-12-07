package performancemonitoring

import (
	"testing"

	"github.com/ai-driven-self-healing-cloud/agents/core"
)

func TestPerformanceMonitoringAgent_Start(t *testing.T) {
	agent := NewPerformanceMonitoringAgent()
	
	if agent.GetID() != "performance-monitoring-agent" {
		t.Errorf("Expected ID 'performance-monitoring-agent', got '%s'", agent.GetID())
	}

	if err := agent.Start(); err != nil {
		t.Errorf("Failed to start agent: %v", err)
	}

	if agent.Status != core.StatusRunning {
		t.Errorf("Expected status 'running', got '%s'", agent.Status)
	}

	agent.Stop()
}

func TestMetricsAnalyzer_AnalyzeMetrics(t *testing.T) {
	analyzer := NewMetricsAnalyzer()
	
	metrics := []Metric{
		{Name: "cpu_usage", Value: 95.0},
		{Name: "memory_usage", Value: 50.0},
	}

	anomalies, err := analyzer.AnalyzeMetrics(metrics)
	if err != nil {
		t.Errorf("Failed to analyze metrics: %v", err)
	}

	if len(anomalies) == 0 {
		t.Error("Expected at least one anomaly for high CPU usage")
	}
}

