package monitoring

import (
	"net/http"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// MetricsRegistry holds all Prometheus metrics
type MetricsRegistry struct {
	// Common metrics
	AgentRequestsTotal   *prometheus.CounterVec
	AgentErrorsTotal     *prometheus.CounterVec
	AgentLatencySeconds  *prometheus.HistogramVec
	AgentUptimeSeconds   *prometheus.GaugeVec
	AgentActiveTasks     *prometheus.GaugeVec

	// Self-Healing Agent metrics
	HealSuccessRate      prometheus.Gauge
	HealFailuresTotal    prometheus.Counter
	HealActionsTotal     prometheus.Counter
	HealDurationSeconds  prometheus.Histogram

	// Scaling Agent metrics
	ScalingActionsTotal  *prometheus.CounterVec
	CurrentReplicas      *prometheus.GaugeVec
	ScalingDurationSeconds prometheus.Histogram

	// Task-Solving Agent metrics
	TasksCompletedTotal  prometheus.Counter
	TaskFailuresTotal    prometheus.Counter
	TasksInProgress      prometheus.Gauge
	TaskDurationSeconds  prometheus.Histogram

	// Security Agent metrics
	IntrusionAlertsTotal *prometheus.CounterVec
	BlockedAttacksTotal  prometheus.Counter
	SecurityScansTotal   prometheus.Counter

	// Performance Monitoring Agent metrics
	AnomaliesDetectedTotal prometheus.Counter
	CPUUsagePercent        *prometheus.GaugeVec
	MemoryUsagePercent     *prometheus.GaugeVec
	NetworkLatencySeconds  prometheus.Histogram

	// Coding Agent metrics
	CodeFixesTotal        prometheus.Counter
	CodeGenerationsTotal   prometheus.Counter
	CodeFixDurationSeconds prometheus.Histogram

	// Optimization Agent metrics
	OptimizationRunsTotal prometheus.Counter
	CostSavingsTotal      prometheus.Gauge
	ResourceOptimizationsTotal prometheus.Counter
}

var globalRegistry *MetricsRegistry

// GetMetricsRegistry returns the global metrics registry
func GetMetricsRegistry() *MetricsRegistry {
	if globalRegistry == nil {
		globalRegistry = NewMetricsRegistry()
	}
	return globalRegistry
}

// NewMetricsRegistry creates a new metrics registry
func NewMetricsRegistry() *MetricsRegistry {
	reg := &MetricsRegistry{
		// Common metrics
		AgentRequestsTotal: prometheus.NewCounterVec(
			prometheus.CounterOpts{
				Name: "agent_requests_total",
				Help: "Total number of requests processed by agents",
			},
			[]string{"agent", "status"},
		),
		AgentErrorsTotal: prometheus.NewCounterVec(
			prometheus.CounterOpts{
				Name: "agent_errors_total",
				Help: "Total number of errors encountered by agents",
			},
			[]string{"agent", "error_type"},
		),
		AgentLatencySeconds: prometheus.NewHistogramVec(
			prometheus.HistogramOpts{
				Name:    "agent_latency_seconds",
				Help:    "Request latency in seconds",
				Buckets: prometheus.DefBuckets,
			},
			[]string{"agent"},
		),
		AgentUptimeSeconds: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "agent_uptime_seconds",
				Help: "Agent uptime in seconds",
			},
			[]string{"agent"},
		),
		AgentActiveTasks: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "agent_active_tasks",
				Help: "Number of active tasks per agent",
			},
			[]string{"agent"},
		),

		// Self-Healing Agent metrics
		HealSuccessRate: prometheus.NewGauge(
			prometheus.GaugeOpts{
				Name: "heal_success_rate",
				Help: "Success rate of healing actions (0.0 to 1.0)",
			},
		),
		HealFailuresTotal: prometheus.NewCounter(
			prometheus.CounterOpts{
				Name: "heal_failures_total",
				Help: "Total number of failed healing actions",
			},
		),
		HealActionsTotal: prometheus.NewCounter(
			prometheus.CounterOpts{
				Name: "heal_actions_total",
				Help: "Total number of healing actions performed",
			},
		),
		HealDurationSeconds: prometheus.NewHistogram(
			prometheus.HistogramOpts{
				Name:    "heal_duration_seconds",
				Help:    "Duration of healing actions in seconds",
				Buckets: []float64{0.1, 0.5, 1.0, 2.0, 5.0, 10.0},
			},
		),

		// Scaling Agent metrics
		ScalingActionsTotal: prometheus.NewCounterVec(
			prometheus.CounterOpts{
				Name: "scaling_actions_total",
				Help: "Total number of scaling actions",
			},
			[]string{"direction", "service"},
		),
		CurrentReplicas: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "current_replicas",
				Help: "Current number of replicas",
			},
			[]string{"service"},
		),
		ScalingDurationSeconds: prometheus.NewHistogram(
			prometheus.HistogramOpts{
				Name:    "scaling_duration_seconds",
				Help:    "Duration of scaling actions in seconds",
				Buckets: []float64{1.0, 5.0, 10.0, 30.0, 60.0},
			},
		),

		// Task-Solving Agent metrics
		TasksCompletedTotal: prometheus.NewCounter(
			prometheus.CounterOpts{
				Name: "tasks_completed_total",
				Help: "Total number of completed tasks",
			},
		),
		TaskFailuresTotal: prometheus.NewCounter(
			prometheus.CounterOpts{
				Name: "task_failures_total",
				Help: "Total number of failed tasks",
			},
		),
		TasksInProgress: prometheus.NewGauge(
			prometheus.GaugeOpts{
				Name: "tasks_in_progress",
				Help: "Number of tasks currently in progress",
			},
		),
		TaskDurationSeconds: prometheus.NewHistogram(
			prometheus.HistogramOpts{
				Name:    "task_duration_seconds",
				Help:    "Duration of task processing in seconds",
				Buckets: prometheus.DefBuckets,
			},
		),

		// Security Agent metrics
		IntrusionAlertsTotal: prometheus.NewCounterVec(
			prometheus.CounterOpts{
				Name: "intrusion_alerts_total",
				Help: "Total number of intrusion alerts",
			},
			[]string{"severity", "type"},
		),
		BlockedAttacksTotal: prometheus.NewCounter(
			prometheus.CounterOpts{
				Name: "blocked_attacks_total",
				Help: "Total number of blocked attacks",
			},
		),
		SecurityScansTotal: prometheus.NewCounter(
			prometheus.CounterOpts{
				Name: "security_scans_total",
				Help: "Total number of security scans performed",
			},
		),

		// Performance Monitoring Agent metrics
		AnomaliesDetectedTotal: prometheus.NewCounter(
			prometheus.CounterOpts{
				Name: "anomalies_detected_total",
				Help: "Total number of anomalies detected",
			},
		),
		CPUUsagePercent: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "cpu_usage_percent",
				Help: "CPU usage percentage",
			},
			[]string{"service", "node"},
		),
		MemoryUsagePercent: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "memory_usage_percent",
				Help: "Memory usage percentage",
			},
			[]string{"service", "node"},
		),
		NetworkLatencySeconds: prometheus.NewHistogram(
			prometheus.HistogramOpts{
				Name:    "network_latency_seconds",
				Help:    "Network latency in seconds",
				Buckets: []float64{0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0},
			},
		),

		// Coding Agent metrics
		CodeFixesTotal: prometheus.NewCounter(
			prometheus.CounterOpts{
				Name: "code_fixes_total",
				Help: "Total number of code fixes performed",
			},
		),
		CodeGenerationsTotal: prometheus.NewCounter(
			prometheus.CounterOpts{
				Name: "code_generations_total",
				Help: "Total number of code generations performed",
			},
		),
		CodeFixDurationSeconds: prometheus.NewHistogram(
			prometheus.HistogramOpts{
				Name:    "code_fix_duration_seconds",
				Help:    "Duration of code fixes in seconds",
				Buckets: []float64{1.0, 5.0, 10.0, 30.0, 60.0},
			},
		),

		// Optimization Agent metrics
		OptimizationRunsTotal: prometheus.NewCounter(
			prometheus.CounterOpts{
				Name: "optimization_runs_total",
				Help: "Total number of optimization runs",
			},
		),
		CostSavingsTotal: prometheus.NewGauge(
			prometheus.GaugeOpts{
				Name: "cost_savings_total",
				Help: "Total cost savings in dollars",
			},
		),
		ResourceOptimizationsTotal: prometheus.NewCounter(
			prometheus.CounterOpts{
				Name: "resource_optimizations_total",
				Help: "Total number of resource optimizations",
			},
		),
	}

	// Register all metrics
	prometheus.MustRegister(
		reg.AgentRequestsTotal,
		reg.AgentErrorsTotal,
		reg.AgentLatencySeconds,
		reg.AgentUptimeSeconds,
		reg.AgentActiveTasks,
		reg.HealSuccessRate,
		reg.HealFailuresTotal,
		reg.HealActionsTotal,
		reg.HealDurationSeconds,
		reg.ScalingActionsTotal,
		reg.CurrentReplicas,
		reg.ScalingDurationSeconds,
		reg.TasksCompletedTotal,
		reg.TaskFailuresTotal,
		reg.TasksInProgress,
		reg.TaskDurationSeconds,
		reg.IntrusionAlertsTotal,
		reg.BlockedAttacksTotal,
		reg.SecurityScansTotal,
		reg.AnomaliesDetectedTotal,
		reg.CPUUsagePercent,
		reg.MemoryUsagePercent,
		reg.NetworkLatencySeconds,
		reg.CodeFixesTotal,
		reg.CodeGenerationsTotal,
		reg.CodeFixDurationSeconds,
		reg.OptimizationRunsTotal,
		reg.CostSavingsTotal,
		reg.ResourceOptimizationsTotal,
	)

	return reg
}

