package core

import (
	"encoding/json"
	"fmt"
	"time"
)

// Explainable interface allows agents to provide explanations for their actions
// This is part of the Explainability Layer for transparency in AI-driven decisions
type Explainable interface {
	// ExplainAction provides a human-readable explanation of why an action was taken
	// input: The input data or context that led to the action
	// output: The output or result of the action
	// Returns: A string explanation of the reasoning behind the action
	ExplainAction(input interface{}, output interface{}) string

	// ExplainActionDetailed provides a comprehensive explanation with reasoning chain
	// Returns: A DecisionExplanation with full details
	ExplainActionDetailed(input interface{}, output interface{}) *DecisionExplanation

	// GetReasoningChain returns the step-by-step reasoning process
	GetReasoningChain() []ReasoningStep

	// GetConfidence returns the confidence level for the action
	GetConfidence() float64

	// GetAlternativeActions returns alternative actions that could have been taken
	GetAlternativeActions() []string
}

// ActionExplanation represents a comprehensive explanation for an agent action
type ActionExplanation struct {
	// AgentID identifies which agent took the action
	AgentID string `json:"agent_id"`

	// AgentName is the human-readable name
	AgentName string `json:"agent_name"`

	// ActionTaken describes what action was performed
	ActionTaken string `json:"action_taken"`

	// Reasoning provides the explanation for why the action was taken
	Reasoning string `json:"reasoning"`

	// ReasoningChain provides step-by-step Chain-of-Thought reasoning
	ReasoningChain []ReasoningStep `json:"reasoning_chain"`

	// ConfidenceLevel indicates how confident the agent is (0.0 to 1.0)
	ConfidenceLevel float64 `json:"confidence_level"`

	// Mode indicates whether this was auto or manual mode
	Mode Mode `json:"mode"`

	// AlternativeActions lists other actions that could have been taken
	AlternativeActions []string `json:"alternative_actions"`

	// Context provides additional context about the decision
	Context map[string]interface{} `json:"context"`

	// Timestamp when the action was taken
	Timestamp time.Time `json:"timestamp"`

	// InputData is the input that led to this action
	InputData interface{} `json:"input_data,omitempty"`

	// OutputData is the result of the action
	OutputData interface{} `json:"output_data,omitempty"`
}

// XAIEngine provides explainability services for agents
type XAIEngine struct {
	// Logger for reasoning logs
	logger ReasoningLogger

	// LLMReasoning for Chain-of-Thought reasoning
	llmReasoning LLMReasoningService

	// ExplanationLevel determines the detail level
	explanationLevel ExplanationLevel
}

// LLMReasoningService interface for LLM-based reasoning
type LLMReasoningService interface {
	// GenerateChainOfThought generates CoT reasoning for an action
	GenerateChainOfThought(agentID, action, problem string, context map[string]interface{}) ([]ReasoningStep, error)

	// GenerateExplanation generates a human-readable explanation
	GenerateExplanation(agentID, action, problem string, reasoningChain []ReasoningStep) (string, error)
}

// ReasoningLogger interface for logging explanations
type ReasoningLogger interface {
	// LogExplanation logs an action explanation
	LogExplanation(explanation *ActionExplanation) error

	// LogReasoningStep logs a single reasoning step
	LogReasoningStep(agentID string, step ReasoningStep) error
}

// NewXAIEngine creates a new XAI engine
func NewXAIEngine(logger ReasoningLogger, llmReasoning LLMReasoningService) *XAIEngine {
	return &XAIEngine{
		logger:           logger,
		llmReasoning:     llmReasoning,
		explanationLevel: DetailedExplanation,
	}
}

