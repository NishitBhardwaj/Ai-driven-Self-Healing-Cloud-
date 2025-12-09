package tasksolving

import (
	"time"

	"github.com/ai-driven-self-healing-cloud/config/monitoring"
)

var metrics *monitoring.MetricsRegistry

func init() {
	metrics = monitoring.GetMetricsRegistry()
}

// recordTaskCompleted records a completed task
func recordTaskCompleted(duration time.Duration) {
	metrics.TasksCompletedTotal.Inc()
	metrics.TaskDurationSeconds.Observe(duration.Seconds())
	metrics.RecordAgentRequest("task-solving-agent", "success")
}

// recordTaskFailure records a failed task
func recordTaskFailure() {
	metrics.TaskFailuresTotal.Inc()
	metrics.RecordAgentRequest("task-solving-agent", "failure")
}

// setTasksInProgress sets number of tasks in progress
func setTasksInProgress(count int) {
	metrics.TasksInProgress.Set(float64(count))
}

// updateAgentUptime updates agent uptime metric
func updateAgentUptime(startTime time.Time) {
	uptime := time.Since(startTime)
	metrics.SetAgentUptime("task-solving-agent", uptime)
}

