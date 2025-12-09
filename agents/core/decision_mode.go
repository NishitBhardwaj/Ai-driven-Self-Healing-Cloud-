package core

import (
	"encoding/json"
	"fmt"
	"time"
)

// Mode represents the decision-making mode of an agent
type Mode string

const (
	// AutoMode allows agents to act without user input
	AutoMode Mode = "auto"

	// ManualMode waits for user input before taking action
	ManualMode Mode = "manual"
)

// ActionOption represents a possible action the agent can take
type ActionOption struct {
	ID          string                 `json:"id"`
	Description string                 `json:"description"`
	Reasoning   string                 `json:"reasoning"`
	Risk        string                 `json:"risk"`        // "low", "medium", "high"
	Impact      string                 `json:"impact"`     // "low", "medium", "high"
	EstimatedCost float64              `json:"estimated_cost"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// AgentDecision represents a decision made by an agent
type AgentDecision struct {
	// Mode determines whether this is an auto or manual decision
	Mode Mode `json:"mode"`

	// AgentID identifies which agent made this decision
	AgentID string `json:"agent_id"`

	// AgentName is the human-readable name of the agent
	AgentName string `json:"agent_name"`

	// Problem describes the issue detected
	Problem string `json:"problem"`

	// Reasoning explains why this decision was made
	Reasoning string `json:"reasoning"`

	// Options are the possible actions (used in Manual Mode)
	Options []ActionOption `json:"options,omitempty"`

	// SelectedOption is the action chosen (by agent in Auto Mode, by user in Manual Mode)
	SelectedOption *ActionOption `json:"selected_option,omitempty"`

	// UserChoice is the user's selection in Manual Mode
	UserChoice string `json:"user_choice,omitempty"`

	// ActionExecuted indicates if the action has been executed
	ActionExecuted bool `json:"action_executed"`

	// ExecutionResult contains the result of the executed action
	ExecutionResult interface{} `json:"execution_result,omitempty"`

	// Explanation is the final explanation provided after execution
	Explanation string `json:"explanation"`

	// Timestamp when the decision was made
	Timestamp time.Time `json:"timestamp"`

	// Confidence score (0.0 to 1.0) indicating how confident the agent is
	Confidence float64 `json:"confidence"`

	// RiskAssessment evaluates the risk of the action
	RiskAssessment string `json:"risk_assessment"`

	// RequiresApproval indicates if this decision requires explicit approval
	RequiresApproval bool `json:"requires_approval"`
}

// DecisionHandler handles decision execution and user interaction
type DecisionHandler struct {
	// DefaultMode is the default mode for new decisions
	DefaultMode Mode

	// UserInputCallback is called when user input is needed (Manual Mode)
	UserInputCallback func(decision *AgentDecision) (string, error)

	// NotificationCallback is called to notify users of decisions
	NotificationCallback func(decision *AgentDecision) error

	// ApprovalRequiredForActions lists action types that always require approval
	ApprovalRequiredForActions []string
}

// NewDecisionHandler creates a new decision handler
func NewDecisionHandler(defaultMode Mode) *DecisionHandler {
	return &DecisionHandler{
		DefaultMode:                defaultMode,
		ApprovalRequiredForActions: []string{"delete", "rebuild", "rollback"},
	}
}

// CreateDecision creates a new agent decision
func (dh *DecisionHandler) CreateDecision(agentID, agentName, problem, reasoning string, options []ActionOption) *AgentDecision {
	mode := dh.DefaultMode

	// Check if any option requires approval
	requiresApproval := false
	for _, actionType := range dh.ApprovalRequiredForActions {
		for _, opt := range options {
			if opt.ID == actionType {
				requiresApproval = true
				mode = ManualMode
				break
			}
		}
		if requiresApproval {
			break
		}
	}

	decision := &AgentDecision{
		Mode:              mode,
		AgentID:           agentID,
		AgentName:         agentName,
		Problem:           problem,
		Reasoning:         reasoning,
		Options:           options,
		ActionExecuted:    false,
		Timestamp:         time.Now(),
		Confidence:        0.0,
		RequiresApproval:  requiresApproval,
	}

	return decision
}

// ExecuteDecision executes the decision based on the mode
func (d *AgentDecision) ExecuteDecision(handler *DecisionHandler, actionExecutor func(option *ActionOption) (interface{}, error)) error {
	if d.Mode == AutoMode {
		return d.executeAutoMode(handler, actionExecutor)
	} else {
		return d.executeManualMode(handler, actionExecutor)
	}
}

// executeAutoMode handles automatic decision execution
func (d *AgentDecision) executeAutoMode(handler *DecisionHandler, actionExecutor func(option *ActionOption) (interface{}, error)) error {
	// In Auto Mode, select the best option automatically
	if len(d.Options) > 0 && d.SelectedOption == nil {
		// Select the option with highest confidence or best risk/impact ratio
		d.SelectedOption = d.selectBestOption()
	}

	if d.SelectedOption == nil {
		return fmt.Errorf("no action option selected for auto mode")
	}

	// Execute the action
	fmt.Printf("[AUTO MODE] %s executing action: %s\n", d.AgentName, d.SelectedOption.Description)
	fmt.Printf("Reasoning: %s\n", d.Reasoning)

	result, err := actionExecutor(d.SelectedOption)
	if err != nil {
		d.Explanation = fmt.Sprintf("Action execution failed: %v. Original reasoning: %s", err, d.Reasoning)
		return err
	}

	d.ActionExecuted = true
	d.ExecutionResult = result
	d.Explanation = d.generateExplanation()

	// Notify user after execution
	if handler.NotificationCallback != nil {
		if err := handler.NotificationCallback(d); err != nil {
			// Log error but don't fail the execution
			fmt.Printf("Warning: Failed to send notification: %v\n", err)
		}
	}

	fmt.Printf("[AUTO MODE] Action completed. Explanation: %s\n", d.Explanation)
	return nil
}

// executeManualMode handles manual decision execution with user input
func (d *AgentDecision) executeManualMode(handler *DecisionHandler, actionExecutor func(option *ActionOption) (interface{}, error)) error {
	// In Manual Mode, present options to user and wait for selection
	fmt.Printf("[MANUAL MODE] %s detected issue: %s\n", d.AgentName, d.Problem)
	fmt.Printf("Reasoning: %s\n\n", d.Reasoning)
	fmt.Println("Available actions:")

	for i, opt := range d.Options {
		fmt.Printf("  [%d] %s\n", i+1, opt.Description)
		fmt.Printf("      Reasoning: %s\n", opt.Reasoning)
		fmt.Printf("      Risk: %s | Impact: %s\n", opt.Risk, opt.Impact)
		if opt.EstimatedCost > 0 {
			fmt.Printf("      Estimated Cost: $%.2f\n", opt.EstimatedCost)
		}
		fmt.Println()
	}

	// Get user input
	var selectedOption *ActionOption
	if handler.UserInputCallback != nil {
		choice, err := handler.UserInputCallback(d)
		if err != nil {
			return fmt.Errorf("failed to get user input: %w", err)
		}
		d.UserChoice = choice

		// Find the selected option
		for i, opt := range d.Options {
			if opt.ID == choice || fmt.Sprintf("%d", i+1) == choice {
				selectedOption = &d.Options[i]
				break
			}
		}
	} else {
		// Fallback: use first option if no callback provided
		if len(d.Options) > 0 {
			selectedOption = &d.Options[0]
			d.UserChoice = selectedOption.ID
		}
	}

	if selectedOption == nil {
		return fmt.Errorf("invalid option selected: %s", d.UserChoice)
	}

	d.SelectedOption = selectedOption

	// Execute the selected action
	fmt.Printf("[MANUAL MODE] User selected: %s\n", selectedOption.Description)
	fmt.Printf("Executing action...\n")

	result, err := actionExecutor(selectedOption)
	if err != nil {
		d.Explanation = fmt.Sprintf("Action execution failed: %v. User selected: %s. Original reasoning: %s", err, selectedOption.Description, d.Reasoning)
		return err
	}

	d.ActionExecuted = true
	d.ExecutionResult = result
	d.Explanation = d.generateExplanation()

	fmt.Printf("[MANUAL MODE] Action completed. Explanation: %s\n", d.Explanation)
	return nil
}

// selectBestOption automatically selects the best option based on risk, impact, and confidence
func (d *AgentDecision) selectBestOption() *ActionOption {
	if len(d.Options) == 0 {
		return nil
	}

	bestOption := &d.Options[0]
	bestScore := d.scoreOption(bestOption)

	for i := 1; i < len(d.Options); i++ {
		score := d.scoreOption(&d.Options[i])
		if score > bestScore {
			bestScore = score
			bestOption = &d.Options[i]
		}
	}

	return bestOption
}

// scoreOption calculates a score for an option (higher is better)
func (d *AgentDecision) scoreOption(option *ActionOption) float64 {
	score := 0.0

	// Risk scoring (lower risk = higher score)
	switch option.Risk {
	case "low":
		score += 3.0
	case "medium":
		score += 2.0
	case "high":
		score += 1.0
	}

	// Impact scoring (higher impact = higher score, but we want positive impact)
	switch option.Impact {
	case "high":
		score += 3.0
	case "medium":
		score += 2.0
	case "low":
		score += 1.0
	}

	// Cost scoring (lower cost = higher score)
	if option.EstimatedCost > 0 {
		score -= option.EstimatedCost / 100.0 // Normalize cost impact
	}

	// Confidence boost
	score += d.Confidence * 2.0

	return score
}

// generateExplanation creates a comprehensive explanation for the executed action
func (d *AgentDecision) generateExplanation() string {
	if d.SelectedOption == nil {
		return d.Reasoning
	}

	explanation := fmt.Sprintf(
		"%s detected: %s. ",
		d.AgentName,
		d.Problem,
	)

	explanation += fmt.Sprintf(
		"After analyzing the situation, the system determined that '%s' was the most appropriate action. ",
		d.SelectedOption.Description,
	)

	explanation += fmt.Sprintf(
		"Reasoning: %s. ",
		d.SelectedOption.Reasoning,
	)

	if d.SelectedOption.Risk != "" {
		explanation += fmt.Sprintf(
			"The action was assessed as %s risk with %s impact. ",
			d.SelectedOption.Risk,
			d.SelectedOption.Impact,
		)
	}

	if d.Confidence > 0 {
		explanation += fmt.Sprintf(
			"Confidence level: %.0f%%. ",
			d.Confidence*100,
		)
	}

	if d.Mode == ManualMode {
		explanation += "This action was approved by the user. "
	} else {
		explanation += "This action was executed automatically based on the system's analysis. "
	}

	if d.ExecutionResult != nil {
		explanation += fmt.Sprintf("Execution result: %v. ", d.ExecutionResult)
	}

	return explanation
}

// ToJSON converts the decision to JSON format
func (d *AgentDecision) ToJSON() ([]byte, error) {
	return json.MarshalIndent(d, "", "  ")
}

// FromJSON creates a decision from JSON
func FromJSON(data []byte) (*AgentDecision, error) {
	var decision AgentDecision
	err := json.Unmarshal(data, &decision)
	return &decision, err
}

// SetMode changes the decision mode
func (d *AgentDecision) SetMode(mode Mode) {
	d.Mode = mode
}

// AddOption adds an action option to the decision
func (d *AgentDecision) AddOption(option ActionOption) {
	d.Options = append(d.Options, option)
}

// SetConfidence sets the confidence score for the decision
func (d *AgentDecision) SetConfidence(confidence float64) {
	if confidence < 0.0 {
		confidence = 0.0
	}
	if confidence > 1.0 {
		confidence = 1.0
	}
	d.Confidence = confidence
}

// RequiresUserApproval checks if this decision requires user approval
func (d *AgentDecision) RequiresUserApproval() bool {
	return d.RequiresApproval || d.Mode == ManualMode
}

// GetStatus returns a human-readable status of the decision
func (d *AgentDecision) GetStatus() string {
	if !d.ActionExecuted {
		if d.Mode == ManualMode {
			return "Waiting for user approval"
		}
		return "Pending execution"
	}
	return "Executed"
}

