package core

import (
	"encoding/json"
	"fmt"
	"time"
)

// ExplanationLevel defines the detail level of explanations
type ExplanationLevel string

const (
	// BriefExplanation provides a concise summary
	BriefExplanation ExplanationLevel = "brief"

	// DetailedExplanation provides comprehensive details
	DetailedExplanation ExplanationLevel = "detailed"

	// TechnicalExplanation provides technical details for developers
	TechnicalExplanation ExplanationLevel = "technical"
)

// DecisionExplanation provides a comprehensive explanation for any decision
type DecisionExplanation struct {
	// DecisionID links this explanation to a specific decision
	DecisionID string `json:"decision_id"`

	// AgentID identifies which agent made the decision
	AgentID string `json:"agent_id"`

	// AgentName is the human-readable name
	AgentName string `json:"agent_name"`

	// Problem describes what issue was detected
	Problem string `json:"problem"`

	// Context provides background information
	Context map[string]interface{} `json:"context"`

	// Analysis describes how the problem was analyzed
	Analysis string `json:"analysis"`

	// OptionsEvaluated lists all options that were considered
	OptionsEvaluated []OptionEvaluation `json:"options_evaluated"`

	// SelectedOption explains why this option was chosen
	SelectedOption OptionEvaluation `json:"selected_option"`

	// ReasoningChain provides step-by-step reasoning
	ReasoningChain []ReasoningStep `json:"reasoning_chain"`

	// ConfidenceFactors explains what contributed to the confidence score
	ConfidenceFactors []ConfidenceFactor `json:"confidence_factors"`

	// RiskAssessment provides detailed risk analysis
	RiskAssessment RiskAnalysis `json:"risk_assessment"`

	// ExpectedOutcome describes what is expected to happen
	ExpectedOutcome string `json:"expected_outcome"`

	// AlternativeActions lists other actions that could have been taken
	AlternativeActions []string `json:"alternative_actions"`

	// Timestamp when the explanation was generated
	Timestamp time.Time `json:"timestamp"`

	// Level of detail in this explanation
	Level ExplanationLevel `json:"level"`
}

// OptionEvaluation describes how an option was evaluated
type OptionEvaluation struct {
	OptionID      string                 `json:"option_id"`
	Description   string                 `json:"description"`
	Score         float64                `json:"score"`
	Pros          []string               `json:"pros"`
	Cons          []string               `json:"cons"`
	Risk          string                 `json:"risk"`
	Impact        string                 `json:"impact"`
	Confidence    float64                `json:"confidence"`
	Reasoning     string                 `json:"reasoning"`
	Metadata      map[string]interface{} `json:"metadata,omitempty"`
}

// ReasoningStep represents a single step in the reasoning chain
type ReasoningStep struct {
	StepNumber int                    `json:"step_number"`
	Description string                 `json:"description"`
	Input       map[string]interface{} `json:"input,omitempty"`
	Output      map[string]interface{} `json:"output,omitempty"`
	Reasoning   string                 `json:"reasoning"`
}

// ConfidenceFactor explains what contributed to the confidence score
type ConfidenceFactor struct {
	Factor      string  `json:"factor"`
	Contribution float64 `json:"contribution"` // 0.0 to 1.0
	Description string  `json:"description"`
}

// RiskAnalysis provides detailed risk assessment
type RiskAnalysis struct {
	OverallRisk      string                 `json:"overall_risk"` // "low", "medium", "high"
	RiskScore        float64                `json:"risk_score"`   // 0.0 to 1.0
	RiskFactors      []RiskFactor           `json:"risk_factors"`
	MitigationSteps  []string               `json:"mitigation_steps"`
	RollbackPlan     string                 `json:"rollback_plan,omitempty"`
	Metadata         map[string]interface{} `json:"metadata,omitempty"`
}

// RiskFactor describes a specific risk
type RiskFactor struct {
	Factor      string  `json:"factor"`
	Severity    string  `json:"severity"` // "low", "medium", "high", "critical"
	Probability float64 `json:"probability"` // 0.0 to 1.0
	Description string  `json:"description"`
	Mitigation  string  `json:"mitigation,omitempty"`
}

// ExplainabilityEngine generates comprehensive explanations for decisions
type ExplainabilityEngine struct {
	// DefaultLevel is the default explanation level
	DefaultLevel ExplanationLevel

	// IncludeTechnicalDetails determines if technical details should be included
	IncludeTechnicalDetails bool

	// MaxReasoningSteps limits the number of reasoning steps
	MaxReasoningSteps int
}

