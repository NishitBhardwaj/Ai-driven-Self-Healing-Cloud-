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

// ExplainAction provides human-readable explanation for scaling actions
func (a *ScalingAgent) ExplainAction(input interface{}, output interface{}) string {
	var problem, action, reason string
	var cpuUsage, memoryUsage float64
	var currentReplicas, newReplicas int
	
	// Parse input to extract metrics
	if inputMap, ok := input.(map[string]interface{}); ok {
		if cpu, ok := inputMap["cpu_usage"].(float64); ok {
			cpuUsage = cpu
		}
		if mem, ok := inputMap["memory_usage"].(float64); ok {
			memoryUsage = mem
		}
		if replicas, ok := inputMap["replicas"].(int); ok {
			currentReplicas = replicas
		}
	}
	
	// Parse output to extract action
	if outputMap, ok := output.(map[string]interface{}); ok {
		if actionTaken, ok := outputMap["action"].(string); ok {
			action = actionTaken
		}
		if replicas, ok := outputMap["replicas"].(int); ok {
			newReplicas = replicas
		}
	}
	
	// Build problem description
	if cpuUsage > 0 {
		if cpuUsage > 90 {
			problem = fmt.Sprintf("CPU usage exceeded 90%% (current: %.1f%%)", cpuUsage*100)
		} else if cpuUsage > 85 {
			problem = fmt.Sprintf("CPU usage is high (%.1f%%)", cpuUsage*100)
		}
	}
	if memoryUsage > 0 && problem == "" {
		if memoryUsage > 90 {
			problem = fmt.Sprintf("memory usage exceeded 90%% (current: %.1f%%)", memoryUsage*100)
		}
	}
	if problem == "" {
		problem = "resource utilization exceeded threshold"
	}
	
	// Build action description
	if action == "scale_up" || action == "scale" {
		if newReplicas > currentReplicas {
			action = fmt.Sprintf("scaled up from %d to %d replicas", currentReplicas, newReplicas)
		} else {
			action = "scaled up the deployment"
		}
	} else if action == "scale_down" {
		if newReplicas < currentReplicas {
			action = fmt.Sprintf("scaled down from %d to %d replicas", currentReplicas, newReplicas)
		} else {
			action = "scaled down the deployment"
		}
	} else if action == "" {
		action = "adjusted the deployment scale"
	}
	
	// Build reason
	if cpuUsage > 90 || memoryUsage > 90 {
		reason = "to prevent service degradation and ensure optimal performance"
	} else if action == "scale_down" || (newReplicas < currentReplicas) {
		reason = "to optimize resource usage and reduce costs"
	} else {
		reason = "to handle increased load and maintain response times"
	}
	
	// Format explanation
	explanation := fmt.Sprintf("The agent detected that %s and %s %s.", problem, action, reason)
	
	return explanation
}

