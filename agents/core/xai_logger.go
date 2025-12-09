package core

import (
	"encoding/json"
	"fmt"
	"os"
	"time"
)

// ReasoningLogger provides logging for XAI explanations
type ReasoningLogger interface {
	// LogExplanation logs an action explanation
	LogExplanation(explanation *ActionExplanation) error

	// LogReasoningStep logs a single reasoning step
	LogReasoningStep(agentID string, step ReasoningStep) error
}

// ELKStackLogger logs to ELK Stack (Elasticsearch, Logstash, Kibana)
type ELKStackLogger struct {
	elasticsearchURL string
	indexName        string
	enabled          bool
}

// NewELKStackLogger creates a new ELK Stack logger
func NewELKStackLogger(elasticsearchURL, indexName string) *ELKStackLogger {
	return &ELKStackLogger{
		elasticsearchURL: elasticsearchURL,
		indexName:        indexName,
		enabled:          elasticsearchURL != "",
	}
}

// LogExplanation logs explanation to ELK Stack
func (e *ELKStackLogger) LogExplanation(explanation *ActionExplanation) error {
	if !e.enabled {
		// Fallback to file logging
		return e.logToFile(explanation)
	}

	// Create log document
	logDoc := map[string]interface{}{
		"@timestamp":        time.Now().Format(time.RFC3339),
		"agent_id":          explanation.AgentID,
		"agent_name":        explanation.AgentName,
		"action_taken":      explanation.ActionTaken,
		"reasoning":         explanation.Reasoning,
		"reasoning_chain":   explanation.ReasoningChain,
		"confidence_level":  explanation.ConfidenceLevel,
		"mode":              string(explanation.Mode),
		"alternative_actions": explanation.AlternativeActions,
		"context":           explanation.Context,
		"timestamp":         explanation.Timestamp.Format(time.RFC3339),
	}

	// In production, this would send to Elasticsearch
	// For now, log to file as fallback
	return e.logToFile(explanation)
}

// LogReasoningStep logs a reasoning step
func (e *ELKStackLogger) LogReasoningStep(agentID string, step ReasoningStep) error {
	logDoc := map[string]interface{}{
		"@timestamp":      time.Now().Format(time.RFC3339),
		"agent_id":         agentID,
		"step_number":      step.StepNumber,
		"step_description": step.Description,
		"reasoning":        step.Reasoning,
		"input":            step.Input,
		"output":           step.Output,
	}

	// In production, this would send to Elasticsearch
	// For now, log to file as fallback
	return e.logStepToFile(agentID, step)
}

// logToFile logs explanation to file (fallback)
func (e *ELKStackLogger) logToFile(explanation *ActionExplanation) error {
	logDir := "logs/xai"
	if err := os.MkdirAll(logDir, 0755); err != nil {
		return fmt.Errorf("failed to create log directory: %w", err)
	}

	logFile := fmt.Sprintf("%s/xai_%s.log", logDir, time.Now().Format("2006-01-02"))
	file, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return fmt.Errorf("failed to open log file: %w", err)
	}
	defer file.Close()

	logData, err := json.Marshal(explanation)
	if err != nil {
		return fmt.Errorf("failed to marshal explanation: %w", err)
	}

	logEntry := fmt.Sprintf("[%s] %s\n", time.Now().Format(time.RFC3339), string(logData))
	_, err = file.WriteString(logEntry)
	return err
}

// logStepToFile logs reasoning step to file
func (e *ELKStackLogger) logStepToFile(agentID string, step ReasoningStep) error {
	logDir := "logs/xai"
	if err := os.MkdirAll(logDir, 0755); err != nil {
		return fmt.Errorf("failed to create log directory: %w", err)
	}

	logFile := fmt.Sprintf("%s/reasoning_%s.log", logDir, time.Now().Format("2006-01-02"))
	file, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return fmt.Errorf("failed to open log file: %w", err)
	}
	defer file.Close()

	stepData := map[string]interface{}{
		"agent_id":         agentID,
		"step_number":      step.StepNumber,
		"step_description": step.Description,
		"reasoning":        step.Reasoning,
		"input":            step.Input,
		"output":           step.Output,
	}

	logData, err := json.Marshal(stepData)
	if err != nil {
		return fmt.Errorf("failed to marshal step: %w", err)
	}

	logEntry := fmt.Sprintf("[%s] %s\n", time.Now().Format(time.RFC3339), string(logData))
	_, err = file.WriteString(logEntry)
	return err
}

// ConsoleLogger logs to console (for development)
type ConsoleLogger struct{}

// NewConsoleLogger creates a new console logger
func NewConsoleLogger() *ConsoleLogger {
	return &ConsoleLogger{}
}

// LogExplanation logs explanation to console
func (c *ConsoleLogger) LogExplanation(explanation *ActionExplanation) error {
	fmt.Println("=== XAI Explanation ===")
	fmt.Printf("Agent: %s\n", explanation.AgentName)
	fmt.Printf("Action: %s\n", explanation.ActionTaken)
	fmt.Printf("Mode: %s\n", explanation.Mode)
	fmt.Printf("Confidence: %.0f%%\n", explanation.ConfidenceLevel*100)
	fmt.Printf("Reasoning: %s\n", explanation.Reasoning)
	fmt.Printf("Alternative Actions: %v\n", explanation.AlternativeActions)
	fmt.Println("=====================")
	return nil
}

// LogReasoningStep logs reasoning step to console
func (c *ConsoleLogger) LogReasoningStep(agentID string, step ReasoningStep) error {
	fmt.Printf("[%s] Step %d: %s - %s\n", agentID, step.StepNumber, step.Description, step.Reasoning)
	return nil
}

// CompositeLogger combines multiple loggers
type CompositeLogger struct {
	loggers []ReasoningLogger
}

// NewCompositeLogger creates a composite logger
func NewCompositeLogger(loggers ...ReasoningLogger) *CompositeLogger {
	return &CompositeLogger{
		loggers: loggers,
	}
}

// LogExplanation logs to all loggers
func (c *CompositeLogger) LogExplanation(explanation *ActionExplanation) error {
	var lastErr error
	for _, logger := range c.loggers {
		if err := logger.LogExplanation(explanation); err != nil {
			lastErr = err
		}
	}
	return lastErr
}

// LogReasoningStep logs to all loggers
func (c *CompositeLogger) LogReasoningStep(agentID string, step ReasoningStep) error {
	var lastErr error
	for _, logger := range c.loggers {
		if err := logger.LogReasoningStep(agentID, step); err != nil {
			lastErr = err
		}
	}
	return lastErr
}

// GetDefaultLogger returns the default logger based on environment
func GetDefaultLogger() ReasoningLogger {
	elkURL := os.Getenv("ELASTICSEARCH_URL")
	if elkURL != "" {
		return NewELKStackLogger(elkURL, "xai-explanations")
	}

	// Use composite logger with console and file
	return NewCompositeLogger(
		NewConsoleLogger(),
		NewELKStackLogger("", "xai-explanations"), // File fallback
	)
}

