package logging

import (
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/sirupsen/logrus"
)

// AgentLogger provides integrated logging for agents
type AgentLogger struct {
	elkLogger *ELKLogger
	logger    *logrus.Logger
	agentID   string
	agentName string
}

// NewAgentLogger creates a new agent logger
func NewAgentLogger(agentID, agentName string) *AgentLogger {
	return &AgentLogger{
		elkLogger: GetDefaultELKLogger(),
		logger:    logrus.New(),
		agentID:   agentID,
		agentName: agentName,
	}
}

// LogActionTrigger logs when an action is triggered
func (al *AgentLogger) LogActionTrigger(action string, input interface{}, output interface{}) error {
	// Generate explanation
	explanation := &core.ActionExplanation{
		AgentID:       al.agentID,
		AgentName:     al.agentName,
		ActionTaken:   action,
		Timestamp:     time.Now(),
		ConfidenceLevel: 0.90, // Default confidence
		Mode:          core.AutoMode,
	}

	// Log to ELK
	err := al.elkLogger.LogAction(al.agentID, al.agentName, action, explanation)
	if err != nil {
		al.logger.WithError(err).Warn("Failed to log to ELK, using fallback")
	}

	// Also log to standard logger
	al.logger.WithFields(logrus.Fields{
		"agent_id":   al.agentID,
		"agent_name": al.agentName,
		"action":     action,
		"input":      input,
		"output":     output,
	}).Info("Action triggered")

	return err
}

// LogError logs an error with context
func (al *AgentLogger) LogError(err error, context map[string]interface{}) error {
	// Log to ELK
	elkErr := al.elkLogger.LogError(al.agentID, al.agentName, err, context)
	if elkErr != nil {
		al.logger.WithError(elkErr).Warn("Failed to log error to ELK")
	}

	// Also log to standard logger
	fields := logrus.Fields{
		"agent_id":   al.agentID,
		"agent_name": al.agentName,
	}
	for k, v := range context {
		fields[k] = v
	}

	al.logger.WithFields(fields).WithError(err).Error("Agent error occurred")

	return elkErr
}

// LogExplanation logs an explanation with confidence
func (al *AgentLogger) LogExplanation(explanation *core.ActionExplanation) error {
	// Log to ELK
	err := al.elkLogger.LogExplanation(al.agentID, al.agentName, explanation)
	if err != nil {
		al.logger.WithError(err).Warn("Failed to log explanation to ELK")
	}

	// Also log to standard logger
	al.logger.WithFields(logrus.Fields{
		"agent_id":        al.agentID,
		"agent_name":      al.agentName,
		"action":          explanation.ActionTaken,
		"confidence":      explanation.ConfidenceLevel,
		"mode":            string(explanation.Mode),
		"explanation":     explanation.Reasoning,
	}).Info("Action explanation")

	return err
}

// LogConfidence logs confidence level for a decision
func (al *AgentLogger) LogConfidence(confidence float64, mode string, reasoning string) error {
	// Log to ELK
	err := al.elkLogger.LogConfidence(al.agentID, al.agentName, confidence, mode, reasoning)
	if err != nil {
		al.logger.WithError(err).Warn("Failed to log confidence to ELK")
	}

	// Also log to standard logger
	al.logger.WithFields(logrus.Fields{
		"agent_id":   al.agentID,
		"agent_name": al.agentName,
		"confidence": confidence,
		"mode":       mode,
		"reasoning":  reasoning,
	}).Info("Decision confidence")

	return err
}

// LogEvent logs an event received by the agent
func (al *AgentLogger) LogEvent(eventType string, payload interface{}) error {
	// Log to ELK
	err := al.elkLogger.LogEvent(al.agentID, al.agentName, eventType, payload)
	if err != nil {
		al.logger.WithError(err).Warn("Failed to log event to ELK")
	}

	// Also log to standard logger
	al.logger.WithFields(logrus.Fields{
		"agent_id":   al.agentID,
		"agent_name": al.agentName,
		"event_type": eventType,
		"payload":    payload,
	}).Info("Event received")

	return err
}

// Close closes the logger
func (al *AgentLogger) Close() error {
	return al.elkLogger.Close()
}

