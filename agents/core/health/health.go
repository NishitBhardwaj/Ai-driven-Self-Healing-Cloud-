package health

import (
	"github.com/ai-driven-self-healing-cloud/agents/core"
)

// HealthAggregator aggregates health checks from all system components
// Note: For comprehensive system health, use SystemHealthAggregator in system_health.go
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
// Returns a simplified health check result
func (ha *HealthAggregator) CheckSystemHealth() []core.HealthCheckResult {
	results := make([]core.HealthCheckResult, 0)

	// Check all registered agents
	agents := ha.registry.GetAllAgents()
	for name, agent := range agents {
		status := agent.HealthCheck()
		result := core.HealthCheckResult{
			Component:    name,
			HealthStatus: status,
		}
		results = append(results, result)
	}

	return results
}
