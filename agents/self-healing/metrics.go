package selfhealing

import (
	"time"

	"github.com/ai-driven-self-healing-cloud/config/monitoring"
)

var metrics *monitoring.MetricsRegistry

func init() {
	metrics = monitoring.GetMetricsRegistry()
}

// recordHealAction records a healing action
func recordHealAction(success bool, duration time.Duration) {
	metrics.HealActionsTotal.Inc()
	
	if success {
		// Update success rate (simplified - in production, calculate from counters)
		metrics.HealSuccessRate.Set(calculateSuccessRate())
	} else {
		metrics.HealFailuresTotal.Inc()
		metrics.HealSuccessRate.Set(calculateSuccessRate())
	}
	
	metrics.HealDurationSeconds.Observe(duration.Seconds())
	metrics.RecordAgentRequest("self-healing-agent", getStatus(success))
}

// calculateSuccessRate calculates success rate from counters
func calculateSuccessRate() float64 {
	// In production, this would query Prometheus or maintain state
	// For now, return a default value
	// This should be calculated as: heal_actions_total - heal_failures_total / heal_actions_total
	return 0.95 // Placeholder
}

// getStatus returns status string
func getStatus(success bool) string {
	if success {
		return "success"
	}
	return "failure"
}

// updateAgentUptime updates agent uptime metric
func updateAgentUptime(startTime time.Time) {
	uptime := time.Since(startTime)
	metrics.SetAgentUptime("self-healing-agent", uptime)
}

