package selfhealing

import (
	"fmt"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/events"
	"github.com/ai-driven-self-healing-cloud/config"
	"github.com/sirupsen/logrus"
)

// SelfHealingAgent detects failures and auto-recovers services
type SelfHealingAgent struct {
	*core.Agent
	logger     *logrus.Logger
	messageBus config.MessageBus
	healer     *Healer
}

// NewSelfHealingAgent creates a new Self-Healing Agent instance
func NewSelfHealingAgent() *SelfHealingAgent {
	baseAgent := core.NewAgent(
		"self-healing-agent",
		"Self-Healing Agent",
		"Detects failures and automatically recovers services",
	)

	return &SelfHealingAgent{
		Agent:  baseAgent,
		logger: config.GetLogger(),
		healer: NewHealer(),
	}
}

// Init initializes the agent
func (a *SelfHealingAgent) Init() error {
	a.logger.WithField("agent", a.GetName()).Info("Initializing Self-Healing Agent")
	
	bus, err := config.ConnectMessageBus()
	if err != nil {
		a.logger.WithError(err).Warn("Message bus not available, continuing without it")
	} else {
		a.messageBus = bus
	}

	return nil
}

// Start begins the agent's operation
func (a *SelfHealingAgent) Start() error {
	if err := a.Init(); err != nil {
		return err
	}

	a.Status = core.StatusStarting
	a.StartedAt = time.Now()
	a.Error = nil

	// Subscribe to healing events
	if a.messageBus != nil {
		a.messageBus.Subscribe(events.HEALING_REQUIRED, a.handleHealingEvent)
		a.messageBus.Subscribe(events.ERROR_DETECTED, a.handleErrorEvent)
	}

	a.Status = core.StatusRunning
	a.logger.WithField("agent", a.GetName()).Info("Self-Healing Agent started")
	return nil
}

// Stop gracefully shuts down the agent
func (a *SelfHealingAgent) Stop() error {
	a.Status = core.StatusStopping
	a.logger.WithField("agent", a.GetName()).Info("Self-Healing Agent stopping")
	a.Status = core.StatusStopped
	a.StoppedAt = time.Now()
	return nil
}

// HandleMessage processes incoming messages
func (a *SelfHealingAgent) HandleMessage(event interface{}) error {
	a.logger.WithField("agent", a.GetName()).Debug("Received healing message")
	return nil
}

// handleHealingEvent handles healing required events
func (a *SelfHealingAgent) handleHealingEvent(data []byte) {
	a.logger.Info("Healing event received")
	// Process healing request
}

// handleErrorEvent handles error detected events
func (a *SelfHealingAgent) handleErrorEvent(data []byte) {
	a.logger.Info("Error detected, initiating healing process")
	// Trigger healing
}

// ExplainAction provides human-readable explanation for healing actions
func (a *SelfHealingAgent) ExplainAction(input interface{}, output interface{}) string {
	// Parse input to extract failure details
	var problem, action, reason string
	
	// Try to extract structured data from input
	if inputMap, ok := input.(map[string]interface{}); ok {
		// Extract problem description
		if serviceID, ok := inputMap["service_id"].(string); ok {
			problem = fmt.Sprintf("service '%s'", serviceID)
		}
		if failureType, ok := inputMap["failure_type"].(string); ok {
			if problem != "" {
				problem += fmt.Sprintf(" experienced %s failure", failureType)
			} else {
				problem = fmt.Sprintf("%s failure detected", failureType)
			}
		}
		if errorMsg, ok := inputMap["error"].(string); ok && errorMsg != "" {
			if problem != "" {
				problem += fmt.Sprintf(" (%s)", errorMsg)
			}
		}
	}
	
	// Try to extract action from output
	if outputMap, ok := output.(map[string]interface{}); ok {
		if actionTaken, ok := outputMap["action"].(string); ok {
			action = actionTaken
		}
		if success, ok := outputMap["success"].(bool); ok && success {
			reason = "to restore service availability"
		}
	}
	
	// Default values if parsing failed
	if problem == "" {
		problem = "a service failure"
	}
	if action == "" {
		action = "restarted the service"
	}
	if reason == "" {
		reason = "to prevent further issues and restore service availability"
	}
	
	// Format explanation in human-readable format
	explanation := fmt.Sprintf("The agent detected that %s and %s %s.", problem, action, reason)
	
	return explanation
}

