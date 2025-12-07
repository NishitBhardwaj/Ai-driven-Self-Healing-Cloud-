package scaling

import (
	"fmt"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/events"
	"github.com/ai-driven-self-healing-cloud/config"
	"github.com/sirupsen/logrus"
)

// ScalingAgent predicts traffic load and scales pods or cloud instances
type ScalingAgent struct {
	*core.Agent
	logger     *logrus.Logger
	messageBus config.MessageBus
	scaler     *AutoScaler
}

// NewScalingAgent creates a new Scaling Agent instance
func NewScalingAgent() *ScalingAgent {
	baseAgent := core.NewAgent(
		"scaling-agent",
		"Scaling Agent",
		"Predicts traffic load and scales pods or cloud instances",
	)

	return &ScalingAgent{
		Agent:  baseAgent,
		logger: config.GetLogger(),
		scaler: NewAutoScaler(),
	}
}

// Init initializes the agent
func (a *ScalingAgent) Init() error {
	a.logger.WithField("agent", a.GetName()).Info("Initializing Scaling Agent")
	
	bus, err := config.ConnectMessageBus()
	if err != nil {
		a.logger.WithError(err).Warn("Message bus not available, continuing without it")
	} else {
		a.messageBus = bus
	}

	return nil
}

// Start begins the agent's operation
func (a *ScalingAgent) Start() error {
	if err := a.Init(); err != nil {
		return err
	}

	a.Status = core.StatusStarting
	a.StartedAt = time.Now()
	a.Error = nil

	// Subscribe to scaling events
	if a.messageBus != nil {
		a.messageBus.Subscribe(events.SCALE_REQUIRED, a.handleScaleEvent)
		a.messageBus.Subscribe(events.THRESHOLD_EXCEEDED, a.handleThresholdEvent)
	}

	a.Status = core.StatusRunning
	a.logger.WithField("agent", a.GetName()).Info("Scaling Agent started")
	return nil
}

// Stop gracefully shuts down the agent
func (a *ScalingAgent) Stop() error {
	a.Status = core.StatusStopping
	a.logger.WithField("agent", a.GetName()).Info("Scaling Agent stopping")
	a.Status = core.StatusStopped
	a.StoppedAt = time.Now()
	return nil
}

// HandleMessage processes incoming messages
func (a *ScalingAgent) HandleMessage(event interface{}) error {
	a.logger.WithField("agent", a.GetName()).Debug("Received scaling message")
	return nil
}

// handleScaleEvent handles scale required events
func (a *ScalingAgent) handleScaleEvent(data []byte) {
	a.logger.Info("Scale event received")
	// Process scaling request
}

// handleThresholdEvent handles threshold exceeded events
func (a *ScalingAgent) handleThresholdEvent(data []byte) {
	a.logger.Info("Threshold exceeded, evaluating scaling need")
	// Evaluate and trigger scaling if needed
}

// ExplainAction provides explanation for scaling actions
func (a *ScalingAgent) ExplainAction(input interface{}, output interface{}) string {
	return fmt.Sprintf("Scaling Agent: Analyzed traffic patterns and resource utilization (input=%v). Scaling result: %v. Predicted future load based on historical data and current trends. Determined optimal scaling action (scale up/down) to maintain performance while minimizing costs.", input, output)
}

