package core

import (
	"encoding/json"
	"fmt"
	"sync"

	"github.com/ai-driven-self-healing-cloud/agents/events"
	"github.com/ai-driven-self-healing-cloud/config"
	"github.com/sirupsen/logrus"
)

// MessageRouter routes messages between agents via message bus
type MessageRouter struct {
	registry  *AgentRegistry
	messageBus config.MessageBus
	logger    *logrus.Logger
	handlers  map[string]func([]byte) // Topic -> Handler function
}

var globalRouter *MessageRouter
var routerOnce sync.Once

// GetRouter returns the global message router instance (singleton)
func GetRouter() *MessageRouter {
	routerOnce.Do(func() {
		globalRouter = &MessageRouter{
			registry: GetRegistry(),
			logger:   config.GetLogger(),
			handlers: make(map[string]func([]byte)),
		}
	})
	return globalRouter
}

// Init initializes the router and subscribes to all topics
func (r *MessageRouter) Init() error {
	r.logger.Info("Initializing message router")

	bus, err := config.ConnectMessageBus()
	if err != nil {
		return fmt.Errorf("failed to connect message bus: %w", err)
	}
	r.messageBus = bus

	// Register all topic handlers
	r.registerHandlers()

	// Subscribe to all topics
	topics := []string{
		events.TASK_CREATED,
		events.ERROR_DETECTED,
		events.CODE_FIX_REQUIRED,
		events.HEALING_REQUIRED,
		events.SCALE_REQUIRED,
		events.OPTIMIZATION_REQUIRED,
		events.SECURITY_ALERT,
		events.N8N_TRIGGER,
		events.METRICS_COLLECTED,
		events.ANOMALY_DETECTED,
		events.THRESHOLD_EXCEEDED,
	}

	for _, topic := range topics {
		if err := r.subscribeToTopic(topic); err != nil {
			r.logger.WithError(err).WithField("topic", topic).Warn("Failed to subscribe to topic")
		}
	}

	r.logger.WithField("topics", len(topics)).Info("Message router initialized")
	return nil
}

// registerHandlers registers handlers for each topic
func (r *MessageRouter) registerHandlers() {
	r.handlers[events.TASK_CREATED] = r.handleTaskCreated
	r.handlers[events.ERROR_DETECTED] = r.handleErrorDetected
	r.handlers[events.CODE_FIX_REQUIRED] = r.handleCodeFixRequired
	r.handlers[events.HEALING_REQUIRED] = r.handleHealingRequired
	r.handlers[events.SCALE_REQUIRED] = r.handleScaleRequired
	r.handlers[events.OPTIMIZATION_REQUIRED] = r.handleOptimizationRequired
	r.handlers[events.SECURITY_ALERT] = r.handleSecurityAlert
	r.handlers[events.N8N_TRIGGER] = r.handleN8NTrigger
	r.handlers[events.METRICS_COLLECTED] = r.handleMetricsCollected
	r.handlers[events.ANOMALY_DETECTED] = r.handleAnomalyDetected
	r.handlers[events.THRESHOLD_EXCEEDED] = r.handleThresholdExceeded
}

// subscribeToTopic subscribes to a message bus topic
func (r *MessageRouter) subscribeToTopic(topic string) error {
	if r.messageBus == nil {
		return fmt.Errorf("message bus not connected")
	}

	handler := r.handlers[topic]
	if handler == nil {
		handler = r.handleGenericEvent
	}

	return r.messageBus.Subscribe(topic, func(data []byte) {
		r.logger.WithFields(logrus.Fields{
			"topic": topic,
			"size":  len(data),
		}).Debug("Routing message")
		handler(data)
	})
}

// Route routes a message to the appropriate agent
func (r *MessageRouter) Route(topic string, payload interface{}) error {
	if r.messageBus == nil {
		return fmt.Errorf("message bus not connected")
	}

	data, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %w", err)
	}

	r.logger.WithField("topic", topic).Info("Routing message")
	return r.messageBus.Publish(topic, data)
}

// Event handlers for each topic type
func (r *MessageRouter) handleTaskCreated(data []byte) {
	r.logger.Info("Handling TASK_CREATED event")
	// Route to task-solving agent
	agent, err := r.registry.GetAgentByName("Task-Solving Agent")
	if err == nil {
		agent.ReceiveEvent(events.TASK_CREATED, data)
	}
}

