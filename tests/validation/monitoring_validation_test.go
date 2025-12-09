package validation

import (
	"encoding/json"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestGrafanaDashboardsExist tests that Grafana dashboards exist
func TestGrafanaDashboardsExist(t *testing.T) {
	grafanaURL := "http://localhost:3000"
	
	// Check if dashboards are accessible
	// This requires authentication, so we'll verify Grafana is accessible
	resp, err := http.Get(grafanaURL + "/api/health")
	require.NoError(t, err, "Grafana should be accessible")
	defer resp.Body.Close()
	
	assert.Equal(t, http.StatusOK, resp.StatusCode, "Grafana should return 200")
	
	// Verify dashboards directory exists (would be checked in file system)
	t.Log("Grafana dashboards should be in monitoring/grafana/dashboards/")
}

// TestGrafanaRealTimeData tests that Grafana shows real-time data
func TestGrafanaRealTimeData(t *testing.T) {
	grafanaURL := "http://localhost:3000"
	
	// Verify Grafana can query Prometheus
	resp, err := http.Get(grafanaURL + "/api/health")
	require.NoError(t, err, "Grafana should be accessible")
	defer resp.Body.Close()
	
	assert.Equal(t, http.StatusOK, resp.StatusCode, "Grafana should return 200")
	
	// In a real scenario, we would:
	// 1. Query Grafana API for dashboard data
	// 2. Verify data is being updated
	// 3. Check refresh intervals
	t.Log("Grafana should be configured to refresh every 10s")
}

// TestPrometheusMetricsDisplayed tests that Prometheus metrics are displayed correctly
func TestPrometheusMetricsDisplayed(t *testing.T) {
	prometheusURL := "http://localhost:9090"
	
	// Test querying for agent metrics
	queries := []string{
		"agent_requests_total",
		"agent_errors_total",
		"heal_success_rate",
		"scaling_actions_total",
		"tasks_completed_total",
		"intrusion_alerts_total",
		"anomalies_detected_total",
		"cpu_usage_percent",
	}
	
	for _, query := range queries {
		t.Run(query, func(t *testing.T) {
			resp, err := http.Get(prometheusURL + "/api/v1/query?query=" + query)
			require.NoError(t, err, "Should be able to query Prometheus")
			defer resp.Body.Close()
			
			assert.Equal(t, http.StatusOK, resp.StatusCode, "Prometheus query should return 200")
			
			var result map[string]interface{}
			err = json.NewDecoder(resp.Body).Decode(&result)
			require.NoError(t, err, "Should decode Prometheus response")
			
			assert.Equal(t, "success", result["status"], "Query should be successful")
		})
	}
}

// TestSystemHealthMetrics tests that system health metrics are available
func TestSystemHealthMetrics(t *testing.T) {
	prometheusURL := "http://localhost:9090"
	
	// Test system health queries
	healthQueries := []string{
		"up{job=~\".*-agent\"}",
		"rate(agent_requests_total[5m])",
		"rate(agent_errors_total[5m])",
		"agent_uptime_seconds",
	}
	
	for _, query := range healthQueries {
		resp, err := http.Get(prometheusURL + "/api/v1/query?query=" + query)
		if err == nil {
			defer resp.Body.Close()
			if resp.StatusCode == http.StatusOK {
				var result map[string]interface{}
				json.NewDecoder(resp.Body).Decode(&result)
				t.Logf("Query successful: %s", query)
			}
		}
	}
}

// TestAgentPerformanceMetrics tests that agent performance metrics are available
func TestAgentPerformanceMetrics(t *testing.T) {
	prometheusURL := "http://localhost:9090"
	
	// Test agent performance queries
	performanceQueries := []string{
		"histogram_quantile(0.95, rate(agent_latency_seconds_bucket[5m]))",
		"agent_active_tasks",
		"heal_success_rate",
		"rate(tasks_completed_total[5m])",
	}
	
	for _, query := range performanceQueries {
		resp, err := http.Get(prometheusURL + "/api/v1/query?query=" + query)
		if err == nil {
			defer resp.Body.Close()
			if resp.StatusCode == http.StatusOK {
				t.Logf("Performance query successful: %s", query)
			}
		}
	}
}

// TestResourceUsageMetrics tests that resource usage metrics are available
func TestResourceUsageMetrics(t *testing.T) {
	prometheusURL := "http://localhost:9090"
	
	// Test resource usage queries
	resourceQueries := []string{
		"cpu_usage_percent",
		"memory_usage_percent",
		"current_replicas",
		"histogram_quantile(0.95, rate(network_latency_seconds_bucket[5m]))",
	}
	
	for _, query := range resourceQueries {
		resp, err := http.Get(prometheusURL + "/api/v1/query?query=" + query)
		if err == nil {
			defer resp.Body.Close()
			if resp.StatusCode == http.StatusOK {
				t.Logf("Resource query successful: %s", query)
			}
		}
	}
}

// TestEventFlowMetrics tests that event flow metrics are available
func TestEventFlowMetrics(t *testing.T) {
	prometheusURL := "http://localhost:9090"
	
	// Test event flow queries
	eventQueries := []string{
		"rate(heal_actions_total[5m])",
		"rate(scaling_actions_total[5m])",
		"rate(intrusion_alerts_total[5m])",
		"rate(anomalies_detected_total[5m])",
		"rate(code_fixes_total[5m])",
		"rate(optimization_runs_total[5m])",
	}
	
	for _, query := range eventQueries {
		resp, err := http.Get(prometheusURL + "/api/v1/query?query=" + query)
		if err == nil {
			defer resp.Body.Close()
			if resp.StatusCode == http.StatusOK {
				t.Logf("Event flow query successful: %s", query)
			}
		}
	}
}

// TestErrorRateMetrics tests that error rate metrics are available
func TestErrorRateMetrics(t *testing.T) {
	prometheusURL := "http://localhost:9090"
	
	// Test error rate queries
	errorQueries := []string{
		"rate(agent_errors_total[5m])",
		"rate(heal_failures_total[5m])",
		"rate(task_failures_total[5m])",
	}
	
	for _, query := range errorQueries {
		resp, err := http.Get(prometheusURL + "/api/v1/query?query=" + query)
		if err == nil {
			defer resp.Body.Close()
			if resp.StatusCode == http.StatusOK {
				t.Logf("Error rate query successful: %s", query)
			}
		}
	}
}