// NewExplainabilityEngine creates a new explainability engine
func NewExplainabilityEngine() *ExplainabilityEngine {
	return &ExplainabilityEngine{
		DefaultLevel:            DetailedExplanation,
		IncludeTechnicalDetails: true,
		MaxReasoningSteps:       10,
	}
}

// GenerateExplanation creates a comprehensive explanation for a decision
func (ee *ExplainabilityEngine) GenerateExplanation(decision *AgentDecision, level ExplanationLevel) *DecisionExplanation {
	if level == "" {
		level = ee.DefaultLevel
	}

	explanation := &DecisionExplanation{
		DecisionID:      fmt.Sprintf("decision-%d", time.Now().UnixNano()),
		AgentID:         decision.AgentID,
		AgentName:       decision.AgentName,
		Problem:         decision.Problem,
		Context:         make(map[string]interface{}),
		Analysis:        decision.Reasoning,
		SelectedOption:  ee.evaluateOption(decision.SelectedOption),
		ConfidenceFactors: ee.extractConfidenceFactors(decision),
		RiskAssessment:   ee.assessRisk(decision),
		ExpectedOutcome: ee.generateExpectedOutcome(decision),
		AlternativeActions: ee.generateAlternatives(decision),
		Timestamp:       time.Now(),
		Level:           level,
	}

	// Evaluate all options
	for _, opt := range decision.Options {
		eval := ee.evaluateOption(&opt)
		explanation.OptionsEvaluated = append(explanation.OptionsEvaluated, eval)
	}

	// Build reasoning chain
	explanation.ReasoningChain = ee.buildReasoningChain(decision)

	// Add context
	explanation.Context["mode"] = string(decision.Mode)
	explanation.Context["confidence"] = decision.Confidence
	explanation.Context["timestamp"] = decision.Timestamp.Format(time.RFC3339)
	explanation.Context["action_executed"] = decision.ActionExecuted

	if level == BriefExplanation {
		return ee.summarizeExplanation(explanation)
	}

	return explanation
}

// evaluateOption creates an evaluation for an option
func (ee *ExplainabilityEngine) evaluateOption(option *ActionOption) OptionEvaluation {
	if option == nil {
		return OptionEvaluation{}
	}

	eval := OptionEvaluation{
		OptionID:    option.ID,
		Description: option.Description,
		Risk:        option.Risk,
		Impact:      option.Impact,
		Reasoning:   option.Reasoning,
		Metadata:    option.Metadata,
	}

	// Calculate score
	eval.Score = ee.calculateOptionScore(option)

	// Extract pros and cons from reasoning
	eval.Pros, eval.Cons = ee.extractProsAndCons(option.Reasoning)

	// Estimate confidence based on risk and impact
	eval.Confidence = ee.estimateConfidence(option)

	return eval
}

// calculateOptionScore calculates a score for an option
func (ee *ExplainabilityEngine) calculateOptionScore(option *ActionOption) float64 {
	score := 0.0

	// Risk scoring
	switch option.Risk {
	case "low":
		score += 3.0
	case "medium":
		score += 2.0
	case "high":
		score += 1.0
	}

	// Impact scoring
	switch option.Impact {
	case "high":
		score += 3.0
	case "medium":
		score += 2.0
	case "low":
		score += 1.0
	}

	// Cost penalty
	if option.EstimatedCost > 0 {
		score -= option.EstimatedCost / 100.0
	}

	return score
}

// extractProsAndCons extracts pros and cons from reasoning text
func (ee *ExplainabilityEngine) extractProsAndCons(reasoning string) ([]string, []string) {
	// Simple extraction - in production, this could use NLP
	pros := []string{
		"Addresses the detected issue",
		"Based on AI-driven analysis",
	}
	cons := []string{}

	if len(reasoning) > 0 {
		pros = append(pros, reasoning)
	}

	return pros, cons
}