// GenerateExplanation generates a comprehensive explanation for an agent action
func (x *XAIEngine) GenerateExplanation(
	agentID, agentName, actionTaken string,
	input, output interface{},
	mode Mode,
	confidence float64,
	problem string,
	context map[string]interface{},
) (*ActionExplanation, error) {
	explanation := &ActionExplanation{
		AgentID:       agentID,
		AgentName:     agentName,
		ActionTaken:   actionTaken,
		Mode:          mode,
		ConfidenceLevel: confidence,
		Context:       context,
		Timestamp:     time.Now(),
		InputData:     input,
		OutputData:    output,
	}

	// Generate Chain-of-Thought reasoning if LLM service is available
	if x.llmReasoning != nil {
		reasoningChain, err := x.llmReasoning.GenerateChainOfThought(
			agentID,
			actionTaken,
			problem,
			context,
		)
		if err != nil {
			// Fallback to basic reasoning if LLM fails
			explanation.ReasoningChain = x.generateBasicReasoningChain(agentID, actionTaken, problem)
		} else {
			explanation.ReasoningChain = reasoningChain
		}

		// Generate explanation text from reasoning chain
		reasoning, err := x.llmReasoning.GenerateExplanation(
			agentID,
			actionTaken,
			problem,
			explanation.ReasoningChain,
		)
		if err != nil {
			explanation.Reasoning = x.generateBasicReasoning(agentID, actionTaken, problem)
		} else {
			explanation.Reasoning = reasoning
		}
	} else {
		// Fallback to basic reasoning
		explanation.ReasoningChain = x.generateBasicReasoningChain(agentID, actionTaken, problem)
		explanation.Reasoning = x.generateBasicReasoning(agentID, actionTaken, problem)
	}

	// Generate alternative actions
	explanation.AlternativeActions = x.generateAlternativeActions(agentID, actionTaken, context)

	// Log the explanation
	if x.logger != nil {
		if err := x.logger.LogExplanation(explanation); err != nil {
			// Log error but don't fail
			fmt.Printf("Warning: Failed to log explanation: %v\n", err)
		}
	}

	return explanation, nil
}

// generateBasicReasoningChain creates a basic reasoning chain without LLM
func (x *XAIEngine) generateBasicReasoningChain(agentID, action, problem string) []ReasoningStep {
	steps := []ReasoningStep{
		{
			StepNumber:  1,
			Description: "Problem Detection",
			Input: map[string]interface{}{
				"problem": problem,
			},
			Reasoning: fmt.Sprintf("Detected issue: %s", problem),
		},
		{
			StepNumber:  2,
			Description: "Analysis",
			Input: map[string]interface{}{
				"agent_id": agentID,
			},
			Reasoning: fmt.Sprintf("%s analyzed the situation and determined action is needed", agentID),
		},
		{
			StepNumber:  3,
			Description: "Action Selection",
			Input: map[string]interface{}{
				"action": action,
			},
			Reasoning: fmt.Sprintf("Selected action: %s", action),
		},
		{
			StepNumber:  4,
			Description: "Execution",
			Input: map[string]interface{}{
				"action": action,
			},
			Reasoning: fmt.Sprintf("Executed action: %s", action),
		},
	}

	return steps
}

// generateBasicReasoning creates a basic explanation without LLM
func (x *XAIEngine) generateBasicReasoning(agentID, action, problem string) string {
	return fmt.Sprintf(
		"%s detected: %s. After analyzing the situation, the agent determined that '%s' was the most appropriate action to resolve the issue.",
		agentID,
		problem,
		action,
	)
}

// generateAlternativeActions generates alternative actions that could have been taken
func (x *XAIEngine) generateAlternativeActions(agentID, actionTaken string, context map[string]interface{}) []string {
	alternatives := []string{}

	// Generate alternatives based on agent type and action
	switch agentID {
	case "self-healing":
		if actionTaken != "restart_pod" {
			alternatives = append(alternatives, "restart_pod")
		}
		if actionTaken != "rebuild_deployment" {
			alternatives = append(alternatives, "rebuild_deployment")
		}
		if actionTaken != "rollback" {
			alternatives = append(alternatives, "rollback")
		}
	case "scaling":
		if actionTaken != "scale_up" {
			alternatives = append(alternatives, "scale_up")
		}
		if actionTaken != "scale_down" {
			alternatives = append(alternatives, "scale_down")
		}
		if actionTaken != "optimize" {
			alternatives = append(alternatives, "optimize")
		}
	case "security":
		if actionTaken != "block_ip" {
			alternatives = append(alternatives, "block_ip")
		}
		if actionTaken != "investigate" {
			alternatives = append(alternatives, "investigate")
		}
		if actionTaken != "alert" {
			alternatives = append(alternatives, "alert")
		}
	}

	return alternatives
}

// ToJSON converts explanation to JSON
func (ae *ActionExplanation) ToJSON() ([]byte, error) {
	return json.MarshalIndent(ae, "", "  ")
}

