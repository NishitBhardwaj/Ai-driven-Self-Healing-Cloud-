package handlers

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/sirupsen/logrus"
)

// AgentStatusHandler handles agent status API requests
type AgentStatusHandler struct {
	registry *core.AgentRegistry
	logger   *logrus.Logger
}

// NewAgentStatusHandler creates a new agent status handler
func NewAgentStatusHandler(registry *core.AgentRegistry, logger *logrus.Logger) *AgentStatusHandler {
	return &AgentStatusHandler{
		registry: registry,
		logger:   logger,
	}
}

// AgentStatusResponse represents the response for agent status
type AgentStatusResponse struct {
	Agents []AgentStatus `json:"agents"`
}

// AgentStatus represents the status of a single agent
type AgentStatus struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Status      string    `json:"status"` // "running", "stopped", "error"
	LastAction  *Action   `json:"last_action,omitempty"`
	Confidence  float64   `json:"confidence"` // Confidence in Auto Mode (0.0 to 1.0)
	Explanation string    `json:"explanation,omitempty"`
	Mode        string    `json:"mode"` // "auto" or "manual"
	LastUpdate  time.Time `json:"last_update"`
}

// Action represents an action taken by an agent
type Action struct {
	Type        string    `json:"type"`
	Description string    `json:"description"`
	Timestamp   time.Time `json:"timestamp"`
	Success     bool      `json:"success"`
}

// GetAgentStatus handles GET /api/agents/status
func (h *AgentStatusHandler) GetAgentStatus(w http.ResponseWriter, r *http.Request) {
	h.logger.WithField("endpoint", "/api/agents/status").Info("Handling agent status request")

	// Get all registered agents
	agentsMap := h.registry.GetAllAgents()

	response := AgentStatusResponse{
		Agents: make([]AgentStatus, 0, len(agentsMap)),
	}

	// Convert agents to status response
	for _, agent := range agentsMap {
		status := AgentStatus{
			ID:     agent.GetID(),
			Name:   agent.GetName(),
			Status: string(agent.HealthCheck().Status),
			Mode:   "auto", // Default mode, can be retrieved from config
			LastUpdate: time.Now(),
		}

		// Get health status
		health := agent.HealthCheck()
		if health.Healthy {
			status.Status = "running"
		} else {
			status.Status = "stopped"
			if health.Message != "" {
				status.Status = "error"
			}
		}

		// Get last action from agent metadata (if available)
		// This would be stored by the agent when it performs actions
		if lastAction := h.getLastAction(agent.GetID()); lastAction != nil {
			status.LastAction = lastAction
		}

		// Get confidence and explanation from decision history
		// This would be retrieved from the decision store
		confidence, explanation := h.getLastDecisionInfo(agent.GetID())
		status.Confidence = confidence
		status.Explanation = explanation

		response.Agents = append(response.Agents, status)
	}

	// If no agents registered, return sample data for demo
	if len(response.Agents) == 0 {
		response.Agents = h.getSampleAgentStatuses()
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

// getLastAction retrieves the last action for an agent
func (h *AgentStatusHandler) getLastAction(agentID string) *Action {
	// In production, this would query a database or cache
	// For now, return sample data based on agent ID
	sampleActions := map[string]*Action{
		"self-healing-001": {
			Type:        "restart_pod",
			Description: "Restarted pod 'web-app-123'",
			Timestamp:   time.Now().Add(-5 * time.Minute),
			Success:     true,
		},
		"scaling-001": {
			Type:        "scale_up",
			Description: "Scaled up from 3 to 5 replicas",
			Timestamp:   time.Now().Add(-10 * time.Minute),
			Success:     true,
		},
		"security-001": {
			Type:        "block_ip",
			Description: "Blocked suspicious IP address",
			Timestamp:   time.Now().Add(-15 * time.Minute),
			Success:     true,
		},
		"monitoring-001": {
			Type:        "collect_metrics",
			Description: "Collected system metrics",
			Timestamp:   time.Now().Add(-1 * time.Minute),
			Success:     true,
		},
	}

	if action, exists := sampleActions[agentID]; exists {
		return action
	}
	return nil
}

// getLastDecisionInfo retrieves the last decision's confidence and explanation
func (h *AgentStatusHandler) getLastDecisionInfo(agentID string) (float64, string) {
	// In production, this would query the decision history
	// For now, return sample data
	sampleDecisions := map[string]struct {
		confidence  float64
		explanation string
	}{
		"self-healing-001": {
			confidence:  0.95,
			explanation: "Pod was restarted due to crash loop detection. The system detected repeated pod crashes and automatically restarted the pod to restore service.",
		},
		"scaling-001": {
			confidence:  0.85,
			explanation: "CPU usage exceeded 95% threshold. Scaled up from 3 to 5 replicas to distribute load and reduce CPU usage per instance.",
		},
		"security-001": {
			confidence:  0.92,
			explanation: "Multiple failed login attempts detected from suspicious IP. Blocked the IP address to prevent potential security breach.",
		},
		"monitoring-001": {
			confidence:  0.98,
			explanation: "Collected system metrics and updated health status. All systems operating normally.",
		},
	}

	if decision, exists := sampleDecisions[agentID]; exists {
		return decision.confidence, decision.explanation
	}

	// Default values
	return 0.90, "Agent is operating normally."
}

// getSampleAgentStatuses returns sample agent statuses for demo
func (h *AgentStatusHandler) getSampleAgentStatuses() []AgentStatus {
	return []AgentStatus{
		{
			ID:   "self-healing-001",
			Name: "Self-Healing Agent",
			Status: "running",
			LastAction: &Action{
				Type:        "restart_pod",
				Description: "Restarted pod 'web-app-123'",
				Timestamp:   time.Now().Add(-5 * time.Minute),
				Success:     true,
			},
			Confidence: 0.95,
			Explanation: "Pod was restarted due to crash loop detection. The system detected repeated pod crashes and automatically restarted the pod to restore service.",
			Mode:       "auto",
			LastUpdate: time.Now(),
		},
		{
			ID:   "scaling-001",
			Name: "Scaling Agent",
			Status: "running",
			LastAction: &Action{
				Type:        "scale_up",
				Description: "Scaled up from 3 to 5 replicas",
				Timestamp:   time.Now().Add(-10 * time.Minute),
				Success:     true,
			},
			Confidence: 0.85,
			Explanation: "CPU usage exceeded 95% threshold. Scaled up from 3 to 5 replicas to distribute load and reduce CPU usage per instance.",
			Mode:       "auto",
			LastUpdate: time.Now(),
		},
		{
			ID:   "security-001",
			Name: "Security Agent",
			Status: "running",
			LastAction: &Action{
				Type:        "block_ip",
				Description: "Blocked suspicious IP address",
				Timestamp:   time.Now().Add(-15 * time.Minute),
				Success:     true,
			},
			Confidence: 0.92,
			Explanation: "Multiple failed login attempts detected from suspicious IP. Blocked the IP address to prevent potential security breach.",
			Mode:       "auto",
			LastUpdate: time.Now(),
		},
		{
			ID:   "monitoring-001",
			Name: "Performance Monitoring Agent",
			Status: "running",
			LastAction: &Action{
				Type:        "collect_metrics",
				Description: "Collected system metrics",
				Timestamp:   time.Now().Add(-1 * time.Minute),
				Success:     true,
			},
			Confidence: 0.98,
			Explanation: "Collected system metrics and updated health status. All systems operating normally.",
			Mode:       "auto",
			LastUpdate: time.Now(),
		},
	}
}