// StartMetricsServer starts the Prometheus metrics HTTP server
func StartMetricsServer(port string) error {
	http.Handle("/metrics", promhttp.Handler())
	return http.ListenAndServe(":"+port, nil)
}

// RecordAgentRequest records an agent request
func (m *MetricsRegistry) RecordAgentRequest(agent string, status string) {
	m.AgentRequestsTotal.WithLabelValues(agent, status).Inc()
}

// RecordAgentError records an agent error
func (m *MetricsRegistry) RecordAgentError(agent string, errorType string) {
	m.AgentErrorsTotal.WithLabelValues(agent, errorType).Inc()
}

// RecordAgentLatency records agent request latency
func (m *MetricsRegistry) RecordAgentLatency(agent string, duration time.Duration) {
	m.AgentLatencySeconds.WithLabelValues(agent).Observe(duration.Seconds())
}

// SetAgentUptime sets agent uptime
func (m *MetricsRegistry) SetAgentUptime(agent string, uptime time.Duration) {
	m.AgentUptimeSeconds.WithLabelValues(agent).Set(uptime.Seconds())
}

// SetAgentActiveTasks sets number of active tasks
func (m *MetricsRegistry) SetAgentActiveTasks(agent string, count float64) {
	m.AgentActiveTasks.WithLabelValues(agent).Set(count)
}

