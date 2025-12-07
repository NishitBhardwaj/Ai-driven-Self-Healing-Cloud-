package core

// Explainable interface allows agents to provide explanations for their actions
// This is part of the Explainability Layer for transparency in AI-driven decisions
type Explainable interface {
	// ExplainAction provides a human-readable explanation of why an action was taken
	// input: The input data or context that led to the action
	// output: The output or result of the action
	// Returns: A string explanation of the reasoning behind the action
	ExplainAction(input interface{}, output interface{}) string
}