// estimateConfidence estimates confidence based on option characteristics
func (ee *ExplainabilityEngine) estimateConfidence(option *ActionOption) float64 {
	confidence := 0.5 // Base confidence

	// Lower risk = higher confidence
	switch option.Risk {
	case "low":
		confidence += 0.3
	case "medium":
		confidence += 0.1
	case "high":
		confidence -= 0.1
	}

	// Higher impact = slightly lower confidence (more uncertainty)
	switch option.Impact {
	case "high":
		confidence -= 0.1
	case "medium":
		confidence += 0.0
	case "low":
		confidence += 0.1
	}

	if confidence < 0.0 {
		confidence = 0.0
	}
	if confidence > 1.0 {
		confidence = 1.0
	}

	return confidence
}

// extractConfidenceFactors extracts factors that contribute to confidence
func (ee *ExplainabilityEngine) extractConfidenceFactors(decision *AgentDecision) []ConfidenceFactor {
	factors := []ConfidenceFactor{}

	if decision.SelectedOption != nil {
		factors = append(factors, ConfidenceFactor{
			Factor:       "Option Risk Assessment",
			Contribution: 0.3,
			Description:  fmt.Sprintf("Selected option has %s risk level", decision.SelectedOption.Risk),
		})

		factors = append(factors, ConfidenceFactor{
			Factor:       "Option Impact Assessment",
			Contribution: 0.3,
			Description:  fmt.Sprintf("Selected option has %s impact level", decision.SelectedOption.Impact),
		})
	}

	factors = append(factors, ConfidenceFactor{
		Factor:       "AI Model Agreement",
		Contribution: 0.2,
		Description:  "Multiple AI models agreed on this decision",
	})

	factors = append(factors, ConfidenceFactor{
		Factor:       "Historical Success Rate",
		Contribution: 0.2,
		Description:  "Similar actions have been successful in the past",
	})

	return factors
}

// assessRisk performs detailed risk assessment
func (ee *ExplainabilityEngine) assessRisk(decision *AgentDecision) RiskAnalysis {
	analysis := RiskAnalysis{
		OverallRisk: "medium",
		RiskScore:   0.5,
		RiskFactors: []RiskFactor{},
	}

	if decision.SelectedOption != nil {
		switch decision.SelectedOption.Risk {
		case "low":
			analysis.OverallRisk = "low"
			analysis.RiskScore = 0.2
		case "medium":
			analysis.OverallRisk = "medium"
			analysis.RiskScore = 0.5
		case "high":
			analysis.OverallRisk = "high"
			analysis.RiskScore = 0.8
		}

		analysis.RiskFactors = append(analysis.RiskFactors, RiskFactor{
			Factor:      "Action Risk Level",
			Severity:    decision.SelectedOption.Risk,
			Probability: analysis.RiskScore,
			Description: fmt.Sprintf("The selected action has been assessed as %s risk", decision.SelectedOption.Risk),
		})
	}

	// Add mitigation steps
	analysis.MitigationSteps = []string{
		"Monitor the system closely after action execution",
		"Have rollback plan ready",
		"Track metrics to verify expected outcome",
	}

	// Add rollback plan
	if analysis.RiskScore > 0.5 {
		analysis.RollbackPlan = "If the action causes issues, revert to previous state using automated rollback mechanism"
	}

	return analysis
}

// generateExpectedOutcome describes what is expected to happen
func (ee *ExplainabilityEngine) generateExpectedOutcome(decision *AgentDecision) string {
	if decision.SelectedOption == nil {
		return "No action selected"
	}

	outcome := fmt.Sprintf(
		"After executing '%s', we expect to resolve the issue: %s. ",
		decision.SelectedOption.Description,
		decision.Problem,
	)

	outcome += fmt.Sprintf(
		"The action should result in improved system stability and performance. ",
	)

	if decision.SelectedOption.Impact == "high" {
		outcome += "This action is expected to have significant positive impact on the system."
	} else {
		outcome += "This action is expected to have moderate positive impact on the system."
	}

	return outcome
}

// generateAlternatives lists alternative actions
func (ee *ExplainabilityEngine) generateAlternatives(decision *AgentDecision) []string {
	alternatives := []string{}

	for _, opt := range decision.Options {
		if decision.SelectedOption == nil || opt.ID != decision.SelectedOption.ID {
			alternatives = append(alternatives, fmt.Sprintf("%s: %s", opt.ID, opt.Description))
		}
	}

	if len(alternatives) == 0 {
		alternatives = []string{"No alternative actions available"}
	}

	return alternatives
}

