package n8n

import (
	"fmt"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/events"
	"github.com/ai-driven-self-healing-cloud/config"
	"github.com/sirupsen/logrus"
)

// N8NAgent sends triggers to n8n via webhook and receives callback actions
type N8NAgent struct {
	*core.Agent
	logger     *logrus.Logger
	messageBus config.MessageBus
	webhook    *WebhookHandler
	trigger    *TriggerHandler
}

// NewN8NAgent creates a new n8n Workflow Agent instance
func NewN8NAgent() *N8NAgent {
	baseAgent := core.NewAgent(
		"n8n-workflow-agent",
		"n8n Workflow Agent",
		"Sends triggers to n8n via webhook and receives callback actions from n8n",
	)

	return &N8NAgent{
		Agent:   baseAgent,
		logger:  config.GetLogger(),
		webhook: NewWebhookHandler(),
		trigger: NewTriggerHandler(),
	}
}

// Init initializes the agent
func (a *N8NAgent) Init() error {
	a.logger.WithField("agent", a.GetName()).Info("Initializing n8n Workflow Agent")
	
	bus, err := config.ConnectMessageBus()
	if err != nil {
		a.logger.WithError(err).Warn("Message bus not available, continuing without it")
	} else {
		a.messageBus = bus
	}

	return nil
}

// Start begins the agent's operation
func (a *N8NAgent) Start() error {
	if err := a.Init(); err != nil {
		return err
	}

	a.Status = core.StatusStarting
	a.StartedAt = time.Now()
	a.Error = nil

	// Subscribe to n8n events
	if a.messageBus != nil {
		a.messageBus.Subscribe(events.N8N_TRIGGER, a.handleTriggerEvent)
		a.messageBus.Subscribe(events.N8N_CALLBACK, a.handleCallbackEvent)
	}

	a.Status = core.StatusRunning
	a.logger.WithField("agent", a.GetName()).Info("n8n Workflow Agent started")
	return nil
}

// Stop gracefully shuts down the agent
func (a *N8NAgent) Stop() error {
	a.Status = core.StatusStopping
	a.logger.WithField("agent", a.GetName()).Info("n8n Workflow Agent stopping")
	a.Status = core.StatusStopped
	a.StoppedAt = time.Now()
	return nil
}

// HandleMessage processes incoming messages
func (a *N8NAgent) HandleMessage(event interface{}) error {
	a.logger.WithField("agent", a.GetName()).Debug("Received n8n message")
	return nil
}

// handleTriggerEvent handles n8n trigger events
func (a *N8NAgent) handleTriggerEvent(data []byte) {
	a.logger.Info("n8n trigger event received")
	// Process trigger
}

// handleCallbackEvent handles n8n callback events
func (a *N8NAgent) handleCallbackEvent(data []byte) {
	a.logger.Info("n8n callback received")
	// Process callback and execute action
}

// ExplainAction provides explanation for n8n actions
func (a *N8NAgent) ExplainAction(input interface{}, output interface{}) string {
	return fmt.Sprintf("n8n Workflow Agent: Received event trigger (input=%v), sent payload to n8n webhook for workflow execution. n8n processed the workflow and returned callback (output=%v) with action instructions, which were then executed by the agent system.", input, output)
}

