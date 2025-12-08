package selfhealing

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/ai-driven-self-healing-cloud/agents/events"
	"github.com/sirupsen/logrus"
)

// Healer handles healing operations
type Healer struct {
	logger *logrus.Logger
}

// NewHealer creates a new Healer instance
func NewHealer() *Healer {
	return &Healer{
		logger: logrus.New(),
	}
}

// HealingRequest represents a request to heal a service
type HealingRequest struct {
	ServiceID   string                 `json:"service_id"`
	FailureType string                 `json:"failure_type"`
	Error       string                 `json:"error"`
	Metadata    map[string]interface{} `json:"metadata"`
}

// HealingResult represents the result of a healing operation
type HealingResult struct {
	ServiceID    string `json:"service_id"`
	Action       string `json:"action"`
	Success      bool   `json:"success"`
	Reasoning    string `json:"reasoning"`
	TimeTaken    int64  `json:"time_taken_ms"`
}

// Heal performs healing action on a service
func (h *Healer) Heal(request *HealingRequest) (*HealingResult, error) {
	h.logger.WithField("service_id", request.ServiceID).Info("Initiating healing process")

	// Determine healing strategy based on failure type
	action := h.determineHealingStrategy(request)
	
	// Execute healing action (placeholder)
	result := &HealingResult{
		ServiceID: request.ServiceID,
		Action:    action,
		Success:   true,
		Reasoning: fmt.Sprintf("Applied %s strategy for %s failure", action, request.FailureType),
	}

	h.logger.WithField("action", action).Info("Healing action completed")
	return result, nil
}

// determineHealingStrategy determines the best healing strategy using AI Engine (RL, GNN, LLM)
func (h *Healer) determineHealingStrategy(request *HealingRequest) string {
	// Try to use AI Engine integration
	aiAction, err := h.callAIIntegration(request)
	if err != nil {
		h.logger.WithError(err).Warn("AI Engine integration failed, using fallback strategy")
		return h.fallbackHealingStrategy(request)
	}
	
	if aiAction != "" {
		return aiAction
	}
	
	return h.fallbackHealingStrategy(request)
}

// callAIIntegration calls Python AI integration wrapper
func (h *Healer) callAIIntegration(request *HealingRequest) (string, error) {
	// Get script path
	scriptPath := filepath.Join(filepath.Dir(os.Args[0]), "agents", "self-healing", "ai_integration_wrapper.py")
	if _, err := os.Stat(scriptPath); os.IsNotExist(err) {
		// Try relative path
		scriptPath = "agents/self-healing/ai_integration_wrapper.py"
	}
	
	// Prepare input
	input := map[string]interface{}{
		"failure_info": map[string]interface{}{
			"service_id":   request.ServiceID,
			"type":         request.FailureType,
			"description": request.Error,
			"severity":     "high",
		},
		"system_state": map[string]interface{}{
			"cpu_usage":        0.0,
			"memory_usage":     0.0,
			"error_rate":       0.0,
			"network_latency":  0.0,
			"replicas":         1,
			"dependency_health": 1.0,
		},
		"dependency_graph_data": request.Metadata,
	}
	
	inputJSON, err := json.Marshal(input)
	if err != nil {
		return "", err
	}
	
	// Call Python script
	cmd := exec.Command("python3", scriptPath, "decide_healing_action")
	cmd.Stdin = bytes.NewReader(inputJSON)
	output, err := cmd.Output()
	if err != nil {
		return "", err
	}
	
	// Parse output
	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		return "", err
	}
	
	action, ok := result["action"].(string)
	if !ok {
		return "", fmt.Errorf("invalid action in AI response")
	}
	
	return action, nil
}

// fallbackHealingStrategy provides fallback strategy when AI is unavailable
func (h *Healer) fallbackHealingStrategy(request *HealingRequest) string {
	switch request.FailureType {
	case "crash", "timeout":
		return "restart"
	case "deployment_error", "config_error":
		return "rollback"
	case "resource_exhaustion", "pod_failure":
		return "replace"
	default:
		return "restart"
	}
}

// RestartService restarts a service
func (h *Healer) RestartService(serviceID string) error {
	h.logger.WithField("service_id", serviceID).Info("Restarting service")
	// TODO: Implement actual restart logic in Phase 5
	return nil
}

// RollbackService rolls back a service to previous version
func (h *Healer) RollbackService(serviceID string) error {
	h.logger.WithField("service_id", serviceID).Info("Rolling back service")
	// TODO: Implement actual rollback logic in Phase 5
	return nil
}

// ReplacePod replaces a failed pod
func (h *Healer) ReplacePod(serviceID string) error {
	h.logger.WithField("service_id", serviceID).Info("Replacing pod")
	// TODO: Implement actual pod replacement logic in Phase 5
	return nil
}

