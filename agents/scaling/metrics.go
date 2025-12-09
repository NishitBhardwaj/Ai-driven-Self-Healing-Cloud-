package scaling

import (
	"time"

	"github.com/ai-driven-self-healing-cloud/config/monitoring"
)

var metrics *monitoring.MetricsRegistry

func init() {
	metrics = monitoring.GetMetricsRegistry()
}

// recordScalingAction records a scaling action
func recordScalingAction(direction string, serviceID string, duration time.Duration) {
	metrics.ScalingActionsTotal.WithLabelValues(direction, serviceID).Inc()
	metrics.ScalingDurationSeconds.Observe(duration.Seconds())
	metrics.RecordAgentRequest("scaling-agent", "success")
}

// setCurrentReplicas sets current replica count
func setCurrentReplicas(serviceID string, replicas int) {
	metrics.CurrentReplicas.WithLabelValues(serviceID).Set(float64(replicas))
}

// updateAgentUptime updates agent uptime metric
func updateAgentUptime(startTime time.Time) {
	uptime := time.Since(startTime)
	metrics.SetAgentUptime("scaling-agent", uptime)
}