func (r *MessageRouter) handleErrorDetected(data []byte) {
	r.logger.Info("Handling ERROR_DETECTED event")
	// Route to self-healing and coding agents
	if agent, err := r.registry.GetAgentByName("Self-Healing Agent"); err == nil {
		agent.ReceiveEvent(events.ERROR_DETECTED, data)
	}
	if agent, err := r.registry.GetAgentByName("Coding/Code-Fixer Agent"); err == nil {
		agent.ReceiveEvent(events.ERROR_DETECTED, data)
	}
}

func (r *MessageRouter) handleCodeFixRequired(data []byte) {
	r.logger.Info("Handling CODE_FIX_REQUIRED event")
	// Route to coding agent
	agent, err := r.registry.GetAgentByName("Coding/Code-Fixer Agent")
	if err == nil {
		agent.ReceiveEvent(events.CODE_FIX_REQUIRED, data)
	}
}

func (r *MessageRouter) handleHealingRequired(data []byte) {
	r.logger.Info("Handling HEALING_REQUIRED event")
	// Route to self-healing agent
	agent, err := r.registry.GetAgentByName("Self-Healing Agent")
	if err == nil {
		agent.ReceiveEvent(events.HEALING_REQUIRED, data)
	}
}

func (r *MessageRouter) handleScaleRequired(data []byte) {
	r.logger.Info("Handling SCALE_REQUIRED event")
	// Route to scaling agent
	agent, err := r.registry.GetAgentByName("Scaling Agent")
	if err == nil {
		agent.ReceiveEvent(events.SCALE_REQUIRED, data)
	}
}

func (r *MessageRouter) handleOptimizationRequired(data []byte) {
	r.logger.Info("Handling OPTIMIZATION_REQUIRED event")
	// Route to optimization agent
	agent, err := r.registry.GetAgentByName("Optimization Agent")
	if err == nil {
		agent.ReceiveEvent(events.OPTIMIZATION_REQUIRED, data)
	}
}

func (r *MessageRouter) handleSecurityAlert(data []byte) {
	r.logger.Info("Handling SECURITY_ALERT event")
	// Route to security agent
	agent, err := r.registry.GetAgentByName("Security Agent")
	if err == nil {
		agent.ReceiveEvent(events.SECURITY_ALERT, data)
	}
}

func (r *MessageRouter) handleN8NTrigger(data []byte) {
	r.logger.Info("Handling N8N_TRIGGER event")
	// Route to n8n agent
	agent, err := r.registry.GetAgentByName("n8n Workflow Agent")
	if err == nil {
		agent.ReceiveEvent(events.N8N_TRIGGER, data)
	}
}

func (r *MessageRouter) handleMetricsCollected(data []byte) {
	r.logger.Info("Handling METRICS_COLLECTED event")
	// Route to performance monitoring agent
	agent, err := r.registry.GetAgentByName("Performance Monitoring Agent")
	if err == nil {
		agent.ReceiveEvent(events.METRICS_COLLECTED, data)
	}
}

func (r *MessageRouter) handleAnomalyDetected(data []byte) {
	r.logger.Info("Handling ANOMALY_DETECTED event")
	// Route to performance monitoring and self-healing agents
	if agent, err := r.registry.GetAgentByName("Performance Monitoring Agent"); err == nil {
		agent.ReceiveEvent(events.ANOMALY_DETECTED, data)
	}
	if agent, err := r.registry.GetAgentByName("Self-Healing Agent"); err == nil {
		agent.ReceiveEvent(events.ANOMALY_DETECTED, data)
	}
}

func (r *MessageRouter) handleThresholdExceeded(data []byte) {
	r.logger.Info("Handling THRESHOLD_EXCEEDED event")
	// Route to scaling and performance monitoring agents
	if agent, err := r.registry.GetAgentByName("Scaling Agent"); err == nil {
		agent.ReceiveEvent(events.THRESHOLD_EXCEEDED, data)
	}
	if agent, err := r.registry.GetAgentByName("Performance Monitoring Agent"); err == nil {
		agent.ReceiveEvent(events.THRESHOLD_EXCEEDED, data)
	}
}

func (r *MessageRouter) handleGenericEvent(data []byte) {
	r.logger.Debug("Handling generic event")
	// Broadcast to all agents
	agents := r.registry.GetAllAgents()
	for _, agent := range agents {
		agent.ReceiveEvent("generic", data)
	}
}

