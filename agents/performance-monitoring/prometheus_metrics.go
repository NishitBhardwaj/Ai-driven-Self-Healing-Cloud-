package performancemonitoring

import (
	"github.com/ai-driven-self-healing-cloud/config/monitoring"
)

var metrics *monitoring.MetricsRegistry

func init() {
	metrics = monitoring.GetMetricsRegistry()
}

// recordAnomalyDetected records an anomaly detection
func recordAnomalyDetected() {
	metrics.AnomaliesDetectedTotal.Inc()
	metrics.RecordAgentRequest("performance-monitoring-agent", "success")
}

// setCPUUsage sets CPU usage percentage
func setCPUUsage(service string, node string, percent float64) {
	metrics.CPUUsagePercent.WithLabelValues(service, node).Set(percent)
}

// setMemoryUsage sets memory usage percentage
func setMemoryUsage(service string, node string, percent float64) {
	metrics.MemoryUsagePercent.WithLabelValues(service, node).Set(percent)
}

// recordNetworkLatency records network latency
func recordNetworkLatency(latencySeconds float64) {
	metrics.NetworkLatencySeconds.Observe(latencySeconds)
}

