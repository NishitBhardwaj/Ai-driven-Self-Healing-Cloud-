package health

import (
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
)

// SystemHealth represents the overall health of the system
type SystemHealth struct {
	OverallHealthy bool
	Components     []core.HealthCheckResult
	CheckedAt      time.Time
}

// HealthAggregator aggregates health checks from all system components
type HealthAggregator struct {
	registry *core.AgentRegistry
}

// NewHealthAggregator creates a new health aggregator
func NewHealthAggregator() *HealthAggregator {
	return &HealthAggregator{
		registry: core.GetRegistry(),
	}
}

// CheckSystemHealth performs health checks on all registered components
func (ha *HealthAggregator) CheckSystemHealth() SystemHealth {
	health := SystemHealth{
		Components: make([]core.HealthCheckResult, 0),
		CheckedAt:  time.Now(),
		OverallHealthy: true,
	}

	// Check all registered agents
	agents := ha.registry.GetAllAgents()
	for name, agent := range agents {
		status := agent.HealthCheck()
		result := core.HealthCheckResult{
			Component:    name,
			HealthStatus: status,
		}
		health.Components = append(health.Components, result)

		if !status.Healthy {
			health.OverallHealthy = false
		}
	}

	return health
}

// GetSystemHealth returns the current system health status
func GetSystemHealth() SystemHealth {
	aggregator := NewHealthAggregator()
	return aggregator.CheckSystemHealth()
}

