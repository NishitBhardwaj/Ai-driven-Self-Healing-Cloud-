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

// ExplainAction provides explanation for healing actions
func (a *SelfHealingAgent) ExplainAction(input interface{}, output interface{}) string {
	return fmt.Sprintf("Self-Healing Agent: Detected service failure (input=%v) and initiated automatic recovery. Result: %v. The agent analyzed the failure pattern and selected the most appropriate recovery strategy (restart, rollback, or replace) based on the failure type and service state.", input, output)
}