// ToHumanReadable converts explanation to human-readable text
func (ae *ActionExplanation) ToHumanReadable() string {
	text := fmt.Sprintf("=== Action Explanation ===\n\n")
	text += fmt.Sprintf("Agent: %s\n", ae.AgentName)
	text += fmt.Sprintf("Action: %s\n", ae.ActionTaken)
	text += fmt.Sprintf("Mode: %s\n", ae.Mode)
	text += fmt.Sprintf("Confidence: %.0f%%\n\n", ae.ConfidenceLevel*100)

	text += fmt.Sprintf("Reasoning:\n%s\n\n", ae.Reasoning)

	if len(ae.ReasoningChain) > 0 {
		text += "Reasoning Chain:\n"
		for _, step := range ae.ReasoningChain {
			text += fmt.Sprintf("  Step %d: %s\n", step.StepNumber, step.Description)
			text += fmt.Sprintf("    %s\n", step.Reasoning)
		}
		text += "\n"
	}

	if len(ae.AlternativeActions) > 0 {
		text += "Alternative Actions:\n"
		for _, alt := range ae.AlternativeActions {
			text += fmt.Sprintf("  - %s\n", alt)
		}
	}

	text += fmt.Sprintf("\nTimestamp: %s\n", ae.Timestamp.Format(time.RFC3339))

	return text
}

// GetConfidenceDescription returns a human-readable confidence description
func (ae *ActionExplanation) GetConfidenceDescription() string {
	confidence := ae.ConfidenceLevel
	if confidence >= 0.9 {
		return "Very High"
	} else if confidence >= 0.75 {
		return "High"
	} else if confidence >= 0.6 {
		return "Medium"
	} else if confidence >= 0.4 {
		return "Low"
	}
	return "Very Low"
}

// BaseExplainable provides a base implementation of Explainable
type BaseExplainable struct {
	agentID   string
	agentName string
	xaiEngine *XAIEngine
}

// NewBaseExplainable creates a new base explainable
func NewBaseExplainable(agentID, agentName string, xaiEngine *XAIEngine) *BaseExplainable {
	return &BaseExplainable{
		agentID:   agentID,
		agentName: agentName,
		xaiEngine: xaiEngine,
	}
}

// ExplainAction provides a basic explanation
func (be *BaseExplainable) ExplainAction(input interface{}, output interface{}) string {
	if be.xaiEngine == nil {
		return fmt.Sprintf("%s performed an action based on the input data.", be.agentName)
	}

	explanation, err := be.xaiEngine.GenerateExplanation(
		be.agentID,
		be.agentName,
		"action",
		input,
		output,
		AutoMode,
		0.8,
		"Action performed",
		nil,
	)
	if err != nil {
		return fmt.Sprintf("%s performed an action based on the input data.", be.agentName)
	}

	return explanation.Reasoning
}

// ExplainActionDetailed provides a detailed explanation
func (be *BaseExplainable) ExplainActionDetailed(input interface{}, output interface{}) *DecisionExplanation {
	if be.xaiEngine == nil {
		return &DecisionExplanation{
			AgentID:   be.agentID,
			AgentName: be.agentName,
			Problem:   "Action performed",
			Analysis:  fmt.Sprintf("%s performed an action.", be.agentName),
			Timestamp: time.Now(),
			Level:     BriefExplanation,
		}
	}

	explanation, err := be.xaiEngine.GenerateExplanation(
		be.agentID,
		be.agentName,
		"action",
		input,
		output,
		AutoMode,
		0.8,
		"Action performed",
		nil,
	)
	if err != nil {
		return &DecisionExplanation{
			AgentID:   be.agentID,
			AgentName: be.agentName,
			Problem:   "Action performed",
			Analysis:  fmt.Sprintf("%s performed an action.", be.agentName),
			Timestamp: time.Now(),
			Level:     BriefExplanation,
		}
	}

	// Convert ActionExplanation to DecisionExplanation
	return &DecisionExplanation{
		AgentID:         explanation.AgentID,
		AgentName:        explanation.AgentName,
		Problem:          "Action performed",
		Analysis:         explanation.Reasoning,
		ReasoningChain:    explanation.ReasoningChain,
		AlternativeActions: explanation.AlternativeActions,
		Timestamp:        explanation.Timestamp,
		Level:            DetailedExplanation,
	}
}

// GetReasoningChain returns the reasoning chain
func (be *BaseExplainable) GetReasoningChain() []ReasoningStep {
	return []ReasoningStep{
		{
			StepNumber:  1,
			Description: "Action performed",
			Reasoning:   fmt.Sprintf("%s performed an action.", be.agentName),
		},
	}
}

// GetConfidence returns the confidence level
func (be *BaseExplainable) GetConfidence() float64 {
	return 0.8
}

// GetAlternativeActions returns alternative actions
func (be *BaseExplainable) GetAlternativeActions() []string {
	return []string{}
}