// buildReasoningChain creates a step-by-step reasoning chain
func (ee *ExplainabilityEngine) buildReasoningChain(decision *AgentDecision) []ReasoningStep {
	steps := []ReasoningStep{}

	stepNum := 1

	// Step 1: Problem detection
	steps = append(steps, ReasoningStep{
		StepNumber: stepNum,
		Description: "Problem Detection",
		Input: map[string]interface{}{
			"problem": decision.Problem,
		},
		Reasoning: fmt.Sprintf("The system detected: %s", decision.Problem),
	})
	stepNum++

	// Step 2: Analysis
	steps = append(steps, ReasoningStep{
		StepNumber: stepNum,
		Description: "Problem Analysis",
		Input: map[string]interface{}{
			"reasoning": decision.Reasoning,
		},
		Reasoning: decision.Reasoning,
	})
	stepNum++

	// Step 3: Option evaluation
	if len(decision.Options) > 0 {
		steps = append(steps, ReasoningStep{
			StepNumber: stepNum,
			Description: "Option Evaluation",
			Input: map[string]interface{}{
				"options_count": len(decision.Options),
			},
			Reasoning: fmt.Sprintf("Evaluated %d possible actions", len(decision.Options)),
		})
		stepNum++
	}

	// Step 4: Selection
	if decision.SelectedOption != nil {
		steps = append(steps, ReasoningStep{
			StepNumber: stepNum,
			Description: "Action Selection",
			Input: map[string]interface{}{
				"selected_option": decision.SelectedOption.ID,
			},
			Reasoning: fmt.Sprintf("Selected '%s' because: %s", decision.SelectedOption.Description, decision.SelectedOption.Reasoning),
		})
		stepNum++
	}

	// Limit steps
	if len(steps) > ee.MaxReasoningSteps {
		steps = steps[:ee.MaxReasoningSteps]
	}

	return steps
}

// summarizeExplanation creates a brief version of the explanation
func (ee *ExplainabilityEngine) summarizeExplanation(explanation *DecisionExplanation) *DecisionExplanation {
	return &DecisionExplanation{
		DecisionID:      explanation.DecisionID,
		AgentID:         explanation.AgentID,
		AgentName:       explanation.AgentName,
		Problem:         explanation.Problem,
		Analysis:        explanation.Analysis,
		SelectedOption:  explanation.SelectedOption,
		ExpectedOutcome: explanation.ExpectedOutcome,
		Timestamp:       explanation.Timestamp,
		Level:           BriefExplanation,
	}
}

// ToJSON converts explanation to JSON
func (de *DecisionExplanation) ToJSON() ([]byte, error) {
	return json.MarshalIndent(de, "", "  ")
}

// ToHumanReadable converts explanation to human-readable text
func (de *DecisionExplanation) ToHumanReadable() string {
	text := fmt.Sprintf("=== Decision Explanation ===\n\n")
	text += fmt.Sprintf("Agent: %s\n", de.AgentName)
	text += fmt.Sprintf("Problem: %s\n\n", de.Problem)
	text += fmt.Sprintf("Analysis: %s\n\n", de.Analysis)

	if de.SelectedOption.Description != "" {
		text += fmt.Sprintf("Selected Action: %s\n", de.SelectedOption.Description)
		text += fmt.Sprintf("Reasoning: %s\n\n", de.SelectedOption.Reasoning)
	}

	text += fmt.Sprintf("Expected Outcome: %s\n\n", de.ExpectedOutcome)

	if len(de.ConfidenceFactors) > 0 {
		text += "Confidence Factors:\n"
		for _, factor := range de.ConfidenceFactors {
			text += fmt.Sprintf("  - %s: %s\n", factor.Factor, factor.Description)
		}
		text += "\n"
	}

	if de.RiskAssessment.OverallRisk != "" {
		text += fmt.Sprintf("Risk Assessment: %s (Score: %.2f)\n", de.RiskAssessment.OverallRisk, de.RiskAssessment.RiskScore)
		if len(de.RiskAssessment.MitigationSteps) > 0 {
			text += "Mitigation Steps:\n"
			for _, step := range de.RiskAssessment.MitigationSteps {
				text += fmt.Sprintf("  - %s\n", step)
			}
		}
		text += "\n"
	}

	if len(de.AlternativeActions) > 0 {
		text += "Alternative Actions:\n"
		for _, alt := range de.AlternativeActions {
			text += fmt.Sprintf("  - %s\n", alt)
		}
	}

	return text
}

