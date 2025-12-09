package core

import (
	"fmt"
	"strings"
)

// FormatExplanation creates a human-readable explanation in the standard format
// Format: "The agent detected that [problem] and [action] to [reason]."
func FormatExplanation(problem, action, reason string) string {
	// Ensure proper capitalization
	if problem != "" && !strings.HasPrefix(problem, strings.ToUpper(string(problem[0]))) {
		problem = strings.ToLower(problem)
	}
	if action != "" {
		action = strings.ToLower(action)
	}
	if reason != "" {
		reason = strings.ToLower(reason)
	}
	
	// Build explanation
	var parts []string
	
	if problem != "" {
		parts = append(parts, fmt.Sprintf("The agent detected that %s", problem))
	}
	
	if action != "" {
		if len(parts) > 0 {
			parts = append(parts, fmt.Sprintf("and %s", action))
		} else {
			parts = append(parts, fmt.Sprintf("The agent %s", action))
		}
	}
	
	if reason != "" {
		parts = append(parts, fmt.Sprintf("to %s", reason))
	}
	
	explanation := strings.Join(parts, " ")
	
	// Ensure it ends with a period
	if !strings.HasSuffix(explanation, ".") {
		explanation += "."
	}
	
	return explanation
}

// FormatAutoModeMessage creates the standard auto mode message
func FormatAutoModeMessage() string {
	return "Action automatically executed."
}

// FormatExplanationWithContext creates a detailed explanation with context
func FormatExplanationWithContext(agentName, problem, action, reason string, context map[string]interface{}) string {
	baseExplanation := FormatExplanation(problem, action, reason)
	
	// Add context if available
	if len(context) > 0 {
		var contextParts []string
		for key, value := range context {
			contextParts = append(contextParts, fmt.Sprintf("%s: %v", key, value))
		}
		if len(contextParts) > 0 {
			baseExplanation += fmt.Sprintf(" Context: %s.", strings.Join(contextParts, ", "))
		}
	}
	
	return baseExplanation
}

