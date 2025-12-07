package health

import (
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/config"
)

// SystemHealth represents the overall health of the entire system
type SystemHealth struct {
	OverallHealthy   bool                      `json:"overall_healthy"`
	Agents           map[string]core.HealthStatus `json:"agents"`
	MessageBusStatus string                    `json:"message_bus_status"`
	LLMConnectivity  LLMStatus                 `json:"llm_connectivity"`
	CheckedAt        time.Time                 `json:"checked_at"`
}

// LLMStatus represents LLM API connectivity status
type LLMStatus struct {
	OpenRouter bool   `json:"openrouter"`
	Gemini     bool   `json:"gemini"`
	Message    string `json:"message"`
}

// SystemHealthAggregator aggregates health from all system components
type SystemHealthAggregator struct {
	registry *core.AgentRegistry
}

// NewSystemHealthAggregator creates a new system health aggregator
func NewSystemHealthAggregator() *SystemHealthAggregator {
	return &SystemHealthAggregator{
		registry: core.GetRegistry(),
	}
}

// GetSystemHealth performs comprehensive health check of entire system
func (sha *SystemHealthAggregator) GetSystemHealth() SystemHealth {
	health := SystemHealth{
		Agents:         make(map[string]core.HealthStatus),
		CheckedAt:      time.Now(),
		OverallHealthy: true,
	}

	// Check all agents
	agents := sha.registry.GetAllAgents()
	for name, agent := range agents {
		agentHealth := agent.HealthCheck()
		health.Agents[name] = agentHealth
		if !agentHealth.Healthy {
			health.OverallHealthy = false
		}
	}

	// Check message bus
	health.MessageBusStatus = sha.checkMessageBus()

	// Check LLM connectivity
	health.LLMConnectivity = sha.checkLLMConnectivity()

	return health
}

// checkMessageBus checks message bus connectivity
func (sha *SystemHealthAggregator) checkMessageBus() string {
	bus, err := config.ConnectMessageBus()
	if err != nil {
		return "disconnected"
	}
	if bus != nil && bus.IsConnected() {
		return "connected"
	}
	return "disconnected"
}

// checkLLMConnectivity checks LLM API connectivity
func (sha *SystemHealthAggregator) checkLLMConnectivity() LLMStatus {
	status := LLMStatus{
		OpenRouter: false,
		Gemini:     false,
		Message:    "",
	}

	cfg := config.GetConfig()
	if cfg == nil {
		status.Message = "Config not loaded"
		return status
	}

	// Quick connectivity test (simplified - full test in Phase 5)
	if cfg.OpenRouterAPIKey != "" {
		status.OpenRouter = true
	}
	if cfg.GeminiAPIKey != "" {
		status.Gemini = true
	}

	if status.OpenRouter && status.Gemini {
		status.Message = "All LLM APIs available"
	} else if status.OpenRouter || status.Gemini {
		status.Message = "Partial LLM connectivity"
	} else {
		status.Message = "No LLM connectivity"
	}

	return status
}

// GetSystemHealth returns the current system health (convenience function)
func GetSystemHealth() SystemHealth {
	aggregator := NewSystemHealthAggregator()
	return aggregator.GetSystemHealth()
}

