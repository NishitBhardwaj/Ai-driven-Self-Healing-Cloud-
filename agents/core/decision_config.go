package core

import (
	"encoding/json"
	"os"
	"path/filepath"
)

// DecisionConfig holds configuration for decision-making modes
type DecisionConfig struct {
	// DefaultMode is the default mode for all agents
	DefaultMode Mode `json:"default_mode"`

	// AgentModes allows per-agent mode configuration
	AgentModes map[string]Mode `json:"agent_modes"`

	// AutoApproveActions lists action types that can be auto-approved even in manual mode
	AutoApproveActions []string `json:"auto_approve_actions"`

	// RequireApprovalForActions lists action types that always require approval
	RequireApprovalForActions []string `json:"require_approval_for_actions"`

	// ConfidenceThreshold is the minimum confidence for auto-mode execution
	ConfidenceThreshold float64 `json:"confidence_threshold"`

	// NotificationEnabled determines if users should be notified of auto-mode actions
	NotificationEnabled bool `json:"notification_enabled"`

	// ExplanationLevel is the default explanation detail level
	ExplanationLevel ExplanationLevel `json:"explanation_level"`
}

// DefaultDecisionConfig returns the default configuration
func DefaultDecisionConfig() *DecisionConfig {
	return &DecisionConfig{
		DefaultMode: AutoMode,
		AgentModes: map[string]Mode{
			"self-healing":   AutoMode,
			"scaling":        AutoMode,
			"security":       ManualMode, // Security actions should be reviewed
			"coding":         ManualMode, // Code changes should be reviewed
			"monitoring":     AutoMode,
		},
		AutoApproveActions: []string{
			"restart_pod",
			"scale_up",
			"collect_metrics",
		},
		RequireApprovalForActions: []string{
			"delete",
			"rebuild",
			"rollback",
			"code_change",
		},
		ConfidenceThreshold:  0.7,
		NotificationEnabled: true,
		ExplanationLevel:     DetailedExplanation,
	}
}

// LoadDecisionConfig loads configuration from a file
func LoadDecisionConfig(configPath string) (*DecisionConfig, error) {
	if configPath == "" {
		// Try default locations
		configPath = "config/decision_config.json"
		if _, err := os.Stat(configPath); os.IsNotExist(err) {
			return DefaultDecisionConfig(), nil
		}
	}

	data, err := os.ReadFile(configPath)
	if err != nil {
		return DefaultDecisionConfig(), err
	}

	var config DecisionConfig
	if err := json.Unmarshal(data, &config); err != nil {
		return DefaultDecisionConfig(), err
	}

	return &config, nil
}

// SaveDecisionConfig saves configuration to a file
func (dc *DecisionConfig) SaveDecisionConfig(configPath string) error {
	if configPath == "" {
		configPath = "config/decision_config.json"
	}

	// Create directory if it doesn't exist
	dir := filepath.Dir(configPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}

	data, err := json.MarshalIndent(dc, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(configPath, data, 0644)
}

// GetModeForAgent returns the mode for a specific agent
func (dc *DecisionConfig) GetModeForAgent(agentID string) Mode {
	if mode, exists := dc.AgentModes[agentID]; exists {
		return mode
	}
	return dc.DefaultMode
}

// SetModeForAgent sets the mode for a specific agent
func (dc *DecisionConfig) SetModeForAgent(agentID string, mode Mode) {
	if dc.AgentModes == nil {
		dc.AgentModes = make(map[string]Mode)
	}
	dc.AgentModes[agentID] = mode
}

// CanAutoApprove checks if an action can be auto-approved
func (dc *DecisionConfig) CanAutoApprove(actionID string) bool {
	for _, autoAction := range dc.AutoApproveActions {
		if autoAction == actionID {
			return true
		}
	}
	return false
}

// RequiresApproval checks if an action requires approval
func (dc *DecisionConfig) RequiresApproval(actionID string) bool {
	for _, reqAction := range dc.RequireApprovalForActions {
		if reqAction == actionID {
			return true
		}
	}
	return false
}

// ShouldExecuteAuto checks if an action should be executed in auto mode
func (dc *DecisionConfig) ShouldExecuteAuto(agentID string, actionID string, confidence float64) bool {
	mode := dc.GetModeForAgent(agentID)

	// If manual mode, check if action can be auto-approved
	if mode == ManualMode {
		return dc.CanAutoApprove(actionID) && confidence >= dc.ConfidenceThreshold
	}

	// If auto mode, check if action requires approval
	if mode == AutoMode {
		if dc.RequiresApproval(actionID) {
			return false // Switch to manual mode
		}
		return confidence >= dc.ConfidenceThreshold
	}

	return false
}

